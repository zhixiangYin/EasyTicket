from uuid import uuid4

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.agent.clients import LLMClientError
from app.agent.search_agent import AgentSearchResponse
from app.api.schemas import (
    ErrorDetail,
    ErrorResponse,
    ConnectorErrorResponse,
    ParsedQueryResponse,
    SearchRequest,
    SearchResponse,
    TicketResultResponse,
)
from app.factory import build_agent_search_service

router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
def search(request: SearchRequest) -> SearchResponse | JSONResponse:
    request_id = request.request_id or str(uuid4())

    try:
        response = build_agent_search_service().search(
            request.query,
            fallback_to_rule=request.fallback_to_rule,
            request_id=request_id,
        )
    except LLMClientError as exc:
        return _error_response(
            request_id=request_id,
            status_code=503,
            code="llm_unavailable",
            message=str(exc),
        )
    except ValueError as exc:
        return _error_response(
            request_id=request_id,
            status_code=400,
            code="invalid_search_request",
            message=str(exc),
        )

    return _to_search_response(response)


def _error_response(
    *,
    request_id: str,
    status_code: int,
    code: str,
    message: str,
) -> JSONResponse:
    response = ErrorResponse(
        request_id=request_id,
        error=ErrorDetail(code=code, message=message),
    )
    return JSONResponse(status_code=status_code, content=response.model_dump())


def _to_search_response(response: AgentSearchResponse) -> SearchResponse:
    search_input = response.search_input
    return SearchResponse(
        request_id=response.request_id,
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
        summary=response.summary,
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
        connector_errors=[
            ConnectorErrorResponse(
                connector=connector_error.connector,
                code=connector_error.code,
                message=connector_error.message,
            )
            for connector_error in response.connector_errors
        ],
        parser_used=response.parser_used,
        fallback_reason=response.fallback_reason,
        parser_notes=response.parser_notes,
    )
