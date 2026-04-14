from dataclasses import dataclass

from app.connectors.base import BaseConnector, ConnectorException
from app.schemas.result import TicketResult
from app.schemas.search import SearchInput
from app.services.ranking_service import RankingService


@dataclass(slots=True)
class ConnectorError:
    connector: str
    code: str
    message: str


@dataclass(slots=True)
class SearchExecutionResult:
    results: list[TicketResult]
    connector_errors: list[ConnectorError]


class SearchService:
    def __init__(
        self,
        connectors: list[BaseConnector],
        ranking_service: RankingService | None = None,
    ) -> None:
        self.connectors = connectors
        self.ranking_service = ranking_service or RankingService()

    def search(self, search_input: SearchInput) -> SearchExecutionResult:
        aggregated_results: list[TicketResult] = []
        connector_errors: list[ConnectorError] = []

        for connector in self.connectors:
            try:
                aggregated_results.extend(connector.search(search_input))
            except ConnectorException as exc:
                connector_errors.append(
                    ConnectorError(
                        connector=connector.name,
                        code=exc.code,
                        message=str(exc),
                    )
                )
            except Exception as exc:
                connector_errors.append(
                    ConnectorError(
                        connector=connector.name,
                        code="unexpected_connector_error",
                        message=str(exc),
                    )
                )

        filtered = self.ranking_service.filter_results(aggregated_results, search_input)
        return SearchExecutionResult(
            results=self.ranking_service.sort_results(filtered),
            connector_errors=connector_errors,
        )
