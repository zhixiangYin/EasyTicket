import logging
from dataclasses import dataclass
from uuid import uuid4

from app.agent.base import ParsedSearchRequest
from app.agent.clients import LLMClientError
from app.agent.llm_parser import LLMSearchParser
from app.agent.parser import NaturalLanguageSearchParser
from app.agent.summarizer import ResultSummarizer
from app.connectors.base import BaseConnector
from app.schemas.result import TicketResult
from app.schemas.search import SearchInput
from app.services.search_service import SearchService


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AgentSearchResponse:
    request_id: str
    query: str
    search_input: SearchInput
    results: list[TicketResult]
    parser_used: str
    parser_notes: list[str]
    summary: str
    fallback_reason: str | None = None


class AgentSearchService:
    def __init__(
        self,
        *,
        connectors: list[BaseConnector],
        llm_parser: LLMSearchParser | None = None,
        fallback_parser: NaturalLanguageSearchParser | None = None,
        search_service: SearchService | None = None,
        summarizer: ResultSummarizer | None = None,
    ) -> None:
        self.llm_parser = llm_parser
        self.fallback_parser = fallback_parser or NaturalLanguageSearchParser()
        self.search_service = search_service or SearchService(connectors=connectors)
        self.summarizer = summarizer or ResultSummarizer()

    def search(
        self,
        query: str,
        *,
        fallback_to_rule: bool = True,
        request_id: str | None = None,
    ) -> AgentSearchResponse:
        resolved_request_id = request_id or str(uuid4())
        parser_used = "llm"
        fallback_reason: str | None = None

        try:
            llm_parser = self.llm_parser or LLMSearchParser()
            parsed_request = llm_parser.parse(query)
        except (LLMClientError, ValueError) as exc:
            if not fallback_to_rule:
                raise

            parser_used = "rule"
            fallback_reason = str(exc)
            parsed_request = self.fallback_parser.parse(query)

        logger.info(
            "agent_search_parsed request_id=%s parser=%s fallback=%s",
            resolved_request_id,
            parser_used,
            fallback_reason is not None,
        )

        results = self.search_service.search(parsed_request.search_input)
        logger.info(
            "agent_search_completed request_id=%s results_count=%s",
            resolved_request_id,
            len(results),
        )

        summary = self.summarizer.summarize(
            search_input=parsed_request.search_input,
            results=results,
        )
        return self._build_response(
            request_id=resolved_request_id,
            query=query,
            parsed_request=parsed_request,
            results=results,
            parser_used=parser_used,
            summary=summary,
            fallback_reason=fallback_reason,
        )

    def _build_response(
        self,
        *,
        request_id: str,
        query: str,
        parsed_request: ParsedSearchRequest,
        results: list[TicketResult],
        parser_used: str,
        summary: str,
        fallback_reason: str | None,
    ) -> AgentSearchResponse:
        return AgentSearchResponse(
            request_id=request_id,
            query=query,
            search_input=parsed_request.search_input,
            results=results,
            parser_used=parser_used,
            parser_notes=parsed_request.notes,
            summary=summary,
            fallback_reason=fallback_reason,
        )
