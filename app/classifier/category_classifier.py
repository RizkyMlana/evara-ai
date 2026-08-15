from dataclasses import dataclass

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class CategoryPrediction:
    category: str
    score: float


class ExpenseCategoryClassifier:
    CATEGORY_EXAMPLES = {
        "food": [
            "buying groceries at supermarket",
            "buying bread milk eggs and cheese",
            "buying snacks and drinks",
            "restaurant food and meals",
            "buying food at Indomaret",
            "buying food at Alfamart",
            "buying instant noodles and beverages",
        ],
        "transportation": [
            "buying gasoline and fuel",
            "paying for Gojek ride",
            "paying for Grab ride",
            "taxi fare",
            "bus ticket",
            "train ticket",
            "parking and toll payment",
        ],
        "shopping": [
            "buying clothes and shoes",
            "buying electronics",
            "buying bags and accessories",
            "buying household products",
            "buying cosmetics and personal items",
            "shopping for non-food products",
        ],
        "bills": [
            "paying electricity bill",
            "paying water bill",
            "paying internet bill",
            "paying phone bill",
            "buying mobile data package",
            "paying monthly subscription",
        ],
        "health": [
            "buying medicine at pharmacy",
            "buying vitamins and supplements",
            "doctor consultation",
            "hospital payment",
            "clinic payment",
            "buying healthcare products",
        ],
        "entertainment": [
            "watching movie at cinema",
            "buying video game",
            "music subscription",
            "entertainment streaming subscription",
            "concert ticket",
            "recreational activity",
        ],
        "education": [
            "buying school books",
            "buying university books",
            "paying tuition",
            "online course payment",
            "education training",
            "school supplies",
        ],
        "other": [
            "miscellaneous expense",
            "expense that does not fit another category",
            "other personal expense",
        ],
    }

    def __init__(
        self,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
    ) -> None:
        self.model = SentenceTransformer(model_name)

        self.category_names = list(self.CATEGORY_EXAMPLES.keys())

        self.example_texts: list[str] = []
        self.example_categories: list[str] = []

        for category, examples in self.CATEGORY_EXAMPLES.items():
            for example in examples:
                self.example_texts.append(example)
                self.example_categories.append(category)

        self.example_embeddings = self.model.encode(
            self.example_texts,
            normalize_embeddings=True,
        )

    def predict(self, text: str) -> CategoryPrediction:
        predictions = self.predict_all(text)

        return predictions[0]

    def predict_all(
        self,
        text: str,
    ) -> list[CategoryPrediction]:
        text_embedding = self.model.encode(
            [text],
            normalize_embeddings=True,
        )

        scores = cosine_similarity(
            text_embedding,
            self.example_embeddings,
        )[0]

        category_scores: dict[str, list[float]] = {
            category: []
            for category in self.category_names
        }

        for category, score in zip(
            self.example_categories,
            scores,
        ):
            category_scores[category].append(float(score))

        predictions = []

        for category, scores_for_category in category_scores.items():
            # Use the strongest matching example.
            best_score = max(scores_for_category)

            predictions.append(
                CategoryPrediction(
                    category=category,
                    score=best_score,
                )
            )

        return sorted(
            predictions,
            key=lambda prediction: prediction.score,
            reverse=True,
        )