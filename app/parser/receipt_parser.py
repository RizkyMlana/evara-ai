import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from app.schemas.receipt import Receipt, ReceiptItem

class IndomaretReceiptParser:
    DATE_PATTERN = re.compile(
        r"(?P<day>\d{2})\.(?P<month>\d{2})\.?\s*"
        r"(?P<year>\d{2})?\s*[-–]?\s*"
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
            day = int(match.group("day"))
            month = int(match.group("month"))
            year = match.group("year")
            time = match.group("time")
            if year is None:
                return None
            try:
                return datetime.strptime(
                    f"{day:02d}.{month:02d}.{year} {time}",
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
    def _detect_discount(self, texts: list[str],) -> Decimal | None:
        for index, text in enumerate(texts):
            if "DISKON" not in text.upper():
                continue
            for next_text in texts[index + 1:index + 4]:
                amount = self._parse_money(next_text)
                if amount is not None:
                    return abs(amount)
        return None
    def _extract_money_from_text(self, text: str,) -> Decimal | None:
        matches = re.findall(
            r"\(?\s*\d[\d., ]*\s*\)?",
            text,
        )
        for match in reversed(matches):
            amount = self._parse_money(match)
            if amount is not None:
                return amount
        return None
    def _parse_money(self, value: str)-> Decimal | None:
        value = value.strip()
        if not self.MONEY_PATTERN.match(value):
            return None
        negative = value.startswith("(") and value.endswith(")")
        value = value.strip("() ")
        value = value.replace(" ", "")
        value = value.replace(",", "").replace(".", "")
        try:
            amount = Decimal(value)
            return -amount if negative else amount
        except InvalidOperation:
            return None
    def _parse_items(
        self,
        texts: list[str],
    ) -> list[ReceiptItem]:
        items: list[ReceiptItem] = []
        stop_words = {
            "DISKON",
            "HARGA",
            "JUAL",
            "TOTAL",
            "TUNAI",
            "KEMBALI",
            "ANDA HEMAT",
        }
        index = 0
        while index < len(texts):
            text = texts[index]
            if text.upper() in stop_words:
                break
            if not self._is_quantity(text):
                index += 1
                continue
            if index + 2 >= len(texts):
                index += 1
                continue
            quantity = self._parse_money(texts[index])
            unit_price = self._parse_money(texts[index + 1])
            total_price = self._parse_money(texts[index + 2])
            if (
                quantity is None
                or unit_price is None
                or total_price is None
            ):
                index += 1
                continue
            name = self._build_item_name(texts, index)
            if not name:
                index += 1
                continue
            items.append(
                ReceiptItem(
                    name=name,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                )
            )
            index += 3
        return items
    def _is_quantity(self, text:str) -> bool:
        try:
            value = Decimal(text.replace(",", "."))

            return(
                value > 0 and value <= 99 and value == value.to_integral_value()
            )
        except InvalidOperation:
            return False
    def _build_item_name(self, texts: list[str], quantity_index: int) -> str | None:
        name_parts: list[str] = []
        index = quantity_index - 1
        while index >= 0:
            text = texts[index]
            if self._parse_money(text) is not None:
                break
            if self._is_quantity(text):
                break

            if text.upper() in {
                "DISKON",
                "HARGA",
                "JUAL",
                "TOTAL",
                "TUNAI",
                "KEMBALI",
            }:
                break
            name_parts.insert(0, text)
            index -= 1

        if not name_parts:
            return None
        return " ".join(name_parts)     