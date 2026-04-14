from datetime import date

from app.agent.base import BaseSearchParser, ParsedSearchRequest
from app.agent.clients import LLMClientError
from app.agent.search_agent import AgentSearchService
from tests.helpers import (
    FailingConnector,
    StaticConnector,
    make_search_input,
    make_ticket_result,
)


class SuccessfulParser(BaseSearchParser):
    def parse(self, text: str, *, today: date | None = None) -> ParsedSearchRequest:
        return ParsedSearchRequest(search_input=make_search_input(), notes=["success"])


class FailingParser(BaseSearchParser):
    def parse(self, text: str, *, today: date | None = None) -> ParsedSearchRequest:
        raise LLMClientError("model unavailable")


def test_agent_search_service_uses_llm_parser_when_successful() -> None:
    service = AgentSearchService(
        connectors=[StaticConnector([make_ticket_result(platform="mock_a")])],
        llm_parser=SuccessfulParser(),
        fallback_parser=SuccessfulParser(),
    )

    response = service.search("natural language query", request_id="test-request")

    assert response.request_id == "test-request"
    assert response.parser_used == "llm"
    assert response.fallback_reason is None
    assert response.results[0].platform == "mock_a"
    assert response.summary


def test_agent_search_service_falls_back_to_rule_parser() -> None:
    service = AgentSearchService(
        connectors=[StaticConnector([make_ticket_result(platform="mock_a")])],
        llm_parser=FailingParser(),
        fallback_parser=SuccessfulParser(),
    )

    response = service.search("natural language query", request_id="test-request")

    assert response.request_id == "test-request"
    assert response.parser_used == "rule"
    assert response.fallback_reason == "model unavailable"
    assert response.results[0].platform == "mock_a"


def test_agent_search_service_keeps_partial_results_when_connector_fails() -> None:
    service = AgentSearchService(
        connectors=[
            FailingConnector(),
            StaticConnector([make_ticket_result(platform="mock_a")]),
        ],
        llm_parser=SuccessfulParser(),
        fallback_parser=SuccessfulParser(),
    )

    response = service.search("natural language query", request_id="test-request")

    assert response.results[0].platform == "mock_a"
    assert response.connector_errors[0].connector == "failing"
    assert response.connector_errors[0].message == "connector unavailable"
