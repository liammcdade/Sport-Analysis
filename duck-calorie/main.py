import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier
from sklearn.metrics import label_ranking_average_precision_score
import optuna

# === Load Data ===
train = pd.read_csv("duck-calorie/train.csv")
test = pd.read_csv("duck-calorie/test.csv")

# === Encode Categorical Features ===
categorical_cols = ["Soil Type", "Crop Type"]
encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    train[col] = le.fit_transform(train[col])
    test[col] = le.transform(test[col])
    encoders[col] = le

# === Encode Target ===
target_enc = LabelEncoder()
train["target"] = target_enc.fit_transform(train["Fertilizer Name"])

X = train.drop(columns=["id", "Fertilizer Name", "target"])
y = train["target"]
X_test = test.drop(columns=["id"])

# === MAP@3 Calculation ===
def map3(y_true, y_prob):
    return label_ranking_average_precision_score(
        np.eye(len(np.unique(y_true)))[y_true], y_prob
    )

# === Objective Function for Optuna ===
def objective(trial):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 300),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "use_label_encoder": False,
        "eval_metric": "mlogloss",
        "tree_method": "hist"  # faster on CPU
    }

    kf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    map_scores = []

    for train_idx, val_idx in kf.split(X, y):
        model = XGBClassifier(**params)
        model.fit(X.iloc[train_idx], y.iloc[train_idx])
        prob = model.predict_proba(X.iloc[val_idx])
        score = map3(y.iloc[val_idx].values, prob)
        map_scores.append(score)

    return np.mean(map_scores)

# === Run Optuna Search ===
study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=50, show_progress_bar=True)

# === Train Final Model ===
best_params = study.best_params
best_params.update({"use_label_encoder": False, "eval_metric": "mlogloss", "tree_method": "hist"})
final_model = XGBClassifier(**best_params)
final_model.fit(X, y)

# === Predict on Test Set ===
probs = final_model.predict_proba(X_test)
top3 = np.argsort(probs, axis=1)[:, -3:][:, ::-1]
top3_labels = np.vectorize(lambda x: target_enc.inverse_transform([x])[0])(top3)

# === Submission File ===
submission = pd.DataFrame({
    "id": test["id"],
    "Top1": top3_labels[:, 0],
    "Top2": top3_labels[:, 1],
    "Top3": top3_labels[:, 2]
})
submission.to_csv("duck-calorie/fertilizer_submission.csv", index=False)
print("Saved: duck-calorie/fertilizer_submission.csv")
