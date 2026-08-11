from pathlib import Path
from app.ocr.paddle_ocr import ReceiptOCR

def main() -> None:
    image_path = Path("tests/fixtures/1.jpg")
    ocr = ReceiptOCR()
    result = ocr.extract(image_path)
    for item in result :
        print(
            f"{item['confidence']:.2f} | {item['text']}"
        )

if __name__ == "__main__":
    main()