import random
import numpy as np
from collections import defaultdict
from tqdm import tqdm
import itertools

# --- 1. Define Teams and their raw playing stats + Abstract Strength values for 2025-26 Season ---

# Historical Playing Data (Goals For/Against per game)
teams_data_raw_historical = [
    # Premier League 2023-24 Stats (e.g., 37 games played for PL teams)
    {"Team": "Arsenal Football Club", "Pld": 37, "GF": 67, "GA": 33},
    {"Team": "Aston Villa Football Club", "Pld": 37, "GF": 58, "GA": 49},
    {"Team": "AFC Bournemouth", "Pld": 37, "GF": 56, "GA": 46},
    {"Team": "Brentford Football Club", "Pld": 37, "GF": 65, "GA": 56},
    {"Team": "Brighton & Hove Albion Football Club", "Pld": 37, "GF": 62, "GA": 58},
    {"Team": "Chelsea Football Club", "Pld": 37, "GF": 63, "GA": 43},
    {"Team": "Crystal Palace Football Club", "Pld": 37, "GF": 50, "GA": 50},
    {"Team": "Everton Football Club", "Pld": 37, "GF": 41, "GA": 44},
    {"Team": "Fulham Football Club", "Pld": 37, "GF": 54, "GA": 52},
    {"Team": "Liverpool Football Club", "Pld": 37, "GF": 85, "GA": 40},
    {"Team": "Manchester City Football Club", "Pld": 37, "GF": 70, "GA": 44},
    {"Team": "Manchester United Football Club", "Pld": 37, "GF": 42, "GA": 54},
    {"Team": "Newcastle United Football Club", "Pld": 37, "GF": 68, "GA": 46},
    {"Team": "Nottingham Forest Football Club", "Pld": 37, "GF": 58, "GA": 45},
    {"Team": "Tottenham Hotspur Football Club", "Pld": 37, "GF": 63, "GA": 61},
    {"Team": "West Ham United Football Club", "Pld": 37, "GF": 43, "GA": 61},
    {"Team": "Wolverhampton Wanderers Football Club", "Pld": 37, "GF": 53, "GA": 68},
    
    # Championship 2023-24 Stats (46 games played for Championship teams)
    {"Team": "Leeds United Football Club", "Pld": 46, "GF": 95, "GA": 30},
    {"Team": "Burnley Football Club", "Pld": 46, "GF": 69, "GA": 16},
    {"Team": "Sunderland Association Football Club", "Pld": 46, "GF": 58, "GA": 44},
]

# Abstract Team Strength Ratings (provided by user)
team_strengths_abstract = {
    "Arsenal Football Club": 95.9,
    "Aston Villa Football Club": 91.4,
    "AFC Bournemouth": 88.7,
    "Brentford Football Club": 88.3,
    "Brighton & Hove Albion Football Club": 88.5,
    "Burnley Football Club": 85.0,
    "Chelsea Football Club": 91.5,
    "Crystal Palace Football Club": 89.7,
    "Everton Football Club": 86.3,
    "Fulham Football Club": 87.9,
    "Leeds United Football Club": 84.0,
    "Liverpool Football Club": 97.3,
    "Manchester City Football Club": 95.0,
    "Manchester United Football Club": 88.6,
    "Newcastle United Football Club": 91.9,
    "Nottingham Forest Football Club": 88.4,
    "Sunderland Association Football Club": 81.0,
    "Tottenham Hotspur Football Club": 87.8,
    "West Ham United Football Club": 85.5,
    "Wolverhampton Wanderers Football Club": 86.8
}

# Ensure all teams in historical data match the abstract strengths and the 2025-26 list
all_teams = list(team_strengths_abstract.keys())
assert len(all_teams) == 20, "There must be exactly 20 teams for a Premier League season."
assert all(team["Team"] in all_teams for team in teams_data_raw_historical), "Historical data contains teams not in the 2025-26 list."
assert all(team_name in [d["Team"] for d in teams_data_raw_historical] for team_name in all_teams), "2025-26 list contains teams not in historical data."

# User-provided average league ratings
PL_AVG_STRENGTH_PROVIDED = 86.4
CHAMP_AVG_STRENGTH_PROVIDED = 76.2
CHAMP_TO_PL_RATIO = CHAMP_AVG_STRENGTH_PROVIDED / PL_AVG_STRENGTH_PROVIDED

# Calculate average abstract strength across all 20 teams in the current PL list
average_abstract_strength_across_league = sum(team_strengths_abstract.values()) / len(team_strengths_abstract)

# --- Normalization and Combination Strategy ---
teams_combined_strength_data = {}
print(f"--- Normalizing and Combining Team Strengths ---")
print(f"1. All historical GF/GA stats normalized to a 38-game season.")
print(f"2. Championship teams' stats adjusted by league quality ratio: {CHAMP_AVG_STRENGTH_PROVIDED:.1f} (Champ) / {PL_AVG_STRENGTH_PROVIDED:.1f} (PL) = {CHAMP_TO_PL_RATIO:.4f}")
print(f"3. All teams' stats refined by individual abstract strength (relative to overall league average {average_abstract_strength_across_league:.2f}).\n")


