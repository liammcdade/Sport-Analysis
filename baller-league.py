import random
import numpy as np
from collections import defaultdict
from tqdm import tqdm
import itertools

# 1. Define the 12 teams based on your provided table
teams = [
    "Deportrio", "Yanited", "MVPs United", "Santan", "Trebol", "SDS",
    "VZN", "26ers", "M7", "Rules the World", "Wembley Rangers", "N5"
]

# 2. Parse current league standings (Pld is 10)
current_standings_data = {
    "Deportrio":         {"Pld": 10, "W": 7, "D": 1, "L": 2, "GF": 39, "GA": 29, "Pts": 23},
    "Yanited":           {"Pld": 10, "W": 7, "D": 1, "L": 2, "GF": 46, "GA": 27, "Pts": 22},
    "MVPs United":       {"Pld": 10, "W": 7, "D": 0, "L": 3, "GF": 40, "GA": 37, "Pts": 21},
    "Santan":            {"Pld": 10, "W": 6, "D": 0, "L": 4, "GF": 42, "GA": 40, "Pts": 18},
    "Trebol":            {"Pld": 10, "W": 5, "D": 2, "L": 3, "GF": 44, "GA": 35, "Pts": 17},
    "SDS":               {"Pld": 10, "W": 5, "D": 1, "L": 4, "GF": 41, "GA": 34, "Pts": 17},
    "VZN":               {"Pld": 10, "W": 4, "D": 2, "L": 4, "GF": 41, "GA": 49, "Pts": 17},
    "26ers":             {"Pld": 10, "W": 3, "D": 3, "L": 4, "GF": 45, "GA": 44, "Pts": 13},
    "M7":                {"Pld": 10, "W": 3, "D": 2, "L": 5, "GF": 32, "GA": 37, "Pts": 11},
    "Rules the World":   {"Pld": 10, "W": 2, "D": 2, "L": 6, "GF": 30, "GA": 41, "Pts": 10},
    "Wembley Rangers":   {"Pld": 10, "W": 2, "D": 2, "L": 6, "GF": 31, "GA": 39, "Pts": 8},
    "N5":                {"Pld": 10, "W": 1, "D": 0, "L": 9, "GF": 34, "GA": 53, "Pts": 4}
}

for team, stats in current_standings_data.items():
    stats["GD"] = stats["GF"] - stats["GA"]

TOTAL_GAMES_PER_TEAM_SEASON = len(teams) - 1

GAMES_TO_SIMULATE_PER_TEAM = TOTAL_GAMES_PER_TEAM_SEASON - current_standings_data[teams[0]]["Pld"]

if GAMES_TO_SIMULATE_PER_TEAM != 1:
    print(f"Error: Expected 1 game per team remaining, but {GAMES_TO_SIMULATE_PER_TEAM} calculated.")
    print("Please verify 'Pld' values in current_standings_data.")
    exit()

team_strengths = {}
for team, stats in current_standings_data.items():
    team_strengths[team] = {
        "GF_avg": stats["GF"] / stats["Pld"],
        "GA_avg": stats["GA"] / stats["Pld"]
    }

position_counts = defaultdict(lambda: defaultdict(int))
# New counter for overall champion (playoff winner)
overall_champion_counts = defaultdict(int)
average_points_sum = defaultdict(float)


def simulate_score(team_avg_gf, opponent_avg_ga, default_avg_goals=1.5):
    lambda_val = (team_avg_gf + opponent_avg_ga) / 2
    return np.random.poisson(max(0.1, lambda_val))

def simulate_match_with_strengths(home_team, away_team, initial_strengths):
    home_attack_strength = initial_strengths[home_team]["GF_avg"]
    home_defense_strength = initial_strengths[home_team]["GA_avg"]

    away_attack_strength = initial_strengths[away_team]["GF_avg"]
    away_defense_strength = initial_strengths[away_team]["GA_avg"]

    home_goals = simulate_score(home_attack_strength, away_defense_strength)
    away_goals = simulate_score(away_attack_strength, home_defense_strength)
    
    # Handle draws in playoffs - typically goes to extra time/penalties.
    # For simplicity in simulation, we'll assign a random winner if it's a draw.
    # A more complex model could simulate extra time goals or penalties.
    if home_goals == away_goals:
        if random.random() < 0.5:
            return home_goals + 1, away_goals # Home wins by 1
        else:
            return home_goals, away_goals + 1 # Away wins by 1
    return home_goals, away_goals


NUM_RUNS = 100000

