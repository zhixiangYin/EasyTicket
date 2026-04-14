from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    fallback_to_rule: bool = True
    request_id: str | None = None


class ParsedQueryResponse(BaseModel):
    origin: str
    destination: str
    travel_date: date
    passengers: int
    cabin_class: Literal["economy", "business", "first"]
    max_price: float | None
    direct_only: bool


class TicketResultResponse(BaseModel):
    platform: str
    ticket_type: Literal["train", "flight", "bus"]
    origin: str
    destination: str
    depart_at: datetime
    arrive_at: datetime
    cabin_class: str
    price: float
    currency: str
    direct: bool
    transfer_count: int
    duration_minutes: int
    deep_link: str
    fetched_at: datetime


class SearchResponse(BaseModel):
    request_id: str
    query: str
    parsed_query: ParsedQueryResponse
    summary: str
    results: list[TicketResultResponse]
    parser_used: str
    fallback_reason: str | None
    parser_notes: list[str]