for team_data in teams_data_raw_historical:
    team_name = team_data["Team"]
    pld_original = team_data["Pld"]
    raw_gf_total = team_data["GF"]
    raw_ga_total = team_data["GA"]

    # Step 1: Normalize raw historical data to a 38-game season equivalent
    # Calculate per-game rates from original data
    gf_per_game_original = raw_gf_total / pld_original
    ga_per_game_original = raw_ga_total / pld_original
    
    # Calculate 38-game equivalent average per game
    # (conceptually, if they played 38 games at their historical rate)
    base_gf_avg = gf_per_game_original
    base_ga_avg = ga_per_game_original

    print(f"Processing {team_name} (Original Pld: {pld_original}):")
    print(f"  Initial per-game rates (normalized to 38-game equivalent): GF_avg={base_gf_avg:.2f}, GA_avg={base_ga_avg:.2f}")

    # Step 2: Apply Championship-to-PL scaling if from Championship
    if team_name in ["Leeds United Football Club", "Burnley Football Club", "Sunderland Association Football Club"]:
        gf_avg_pre_league_scale = base_gf_avg
        ga_avg_pre_league_scale = base_ga_avg
        
        base_gf_avg *= CHAMP_TO_PL_RATIO
        base_ga_avg /= CHAMP_TO_PL_RATIO
        
        # Ensure GA_avg doesn't become unrealistically low or zero
        base_ga_avg = max(base_ga_avg, 0.5) 
        
        print(f"  After Championship-to-PL scaling:")
        print(f"    GF_avg={gf_avg_pre_league_scale:.2f} -> {base_gf_avg:.2f}, GA_avg={ga_avg_pre_league_scale:.2f} -> {base_ga_avg:.2f}")
    
    # Get the abstract strength for the team
    abstract_strength = team_strengths_abstract[team_name]

    # Step 3: Calculate the individual strength adjustment factor
    strength_adj_factor = abstract_strength / average_abstract_strength_across_league

    # Apply the individual adjustment factor to the current base GF/GA averages
    adjusted_gf_avg = base_gf_avg * strength_adj_factor
    adjusted_ga_avg = base_ga_avg / strength_adj_factor 

    # Final sanity check for GA_avg
    adjusted_ga_avg = max(adjusted_ga_avg, 0.5) 

    teams_combined_strength_data[team_name] = {
        "GF_avg": adjusted_gf_avg,
        "GA_avg": adjusted_ga_avg
    }
    print(f"  Final Adjusted Strengths (after abstract strength refinement): GF_avg={adjusted_gf_avg:.2f}, GA_avg={adjusted_ga_avg:.2f}\n")


# --- 2. Generate all fixtures (home and away) for a 38-game season ---
fixtures = []
for team1, team2 in itertools.combinations(all_teams, 2):
    fixtures.append((team1, team2)) # Team1 home, Team2 away
    fixtures.append((team2, team1)) # Team2 home, Team1 away
random.shuffle(fixtures) # Randomize the order of games

# --- Simulation Parameters ---
runs = 1000 # Number of seasons to simulate (as requested)

# --- Data Storage for Results ---
position_counts = defaultdict(lambda: defaultdict(int))
title_counts = defaultdict(int)
total_points_per_team = defaultdict(int) 

# Variables to track min/max points across all simulations
global_min_points = float('inf')
global_max_points = float('-inf')

# --- Simulation Functions ---
def simulate_score_poisson(expected_goals):
    """Generates goals using a Poisson distribution based on expected goals."""
    return np.random.poisson(max(0, expected_goals)) # Ensure lambda is non-negative

def simulate_match(home_team, away_team, team_strengths_data):
    """
    Simulates a single match using teams' adjusted GF_avg and GA_avg.
    Expected goals for each team are based on their attack strength vs. opponent's defense strength.
    """
    home_strength = team_strengths_data[home_team]
    away_strength = team_strengths_data[away_team]

    # Expected goals calculation using adjusted GF_avg and GA_avg
    home_expected_goals = (home_strength["GF_avg"] + away_strength["GA_avg"]) / 2
    away_expected_goals = (away_strength["GF_avg"] + home_strength["GA_avg"]) / 2

    # Apply home advantage (simple addition to home team's expected goals)
    HOME_ADVANTAGE_GOALS = 0.15 # Example: home team gets an extra 0.15 expected goals
    home_expected_goals += HOME_ADVANTAGE_GOALS

    # Ensure expected goals are non-negative
    home_expected_goals = max(0.1, home_expected_goals) # Minimum non-zero for Poisson
    away_expected_goals = max(0.1, away_expected_goals)

    home_goals = simulate_score_poisson(home_expected_goals)
    away_goals = simulate_score_poisson(away_expected_goals)
    
    return home_goals, away_goals

