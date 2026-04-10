import json
import os
import re
from dataclasses import dataclass
from datetime import date, timedelta
from urllib import error, request


class LLMClientError(RuntimeError):
    """Raised when the LLM client cannot complete a request."""


class BaseLLMClient:
    def complete(self, prompt: str, user_query: str, *, today: date) -> str:
        raise NotImplementedError


@dataclass(slots=True)
class MockLLMClient(BaseLLMClient):
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
            raise LLMClientError("mock model could not infer route")
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
        raise LLMClientError("mock model could not infer travel_date")

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


class OpenAIChatCompletionsClient(BaseLLMClient):
    """OpenAI client using the Chat Completions API with JSON schema output."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout_seconds: int = 20,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("EASYTICKET_OPENAI_MODEL", "gpt-5.4-mini")
        self.base_url = base_url or os.getenv(
            "EASYTICKET_OPENAI_BASE_URL",
            "https://api.openai.com/v1/chat/completions",
        )
        self.timeout_seconds = timeout_seconds

        if not self.api_key:
            raise LLMClientError("OPENAI_API_KEY is not set")

    def complete(self, prompt: str, user_query: str, *, today: date) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_query},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "ticket_search_query",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "origin": {"type": "string"},
                            "destination": {"type": "string"},
                            "travel_date": {"type": "string"},
                            "passengers": {"type": "integer"},
                            "cabin_class": {
                                "type": "string",
                                "enum": ["economy", "business", "first"],
                            },
                            "max_price": {
                                "type": ["number", "null"],
                            },
                            "direct_only": {"type": "boolean"},
                        },
                        "required": [
                            "origin",
                            "destination",
                            "travel_date",
                            "passengers",
                            "cabin_class",
                            "max_price",
                            "direct_only",
                        ],
                    },
                },
            },
        }

        req = request.Request(
            self.base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="ignore")
            raise LLMClientError(
                f"OpenAI API returned HTTP {exc.code}: {error_body or 'no error body'}"
            ) from exc
        except error.URLError as exc:
            raise LLMClientError(f"OpenAI API request failed: {exc.reason}") from exc

        return self._extract_text_content(body)

    def _extract_text_content(self, body: str) -> str:
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            raise LLMClientError("OpenAI API response was not valid JSON") from exc

        if not isinstance(parsed, dict):
            raise LLMClientError("OpenAI API response root was not an object")

        choices = parsed.get("choices")
        if not isinstance(choices, list) or not choices:
            raise LLMClientError("OpenAI API response did not include choices")

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise LLMClientError("OpenAI API choice payload was invalid")

        message = first_choice.get("message")
        if not isinstance(message, dict):
            raise LLMClientError("OpenAI API response did not include a message")

        content = message.get("content")
        if isinstance(content, str):
            return content

        if isinstance(content, list):
            text_parts: list[str] = []
            for part in content:
                if isinstance(part, dict):
                    text = part.get("text")
                    if isinstance(text, str):
                        text_parts.append(text)
            if text_parts:
                return "".join(text_parts)

        raise LLMClientError(
            "OpenAI API response did not contain text content in a supported shape"
        )


def build_llm_client(mode: str | None = None) -> BaseLLMClient:
    selected_mode = (mode or os.getenv("EASYTICKET_LLM_CLIENT", "mock")).lower()
    if selected_mode in {"openai", "real"}:
        return OpenAIChatCompletionsClient()
    return MockLLMClient()
