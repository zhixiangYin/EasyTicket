from datetime import datetime, time, timedelta

from app.connectors.base import BaseConnector
from app.schemas.result import TicketResult
from app.schemas.search import SearchInput


class MockAConnector(BaseConnector):
    name = "mock_a"

    def search(self, search_input: SearchInput) -> list[TicketResult]:
        base_departure = datetime.combine(search_input.travel_date, time(hour=9))
        fetched_at = datetime.now()

        return [
            TicketResult(
                platform=self.name,
                origin=search_input.origin,
                destination=search_input.destination,
                depart_at=base_departure,
                arrive_at=base_departure + timedelta(hours=4),
                cabin_class=search_input.cabin_class,
                price=78.0,
                direct=True,
                transfer_count=0,
                deep_link="https://example.com/mock-a/direct",
                fetched_at=fetched_at,
            ),
            TicketResult(
                platform=self.name,
                origin=search_input.origin,
                destination=search_input.destination,
                depart_at=base_departure + timedelta(hours=2),
                arrive_at=base_departure + timedelta(hours=7),
                cabin_class=search_input.cabin_class,
                price=62.0,
                direct=False,
                transfer_count=1,
                deep_link="https://example.com/mock-a/transfer",
                fetched_at=fetched_at,
            ),
        ]
