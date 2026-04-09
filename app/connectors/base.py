from abc import ABC, abstractmethod

from app.schemas.result import TicketResult
from app.schemas.search import SearchInput


class BaseConnector(ABC):
    name: str

    @abstractmethod
    def search(self, search_input: SearchInput) -> list[TicketResult]:
        """Return normalized ticket results for a platform."""
