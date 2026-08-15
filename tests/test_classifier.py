from app.classifier.category_classifier import ExpenseCategoryClassifier

def main() -> None:
    classifier = ExpenseCategoryClassifier()
    receipt_text = """
    Indomaret
    Roti Krim Keju 72G
    Cimory Mix Berry 225
    Cafela Expresso 200ML
    FF Low Fat Van 225
    Plastik SDG
    """

    predictions = classifier.predict_all(receipt_text)

    print("Category Predictions: ")
    print()

    for prediction in predictions:
        print(
            f"{prediction.category:20}"
            f"{prediction.score:.4f}"
        )
    print()
    print("Prediction:")
    print(classifier.predict(receipt_text))

if __name__ == "__main__":
    main()