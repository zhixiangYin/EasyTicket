from app.agent.summarizer import ResultSummarizer
from tests.helpers import make_search_input, make_ticket_result


def test_summarizer_explains_best_result() -> None:
    summary = ResultSummarizer().summarize(
        search_input=make_search_input(),
        results=[make_ticket_result(platform="mock_a", price=78.0)],
    )

    assert "mock_a" in summary
    assert "USD 78.00" in summary
    assert "direct" in summary
    assert "fits the USD 80.00 budget" in summary


def test_summarizer_handles_empty_results() -> None:
    summary = ResultSummarizer().summarize(
        search_input=make_search_input(),
        results=[],
    )

    assert "No matching tickets" in summary
