from app.schemas.result import TicketResult
from app.schemas.search import SearchInput


class RankingService:
    def filter_results(
        self, results: list[TicketResult], search_input: SearchInput
    ) -> list[TicketResult]:
        filtered = results

        if search_input.direct_only:
            filtered = [result for result in filtered if result.direct]

        if search_input.max_price is not None:
            filtered = [
                result for result in filtered if result.price <= search_input.max_price
            ]

        return filtered

    def sort_results(self, results: list[TicketResult]) -> list[TicketResult]:
        return sorted(results, key=lambda result: (result.price, result.duration_minutes))
