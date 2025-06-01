import pandas as pd
import numpy as np

df = pd.read_csv(r'\\wsl.localhost\Ubuntu\home\liam\formula1-datasets\Formula1_2025Season_RaceResults.csv')

# Clean and convert
# Prepare data
df['Position'] = pd.to_numeric(df['Position'], errors='coerce')
df['Starting Grid'] = pd.to_numeric(df['Starting Grid'], errors='coerce')
df['Points'] = pd.to_numeric(df['Points'], errors='coerce').fillna(0)
df['Set Fastest Lap'] = df['Set Fastest Lap'].map({'Yes': 1, 'No': 0}).fillna(0)
df['DNF'] = df['Time/Retired'].str.contains(
    'DNF|Accident|Engine|Gearbox|Hydraulics|Retired|Electrical|Crash|Suspension|Overheating',
    case=False, na=False
).astype(int)

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

# Score: tune weights as needed
driver_stats['Score'] = (
    - driver_stats['AvgFinish'] * 50
    - driver_stats['AvgGrid'] * 2
    - driver_stats['DNFRate'] * 200
    + driver_stats['TotalPoints'] * 5
    + driver_stats['FastestLaps'] * 10
)

# Convert to probabilities
scores = driver_stats['Score']
scores = scores - scores.min() + 1e-3  # shift to make all scores positive
probabilities = scores / scores.sum()

# Monte Carlo Simulation
n_simulations = 100_000
drivers = probabilities.index.tolist()
weights = probabilities.values

sim_results = np.random.choice(drivers, size=n_simulations, p=weights)
sim_counts = pd.Series(sim_results).value_counts(normalize=True) * 100

# Final result: win chance in %
sim_counts = sim_counts.rename("WinChance (%)").sort_values(ascending=False)
print(sim_counts.round(2))