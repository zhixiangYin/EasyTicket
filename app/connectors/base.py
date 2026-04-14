from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.result import TicketResult
from app.schemas.search import SearchInput


@dataclass(frozen=True, slots=True)
class ConnectorMetadata:
    name: str
    display_name: str
    supports_auth: bool = False
    supports_local_agent: bool = False
    timeout_seconds: float = 10.0


class ConnectorException(RuntimeError):
    def __init__(self, message: str, *, code: str = "connector_error") -> None:
        super().__init__(message)
        self.code = code


class BaseConnector(ABC):
    name: str
    display_name: str | None = None
    supports_auth = False
    supports_local_agent = False
    timeout_seconds = 10.0

    @property
    def metadata(self) -> ConnectorMetadata:
        return ConnectorMetadata(
            name=self.name,
            display_name=self.display_name or self.name,
            supports_auth=self.supports_auth,
            supports_local_agent=self.supports_local_agent,
            timeout_seconds=self.timeout_seconds,
        )

    @abstractmethod
    def search(self, search_input: SearchInput) -> list[TicketResult]:
        """Return normalized ticket results for a platform."""
