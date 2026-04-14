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
