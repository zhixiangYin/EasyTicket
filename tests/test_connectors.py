from app.connectors.mock_a import MockAConnector
from tests.helpers import StaticConnector


def test_connector_metadata_uses_explicit_values() -> None:
    metadata = MockAConnector().metadata

    assert metadata.name == "mock_a"
    assert metadata.display_name == "Mock Platform A"
    assert metadata.supports_auth is False
    assert metadata.supports_local_agent is False
    assert metadata.timeout_seconds == 2.0


def test_connector_metadata_falls_back_to_name_when_display_name_missing() -> None:
    class MinimalConnector(StaticConnector):
        name = "minimal"
        display_name = None

    metadata = MinimalConnector([]).metadata

    assert metadata.name == "minimal"
    assert metadata.display_name == "minimal"
