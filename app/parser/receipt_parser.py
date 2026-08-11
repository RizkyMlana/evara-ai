import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from app.schemas.receipt import Receipt, ReceiptItem

class IndomaretReceiptParser:
    DATE_PATTERN = re.compile(
        r"(?P<date>\d{2}\. \d{2}\.)\s"
        r"(?P<date>\d{2})\s*[--]\s*"
        r"(?P<time>\d{2}:\d{2})"
    )

    MONEY_PATTERN = re.compile(
        r"^\(?\s*\d[\d., ]*\s*\)?$"
    )

    def parse(self, texts: list[str]) -> Receipt:
        normalized = [self._normalize_text(text) for text in texts]
        normalized = [text for text in normalized if text]

        receipt = Receipt(
            merchant = self._detect_merchant(normalized),
            date = self._detect_date(normalized),
            subtotal=self._detect_labeled_amount(
                normalized,
                "HARGA JUAL",
            ),
            discount= self._detect_discount(normalized),
            total=self._detect_labeled_amount(
                normalized,
                "TOTAL",
            ),
            cash=self._detect_labeled_amount(
                normalized,
                "TUNAI",
            ),
            change=self._detect_labeled_amount(
                normalized,
                "KEMBALI",
            ),
        )
        receipt.items = self._parse_items(normalized)
        return receipt

    def _normalize_text(self, text:str)-> str:
        text = text.strip()
        text = re.sub(r"\s+", " ", text)

        return text
    def _detect_merchant(self, texts: list[str]) -> str | None:
        for text in texts :
            if "INDOMARET" in text.upper():
                return "Indomaret"
        return None
    def _detect_date(self, texts: list[str]) -> datetime | None:
        for text in texts:
            match = self.DATE_PATTERN.search(text)
            if not match:
                continue
            date_part = match.group("date")
            year = match.group("year")
            time = match.group("time")

            try:
                return datetime.strptime(
                    f"{date_part}{year}{time}",
                    "%d.%m.%y %H:%M",
                )
            except ValueError:
                continue
        return None
    def _detect_labeled_amount(self,texts: list[str], label: str) -> Decimal | None :
        label_upper = label.upper()
        for index, text in enumerate(texts):
            if label_upper not in text.upper():
                continue

            inline_amount = self._extract_money_from_text(text)

            if inline_amount is not None:
                return inline_amount

            for next_text in texts[index + 1:index + 4]:
                amount = self._parse_money(next_text)
                if amount is not None:
                    return amount
        return None
