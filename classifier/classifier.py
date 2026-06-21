import re
import joblib
from sklearn.ensemble import RandomForestClassifier

COMPLEX_KEYWORDS = ["analyze", "evaluate", "compare", "argue", "recommend",
                    "assess", "critique", "design", "diagnose", "reason",
                    "trade-off", "trade off", "ethical", "justify", "debate"]
SIMPLE_KEYWORDS = ["translate", "convert", "what is", "what does", "what are",
                   "how many", "how much", "spell", "format", "list the", "define"]
MEDIUM_KEYWORDS = ["summarize", "summary", "classify", "extract", "identify",
                   "compare", "differences between", "pros and cons", "list the steps",
                   "what are the differences", "explain what"]


def extract_features(prompt: str) -> list:
    lower = prompt.lower()
    length = len(prompt)
    word_count = len(prompt.split())
    sentence_count = max(1, len(re.findall(r"[.!?]+", prompt)))
    has_complex = int(any(kw in lower for kw in COMPLEX_KEYWORDS))
    has_simple = int(any(kw in lower for kw in SIMPLE_KEYWORDS))
    has_medium = int(any(kw in lower for kw in MEDIUM_KEYWORDS))
    return [length, word_count, sentence_count, has_complex, has_simple, has_medium]


def _rule_predict(prompt: str) -> int:
    lower = prompt.lower()
    word_count = len(prompt.split())
    if any(kw in lower for kw in COMPLEX_KEYWORDS) and word_count > 15:
        return 3
    if any(kw in lower for kw in MEDIUM_KEYWORDS):
        return 2
    if any(kw in lower for kw in SIMPLE_KEYWORDS) or word_count <= 12:
        return 1
    if word_count > 20:
        return 2
    return 1


def train(examples: list[dict]):
    X = [extract_features(e["prompt"]) for e in examples]
    y = [e["tier"] for e in examples]
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model


def predict(prompt: str, model) -> int:
    features = extract_features(prompt)
    return int(model.predict([features])[0])


def save_model(model, path: str) -> None:
    joblib.dump(model, path)


def load_model(path: str):
    return joblib.load(path)
