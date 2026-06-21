import json
import re
from pathlib import Path

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


class _SimpleModel:
    """Pure-Python model — no C dependencies."""
    def predict(self, X: list) -> list:
        return [1]  # placeholder, real logic in predict()


def train(examples: list[dict]):
    model = _SimpleModel()
    return model


def predict(prompt: str, model=None) -> int:
    return _rule_predict(prompt)


def save_model(model, path: str) -> None:
    Path(path).write_text(json.dumps({"type": "rule_based"}))


def load_model(path: str) -> _SimpleModel:
    return _SimpleModel()
