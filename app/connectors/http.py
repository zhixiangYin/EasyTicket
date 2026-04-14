from typing import Any

import httpx

from app.connectors.base import BaseConnector, ConnectorException


class HttpConnector(BaseConnector):
    def __init__(self, client: httpx.Client | None = None) -> None:
        self.client = client or httpx.Client(timeout=self.timeout_seconds)

    def get_json(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        try:
            response = self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as exc:
            raise ConnectorException(
                "connector request timed out",
                code="connector_timeout",
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise ConnectorException(
                f"connector returned HTTP {exc.response.status_code}",
                code=self._code_for_status(exc.response.status_code),
            ) from exc
        except httpx.RequestError as exc:
            raise ConnectorException(
                f"connector request failed: {exc}",
                code="connector_unavailable",
            ) from exc
        except ValueError as exc:
            raise ConnectorException(
                "connector returned invalid JSON",
                code="connector_parse_error",
            ) from exc

    def close(self) -> None:
        self.client.close()

    def _code_for_status(self, status_code: int) -> str:
        if status_code == 401 or status_code == 403:
            return "connector_auth_required"
        if status_code == 429:
            return "connector_rate_limited"
        if 500 <= status_code:
            return "connector_unavailable"
        return "connector_http_error"
