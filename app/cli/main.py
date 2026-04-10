import argparse

from app.agent.clients import LLMClientError
from app.agent.llm_parser import LLMSearchParser
from app.agent.parser import NaturalLanguageSearchParser
from app.config import load_dotenv
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


def ask(args: argparse.Namespace) -> int:
    parser_mode_used = "llm"

    try:
        parser = LLMSearchParser()
        parsed_request = parser.parse(args.query)
    except (LLMClientError, ValueError) as exc:
        if args.fallback_to_rule:
            print(f"LLM parser failed: {exc}")
            print("Falling back to rule parser.")
            print("")
            parser_mode_used = "rule"
            parser = NaturalLanguageSearchParser()
            parsed_request = parser.parse(args.query)
        else:
            raise

    search_input = parsed_request.search_input

    print(f"Parsed query using {parser_mode_used} parser:")
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

    ask_parser = subparsers.add_parser(
        "ask",
        help="Use natural language to search tickets",
    )
    ask_parser.add_argument("query", help="Natural-language search request")
    ask_parser.add_argument(
        "--fallback-to-rule",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="When OpenAI parsing fails, retry with the internal rule-based parser",
    )
    ask_parser.set_defaults(handler=ask)
    return parser


def main() -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
