"""
Analyzes Formula 1 race data to calculate driver performance scores and
simulates championship win probabilities using Monte Carlo simulation.

The script reads race results from a CSV file, cleans the data, calculates
various driver statistics (average finish, DNF rate, points, etc.),
assigns a score to each driver based on these stats, and then runs a
Monte Carlo simulation to estimate each driver's chance of winning a
hypothetical championship.

Assumes 'Formula1_2025Season_RaceResults.csv' is in the same directory.
"""

import pandas as pd
import numpy as np
import sys

# --- Configuration ---
RESULTS_CSV_FILE = "Formula1_2025Season_RaceResults.csv"
OUTPUT_CSV_FILE = "f1_championship_probabilities.csv"
N_SIMULATIONS = 100_000
RANDOM_SEED = 42

# Define weights for score calculation (can be tuned)
WEIGHT_AVG_FINISH = -50  # Higher average finish position is worse
WEIGHT_AVG_GRID = (
    -2
)  # Higher average grid position is generally worse (less impact than finish)
WEIGHT_DNF_RATE = -200  # Higher DNF rate is significantly worse
WEIGHT_TOTAL_POINTS = 5  # More points are better
WEIGHT_FASTEST_LAPS = 10  # More fastest laps are better


def main():
    """
    Loads F1 race data, calculates driver performance scores,
    and simulates championship win probabilities.
    """
    # Load the dataset
    try:
        df = pd.read_csv(RESULTS_CSV_FILE)
    except FileNotFoundError:
        print(
            f"Error: The data file '{RESULTS_CSV_FILE}' was not found. "
            "Please ensure it is in the same directory as the script."
        )
        sys.exit(1)
    except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
        print(
            f"Error: Could not parse the data file '{RESULTS_CSV_FILE}'. It might be corrupted or not a valid CSV. Details: {e}"
        )
        sys.exit(1)

    # --- Data Cleaning and Preparation ---
    df["Position"] = pd.to_numeric(df["Position"], errors="coerce")
    df["Starting Grid"] = pd.to_numeric(df["Starting Grid"], errors="coerce")
    # Convert 'Points' to numeric, fill NaNs (from errors or missing) with 0
    df["Points"] = pd.to_numeric(df["Points"], errors="coerce").fillna(0)
    # Map 'Set Fastest Lap' to 1/0, fill NaNs with 0 (no fastest lap)
    df["Set Fastest Lap"] = df["Set Fastest Lap"].map({"Yes": 1, "No": 0}).fillna(0)
    # Treat NaNs in 'Time/Retired' as DNFs and use an expanded keyword list for DNF detection.
    dnf_keywords = "DNF|Accident|Engine|Gearbox|Hydraulics|Retired|Electrical|Crash|Suspension|Overheating|Collision|Puncture|Disqualified|Withdrew|Power unit|Brakes"
    df["DNF"] = (
        df["Time/Retired"]
        .fillna("DNF")  # Assume NaN in Time/Retired means DNF
        .str.contains(
            dnf_keywords, case=False, na=False
        )  # na=False ensures non-string NaNs (already filled) don't cause errors
        .astype(int)
    )

    # --- Aggregate Stats per Driver ---
    driver_stats = df.groupby("Driver").agg(
        Races=("Position", "count"),  # Renaming directly in agg
        AvgFinish=("Position", "mean"),
        AvgGrid=("Starting Grid", "mean"),
        TotalPoints=("Points", "sum"),
        FastestLaps=("Set Fastest Lap", "sum"),
        DNFs=("DNF", "sum"),
    )

    # Calculate DNF Rate, handling cases with zero races
    driver_stats["DNFRate"] = 0.0  # Initialize column
    driver_stats.loc[driver_stats["Races"] > 0, "DNFRate"] = (
        driver_stats["DNFs"] / driver_stats["Races"]
    )

    # --- Calculate Driver Score ---
    driver_stats["Score"] = (
        driver_stats["AvgFinish"].fillna(driver_stats["AvgFinish"].mean())
        * WEIGHT_AVG_FINISH  # FillNa for AvgFinish if driver DNF'd all races
        + driver_stats["AvgGrid"].fillna(driver_stats["AvgGrid"].mean())
        * WEIGHT_AVG_GRID  # FillNa for AvgGrid
        + driver_stats["DNFRate"] * WEIGHT_DNF_RATE
        + driver_stats["TotalPoints"] * WEIGHT_TOTAL_POINTS
        + driver_stats["FastestLaps"] * WEIGHT_FASTEST_LAPS
    )

    # --- Convert Scores to Probabilities ---
    # Shift scores to be positive for probability calculation
    min_score = driver_stats["Score"].min()
    scores_shifted = (
        driver_stats["Score"] - min_score + 1e-3
    )  # Add small epsilon to avoid zero probabilities if all scores were identical

    # Handle case where all scores are identical (or only one driver) leading to sum of scores being zero
    if scores_shifted.sum() == 0:
        # Assign equal probability if sum is zero (e.g. one driver, or all scores are the same after shift)
        probabilities = pd.Series(
            1 / len(scores_shifted) if len(scores_shifted) > 0 else 0,
            index=scores_shifted.index,
        )
    else:
        probabilities = scores_shifted / scores_shifted.sum()

    # Ensure probabilities sum to 1 (due to potential floating point inaccuracies)
    if not np.isclose(probabilities.sum(), 1.0):
        probabilities = probabilities / probabilities.sum()

    # --- Monte Carlo Simulation ---
    np.random.seed(RANDOM_SEED)
    drivers = probabilities.index.tolist()

    if not drivers:
        print("No drivers found to simulate. Exiting.")
        sys.exit(0)

    # Ensure weights match drivers, handle empty probabilities
    if probabilities.empty or probabilities.sum() == 0:
        print(
            "Warning: Probabilities are zero or empty. Assigning equal weights for simulation."
        )
        weights = [1 / len(drivers)] * len(drivers) if len(drivers) > 0 else []
    else:
        weights = probabilities.values

    if not list(weights):  # Handle empty weights list if drivers list was also empty
        print("No weights available for simulation. Exiting.")
        sys.exit(0)

    sim_results = np.random.choice(drivers, size=N_SIMULATIONS, p=weights)
    sim_counts_percent = pd.Series(sim_results).value_counts(normalize=True) * 100

    # --- Output Results ---
    final_probabilities = sim_counts_percent.rename("WinChance (%)").sort_values(
        ascending=False
    )
    print("\n--- Championship Win Probabilities ---")
    print(final_probabilities.round(2))

    try:
        final_probabilities.round(2).to_csv(OUTPUT_CSV_FILE)
        print(f"\nResults saved to {OUTPUT_CSV_FILE}")
    except Exception as e:
        print(f"\nError saving results to CSV: {e}")


if __name__ == "__main__":
    main()
