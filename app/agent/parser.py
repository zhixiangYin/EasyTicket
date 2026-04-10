import re
from datetime import date, timedelta

from app.agent.base import BaseSearchParser, ParsedSearchRequest
from app.schemas.search import SearchInput


WEEKDAY_NAMES = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


class NaturalLanguageSearchParser(BaseSearchParser):
    def parse(self, text: str, *, today: date | None = None) -> ParsedSearchRequest:
        normalized_text = " ".join(text.strip().split())
        if not normalized_text:
            raise ValueError("query cannot be empty")

        base_date = today or date.today()
        origin, destination = self._parse_route(normalized_text)
        travel_date = self._parse_travel_date(normalized_text, base_date)
        passengers = self._parse_passengers(normalized_text)
        cabin_class = self._parse_cabin_class(normalized_text)
        max_price = self._parse_max_price(normalized_text)
        direct_only = self._parse_direct_only(normalized_text)

        notes = [
            "Parsed query with rule-based extraction.",
            "This parser is a temporary learning step before adding an LLM.",
        ]

        return ParsedSearchRequest(
            search_input=SearchInput(
                origin=origin,
                destination=destination,
                travel_date=travel_date,
                passengers=passengers,
                cabin_class=cabin_class,
                max_price=max_price,
                direct_only=direct_only,
            ),
            notes=notes,
        )

    def _parse_route(self, text: str) -> tuple[str, str]:
        route_match = re.search(
            r"\bfrom\s+(?P<origin>.+?)\s+to\s+(?P<destination>.+?)(?=\s+(?:on|for|with|under|below|direct|tomorrow|today|next)\b|$)",
            text,
            flags=re.IGNORECASE,
        )
        if not route_match:
            raise ValueError(
                "Could not parse route. Use a phrase like 'from New York to Boston'."
            )

        origin = route_match.group("origin").strip(" ,.")
        destination = route_match.group("destination").strip(" ,.")
        return origin, destination

    def _parse_travel_date(self, text: str, base_date: date) -> date:
        iso_match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
        if iso_match:
            return date.fromisoformat(iso_match.group(1))

        if re.search(r"\btoday\b", text, flags=re.IGNORECASE):
            return base_date

        if re.search(r"\btomorrow\b", text, flags=re.IGNORECASE):
            return base_date + timedelta(days=1)

        next_weekday_match = re.search(
            r"\bnext\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
            text,
            flags=re.IGNORECASE,
        )
        if next_weekday_match:
            target_name = next_weekday_match.group(1).lower()
            target_weekday = WEEKDAY_NAMES[target_name]
            days_ahead = (target_weekday - base_date.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            return base_date + timedelta(days=days_ahead)

        raise ValueError(
            "Could not parse travel date. Use YYYY-MM-DD, 'today', 'tomorrow', or 'next Friday'."
        )

    def _parse_passengers(self, text: str) -> int:
        passenger_match = re.search(
            r"\bfor\s+(\d+)\s+passengers?\b|\b(\d+)\s+passengers?\b",
            text,
            flags=re.IGNORECASE,
        )
        if not passenger_match:
            return 1

        passenger_value = passenger_match.group(1) or passenger_match.group(2)
        return int(passenger_value)

    def _parse_cabin_class(self, text: str) -> str:
        for cabin_class in ("first", "business", "economy"):
            if re.search(rf"\b{cabin_class}\b", text, flags=re.IGNORECASE):
                return cabin_class
        return "economy"

    def _parse_max_price(self, text: str) -> float | None:
        price_match = re.search(
            r"(?:under|below|max|budget(?:\s+of)?|within)\s+\$?(\d+(?:\.\d+)?)",
            text,
            flags=re.IGNORECASE,
        )
        if not price_match:
            return None
        return float(price_match.group(1))

    def _parse_direct_only(self, text: str) -> bool:
        return bool(
            re.search(
                r"\b(direct only|nonstop|non-stop|direct)\b",
                text,
                flags=re.IGNORECASE,
            )
        )
