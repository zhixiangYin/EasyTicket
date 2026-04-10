import argparse
from datetime import date

from app.agent.base import BaseSearchParser
from app.agent.llm_parser import LLMSearchParser
from app.agent.parser import NaturalLanguageSearchParser
from app.connectors.mock_a import MockAConnector
from app.connectors.mock_b import MockBConnector
from app.schemas.search import SearchInput
from app.services.search_service import SearchService


def build_search_service() -> SearchService:
    return SearchService(connectors=[MockAConnector(), MockBConnector()])


def render_results(search_input: SearchInput) -> int:
    results = build_search_service().search(search_input)
    if not results:
        print("No tickets found for the current filters.")
        return 0

    print(
        f"Found {len(results)} ticket options from {search_input.origin} to "
        f"{search_input.destination} on {search_input.travel_date}:"
    )

    for index, result in enumerate(results, start=1):
        print(
            f"{index}. [{result.platform}] "
            f"{result.depart_at.strftime('%H:%M')} -> {result.arrive_at.strftime('%H:%M')} | "
            f"${result.price:.2f} | "
            f"{'direct' if result.direct else f'{result.transfer_count} transfer'} | "
            f"{result.duration_minutes} min"
        )
    return 0


def search(args: argparse.Namespace) -> int:
    search_input = SearchInput(
        origin=args.origin,
        destination=args.destination,
        travel_date=date.fromisoformat(args.travel_date),
        passengers=args.passengers,
        cabin_class=args.cabin_class,
        max_price=args.max_price,
        direct_only=args.direct_only,
    )
    return render_results(search_input)


def build_agent_parser(mode: str) -> BaseSearchParser:
    if mode == "llm":
        return LLMSearchParser()
    return NaturalLanguageSearchParser()


def ask(args: argparse.Namespace) -> int:
    parser = build_agent_parser(args.parser_mode)
    parsed_request = parser.parse(args.query)
    search_input = parsed_request.search_input

    print(f"Parsed query using {args.parser_mode} parser:")
    print(f"- origin: {search_input.origin}")
    print(f"- destination: {search_input.destination}")
    print(f"- travel_date: {search_input.travel_date}")
    print(f"- passengers: {search_input.passengers}")
    print(f"- cabin_class: {search_input.cabin_class}")
    print(f"- max_price: {search_input.max_price}")
    print(f"- direct_only: {search_input.direct_only}")

    for note in parsed_request.notes:
        print(f"- note: {note}")

    print("")
    return render_results(search_input)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="EasyTicket command line interface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Search tickets across mock platforms")
    search_parser.add_argument("--origin", required=True, help="Departure city or station")
    search_parser.add_argument("--destination", required=True, help="Arrival city or station")
    search_parser.add_argument("--travel-date", required=True, help="Travel date in YYYY-MM-DD")
    search_parser.add_argument("--passengers", type=int, default=1, help="Passenger count")
    search_parser.add_argument(
        "--cabin-class",
        default="economy",
        choices=["economy", "business", "first"],
        help="Cabin or seat class",
    )
    search_parser.add_argument("--max-price", type=float, default=None, help="Optional budget cap")
    search_parser.add_argument(
        "--direct-only",
        action="store_true",
        help="Only show direct trips",
    )
    search_parser.set_defaults(handler=search)

    ask_parser = subparsers.add_parser(
        "ask",
        help="Parse a natural-language ticket request and run the search",
    )
    ask_parser.add_argument("query", help="Natural-language search request")
    ask_parser.add_argument(
        "--parser-mode",
        default="rule",
        choices=["rule", "llm"],
        help="Choose rule-based parsing or the model-parser interface",
    )
    ask_parser.set_defaults(handler=ask)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
