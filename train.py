"""Train a text classifier for task priority and save the fitted pipeline."""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "tasks.csv"
MODEL_PATH = BASE_DIR / "model.joblib"


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    X = df["task_description"]
    y = df["priority"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("clf", MultinomialNB()),
    ])

    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, preds)
    labels = list(pipeline.classes_)

    print(f"Accuracy: {accuracy:.4f}\n")
    print("Confusion matrix (rows = true, cols = predicted):")
    print(f"Labels: {labels}")
    print(confusion_matrix(y_test, preds, labels=labels))
    print("\nClassification report:")
    print(classification_report(y_test, preds))

    if accuracy < 0.70:
        raise SystemExit(
            f"Accuracy {accuracy:.4f} below 0.70 threshold — model not saved."
        )

    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