# --- Main Simulation Loop ---
for _ in tqdm(range(runs), desc="Simulating Seasons"):
    # Reset current season stats for each new simulation run
    sim_stats = {team: {"Pld": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "Pts": 0, "GD": 0} for team in all_teams}
    
    # Simulate all fixtures for the season (38 games per team)
    for home, away in fixtures:
        hg, ag = simulate_match(home, away, teams_combined_strength_data)
        
        # Update current season stats for both teams
        sim_stats[home]["Pld"] += 1
        sim_stats[away]["Pld"] += 1
        sim_stats[home]["GF"] += hg
        sim_stats[away]["GF"] += ag
        sim_stats[home]["GA"] += ag
        sim_stats[away]["GA"] += hg
        sim_stats[home]["GD"] += hg - ag
        sim_stats[away]["GD"] += ag - hg
        
        if hg > ag:
            sim_stats[home]["Pts"] += 3
            sim_stats[home]["W"] += 1
            sim_stats[away]["L"] += 1
        elif ag > hg:
            sim_stats[away]["Pts"] += 3
            sim_stats[away]["W"] += 1
            sim_stats[home]["L"] += 1
        else:
            sim_stats[home]["Pts"] += 1
            sim_stats[away]["Pts"] += 1
            sim_stats[home]["D"] += 1
            sim_stats[away]["D"] += 1

    # Sort the final league table for this simulation run
    table = sorted(sim_stats.items(), key=lambda x: (x[1]["Pts"], x[1]["GD"], x[1]["GF"]), reverse=True)
    
    # Record positions for each team in this run
    season_min_points = float('inf')
    season_max_points = float('-inf')

    for idx, (team_name, team_data) in enumerate(table):
        position_counts[team_name][idx + 1] += 1
        total_points_per_team[team_name] += team_data["Pts"] # Add points to running total
        
        # Update min/max points for this specific season
        season_min_points = min(season_min_points, team_data["Pts"])
        season_max_points = max(season_max_points, team_data["Pts"])
    
    # Update global min/max points across all simulations
    global_min_points = min(global_min_points, season_min_points)
    global_max_points = max(global_max_points, season_max_points)

    # Record title winner
    title_counts[table[0][0]] += 1


# --- Print Results ---
print(f"\n--- Premier League 2025-2026 Season Simulation Results ({runs} runs) ---")
print("Probabilities of each team winning the title and finishing in each position:")
print(f"Stats normalized using a multi-stage approach for fairness and accuracy (as described above).")
print("-" * 140)

# Prepare data for a more readable table
header = f"{'Team':35} | {'Title %':<9} | " + " | ".join([f"Pos {i+1}%" for i in range(5)]) + " | " + " | ".join([f"Relegation %"])
print(header)
print("-" * 140)

# Sort teams by their probability of winning the title
sorted_teams_by_title_chance = sorted(
    all_teams,
    key=lambda team_name: title_counts[team_name],
    reverse=True
)

for team in sorted_teams_by_title_chance:
    title_prob = title_counts[team] / runs
    
    # Get probabilities for top 5 positions
    pos_probs = [position_counts[team][i+1] / runs for i in range(5)]
    
    # Calculate relegation probability (finishing 18th, 19th, or 20th)
    relegation_prob = (position_counts[team][18] + position_counts[team][19] + position_counts[team][20]) / runs

    row = f"{team:35} | {title_prob:.2%} | " + " | ".join([f"{p:.2%}" for p in pos_probs]) + f" | {relegation_prob:.2%}"
    print(row)

print("-" * 140)


# --- Average Points and Rank Table ---
print("\n--- Average Points and Rank per Team (across all simulations) ---")
print("-" * 55)
print(f"{'Rank':<5} | {'Team':35} | {'Avg Pts':<9}")
print("-" * 55)

average_points_data = []
for team in all_teams:
    avg_pts = total_points_per_team[team] / runs
    average_points_data.append({"Team": team, "AvgPts": avg_pts})

# Sort by average points in descending order
average_points_data_sorted = sorted(average_points_data, key=lambda x: x["AvgPts"], reverse=True)

for rank, data in enumerate(average_points_data_sorted):
    print(f"{rank + 1:<5} | {data['Team']:35} | {data['AvgPts']:.2f}")

print("-" * 55)

# --- Lowest and Most Points Gathered ---
print("\n--- Overall Points Extremes Across All Simulations ---")
print(f"Lowest points gathered by any team in a simulated season: {global_min_points}")
print(f"Highest points gathered by any team in a simulated season: {global_max_points}")
print("-" * 50)

# --- Total Titles Won by Each Team ---
print("\n--- Total Premier League Titles Won ---")
print("-" * 50)
print(f"{'Team':35} | {'Titles Won':<10}")
print("-" * 50)

# Sort teams by the number of titles won in descending order
sorted_titles = sorted(title_counts.items(), key=lambda item: item[1], reverse=True)

for team, wins in sorted_titles:
    print(f"{team:35} | {wins:<10}")

print("-" * 50)