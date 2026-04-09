from dataclasses import dataclass
from datetime import date
from typing import Literal


@dataclass(slots=True)
class SearchInput:
    origin: str
    destination: str
    travel_date: date
    passengers: int = 1
    cabin_class: Literal["economy", "business", "first"] = "economy"
    max_price: float | None = None
    direct_only: bool = False

    def __post_init__(self) -> None:
        self.origin = self.origin.strip()
        self.destination = self.destination.strip()

        if not self.origin:
            raise ValueError("origin cannot be empty")
        if not self.destination:
            raise ValueError("destination cannot be empty")
        if not 1 <= self.passengers <= 9:
            raise ValueError("passengers must be between 1 and 9")
        if self.max_price is not None and self.max_price <= 0:
            raise ValueError("max_price must be greater than 0")
