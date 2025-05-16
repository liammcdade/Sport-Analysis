import pandas as pd
import numpy as np
import os
import time
from sklearn.preprocessing import MinMaxScaler
from tabulate import tabulate

# Load and clean data
df = pd.read_csv('euro 2024\euro2024-country.csv')
df.columns = df.columns.str.strip()

numeric_cols = ['Age', 'Poss', 'MP', 'Starts', 'Min', '90s', 'Gls', 'Ast', 'G+A', 'G-PK',
                'PK', 'PKatt', 'CrdY', 'CrdR', 'xG', 'npxG', 'xAG', 'npxG+xAG', 'PrgC', 'PrgP']
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
df = df[df['Min'] > 0].dropna(subset=['Squad'])

# Derived per-player stats
df['Goals_per_90'] = df['Gls'] / (df['Min'] / 90)
df['Assists_per_90'] = df['Ast'] / (df['Min'] / 90)
df['xG_diff'] = df['Gls'] - df['xG']
df['xGA_diff'] = df['G+A'] - (df['xG'] + df['xAG'])
df['npxGxAG_per_90'] = df['npxG+xAG'] / (df['Min'] / 90)
df['Discipline'] = (df['CrdY'] + 2 * df['CrdR']) / df['Min']
df['PrgC_per_90'] = df['PrgC'] / (df['Min'] / 90)
df['PrgP_per_90'] = df['PrgP'] / (df['Min'] / 90)

# Aggregate per squad
agg = df.groupby('Squad').agg({
    'Goals_per_90': 'mean',
    'Assists_per_90': 'mean',
    'xG_diff': 'mean',
    'xGA_diff': 'mean',
    'npxGxAG_per_90': 'mean',
    'Poss': 'mean',
    'PrgC_per_90': 'mean',
    'PrgP_per_90': 'mean',
    'Discipline': 'mean'
}).reset_index()

metrics = agg.columns[1:]  # All except 'Squad'

# Normalize
scaler = MinMaxScaler()
norm = pd.DataFrame(scaler.fit_transform(agg[metrics]), columns=metrics)
norm['Squad'] = agg['Squad']
norm['Discipline'] *= -1  # Lower is better

# Initialize score tracking
score_tracker = pd.DataFrame({'Squad': norm['Squad'], 'CumulativeScore': 0.0})

# Live update loop
for i, w in enumerate(np.arange(0.05, 1.05, 0.05), 1):
    weighted = norm[metrics] * w
    score = weighted.sum(axis=1)
    score_tracker['CumulativeScore'] += score
    score_tracker['AvgScore'] = score_tracker['CumulativeScore'] / i

    # Sort and display
    display_df = score_tracker[['Squad', 'AvgScore']].sort_values('AvgScore', ascending=False).reset_index(drop=True)
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"🔄 Weight: {w:.2f} | Iteration {i}/20\n")
    print(tabulate(display_df.head(24), headers='keys', tablefmt='fancy_grid', showindex=True))

    time.sleep(0.3)  # Delay for effect; adjust as needed
