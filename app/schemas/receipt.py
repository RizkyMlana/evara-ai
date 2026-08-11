from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass
class ReceiptItem:
    name: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal


@dataclass
class Receipt:
    merchant: str | None = None
    date: datetime | None = None

    items: list[ReceiptItem] = field(default_factory=list)

    subtotal: Decimal | None = None
    discount: Decimal | None = None
    total: Decimal | None = None

    cash: Decimal | None = None

    