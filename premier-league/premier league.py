import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler

# Path to folder containing match CSVs
folder_path = "premier-league"
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Provided weights (used for selecting features, but random weights are applied in simulation)
weights = {
    "Gls": 0.10, "Ast": 0.10, "G+A": 0.10, "xG": 0.05, "xAG": 0.05,
    "G-PK": 0.05, "npxG": 0.05, "PrgP": 0.05, "PrgC": 0.05, "npxG+xAG": 0.05,
    "MP": 0.025, "Starts": 0.025, "PK": 0.025, "PKatt": 0.025,
    "DisciplinePenalty": -0.05
}

# Track total minutes played per team across all CSVs
participation_tracker = {}

def process_csv(csv_file):
    df = pd.read_csv(os.path.join(folder_path, csv_file))
    df.fillna(0, inplace=True)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    grouped = df.groupby("Squad")[numeric_cols].sum().reset_index()

    # Discipline penalty handling
    if "CrdY" in grouped.columns and "CrdR" in grouped.columns:
        grouped["DisciplinePenalty"] = grouped["CrdY"] + 5 * grouped["CrdR"]
        grouped.drop(["CrdY", "CrdR"], axis=1, inplace=True)

    # Track participation using 'MP' if available, else use count of rows
    for _, row in grouped.iterrows():
        team = row["Squad"]
        minutes = row["MP"] if "MP" in row else 1
        participation_tracker[team] = participation_tracker.get(team, 0) + minutes

    # Ensure all expected features are present
    for feature in weights.keys():
        if feature not in grouped.columns:
            grouped[feature] = 0

    features = list(weights.keys())

    # Normalize stats
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(grouped[features])
    scaled_df = pd.DataFrame(scaled_data, columns=features)
    scaled_df["Squad"] = grouped["Squad"]
    scaled_df["CumulativeScore"] = 0.0

    # Run 100 simulations
    for run in range(1, 101):
        raw_weights = np.random.rand(len(features))
        normalized_weights = raw_weights / raw_weights.sum()

        scores = scaled_df[features].values.dot(normalized_weights)
        scaled_df["CumulativeScore"] += scores
        scaled_df["AverageScore"] = scaled_df["CumulativeScore"] / run

        # Print top 5 teams for this run
        top_teams = scaled_df.sort_values("AverageScore", ascending=False).head(5)
        print(f"\n{csv_file} - Run {run}/100 - Live Average Dominance Scores:")
        for _, row in top_teams.iterrows():
            print(f"  {row['Squad']}: {row['AverageScore']:.4f}")

    scaled_df["OverallAverageScore"] = scaled_df["CumulativeScore"] / 100
    return scaled_df[["Squad", "OverallAverageScore"]]

# Aggregate scores from all files
all_teams_scores = pd.DataFrame(columns=["Squad", "OverallAverageScore"])

for csv_file in csv_files:
    print(f"\nProcessing {csv_file}...")
    team_scores = process_csv(csv_file)
    all_teams_scores = pd.concat([all_teams_scores, team_scores], ignore_index=True)

# Average scores across all CSVs
final_scores = all_teams_scores.groupby("Squad")["OverallAverageScore"].mean().reset_index()

# Apply participation-based penalty
max_participation = max(participation_tracker.values())
final_scores["ParticipationFactor"] = final_scores["Squad"].apply(
    lambda team: participation_tracker.get(team, 0) / max_participation
)

# Final weighted score adjusted by participation
final_scores["WeightedScore"] = final_scores["OverallAverageScore"] * final_scores["ParticipationFactor"]

# Normalize final scores to max 0.99
max_score = final_scores["WeightedScore"].max()
if max_score > 0:
    final_scores["WeightedScore"] = final_scores["WeightedScore"] / max_score * 0.99

# Sort results
final_scores = final_scores.sort_values("WeightedScore", ascending=False).reset_index(drop=True)

# Display final scores
print("\nOverall Weighted Dominance Scores (Adjusted for Participation):")
for idx, row in final_scores.iterrows():
    position = idx + 1
    print(f"{position:>2}. {row['Squad']}: {row['WeightedScore']:.4f}")
