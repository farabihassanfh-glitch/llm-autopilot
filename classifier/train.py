from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from classifier.classifier import extract_features, train, save_model
from classifier.training_data import EXAMPLES

MODEL_PATH = "classifier/model.joblib"

train_examples, test_examples = train_test_split(
    EXAMPLES, test_size=0.2, random_state=42, stratify=[e["tier"] for e in EXAMPLES]
)

model = train(train_examples)
save_model(model, MODEL_PATH)

X_test = [extract_features(e["prompt"]) for e in test_examples]
y_test = [e["tier"] for e in test_examples]
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"Test accuracy: {accuracy:.1%} ({sum(p == t for p, t in zip(y_pred, y_test))}/{len(y_test)} correct)")
print(f"Model saved to {MODEL_PATH}")
