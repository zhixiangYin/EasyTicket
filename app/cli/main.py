import argparse

from app.agent.search_agent import AgentSearchResponse
from app.config import load_dotenv
from app.factory import build_agent_search_service


def render_response(response: AgentSearchResponse, *, debug: bool = False) -> int:
    if debug:
        render_debug_info(response)

    if not response.results:
        print("No tickets found for the current filters.")
        if response.connector_errors:
            print(
                f"{len(response.connector_errors)} platform connector(s) failed. "
                "Use --debug for details."
            )
        return 0

    print(response.summary)
    print("")

    search_input = response.search_input
    print(
        f"Found {len(response.results)} ticket options from {search_input.origin} to "
        f"{search_input.destination} on {search_input.travel_date}:"
    )

    for index, result in enumerate(response.results, start=1):
        print(
            f"{index}. [{result.platform}] "
            f"{result.depart_at.strftime('%H:%M')} -> {result.arrive_at.strftime('%H:%M')} | "
            f"${result.price:.2f} | "
            f"{'direct' if result.direct else f'{result.transfer_count} transfer'} | "
            f"{result.duration_minutes} min"
        )
    return 0


def render_debug_info(response: AgentSearchResponse) -> None:
    search_input = response.search_input

    print(f"Request ID: {response.request_id}")
    print(f"Parsed query using {response.parser_used} parser:")
    print(f"- origin: {search_input.origin}")
    print(f"- destination: {search_input.destination}")
    print(f"- travel_date: {search_input.travel_date}")
    print(f"- passengers: {search_input.passengers}")
    print(f"- cabin_class: {search_input.cabin_class}")
    print(f"- max_price: {search_input.max_price}")
    print(f"- direct_only: {search_input.direct_only}")

    if response.fallback_reason:
        print(f"- fallback_reason: {response.fallback_reason}")

    for note in response.parser_notes:
        print(f"- note: {note}")

    for connector_error in response.connector_errors:
        print(
            f"- connector_error: {connector_error.connector}: {connector_error.message}"
        )

    print("")


def ask(args: argparse.Namespace) -> int:
    response = build_agent_search_service().search(
        args.query,
        fallback_to_rule=args.fallback_to_rule,
    )
    return render_response(response, debug=args.debug)


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
    ask_parser.add_argument(
        "--debug",
        action="store_true",
        help="Show parsed query fields and parser diagnostics",
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
