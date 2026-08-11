from pathlib import Path
from paddleocr import PaddleOCR

class ReceiptOCR:
    def __init__(self) -> None:
        self.ocr = PaddleOCR(
            lang="en",
        )
    def extract(self, image_path: str | Path) -> list[dict]:
        results = self.ocr.predict(str(image_path))
        extracted: list[dict] = []

        for result in results :
            texts = result["rec_texts"]
            scores = result["rec_scores"]

            for text, score in zip(texts, scores):
                extracted.append(
                    {
                        "text": text,
                        "confidence": float(score)
                    }
                )

        return extracted