for _ in tqdm(range(NUM_RUNS), desc="Simulating Seasons"):
    sim_stats = {team: stats.copy() for team, stats in current_standings_data.items()}

    teams_for_final_round = list(teams)
    random.shuffle(teams_for_final_round)
    
    final_fixtures_this_run = []
    for i in range(0, len(teams_for_final_round), 2):
        team_a = teams_for_final_round[i]
        team_b = teams_for_final_round[i+1]
        
        if random.random() < 0.5:
            final_fixtures_this_run.append((team_a, team_b))
        else:
            final_fixtures_this_run.append((team_b, team_a))

    for home, away in final_fixtures_this_run:
        hg, ag = simulate_match_with_strengths(home, away, team_strengths)

        sim_stats[home]["Pld"] += 1
        sim_stats[away]["Pld"] += 1
        sim_stats[home]["GF"] += hg
        sim_stats[away]["GF"] += ag
        sim_stats[home]["GA"] += ag
        sim_stats[away]["GA"] += hg
        sim_stats[home]["GD"] = sim_stats[home]["GF"] - sim_stats[home]["GA"]
        sim_stats[away]["GD"] = sim_stats[away]["GF"] - sim_stats[away]["GA"]
        
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
        
    final_regular_season_table = sorted(sim_stats.items(), key=lambda x: (x[1]["Pts"], x[1]["GD"], x[1]["GF"]), reverse=True)

    # Record regular season final positions
    for idx, (team, stats) in enumerate(final_regular_season_table):
        position_counts[team][idx + 1] += 1
        average_points_sum[team] += stats["Pts"]
    
    # --- Playoff Simulation ---
    # Get the top 4 teams based on regular season standings
    top_4_teams = [team_data[0] for team_data in final_regular_season_table[:4]]

    # Only proceed with playoffs if there are exactly 4 teams
    if len(top_4_teams) == 4:
        team_1 = top_4_teams[0]
        team_2 = top_4_teams[1]
        team_3 = top_4_teams[2]
        team_4 = top_4_teams[3]

        # Semi-final 1: 1st vs 4th
        # Assume home advantage for the higher-ranked team in playoffs
        s1_winner = None
        hg1, ag1 = simulate_match_with_strengths(team_1, team_4, team_strengths)
        if hg1 > ag1:
            s1_winner = team_1
        else:
            s1_winner = team_4

        # Semi-final 2: 2nd vs 3rd
        s2_winner = None
        hg2, ag2 = simulate_match_with_strengths(team_2, team_3, team_strengths)
        if hg2 > ag2:
            s2_winner = team_2
        else:
            s2_winner = team_3
        
        # Final: Winner Semi-final 1 vs Winner Semi-final 2
        final_winner = None
        # In a final, assume neutral ground, or flip for home advantage
        if random.random() < 0.5: # Randomly decide home/away for the final
            final_hg, final_ag = simulate_match_with_strengths(s1_winner, s2_winner, team_strengths)
            if final_hg > final_ag:
                final_winner = s1_winner
            else:
                final_winner = s2_winner
        else:
            final_hg, final_ag = simulate_match_with_strengths(s2_winner, s1_winner, team_strengths)
            if final_hg > final_ag:
                final_winner = s2_winner
            else:
                final_winner = s1_winner
        
        overall_champion_counts[final_winner] += 1
    # else: If less than 4 teams, no playoffs or title winner for this run (shouldn't happen with 12 teams)


print("\n" + "="*80)
print("                      SIMULATION RESULTS ANALYSIS")
print("        (Based on Current Standings, Final Regular Game & Playoff)")
print("="*80 + "\n")

print(f"Simulations run: {NUM_RUNS}")
print(f"Total games in regular season: {TOTAL_GAMES_PER_TEAM_SEASON}")
print(f"Games already played per team: {current_standings_data[teams[0]]['Pld']}")
print(f"Games simulated per team for regular season: {GAMES_TO_SIMULATE_PER_TEAM}\n")
print(f"Playoff structure: Top 4 teams, 1st vs 4th, 2nd vs 3rd, then Final.\n")

print("## Probabilities of Finishing in Regular Season Top 4")
print("--------------------------------------------------------------------------------")
print(f"{'Team':25} | {'Top 4 Chance':<15} | {'Playoff Champion':<18} | {'Avg Final Pts':<15}")
print("--------------------------------------------------------------------------------")

team_analysis_data = []
for team in teams:
    top_4_count = sum(position_counts[team][i] for i in range(1, 5))
    top_4_chance = top_4_count / NUM_RUNS
    
    playoff_champion_chance = overall_champion_counts[team] / NUM_RUNS
    avg_points = average_points_sum[team] / NUM_RUNS
    
    team_analysis_data.append({
        "team": team,
        "top_4_chance": top_4_chance,
        "playoff_champion_chance": playoff_champion_chance,
        "avg_points": avg_points
    })

sorted_teams_for_display = sorted(
    team_analysis_data,
    key=lambda x: (x["top_4_chance"], x["playoff_champion_chance"], x["avg_points"]),
    reverse=True
)

for data in sorted_teams_for_display:
    print(f"{data['team']:25} | {data['top_4_chance']:.2%} | {data['playoff_champion_chance']:.2%} | {data['avg_points']:.2f}")

print("\n")

print("## Full Regular Season Position Probabilities (All 12 Positions Displayed)")
print("--------------------------------------------------------------------------------")
max_pos_display = len(teams)
header_cols = [f"{i}st" if i == 1 else f"{i}nd" if i == 2 else f"{i}rd" if i == 3 else f"{i}th" for i in range(1, max_pos_display + 1)]
header = f"{'Team':20} | " + " | ".join(header_cols)
print(header)
separator_length = 20 + 3 + sum(len(f"{100.0:.1%}") + 3 for _ in range(max_pos_display))
print("-" * min(separator_length, 120)) 

for data in sorted_teams_for_display:
    team_name = data['team']
    pos_probs = []
    for i in range(1, max_pos_display + 1):
        prob = position_counts[team_name][i] / NUM_RUNS
        pos_probs.append(f"{prob:.1%}")
    print(f"{team_name:20} | " + " | ".join(pos_probs))
print("\n")

print("="*80)
print("Simulation Complete!")
print("="*80)