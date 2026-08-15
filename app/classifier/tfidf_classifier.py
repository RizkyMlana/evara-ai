from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

@dataclass
class CategoryPrediction:
    category: str
    confidence: float

class TfidfCategoryClassifier:
    def __init__(self) -> None:
        self.pipeline = Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(
                        lowercase=True,
                        ngram_range=(1, 2),
                        sublinear_tf=True,
                    ),
                ),
                (
                    "classifier",
                    LogisticRegression(
                        max_iter=1000,
                    ),
                ),
            ]
        )
        self.is_trained = False

    def fit(
        self,
        texts: list[str],
        labels: list[str],
    ) -> None:
        self.pipeline.fit(texts, labels)
        self.is_trained = True

    def predict(self, text: str) -> CategoryPrediction:
        if not self.is_trained:
            raise RuntimeError(
                "Classifier must be trained before prediction."
            )
        category = self.pipeline.predict([text])[0]
        probabilites = self.pipeline.predict_proba([text])[0]
        classes = self.pipeline.classes_
        category_index = list(classes).index(category)
        confidence = float(probabilites[category_index])

        return CategoryPrediction(
            category=category,
            confidence=confidence,
        )

    