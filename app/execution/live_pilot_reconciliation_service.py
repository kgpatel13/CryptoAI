from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

from web3 import Web3

from app.blockchain.chains import SUPPORTED_CHAINS
from app.blockchain.rpc_client import RpcClient
from app.registry.tokens import get_token


ERC20_BALANCE_ABI = [
    {
        "name": "balanceOf",
        "type": "function",
        "stateMutability": "view",
        "inputs": [{"name": "account", "type": "address"}],
        "outputs": [{"name": "", "type": "uint256"}],
    }
]

BalanceReader = Callable[[str], dict[str, str]]


class LivePilotReconciliationService:
    """Read-only reconciliation for manual tiny-live pilot transactions."""

    def __init__(
        self,
        data_dir: Path | str = "data",
        report_dir: Path | str = "reports",
        balance_reader: BalanceReader | None = None,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.journal_file = self.data_dir / "live_pilot_orders.jsonl"
        self.output_json = self.report_dir / "live_pilot_reconciliation.json"
        self.output_md = self.report_dir / "live_pilot_reconciliation.md"
        self.balance_reader = balance_reader or self._read_base_balances

    def generate(self) -> dict[str, Any]:
        rows = self._read_journal()
        wallet = self._wallet(rows)
        approvals = [row for row in rows if str(row.get("mode", "")).lower() == "approve"]
        swaps = [row for row in rows if str(row.get("mode", "")).lower() == "swap"]
        failed = [row for row in rows if self._receipt_status(row) != 1]
        balances = self._safe_balances(wallet)
        status = self._status(rows=rows, swaps=swaps, failed=failed, balances=balances)
        payload = {
            "generated_at": self._utc_now(),
            "mode": "live_pilot_reconciliation",
            "overall_status": status,
            "live_trading_approval": False,
            "wallet_address": wallet,
            "journal_count": len(rows),
            "approval_count": len(approvals),
            "swap_count": len(swaps),
            "failed_transaction_count": len(failed),
            "total_gas_used": sum(self._int(row.get("send_result", {}).get("gas_used")) for row in rows),
            "total_swap_usd": self._fmt(sum((self._decimal(row.get("smoke_usd")) for row in swaps), Decimal("0"))),
            "latest_approval": self._compact(approvals[-1]) if approvals else None,
            "latest_swap": self._compact(swaps[-1]) if swaps else None,
            "current_balances": balances,
            "transactions": [self._compact(row) for row in rows[-20:]],
            "findings": self._findings(rows=rows, swaps=swaps, failed=failed, balances=balances),
            "notes": [
                "Live Pilot Reconciliation is read-only and never sends transactions.",
                "A reconciled tiny smoke test is not approval for continuous live arbitrage.",
                "Continuous live trading still requires a reviewed live executor, nonce handling, failure handling, and atomic route execution.",
            ],
        }
        self.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self.output_md.write_text(self._markdown(payload), encoding="utf-8")
        return payload

    def _status(self, *, rows: list[dict[str, Any]], swaps: list[dict[str, Any]], failed: list[dict[str, Any]], balances: dict[str, str]) -> str:
        if not rows:
            return "NO_LIVE_PILOT_JOURNAL"
        if failed:
            return "LIVE_PILOT_RECONCILE_ACTION"
        if not swaps:
            return "LIVE_APPROVAL_ONLY"
        if balances.get("status") != "OK":
            return "LIVE_PILOT_RECONCILE_ACTION"
        return "LIVE_PILOT_RECONCILED"

    def _findings(
        self,
        *,
        rows: list[dict[str, Any]],
        swaps: list[dict[str, Any]],
        failed: list[dict[str, Any]],
        balances: dict[str, str],
    ) -> list[dict[str, str]]:
        findings: list[dict[str, str]] = []
        if not rows:
            findings.append({"severity": "ACTION", "message": "No live pilot journal rows were found."})
        if failed:
            findings.append({"severity": "BLOCK", "message": f"{len(failed)} live pilot transaction(s) did not have receipt_status=1."})
        if not swaps:
            findings.append({"severity": "ACTION", "message": "No live smoke swap has been recorded yet."})
        if balances.get("status") != "OK":
            findings.append({"severity": "ACTION", "message": balances.get("reason", "Current wallet balances could not be read.")})
        if swaps and balances.get("USDC") == "0":
            findings.append({"severity": "WATCH", "message": "USDC balance is zero after live pilot."})
        if swaps:
            findings.append({"severity": "INFO", "message": "Tiny live smoke succeeded; keep continuous live arbitrage disabled until the live executor exists."})
        return findings

    def _safe_balances(self, wallet: str) -> dict[str, str]:
        if not wallet:
            return {"status": "ACTION", "reason": "No wallet address is available."}
        try:
            balances = self.balance_reader(wallet)
            return {"status": "OK", **balances}
        except Exception as exc:
            return {"status": "ACTION", "reason": f"{type(exc).__name__}: {exc}"}

    def _read_base_balances(self, wallet: str) -> dict[str, str]:
        client = RpcClient(SUPPORTED_CHAINS["base"])
        web3 = client.web3
        wallet_address = Web3.to_checksum_address(wallet)
        balances: dict[str, str] = {}
        for symbol in ["USDC", "WETH"]:
            token = get_token("base", symbol)
            if token is None:
                balances[symbol] = "0"
                continue
            contract = web3.eth.contract(address=Web3.to_checksum_address(token.address), abi=ERC20_BALANCE_ABI)
            raw = int(contract.functions.balanceOf(wallet_address).call())
            balances[symbol] = str(Decimal(raw) / Decimal(10**token.decimals))
        balances["ETH"] = str(Decimal(int(web3.eth.get_balance(wallet_address))) / Decimal(10**18))
        balances["block_number"] = str(int(web3.eth.block_number))
        return balances

    def _read_journal(self) -> list[dict[str, Any]]:
        if not self.journal_file.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line in self.journal_file.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                rows.append(payload)
        return rows

    @staticmethod
    def _wallet(rows: list[dict[str, Any]]) -> str:
        env_wallet = os.getenv("CRYPTOAI_LIVE_WALLET_ADDRESS", "").strip()
        if env_wallet:
            return env_wallet
        for row in reversed(rows):
            wallet = str(row.get("wallet_address", "")).strip()
            if wallet:
                return wallet
        return ""

    def _compact(self, row: dict[str, Any]) -> dict[str, Any]:
        send = row.get("send_result", {}) if isinstance(row.get("send_result"), dict) else {}
        return {
            "timestamp": row.get("timestamp"),
            "mode": row.get("mode"),
            "wallet_address": row.get("wallet_address"),
            "dex": row.get("dex"),
            "smoke_usd": row.get("smoke_usd"),
            "tx_hash": send.get("tx_hash"),
            "receipt_status": self._receipt_status(row),
            "block_number": send.get("block_number"),
            "gas_used": send.get("gas_used"),
        }

    @staticmethod
    def _receipt_status(row: dict[str, Any]) -> int:
        send = row.get("send_result", {}) if isinstance(row.get("send_result"), dict) else {}
        try:
            return int(send.get("receipt_status", 0))
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _decimal(value: Any) -> Decimal:
        try:
            return Decimal(str(value or "0"))
        except Exception:
            return Decimal("0")

    @staticmethod
    def _int(value: Any) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _fmt(value: Decimal) -> str:
        return str(value.quantize(Decimal("0.0000")))

    def _markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# Live Pilot Reconciliation",
            "",
            f"Generated: `{payload['generated_at']}`",
            f"- Overall status: `{payload['overall_status']}`",
            f"- Wallet: `{payload['wallet_address']}`",
            f"- Journal rows: `{payload['journal_count']}`",
            f"- Approvals: `{payload['approval_count']}`",
            f"- Swaps: `{payload['swap_count']}`",
            f"- Failed tx count: `{payload['failed_transaction_count']}`",
            f"- Total swap USD: `${payload['total_swap_usd']}`",
            f"- Total gas used: `{payload['total_gas_used']}`",
            "",
            "## Current Balances",
            "",
            "```json",
            json.dumps(payload["current_balances"], indent=2),
            "```",
            "",
            "## Latest Swap",
            "",
            "```json",
            json.dumps(payload["latest_swap"], indent=2),
            "```",
            "",
            "## Findings",
            "",
        ]
        lines.extend(f"- `{row['severity']}` {row['message']}" for row in payload["findings"])
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in payload["notes"])
        return "\n".join(lines) + "\n"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    payload = LivePilotReconciliationService().generate()
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
