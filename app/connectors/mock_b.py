from datetime import datetime, time, timedelta

from app.connectors.base import BaseConnector
from app.schemas.result import TicketResult
from app.schemas.search import SearchInput


class MockBConnector(BaseConnector):
    name = "mock_b"
    display_name = "Mock Platform B"
    timeout_seconds = 2.0

    def search(self, search_input: SearchInput) -> list[TicketResult]:
        base_departure = datetime.combine(search_input.travel_date, time(hour=11, minute=30))
        fetched_at = datetime.now()

        return [
            TicketResult(
                platform=self.name,
                origin=search_input.origin,
                destination=search_input.destination,
                depart_at=base_departure,
                arrive_at=base_departure + timedelta(hours=3, minutes=20),
                cabin_class=search_input.cabin_class,
                price=89.0,
                direct=True,
                transfer_count=0,
                deep_link="https://example.com/mock-b/direct",
                fetched_at=fetched_at,
            ),
            TicketResult(
                platform=self.name,
                origin=search_input.origin,
                destination=search_input.destination,
                depart_at=base_departure + timedelta(hours=4),
                arrive_at=base_departure + timedelta(hours=8, minutes=45),
                cabin_class=search_input.cabin_class,
                price=71.5,
                direct=False,
                transfer_count=1,
                deep_link="https://example.com/mock-b/transfer",
                fetched_at=fetched_at,
            ),
        ]
