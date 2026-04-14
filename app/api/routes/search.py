from fastapi import APIRouter, HTTPException

from app.agent.clients import LLMClientError
from app.agent.search_agent import AgentSearchResponse
from app.api.schemas import (
    ParsedQueryResponse,
    SearchRequest,
    SearchResponse,
    TicketResultResponse,
)
from app.factory import build_agent_search_service

router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
def search(request: SearchRequest) -> SearchResponse:
    try:
        response = build_agent_search_service().search(
            request.query,
            fallback_to_rule=request.fallback_to_rule,
        )
    except (LLMClientError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return _to_search_response(response)


def _to_search_response(response: AgentSearchResponse) -> SearchResponse:
    search_input = response.search_input
    return SearchResponse(
        query=response.query,
        parsed_query=ParsedQueryResponse(
            origin=search_input.origin,
            destination=search_input.destination,
            travel_date=search_input.travel_date,
            passengers=search_input.passengers,
            cabin_class=search_input.cabin_class,
            max_price=search_input.max_price,
            direct_only=search_input.direct_only,
        ),
        results=[
            TicketResultResponse(
                platform=result.platform,
                ticket_type=result.ticket_type,
                origin=result.origin,
                destination=result.destination,
                depart_at=result.depart_at,
                arrive_at=result.arrive_at,
                cabin_class=result.cabin_class,
                price=result.price,
                currency=result.currency,
                direct=result.direct,
                transfer_count=result.transfer_count,
                duration_minutes=result.duration_minutes,
                deep_link=result.deep_link,
                fetched_at=result.fetched_at,
            )
            for result in response.results
        ],
        parser_used=response.parser_used,
        fallback_reason=response.fallback_reason,
        parser_notes=response.parser_notes,
    )
