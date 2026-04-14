from datetime import datetime, time, timedelta

from app.connectors.base import BaseConnector, ConnectorException
from app.schemas.result import TicketResult
from app.schemas.search import SearchInput


def make_search_input(
    *,
    max_price: float | None = 80.0,
    direct_only: bool = True,
) -> SearchInput:
    return SearchInput(
        origin="New York",
        destination="Boston",
        travel_date=datetime(2026, 4, 15).date(),
        passengers=2,
        cabin_class="economy",
        max_price=max_price,
        direct_only=direct_only,
    )


def make_ticket_result(
    *,
    platform: str = "mock",
    price: float = 78.0,
    direct: bool = True,
    transfer_count: int = 0,
    depart_hour: int = 9,
    duration_minutes: int = 240,
) -> TicketResult:
    search_input = make_search_input()
    depart_at = datetime.combine(search_input.travel_date, time(hour=depart_hour))

    return TicketResult(
        platform=platform,
        origin=search_input.origin,
        destination=search_input.destination,
        depart_at=depart_at,
        arrive_at=depart_at + timedelta(minutes=duration_minutes),
        cabin_class=search_input.cabin_class,
        price=price,
        direct=direct,
        transfer_count=transfer_count,
        deep_link=f"https://example.com/{platform}",
        fetched_at=datetime(2026, 4, 14, 12, 0),
    )


class StaticConnector(BaseConnector):
    name = "static"

    def __init__(self, results: list[TicketResult]) -> None:
        self.results = results

    def search(self, search_input: SearchInput) -> list[TicketResult]:
        return self.results


class FailingConnector(BaseConnector):
    name = "failing"

    def search(self, search_input: SearchInput) -> list[TicketResult]:
        raise ConnectorException(
            "connector unavailable",
            code="connector_unavailable",
        )


class UnexpectedFailingConnector(BaseConnector):
    name = "unexpected_failing"

    def search(self, search_input: SearchInput) -> list[TicketResult]:
        raise RuntimeError("unexpected failure")
