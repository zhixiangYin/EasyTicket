from abc import ABC, abstractmethod

from app.schemas.result import TicketResult
from app.schemas.search import SearchInput


class ConnectorException(RuntimeError):
    def __init__(self, message: str, *, code: str = "connector_error") -> None:
        super().__init__(message)
        self.code = code


class BaseConnector(ABC):
    name: str

    @abstractmethod
    def search(self, search_input: SearchInput) -> list[TicketResult]:
        """Return normalized ticket results for a platform."""
