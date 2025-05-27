import random
import numpy as np
from collections import defaultdict
from tqdm import tqdm
import itertools # To generate all combinations for fixtures

# 1. Define the 20 teams
teams = [
    "Liverpool", "Arsenal", "Manchester City", "Newcastle United", "Chelsea",
    "Aston Villa", "Nottingham Forest", "Brighton & Hove Albion", "Brentford", "Fulham",
    "Bournemouth", "Crystal Palace", "Everton", "Wolverhampton Wanderers", "West Ham United",
    "Manchester United", "Tottenham Hotspur", "Leeds United", "Burnley", "Sunderland"
]

# 2. Initialize team stats to a baseline for a fresh season
# We'll use a small non-zero Pld to avoid division by zero immediately, or handle it in simulate_score
# A more common approach is to use 'attack' and 'defense' ratings.
# For simplicity, let's just initialize all stats to 0, and modify simulate_score to handle Pld=0.
initial_team_stats = {team: {"Pld": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "Pts": 0, "GD": 0} for team in teams}

# 3. Generate all fixtures (home and away)
fixtures = []
for team1, team2 in itertools.combinations(teams, 2):
    fixtures.append((team1, team2)) # Team1 home, Team2 away
    fixtures.append((team2, team1)) # Team2 home, Team1 away
random.shuffle(fixtures) # Shuffle the fixtures to randomize the schedule

qualification_counts = defaultdict(lambda: {"CL": 0, "EL": 0, "ECL": 0, "Overall": 0, "Title": 0})

# New counters for total slots assigned per competition across all runs
total_cl_slots_sum = 0
total_el_slots_sum = 0
total_ecl_slots_sum = 0

def simulate_score(avg_goals_for, avg_goals_against, default_avg_goals=1.5):
    # If Pld is 0 for either team, the avg_goals_for/against would be 0 or undefined.
    # Use a default average for the very first games.
    if avg_goals_for == 0 and avg_goals_against == 0: # This implies Pld was 0 for both in the calculation
        lambda_val = default_avg_goals
    else:
        # Use the actual average goals, ensuring it's not negative
        lambda_val = max(0, (avg_goals_for + avg_goals_against) / 2)
    return np.random.poisson(lambda_val)

def simulate_match(home, away, current_team_stats):
    home_stats = current_team_stats[home]
    away_stats = current_team_stats[away]

    # To avoid division by zero when Pld is 0 at the start of the season,
    # use a default average goal rate (e.g., 1.5 goals per team per game)
    # The stats will accumulate, and these averages will quickly become meaningful.
    home_avg_gf = home_stats["GF"] / home_stats["Pld"] if home_stats["Pld"] > 0 else 1.5 # Default average for a neutral game
    away_avg_ga = away_stats["GA"] / away_stats["Pld"] if away_stats["Pld"] > 0 else 1.5

    away_avg_gf = away_stats["GF"] / away_stats["Pld"] if away_stats["Pld"] > 0 else 1.5
    home_avg_ga = home_stats["GA"] / home_stats["Pld"] if home_stats["Pld"] > 0 else 1.5

    home_goals = simulate_score(home_avg_gf, away_avg_ga)
    away_goals = simulate_score(away_avg_gf, home_avg_ga)
    
    return home_goals, away_goals

NUM_CL_LEAGUE_SPOTS = 5 



runs = 10000

