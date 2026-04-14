import httpx
import pytest

from app.connectors.base import ConnectorException
from app.connectors.http import HttpConnector


class ExampleHttpConnector(HttpConnector):
    name = "test_http"

    def search(self, search_input):  # pragma: no cover - not needed for helper tests
        return []


def test_get_json_returns_decoded_json() -> None:
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"ok": True})
        )
    )

    result = ExampleHttpConnector(client=client).get_json("https://example.com")

    assert result == {"ok": True}


def test_get_json_maps_rate_limit_status() -> None:
    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(429))
    )

    with pytest.raises(ConnectorException) as exc:
        ExampleHttpConnector(client=client).get_json("https://example.com")

    assert exc.value.code == "connector_rate_limited"
    assert "HTTP 429" in str(exc.value)


def test_get_json_maps_auth_status() -> None:
    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(403))
    )

    with pytest.raises(ConnectorException) as exc:
        ExampleHttpConnector(client=client).get_json("https://example.com")

    assert exc.value.code == "connector_auth_required"


def test_get_json_maps_invalid_json() -> None:
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, text="not-json")
        )
    )

    with pytest.raises(ConnectorException) as exc:
        ExampleHttpConnector(client=client).get_json("https://example.com")

    assert exc.value.code == "connector_parse_error"
