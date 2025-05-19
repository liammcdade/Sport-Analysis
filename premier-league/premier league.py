import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler

# Path to folder containing match CSVs
folder_path = "premier-league"
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Feature weights
weights = {
    "Gls": 0.10, "Ast": 0.10, "G+A": 0.10, "xG": 0.05, "xAG": 0.05,
    "G-PK": 0.05, "npxG": 0.05, "PrgP": 0.05, "PrgC": 0.05, "npxG+xAG": 0.05,
    "MP": 0.025, "Starts": 0.025, "PK": 0.025, "PKatt": 0.025,
    "DisciplinePenalty": -0.05,
    "Sh": 0.03, "SoT": 0.03, "SoT%": 0.02, "Sh/90": 0.02, "SoT/90": 0.02,
    "G/Sh": 0.03, "G/SoT": 0.03, "Dist": -0.02, "FK": 0.01,
    "npxG/Sh": 0.03, "G-xG": 0.02, "np:G-xG": 0.02,
}

# Track total minutes played per team
participation_tracker = {}

def process_csv(csv_file):
    df = pd.read_csv(os.path.join(folder_path, csv_file))
    df.fillna(0, inplace=True)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    grouped = df.groupby("Squad")[numeric_cols].sum().reset_index()

    # Derived ratio stats — safely
    def safe_div(num, denom):
        return np.where(denom > 0, num / denom, 0)

    if "Sh" in grouped.columns and "Gls" in grouped.columns:
        grouped["G/Sh"] = safe_div(grouped["Gls"], grouped["Sh"])
        grouped["SoT%"] = safe_div(grouped.get("SoT", 0), grouped["Sh"])
    if "SoT" in grouped.columns and "Gls" in grouped.columns:
        grouped["G/SoT"] = safe_div(grouped["Gls"], grouped["SoT"])
    if "npxG" in grouped.columns and "Sh" in grouped.columns:
        grouped["npxG/Sh"] = safe_div(grouped["npxG"], grouped["Sh"])
    if "Sh" in grouped.columns and "90s" in grouped.columns:
        grouped["Sh/90"] = safe_div(grouped["Sh"], grouped["90s"])
    if "SoT" in grouped.columns and "90s" in grouped.columns:
        grouped["SoT/90"] = safe_div(grouped["SoT"], grouped["90s"])

    # Discipline penalty
    if "CrdY" in grouped.columns and "CrdR" in grouped.columns:
        grouped["DisciplinePenalty"] = grouped["CrdY"] + 5 * grouped["CrdR"]
        grouped.drop(["CrdY", "CrdR"], axis=1, inplace=True)

    # Participation tracker
    for _, row in grouped.iterrows():
        team = row["Squad"]
        minutes = row["MP"] if "MP" in row else 1
        participation_tracker[team] = participation_tracker.get(team, 0) + minutes

    # Ensure all expected features exist
    for feature in weights.keys():
        if feature not in grouped.columns:
            grouped[feature] = 0

    features = list(weights.keys())

    # Normalize and simulate
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(grouped[features])
    scaled_df = pd.DataFrame(scaled_data, columns=features)
    scaled_df["Squad"] = grouped["Squad"]
    scaled_df["CumulativeScore"] = 0.0

    for run in range(1, 101):
        raw_weights = np.random.rand(len(features))
        normalized_weights = raw_weights / raw_weights.sum()

        scores = scaled_df[features].values.dot(normalized_weights)
        scaled_df["CumulativeScore"] += scores
        scaled_df["AverageScore"] = scaled_df["CumulativeScore"] / run

        # Optional: show progress
        top_teams = scaled_df.sort_values("AverageScore", ascending=False).head(5)
        print(f"\n{csv_file} - Run {run}/100 - Top 5:")
        for _, row in top_teams.iterrows():
            print(f"  {row['Squad']}: {row['AverageScore']:.4f}")

    scaled_df["OverallAverageScore"] = scaled_df["CumulativeScore"] / 100
    return scaled_df[["Squad", "OverallAverageScore"]]

# Aggregate all CSVs
all_teams_scores = pd.DataFrame(columns=["Squad", "OverallAverageScore"])

for csv_file in csv_files:
    print(f"\nProcessing {csv_file}...")
    team_scores = process_csv(csv_file)
    all_teams_scores = pd.concat([all_teams_scores, team_scores], ignore_index=True)

# Final aggregation
final_scores = all_teams_scores.groupby("Squad")["OverallAverageScore"].mean().reset_index()

# Apply participation penalty
max_participation = max(participation_tracker.values())
final_scores["ParticipationFactor"] = final_scores["Squad"].apply(
    lambda team: participation_tracker.get(team, 0) / max_participation
)

final_scores["WeightedScore"] = final_scores["OverallAverageScore"] * final_scores["ParticipationFactor"]

# Normalize
max_score = final_scores["WeightedScore"].max()
if max_score > 0:
    final_scores["WeightedScore"] = final_scores["WeightedScore"] / max_score * 0.99

# Final sort
final_scores = final_scores.sort_values("WeightedScore", ascending=False).reset_index(drop=True)

# Output
print("\nOverall Weighted Dominance Scores:")
for idx, row in final_scores.iterrows():
    print(f"{idx+1:>2}. {row['Squad']}: {row['WeightedScore']:.4f}")
