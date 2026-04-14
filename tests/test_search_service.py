from app.services.search_service import SearchService
from tests.helpers import (
    FailingConnector,
    StaticConnector,
    UnexpectedFailingConnector,
    make_search_input,
    make_ticket_result,
)


def test_search_service_collects_connector_errors_and_keeps_results() -> None:
    service = SearchService(
        connectors=[
            FailingConnector(),
            StaticConnector([make_ticket_result(platform="mock_a")]),
        ]
    )

    response = service.search(make_search_input())

    assert response.results[0].platform == "mock_a"
    assert response.connector_errors[0].connector == "failing"
    assert response.connector_errors[0].code == "connector_unavailable"
    assert response.connector_errors[0].message == "connector unavailable"


def test_search_service_marks_unexpected_connector_errors() -> None:
    service = SearchService(connectors=[UnexpectedFailingConnector()])

    response = service.search(make_search_input())

    assert response.results == []
    assert response.connector_errors[0].connector == "unexpected_failing"
    assert response.connector_errors[0].code == "unexpected_connector_error"
    assert response.connector_errors[0].message == "unexpected failure"
