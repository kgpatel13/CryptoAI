from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.blockchain.chains import SUPPORTED_CHAINS
from app.market_intelligence.models import ChainReadiness, PairCandidate
from app.registry.dexes import get_dexes_for_chain
from app.registry.pairs import get_pairs_for_chain
from app.registry.tokens import get_token, get_tokens_for_chain


class MarketIntelligenceService:
    """Builds registry, pair-generation, provider-health, and readiness reports."""

    QUOTE_SYMBOLS = {"USDC", "USDT", "DAI"}

    def __init__(
        self,
        data_dir: Path | str = "data",
        report_dir: Path | str = "reports",
    ) -> None:
        self.data_dir = Path(data_dir)
        self.report_dir = Path(report_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def generate(self) -> dict[str, Any]:
        provider_rows = self._read_provider_rows()
        chains: list[ChainReadiness] = []
        pairs: list[PairCandidate] = []

        for chain_key, chain_config in SUPPORTED_CHAINS.items():
            chain_provider_rows = [
                row for row in provider_rows
                if str(row.get("chain", "")).lower() == chain_key.lower()
            ]
            chain_pairs = self._pair_candidates(chain_key)
            pairs.extend(chain_pairs)
            chains.append(
                self._chain_readiness(
                    chain_key=chain_key,
                    chain_name=chain_config.name,
                    pair_candidates=chain_pairs,
                    provider_rows=chain_provider_rows,
                )
            )

        payload = {
            "generated_at": self._utc_now(),
            "mode": "paper",
            "chain_count": len(chains),
            "pair_candidate_count": len(pairs),
            "configured_pair_count": sum(1 for pair in pairs if pair.configured),
            "overall_readiness_score": self._overall_score(chains),
            "chains": [chain.to_dict() for chain in chains],
            "pair_candidates": [pair.to_dict() for pair in sorted(pairs, key=lambda row: (row.chain, row.priority, row.pair))],
            "provider_summary": self._provider_summary(provider_rows),
            "notes": [
                "Market intelligence is paper-mode observability only.",
                "Readiness scores summarize registry completeness and observed provider health.",
                "Missing provider observations lower readiness until real health evidence exists.",
                "Readiness is not a live-trading approval.",
            ],
        }

        (self.report_dir / "market_intelligence.json").write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )
        self._write_markdown(payload)
        return payload

    def _chain_readiness(
        self,
        chain_key: str,
        chain_name: str,
        pair_candidates: list[PairCandidate],
        provider_rows: list[dict[str, Any]],
    ) -> ChainReadiness:
        tokens = get_tokens_for_chain(chain_key)
        dexes = get_dexes_for_chain(chain_key)
        configured_pairs = get_pairs_for_chain(chain_key)
        provider_score = self._provider_score(provider_rows)
        registry_score = self._registry_score(
            token_count=len(tokens),
            dex_count=len(dexes),
            configured_pair_count=len(configured_pairs),
            generated_pair_count=len(pair_candidates),
        )
        readiness_score = round((registry_score * 0.55) + (provider_score * 0.45))
        notes = self._readiness_notes(
            token_count=len(tokens),
            dex_count=len(dexes),
            configured_pair_count=len(configured_pairs),
            generated_pair_count=len(pair_candidates),
            provider_rows=provider_rows,
        )
        return ChainReadiness(
            chain=chain_key,
            name=chain_name,
            token_count=len(tokens),
            dex_count=len(dexes),
            configured_pair_count=len(configured_pairs),
            generated_pair_count=len(pair_candidates),
            provider_count=len(provider_rows),
            provider_score=provider_score,
            registry_score=registry_score,
            readiness_score=readiness_score,
            readiness_status=self._readiness_status(readiness_score),
            notes=notes,
        )

    def _pair_candidates(self, chain_key: str) -> list[PairCandidate]:
        tokens = get_tokens_for_chain(chain_key)
        dex_count = len(get_dexes_for_chain(chain_key))
        configured = {
            (pair.base_symbol.upper(), pair.quote_symbol.upper()): pair
            for pair in get_pairs_for_chain(chain_key)
        }
        quote_tokens = [token for token in tokens if token.symbol.upper() in self.QUOTE_SYMBOLS]
        base_tokens = [token for token in tokens if token.symbol.upper() not in self.QUOTE_SYMBOLS]

        candidates: list[PairCandidate] = []
        for base in base_tokens:
            for quote in quote_tokens:
                key = (base.symbol.upper(), quote.symbol.upper())
                configured_pair = configured.get(key)
                candidates.append(
                    PairCandidate(
                        chain=chain_key,
                        pair=f"{base.symbol}/{quote.symbol}",
                        base_symbol=base.symbol,
                        quote_symbol=quote.symbol,
                        configured=configured_pair is not None,
                        priority=configured_pair.priority if configured_pair else 50,
                        token_ready=get_token(chain_key, base.symbol) is not None
                        and get_token(chain_key, quote.symbol) is not None,
                        dex_count=dex_count,
                    )
                )
        return candidates

    def _registry_score(
        self,
        token_count: int,
        dex_count: int,
        configured_pair_count: int,
        generated_pair_count: int,
    ) -> int:
        score = 0
        if token_count >= 3:
            score += 30
        elif token_count > 0:
            score += 10

        if dex_count >= 2:
            score += 30
        elif dex_count > 0:
            score += 15

        if configured_pair_count >= 2:
            score += 25
        elif configured_pair_count == 1:
            score += 15

        if generated_pair_count >= configured_pair_count and generated_pair_count > 0:
            score += 15

        return min(100, score)

    @staticmethod
    def _provider_score(provider_rows: list[dict[str, Any]]) -> int:
        if not provider_rows:
            return 40
        scores = []
        for row in provider_rows:
            try:
                scores.append(int(row.get("score", 0)))
            except (TypeError, ValueError):
                scores.append(0)
        return round(sum(scores) / len(scores)) if scores else 40

    @staticmethod
    def _readiness_status(score: int) -> str:
        if score >= 80:
            return "READY_FOR_PAPER"
        if score >= 60:
            return "WATCH"
        return "NEEDS_DATA"

    @staticmethod
    def _overall_score(chains: list[ChainReadiness]) -> int:
        if not chains:
            return 0
        return round(sum(chain.readiness_score for chain in chains) / len(chains))

    @staticmethod
    def _readiness_notes(
        token_count: int,
        dex_count: int,
        configured_pair_count: int,
        generated_pair_count: int,
        provider_rows: list[dict[str, Any]],
    ) -> list[str]:
        notes = []
        if token_count < 3:
            notes.append("Token registry is sparse.")
        if dex_count < 2:
            notes.append("DEX registry needs at least two venues for comparison.")
        if configured_pair_count == 0:
            notes.append("No configured trading pairs.")
        if generated_pair_count == 0:
            notes.append("Pair generator found no candidates.")
        if not provider_rows:
            notes.append("No provider health observations yet.")
        if not notes:
            notes.append("Registry and provider inputs are sufficient for paper-mode monitoring.")
        return notes

    def _read_provider_rows(self) -> list[dict[str, Any]]:
        path = self.data_dir / "provider_health.json"
        if not path.exists():
            return []
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except json.JSONDecodeError:
            return []
        rows = payload.get("providers", [])
        return rows if isinstance(rows, list) else []

    @staticmethod
    def _provider_summary(provider_rows: list[dict[str, Any]]) -> dict[str, Any]:
        by_type: dict[str, int] = {}
        by_chain: dict[str, int] = {}
        scores = []
        for row in provider_rows:
            provider_type = str(row.get("provider_type", "unknown"))
            chain = MarketIntelligenceService._normalize_chain(row.get("chain", "unknown"))
            by_type[provider_type] = by_type.get(provider_type, 0) + 1
            by_chain[chain] = by_chain.get(chain, 0) + 1
            try:
                scores.append(int(row.get("score", 0)))
            except (TypeError, ValueError):
                pass
        return {
            "provider_count": len(provider_rows),
            "by_type": dict(sorted(by_type.items())),
            "by_chain": dict(sorted(by_chain.items())),
            "average_score": round(sum(scores) / len(scores)) if scores else None,
        }

    @staticmethod
    def _normalize_chain(chain: Any) -> str:
        normalized = str(chain).strip().lower()
        aliases = {
            "base": "base",
            "ethereum": "ethereum",
            "ethereum mainnet": "ethereum",
            "arbitrum one": "arbitrum",
            "arbitrum": "arbitrum",
            "polygon": "polygon",
        }
        return aliases.get(normalized, normalized)

    def _write_markdown(self, payload: dict[str, Any]) -> None:
        lines = [
            "# CryptoAI Market Intelligence",
            "",
            f"Generated: `{payload['generated_at']}`",
            "",
            "## Summary",
            "",
            f"- Mode: `{payload['mode']}`",
            f"- Overall readiness score: `{payload['overall_readiness_score']}`",
            f"- Chains: `{payload['chain_count']}`",
            f"- Pair candidates: `{payload['pair_candidate_count']}`",
            f"- Configured pairs: `{payload['configured_pair_count']}`",
            "",
            "## Chain Readiness",
            "",
            "| Chain | Tokens | DEXs | Pairs | Provider Score | Registry Score | Readiness | Status |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ]
        for chain in payload["chains"]:
            lines.append(
                f"| {chain['name']} | {chain['token_count']} | {chain['dex_count']} | "
                f"{chain['configured_pair_count']} | {chain['provider_score']} | "
                f"{chain['registry_score']} | {chain['readiness_score']} | {chain['readiness_status']} |"
            )

        lines += [
            "",
            "## Pair Candidates",
            "",
            "| Chain | Pair | Configured | Priority | DEX Count |",
            "|---|---|---|---:|---:|",
        ]
        for pair in payload["pair_candidates"]:
            lines.append(
                f"| {pair['chain']} | {pair['pair']} | {pair['configured']} | "
                f"{pair['priority']} | {pair['dex_count']} |"
            )

        lines += ["", "## Notes", ""]
        for note in payload["notes"]:
            lines.append(f"- {note}")
        (self.report_dir / "market_intelligence.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    payload = MarketIntelligenceService().generate()
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