for _ in tqdm(range(runs), desc="Simulating Seasons"):
    # Reset stats for each new simulation run
    sim_stats = {team: {"Pld": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "Pts": 0, "GD": 0} for team in teams}
    
    for home, away in fixtures:
        hg, ag = simulate_match(home, away, sim_stats)
        
        # Update stats for both teams
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

    table = sorted(sim_stats.items(), key=lambda x: (x[1]["Pts"], x[1]["GD"], x[1]["GF"]), reverse=True)

    final_league_positions = {team_data[0]: idx + 1 for idx, team_data in enumerate(table)}
    
    current_cl_qualifiers = set()
    current_el_qualifiers = set()
    current_ecl_qualifiers = set()
    
    # European Qualification for a "fresh" season (purely league based)
    # Top NUM_CL_LEAGUE_SPOTS (e.g., 5) for Champions League
    for i in range(min(NUM_CL_LEAGUE_SPOTS, len(table))):
        current_cl_qualifiers.add(table[i][0])
            
    # Next few spots for Europa League and Europa Conference League
    # Assuming EL for 6th, ECL for 7th if no cup winners free up spots
    el_spot_found = False
    ecl_spot_found = False

    for team, pos in final_league_positions.items():
        if team not in current_cl_qualifiers and team not in current_el_qualifiers and team not in current_ecl_qualifiers:
            if pos == (NUM_CL_LEAGUE_SPOTS + 1) and not el_spot_found: # E.g., 6th place
                current_el_qualifiers.add(team)
                el_spot_found = True
            elif pos == (NUM_CL_LEAGUE_SPOTS + 2) and not ecl_spot_found: # E.g., 7th place
                current_ecl_qualifiers.add(team)
                ecl_spot_found = True
        
        # Break if all league spots assigned
        if el_spot_found and ecl_spot_found:
            break

    # Accumulate the number of slots for this run
    total_cl_slots_sum += len(current_cl_qualifiers)
    total_el_slots_sum += len(current_el_qualifiers)
    total_ecl_slots_sum += len(current_ecl_qualifiers)

    # Finally, update qualification_counts based on the finalized sets for this run
    for team in current_cl_qualifiers:
        qualification_counts[team]["CL"] += 1
    for team in current_el_qualifiers:
        qualification_counts[team]["EL"] += 1
    for team in current_ecl_qualifiers:
        qualification_counts[team]["ECL"] += 1
    
    # Calculate overall qualification for this run (distinct teams)
    all_european_qualifiers_this_run = current_cl_qualifiers.union(current_el_qualifiers).union(current_ecl_qualifiers)
    for team in all_european_qualifiers_this_run:
        qualification_counts[team]["Overall"] += 1
    
    qualification_counts[table[0][0]]["Title"] += 1

# Calculate average European slots
avg_cl_slots = total_cl_slots_sum / runs
avg_el_slots = total_el_slots_sum / runs
avg_ecl_slots = total_ecl_slots_sum / runs
avg_total_european_slots = avg_cl_slots + avg_el_slots + avg_ecl_slots

print("\n--- Average European Slots Assigned Per Season ---")
print(f"Average Champions League (CL) slots: {avg_cl_slots:.2f}")
print(f"Average Europa League (EL) slots: {avg_el_slots:.2f}")
print(f"Average Europa Conference League (ECL) slots: {avg_ecl_slots:.2f}")
print(f"Average Total European slots: {avg_total_european_slots:.2f}")
print("-" * 60)

print("\nQualification chances over", runs, "simulations (fresh season, purely league based):")
print(f"{'Team':20} | {'CL':<7} | {'EL':<7} | {'ECL':<7} | {'Overall':<9} | {'Title':<7}")
print("-" * 80)

all_team_names = sorted(team_stats_dict.keys())

sorted_teams_for_display = sorted(
    all_team_names,
    key=lambda team_name: (
        -qualification_counts[team_name]["Overall"],
        -qualification_counts[team_name]["CL"],
        -qualification_counts[team_name]["EL"],
        -qualification_counts[team_name]["ECL"],
        -qualification_counts[team_name]["Title"]
    )
)

for team in sorted_teams_for_display:
    counts = qualification_counts[team]
    print(f"{team:20} | {counts['CL']/runs:.2%} | {counts['EL']/runs:.2%} | {counts['ECL']/runs:.2%} | {counts['Overall']/runs:.2%} | {counts['Title']/runs:.2%}")