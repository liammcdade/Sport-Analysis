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

def main():
    # Load the dataset, assuming 'Formula1_2025Season_RaceResults.csv' is in the same directory as the script.
    try:
        df = pd.read_csv('Formula1_2025Season_RaceResults.csv')
    except FileNotFoundError:
        print("Error: The data file 'Formula1_2025Season_RaceResults.csv' was not found. Please ensure it is in the same directory as the script.")
        sys.exit(1)
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        print("Error: Could not parse the data file. It might be corrupted or not a valid CSV.")
        sys.exit(1)

    # Clean and convert
    # Prepare data
    df['Position'] = pd.to_numeric(df['Position'], errors='coerce')
    df['Starting Grid'] = pd.to_numeric(df['Starting Grid'], errors='coerce')
    df['Points'] = pd.to_numeric(df['Points'], errors='coerce').fillna(0)  # Convert 'Points' to numeric, coercing errors to NaN, then fill NaN with 0 (assuming missing/invalid point data means 0 points)
    df['Set Fastest Lap'] = df['Set Fastest Lap'].map({'Yes': 1, 'No': 0}).fillna(0)  # Map 'Yes'/'No' to 1/0 for 'Set Fastest Lap', then fill NaN with 0 (assuming missing data means no fastest lap set)
    # Treat NaNs in 'Time/Retired' as DNFs and use an expanded keyword list for DNF detection.
    dnf_keywords = 'DNF|Accident|Engine|Gearbox|Hydraulics|Retired|Electrical|Crash|Suspension|Overheating|Collision|Puncture|Disqualified|Withdrew|Power unit|Brakes'
    df['DNF'] = df['Time/Retired'].fillna('DNF').str.contains(dnf_keywords, case=False).astype(int)

    # Aggregate stats per driver
    driver_stats = df.groupby('Driver').agg({
        'Position': ['count', 'mean'],
        'Starting Grid': 'mean',
        'Points': 'sum',
        'Set Fastest Lap': 'sum',
        'DNF': 'sum'
    })

    driver_stats.columns = ['Races', 'AvgFinish', 'AvgGrid', 'TotalPoints', 'FastestLaps', 'DNFs']
    driver_stats['DNFRate'] = driver_stats['DNFs'] / driver_stats['Races']

    # Define weights for score calculation (can be tuned)
    WEIGHT_AVG_FINISH = -50    # Higher average finish position is worse
    WEIGHT_AVG_GRID = -2       # Higher average grid position is generally worse (though less impact than finish)
    WEIGHT_DNF_RATE = -200     # Higher DNF rate is significantly worse
    WEIGHT_TOTAL_POINTS = 5    # More points are better
    WEIGHT_FASTEST_LAPS = 10   # More fastest laps are better

    driver_stats['Score'] = (
        driver_stats['AvgFinish'] * WEIGHT_AVG_FINISH +
        driver_stats['AvgGrid'] * WEIGHT_AVG_GRID +
        driver_stats['DNFRate'] * WEIGHT_DNF_RATE +
        driver_stats['TotalPoints'] * WEIGHT_TOTAL_POINTS +
        driver_stats['FastestLaps'] * WEIGHT_FASTEST_LAPS
    )

    # Convert to probabilities
    scores = driver_stats['Score']
    scores = scores - scores.min() + 1e-3  # shift to make all scores positive
    probabilities = scores / scores.sum()

    # Set random seed for reproducibility of Monte Carlo simulation
    np.random.seed(42)
    # Monte Carlo Simulation
    n_simulations = 100_000
    drivers = probabilities.index.tolist()
    weights = probabilities.values

    sim_results = np.random.choice(drivers, size=n_simulations, p=weights)
    sim_counts = pd.Series(sim_results).value_counts(normalize=True) * 100

    # Final result: win chance in %
    sim_counts = sim_counts.rename("WinChance (%)").sort_values(ascending=False)
    print(sim_counts.round(2))

if __name__ == "__main__":
    main()