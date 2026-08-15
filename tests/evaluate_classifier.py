import json
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split

from app.classifier.tfidf_classifier import TfidfCategoryClassifier

def load_dataset() -> list[dict]:
    path = Path("tests/dataset/category.json")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

def main() -> None:
    dataset = load_dataset()
    texts = [item["text"] for item in dataset]
    labels = [item["label"] for item in dataset]


    train_texts, test_texts, train_labels, test_labels= train_test_split(
        texts,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )

    print(f"Total samples : {len(dataset)}")
    print(f"Training      : {len(train_texts)}")
    print(f"Testing       : {len(test_texts)}")
    print()

    classifier = TfidfCategoryClassifier()

    classifier.fit(
        train_texts,
        train_labels,
    )

    predictions = [
        classifier.predict(text).category
        for text in test_texts
    ]

    accuracy = accuracy_score(
        test_labels,
        predictions,
    )

    print(f"Accuracy: {accuracy:.2%}")
    print()
    print(
        classification_report(
            test_labels,
            predictions,
            zero_division=0,
        )
    )
    print("Confusion Matrix:")
    print()

    print(
        confusion_matrix(
            test_labels,
            predictions,
        )
    )

    print("\nMisclassified samples:")
    print("-" * 80)

    for text, actual, predicted in zip(
        test_texts,
        test_labels,
        predictions,
    ):
        if actual != predicted:
            print(f"Text     : {text}")
            print(f"Actual   : {actual}")
            print(f"Predicted: {predicted}")
            print("-" * 80)

if __name__ == "__main__":
    main()