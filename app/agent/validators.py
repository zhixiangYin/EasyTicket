from datetime import date

from app.schemas.search import SearchInput


ALLOWED_CABIN_CLASSES = {"economy", "business", "first"}


def build_search_input_from_llm_payload(payload: dict) -> SearchInput:
    origin = _require_string(payload, "origin")
    destination = _require_string(payload, "destination")
    travel_date_raw = _require_string(payload, "travel_date")
    travel_date = date.fromisoformat(travel_date_raw)

    passengers = payload.get("passengers", 1)
    if not isinstance(passengers, int):
        raise ValueError("passengers must be an integer")

    cabin_class = payload.get("cabin_class", "economy")
    if not isinstance(cabin_class, str):
        raise ValueError("cabin_class must be a string")
    cabin_class = cabin_class.lower()
    if cabin_class not in ALLOWED_CABIN_CLASSES:
        raise ValueError(
            f"cabin_class must be one of {sorted(ALLOWED_CABIN_CLASSES)}"
        )

    max_price = payload.get("max_price")
    if max_price is not None and not isinstance(max_price, (int, float)):
        raise ValueError("max_price must be numeric or null")

    direct_only = payload.get("direct_only", False)
    if not isinstance(direct_only, bool):
        raise ValueError("direct_only must be a boolean")

    return SearchInput(
        origin=origin,
        destination=destination,
        travel_date=travel_date,
        passengers=passengers,
        cabin_class=cabin_class,
        max_price=float(max_price) if max_price is not None else None,
        direct_only=direct_only,
    )


def _require_string(payload: dict, field_name: str) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()
