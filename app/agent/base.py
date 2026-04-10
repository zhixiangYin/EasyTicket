from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

from app.schemas.search import SearchInput


@dataclass(slots=True)
class ParsedSearchRequest:
    search_input: SearchInput
    notes: list[str]


class BaseSearchParser(ABC):
    @abstractmethod
    def parse(self, text: str, *, today: date | None = None) -> ParsedSearchRequest:
        """Convert natural language into a structured search request."""
