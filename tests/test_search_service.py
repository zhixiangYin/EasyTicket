from app.services.search_service import SearchService
from tests.helpers import FailingConnector, StaticConnector, make_search_input, make_ticket_result


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
    assert response.connector_errors[0].message == "connector unavailable"
