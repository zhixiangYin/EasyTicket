import json
import re
from dataclasses import dataclass
from datetime import date, timedelta

from app.agent.base import BaseSearchParser, ParsedSearchRequest
from app.agent.validators import build_search_input_from_llm_payload


@dataclass(slots=True)
class MockLLMClient:
    """Temporary stand-in for a real model client."""

    def complete(self, prompt: str, user_query: str, *, today: date) -> str:
        payload = {
            "origin": self._extract_route_part(user_query, "origin"),
            "destination": self._extract_route_part(user_query, "destination"),
            "travel_date": self._extract_date(user_query, today).isoformat(),
            "passengers": self._extract_passengers(user_query),
            "cabin_class": self._extract_cabin_class(user_query),
            "max_price": self._extract_max_price(user_query),
            "direct_only": self._extract_direct_only(user_query),
        }
        return json.dumps(payload)

    def _extract_route_part(self, query: str, part: str) -> str:
        route_match = re.search(
            r"\bfrom\s+(?P<origin>.+?)\s+to\s+(?P<destination>.+?)(?=\s+(?:on|for|with|under|below|direct|tomorrow|today|next)\b|$)",
            query,
            flags=re.IGNORECASE,
        )
        if not route_match:
            raise ValueError("mock model could not infer route")
        return route_match.group(part).strip(" ,.")

    def _extract_date(self, query: str, today: date) -> date:
        iso_match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", query)
        if iso_match:
            return date.fromisoformat(iso_match.group(1))
        if re.search(r"\btoday\b", query, flags=re.IGNORECASE):
            return today
        if re.search(r"\btomorrow\b", query, flags=re.IGNORECASE):
            return today + timedelta(days=1)
        weekday_map = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }
        next_weekday_match = re.search(
            r"\bnext\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
            query,
            flags=re.IGNORECASE,
        )
        if next_weekday_match:
            target = weekday_map[next_weekday_match.group(1).lower()]
            days_ahead = (target - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            return today + timedelta(days=days_ahead)
        raise ValueError("mock model could not infer travel_date")

    def _extract_passengers(self, query: str) -> int:
        passenger_match = re.search(
            r"\bfor\s+(\d+)\s+passengers?\b|\b(\d+)\s+passengers?\b",
            query,
            flags=re.IGNORECASE,
        )
        if not passenger_match:
            return 1
        return int(passenger_match.group(1) or passenger_match.group(2))

    def _extract_cabin_class(self, query: str) -> str:
        for cabin_class in ("first", "business", "economy"):
            if re.search(rf"\b{cabin_class}\b", query, flags=re.IGNORECASE):
                return cabin_class
        return "economy"

    def _extract_max_price(self, query: str) -> float | None:
        price_match = re.search(
            r"(?:under|below|max|budget(?:\s+of)?|within)\s+\$?(\d+(?:\.\d+)?)",
            query,
            flags=re.IGNORECASE,
        )
        if not price_match:
            return None
        return float(price_match.group(1))

    def _extract_direct_only(self, query: str) -> bool:
        return bool(
            re.search(
                r"\b(direct only|nonstop|non-stop|direct)\b",
                query,
                flags=re.IGNORECASE,
            )
        )


class LLMSearchParser(BaseSearchParser):
    def __init__(self, client: MockLLMClient | None = None) -> None:
        self.client = client or MockLLMClient()

    def parse(self, text: str, *, today: date | None = None) -> ParsedSearchRequest:
        normalized_text = " ".join(text.strip().split())
        if not normalized_text:
            raise ValueError("query cannot be empty")

        base_date = today or date.today()
        prompt = self._build_prompt(base_date)
        raw_response = self.client.complete(prompt, normalized_text, today=base_date)
        payload = json.loads(raw_response)
        search_input = build_search_input_from_llm_payload(payload)

        return ParsedSearchRequest(
            search_input=search_input,
            notes=[
                "Parsed query with the model-parser interface.",
                "Current LLM mode uses a mock client so we can validate parser architecture before adding a real API.",
                f"Raw model output: {raw_response}",
            ],
        )

    def _build_prompt(self, today: date) -> str:
        return (
            "You are a ticket search query parser. "
            "Convert the user request into JSON with keys: "
            "origin, destination, travel_date, passengers, cabin_class, max_price, direct_only. "
            f"Resolve relative dates using today's date {today.isoformat()}. "
            "Return JSON only."
        )
