import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import Ridge
from sklearn.inspection import permutation_importance
import matplotlib.pyplot as plt

# Path to folder containing match CSVs
folder_path = "premier-league"
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Static feature weights (used as ground truth model target)
weights = {
    "Gls": 0.10, "Ast": 0.10, "G+A": 0.10, "xG": 0.05, "xAG": 0.05,
    "G-PK": 0.05, "npxG": 0.05, "PrgP": 0.05, "PrgC": 0.05, "npxG+xAG": 0.05,
    "MP": 0.025, "Starts": 0.025, "PK": 0.025, "PKatt": 0.025,
    "DisciplinePenalty": -0.05
}
feature_list = list(weights.keys())

# Collect all team-level data from all CSVs
all_data = []

for csv_file in csv_files:
    df = pd.read_csv(os.path.join(folder_path, csv_file))
    df.fillna(0, inplace=True)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    grouped = df.groupby("Squad")[numeric_cols].sum().reset_index()

    # Apply discipline penalty
    if "CrdY" in grouped.columns and "CrdR" in grouped.columns:
        grouped["DisciplinePenalty"] = grouped["CrdY"] + 5 * grouped["CrdR"]
        grouped.drop(["CrdY", "CrdR"], axis=1, inplace=True)

    # Ensure all expected features are present
    for feature in feature_list:
        if feature not in grouped.columns:
            grouped[feature] = 0

    grouped["SourceFile"] = csv_file
    all_data.append(grouped[["Squad"] + feature_list + ["SourceFile"]])

# Combine all into one DataFrame
df_all = pd.concat(all_data, ignore_index=True)

# Normalize feature values
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(df_all[feature_list])
X_df = pd.DataFrame(X_scaled, columns=feature_list)

# Compute static score using defined weights
static_weights = np.array([weights[f] for f in feature_list])
df_all["TargetScore"] = X_df.values.dot(static_weights)

# Train regression model on normalized features
model = Ridge(alpha=1.0)
model.fit(X_df, df_all["TargetScore"])

# Compute permutation importance
result = permutation_importance(model, X_df, df_all["TargetScore"], n_repeats=30, random_state=42)

# Format results
importance_df = pd.DataFrame({
    "Feature": feature_list,
    "Importance": result.importances_mean,
    "Std": result.importances_std
}).sort_values("Importance", ascending=False)

# Print results
print("\nPermutation Importance (on Static Weight Model):")
print(importance_df.to_string(index=False))

# Plot
plt.figure(figsize=(10, 6))
plt.barh(importance_df["Feature"], importance_df["Importance"], xerr=importance_df["Std"], color="skyblue")
plt.xlabel("Permutation Importance")
plt.title("Feature Importance - Team Dominance Score")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()