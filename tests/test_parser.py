from tests.fixtures.indomaret_ocr import OCR_TEXTS

from app.parser.receipt_parser import IndomaretReceiptParser


def main() -> None:
    parser = IndomaretReceiptParser()

    receipt = parser.parse(OCR_TEXTS)

    print("MERCHANT :", receipt.merchant)
    print("DATE     :", receipt.date)
    print("SUBTOTAL :", receipt.subtotal)
    print("DISCOUNT :", receipt.discount)
    print("TOTAL    :", receipt.total)
    print("CASH     :", receipt.cash)
    print("CHANGE   :", receipt.change)

    print("\nITEMS:")

    for item in receipt.items:
        print(
            f"- {item.name} | "
            f"qty={item.quantity} | "
            f"unit={item.unit_price} | "
            f"total={item.total_price}"
        )


if __name__ == "__main__":
    main()