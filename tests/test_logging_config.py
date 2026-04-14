import logging

from app.logging_config import configure_logging


def test_configure_logging_uses_env_level(monkeypatch) -> None:
    monkeypatch.setenv("EASYTICKET_LOG_LEVEL", "INFO")

    configure_logging()

    assert logging.getLogger().level == logging.INFO


def test_configure_logging_defaults_to_warning_for_invalid_level(monkeypatch) -> None:
    monkeypatch.setenv("EASYTICKET_LOG_LEVEL", "NOT_A_LEVEL")

    configure_logging()

    assert logging.getLogger().level == logging.WARNING
