from fastapi.testclient import TestClient

from app.api.main import app


def test_search_endpoint_returns_summary_and_results(monkeypatch) -> None:
    monkeypatch.setenv("EASYTICKET_LLM_CLIENT", "mock")
    client = TestClient(app)

    response = client.post(
        "/search",
        json={
            "query": "find me a direct economy ticket from New York to Boston tomorrow under 80 dollars for 2 passengers",
            "request_id": "api-test-request",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["request_id"] == "api-test-request"
    assert body["summary"]
    assert body["parsed_query"]["origin"] == "New York"
    assert body["results"][0]["platform"] == "mock_a"
    assert body["connector_errors"] == []


def test_search_endpoint_returns_structured_error(monkeypatch) -> None:
    monkeypatch.setenv("EASYTICKET_LLM_CLIENT", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = TestClient(app)

    response = client.post(
        "/search",
        json={
            "query": "from nowhere to nowhere",
            "request_id": "api-error-request",
            "fallback_to_rule": False,
        },
    )

    body = response.json()

    assert response.status_code == 503
    assert body["request_id"] == "api-error-request"
    assert body["error"]["code"] == "llm_unavailable"
    assert "OPENAI_API_KEY" in body["error"]["message"]
