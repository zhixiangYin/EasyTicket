import json
from datetime import date

from app.agent.base import BaseSearchParser, ParsedSearchRequest
from app.agent.clients import BaseLLMClient, build_llm_client
from app.agent.validators import build_search_input_from_llm_payload


class LLMSearchParser(BaseSearchParser):
    def __init__(self, client: BaseLLMClient | None = None) -> None:
        self.client = client or build_llm_client()

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
                f"LLM client: {self.client.__class__.__name__}.",
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
