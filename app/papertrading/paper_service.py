from pathlib import Path

from app.papertrading.models import PaperTrade
from app.papertrading.paper_trader import PaperTrader
from app.scanner.opportunity_scanner import OpportunityScanner
from app.storage.csv_store import CsvStore


class PaperTradingService:
    def __init__(self) -> None:
        self.scanner = OpportunityScanner()
        self.paper_trader = PaperTrader()
        self.store = CsvStore(Path("data") / "paper_trades.csv")

    def run_once(self, persist: bool = False) -> list[PaperTrade]:
        opportunities = self.scanner.scan_base_net_opportunities()
        paper_trades = self.paper_trader.evaluate(opportunities)

        if persist:
            self.store.append_rows(paper_trades)

        return paper_trades
