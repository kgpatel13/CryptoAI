from dataclasses import asdict
from pathlib import Path

from app.papertrading.models import PaperTrade
from app.papertrading.paper_trader import PaperTrader
from app.scanner.opportunity_scanner import OpportunityScanner
from app.storage.csv_store import CsvStore
from app.storage.sqlite_store import SQLiteStore


class PaperTradingService:
    def __init__(self) -> None:
        self.scanner = OpportunityScanner()
        self.paper_trader = PaperTrader()
        self.csv_store = CsvStore(Path("data") / "paper_trades.csv")
        self.sqlite_store = SQLiteStore(Path("data") / "cryptoai.db")

    def run_once(self, persist: bool = False) -> list[PaperTrade]:
        opportunities = self.scanner.scan_base_net_opportunities()
        paper_trades = self.paper_trader.evaluate(opportunities)

        if persist:
            self.csv_store.append_rows(paper_trades)
            for trade in paper_trades:
                self.sqlite_store.insert_paper_trade(asdict(trade))

        return paper_trades
