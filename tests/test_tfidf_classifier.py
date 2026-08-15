import json
from pathlib import Path
from app.classifier.tfidf_classifier import TfidfCategoryClassifier

def load_dataset() -> list[dict]:
    path = Path("tests/dataset/category.json")
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

def main() -> None:
    dataset = load_dataset()
    texts = [item["text"] for item in dataset]
    labels = [item["label"] for item in dataset]
    classifier = TfidfCategoryClassifier()
    classifier.fit(texts, labels)

    test_receipts = [
        "Indomaret roti cimory susu dan snack",
        "isi bensin motor",
        "beli sepatu baru",
        "bayar internet bulanan",
        "beli obat di apotek",
        "bayar netflix",
    ]

    for receipt in test_receipts:
        prediction = classifier.predict(receipt)
        print(
            f"{receipt}\n"
            f" -> {prediction.category} "
            f"({prediction.confidence: .2%})\n"
        )

if __name__ == "__main__":
    main()