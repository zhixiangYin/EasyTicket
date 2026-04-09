import argparse
from datetime import date

from app.connectors.mock_a import MockAConnector
from app.connectors.mock_b import MockBConnector
from app.schemas.search import SearchInput
from app.services.search_service import SearchService

def build_search_service() -> SearchService:
    return SearchService(connectors=[MockAConnector(), MockBConnector()])


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
    results = build_search_service().search(search_input)

    if not results:
        print("No tickets found for the current filters.")
        return 0

    print(
        f"Found {len(results)} ticket options from {args.origin} to {args.destination} "
        f"on {args.travel_date}:"
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
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
