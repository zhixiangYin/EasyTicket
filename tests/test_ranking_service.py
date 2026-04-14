from app.services.ranking_service import RankingService
from tests.helpers import make_search_input, make_ticket_result


def test_filter_results_applies_direct_only_and_budget() -> None:
    results = [
        make_ticket_result(platform="direct_under_budget", price=78.0, direct=True),
        make_ticket_result(platform="transfer_under_budget", price=60.0, direct=False, transfer_count=1),
        make_ticket_result(platform="direct_over_budget", price=120.0, direct=True),
    ]

    filtered = RankingService().filter_results(results, make_search_input())

    assert [result.platform for result in filtered] == ["direct_under_budget"]


def test_sort_results_prefers_lower_price_then_duration() -> None:
    results = [
        make_ticket_result(platform="more_expensive", price=90.0, duration_minutes=100),
        make_ticket_result(platform="same_price_slower", price=70.0, duration_minutes=300),
        make_ticket_result(platform="same_price_faster", price=70.0, duration_minutes=200),
    ]

    sorted_results = RankingService().sort_results(results)

    assert [result.platform for result in sorted_results] == [
        "same_price_faster",
        "same_price_slower",
        "more_expensive",
    ]
