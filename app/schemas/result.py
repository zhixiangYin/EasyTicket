from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass(slots=True)
class TicketResult:
    platform: str
    origin: str
    destination: str
    depart_at: datetime
    arrive_at: datetime
    cabin_class: str
    price: float
    deep_link: str
    fetched_at: datetime
    ticket_type: Literal["train", "flight", "bus"] = "train"
    currency: str = "USD"
    direct: bool = True
    transfer_count: int = 0

    @property
    def duration_minutes(self) -> int:
        return int((self.arrive_at - self.depart_at).total_seconds() // 60)

    def __post_init__(self) -> None:
        if self.price <= 0:
            raise ValueError("price must be greater than 0")
        if self.transfer_count < 0:
            raise ValueError("transfer_count cannot be negative")
