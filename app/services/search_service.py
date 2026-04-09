from app.connectors.base import BaseConnector
from app.schemas.result import TicketResult
from app.schemas.search import SearchInput
from app.services.ranking_service import RankingService


class SearchService:
    def __init__(
        self,
        connectors: list[BaseConnector],
        ranking_service: RankingService | None = None,
    ) -> None:
        self.connectors = connectors
        self.ranking_service = ranking_service or RankingService()

    def search(self, search_input: SearchInput) -> list[TicketResult]:
        aggregated_results: list[TicketResult] = []

        for connector in self.connectors:
            aggregated_results.extend(connector.search(search_input))

        filtered = self.ranking_service.filter_results(aggregated_results, search_input)
        return self.ranking_service.sort_results(filtered)
