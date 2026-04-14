from app.schemas.result import TicketResult
from app.schemas.search import SearchInput


class ResultSummarizer:
    def summarize(
        self,
        *,
        search_input: SearchInput,
        results: list[TicketResult],
    ) -> str:
        if not results:
            return (
                f"No matching tickets were found from {search_input.origin} to "
                f"{search_input.destination} on {search_input.travel_date}."
            )

        best = results[0]
        reasons = [
            f"it costs {best.currency} {best.price:.2f}",
            f"takes {best.duration_minutes} minutes",
        ]

        if best.direct:
            reasons.append("is direct")
        else:
            reasons.append(f"has {best.transfer_count} transfer")

        if search_input.max_price is not None and best.price <= search_input.max_price:
            reasons.append(f"fits the {best.currency} {search_input.max_price:.2f} budget")

        return (
            f"The best current option is on {best.platform}: "
            f"{best.depart_at.strftime('%H:%M')} to {best.arrive_at.strftime('%H:%M')} "
            f"because {', '.join(reasons)}."
        )
