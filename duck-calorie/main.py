import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import top_k_accuracy_score
from lightgbm import LGBMClassifier
import time

# === Load ===
train = pd.read_csv("duck-calorie/train.csv")
test = pd.read_csv("duck-calorie/test.csv")

# === Encode ===
cat_cols = ["Soil Type", "Crop Type"]
for col in cat_cols:
    enc = LabelEncoder()
    train[col] = enc.fit_transform(train[col])
    test[col] = enc.transform(test[col])

target_enc = LabelEncoder()
train["Target"] = target_enc.fit_transform(train["Fertilizer Name"])

# === Features & Target ===
features = [
    "Temparature", "Humidity", "Moisture",
    "Soil Type", "Crop Type", "Nitrogen", "Potassium", "Phosphorous"
]
X = train[features]
y = train["Target"]

# === Split ===
X_train, X_val, y_train, y_val = train_test_split(X, y, stratify=y, test_size=0.2, random_state=0)

# === Train Model ===
start = time.time()
model = LGBMClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, n_jobs=-1)
model.fit(X_train, y_train)
print(f"Training time: {round(time.time() - start, 2)} seconds")

# === MAP@3 Evaluation ===
val_probs = model.predict_proba(X_val)
map3 = top_k_accuracy_score(y_val, val_probs, k=3, labels=np.arange(len(target_enc.classes_)))
print("Validation MAP@3:", round(map3, 4))

# === Test Prediction ===
test_probs = model.predict_proba(test[features])
test_top3 = np.argsort(test_probs, axis=1)[:, -3:][:, ::-1]
test_labels = np.vectorize(lambda x: target_enc.inverse_transform([x])[0])(test_top3)

# === Submission ===
submission = pd.DataFrame({
    "id": test["id"],
    "Fertilizer Name": [" ".join(row) for row in test_labels]
})
submission.to_csv("submission.csv", index=False)
print("submission.csv saved.")
