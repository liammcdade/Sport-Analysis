import random
import math
from itertools import permutations, product
from collections import defaultdict

# --- 1. Define the Pots with Teams and Rankings ---
pots_data = {
    "Pot 1": [("Panama", 33), ("Costa Rica", 54), ("Jamaica", 63)],
    "Pot 2": [("Honduras", 75), ("El Salvador", 81), ("Haiti", 83)],
    "Pot 3": [("Curaçao", 90), ("Trinidad and Tobago", 100), ("Guatemala", 106)],
    "Pot 4": [("Nicaragua", 133), ("Suriname", 137), ("Bermuda", 168)]
}

# --- Helper Function: Convert Ranking to Strength Score ---
# A higher strength score indicates a stronger team.
# Using a linear inverse scaling: lower FIFA ranking means higher strength.
# Max FIFA rank in our data is 168 (Bermuda), min is 33 (Panama).
# We map these to a strength scale where higher is better.
# A simple mapping: strength = 170 - ranking (arbitrary offset to ensure positive strengths)
def get_strength_score(ranking):
    return 170 - ranking # Panama: 137, Bermuda: 2

# Prepare teams with their strength scores for quick lookup
teams_with_strength_map = {}
for pot_name, teams in pots_data.items():
    for team, ranking in teams:
        teams_with_strength_map[team] = {
            "ranking": ranking,
            "strength": get_strength_score(ranking)
        }

# --- 2. Match Simulation Function ---
# Simulates a single match between two teams based on their strength scores.
# Returns points and goals for each team based on the simulated outcome.
def simulate_match(team1_name, team1_strength, team2_name, team2_strength):
    # Probabilities for win, draw, loss based on relative strength.
    # Adding a constant to the denominator to temper extreme probabilities and allow for draws/upsets.
    total_strength_plus_constant = team1_strength + team2_strength + 70 

    prob_team1_wins = team1_strength / total_strength_plus_constant
    prob_team2_wins = team2_strength / total_strength_plus_constant
    prob_draw = 1.0 - prob_team1_wins - prob_team2_wins

    # Adjust probabilities if floating point arithmetic leads to negative or sum > 1 for prob_draw
    if prob_draw < 0:
        scale_factor = prob_team1_wins + prob_team2_wins
        prob_team1_wins /= scale_factor
        prob_team2_wins /= scale_factor
        prob_draw = 0.0
    else:
        # Re-normalize to ensure probabilities sum exactly to 1
        total_sum = prob_team1_wins + prob_team2_wins + prob_draw
        prob_team1_wins /= total_sum
        prob_team2_wins /= total_sum
        prob_draw /= total_sum
    
    r = random.random()

    points_t1, points_t2 = 0, 0
    goals_t1, goals_t2 = 0, 0

    if r < prob_team1_wins:
        # Team 1 wins
        points_t1 = 3
        points_t2 = 0
        # Assign goals. Stronger team wins with a more dominant score.
        if team1_strength > team2_strength:
            goals_t1 = random.randint(2, 4) 
            goals_t2 = random.randint(0, 1)
        else: # Upset win by weaker team1
            goals_t1 = random.randint(1, 2)
            goals_t2 = random.randint(0, 1)
            if goals_t1 <= goals_t2: goals_t1 = goals_t2 + 1 # Ensure Team 1 wins
    elif r < prob_team1_wins + prob_draw:
        # Draw
        points_t1 = 1
        points_t2 = 1
        goals = random.randint(0, 2) # Typical low-scoring draw
        goals_t1 = goals
        goals_t2 = goals
    else:
        # Team 2 wins
        points_t1 = 0
        points_t2 = 3
        # Assign goals. Stronger team wins with a more dominant score.
        if team2_strength > team1_strength:
            goals_t2 = random.randint(2, 4) 
            goals_t1 = random.randint(0, 1)
        else: # Upset win by weaker team2
            goals_t2 = random.randint(1, 2)
            goals_t1 = random.randint(0, 1)
            if goals_t2 <= goals_t1: goals_t2 = goals_t1 + 1 # Ensure Team 2 wins
            
    return (points_t1, points_t2, goals_t1, goals_t2)

# --- 3. Group Stage Simulation Function ---
# Simulates a home-and-away round-robin group stage for a given set of 4 teams.
# Returns the 1st place team (direct qualifier) and 2nd place team (playoff contender info).
def simulate_group_stage(group_teams_raw):
    # Initialize standings for all teams in the group
    group_standings = {
        team_name: {
            'points': 0, 'wins': 0, 'draws': 0, 'losses': 0,
            'goals_for': 0, 'goals_against': 0, 'goal_difference': 0
        } for team_name, _ in group_teams_raw
    }

    # Prepare team info with strength for match simulation
    group_teams_info = [(team_name, teams_with_strength_map[team_name]["strength"]) for team_name, _ in group_teams_raw]
    
    # Simulate all matches in a home-and-away round-robin format
    for i in range(len(group_teams_info)):
        for j in range(i + 1, len(group_teams_info)):
            team1_name, team1_strength = group_teams_info[i]
            team2_name, team2_strength = group_teams_info[j]

            # Match 1: Team 1 vs Team 2
            p1_m1, p2_m1, g1_m1, g2_m1 = simulate_match(team1_name, team1_strength, team2_name, team2_strength)

            # Update standings for Team 1 (as home team)
            group_standings[team1_name]['points'] += p1_m1
            group_standings[team1_name]['goals_for'] += g1_m1
            group_standings[team1_name]['goals_against'] += g2_m1
            if p1_m1 == 3: group_standings[team1_name]['wins'] += 1
            elif p1_m1 == 1: group_standings[team1_name]['draws'] += 1
            else: group_standings[team1_name]['losses'] += 1

            # Update standings for Team 2 (as away team)
            group_standings[team2_name]['points'] += p2_m1
            group_standings[team2_name]['goals_for'] += g2_m1
            group_standings[team2_name]['goals_against'] += g1_m1
            if p2_m1 == 3: group_standings[team2_name]['wins'] += 1
            elif p2_m1 == 1: group_standings[team2_name]['draws'] += 1
            else: group_standings[team2_name]['losses'] += 1

            # Match 2: Team 2 vs Team 1 (reverse fixture)
            p2_m2, p1_m2, g2_m2, g1_m2 = simulate_match(team2_name, team2_strength, team1_name, team1_strength) # Note: order of teams/strengths flipped for reverse fixture

            # Update standings for Team 2 (as home team)
            group_standings[team2_name]['points'] += p2_m2
            group_standings[team2_name]['goals_for'] += g2_m2
            group_standings[team2_name]['goals_against'] += g1_m2
            if p2_m2 == 3: group_standings[team2_name]['wins'] += 1
            elif p2_m2 == 1: group_standings[team2_name]['draws'] += 1
            else: group_standings[team2_name]['losses'] += 1
            
            # Update standings for Team 1 (as away team)
            group_standings[team1_name]['points'] += p1_m2
            group_standings[team1_name]['goals_for'] += g1_m2
            group_standings[team1_name]['goals_against'] += g2_m2
            if p1_m2 == 3: group_standings[team1_name]['wins'] += 1
            elif p1_m2 == 1: group_standings[team1_name]['draws'] += 1
            else: group_standings[team1_name]['losses'] += 1

    # After all matches, calculate final goal differences
    for team_name, stats in group_standings.items():
        stats['goal_difference'] = stats['goals_for'] - stats['goals_against']
    
    # Convert standings to a list of tuples for sorting and determining ranks
    # Format: (team_name, points, goal_difference, goals_for, wins)
    sorted_standings_list = []
    for team, stats in group_standings.items():
        sorted_standings_list.append((
            team, 
            stats['points'], 
            stats['goal_difference'], 
            stats['goals_for'],
            stats['wins']
        ))
    
    # Sort standings:
    # 1. Points (descending)
    # 2. Goal Difference (descending)
    # 3. Goals For (descending)
    # 4. Wins (descending) - Standard tie-breaker
    sorted_standings_list.sort(key=lambda x: (x[1], x[2], x[3], x[4]), reverse=True)

    # The first team in the sorted list is 1st place, second is 2nd place
    first_place_team = sorted_standings_list[0][0]
    second_place_team_info = {
        'name': sorted_standings_list[1][0],
        'points': sorted_standings_list[1][1],
        'goal_difference': sorted_standings_list[1][2],
        'goals_for': sorted_standings_list[1][3]
    }
    
    return first_place_team, second_place_team_info

# --- 4. Generate All Possible Draw Configurations ---
pot_permutations = []
for pot_name in pots_data:
    pot_permutations.append(list(permutations(pots_data[pot_name])))

all_draw_configurations = list(product(*pot_permutations))
total_num_draws = len(all_draw_configurations)
print(f"Total number of unique draw configurations to analyze: {total_num_draws}\n")

# --- 5. Simulate All Draws and Aggregate Results ---
overall_qualification_results = defaultdict(lambda: {'direct_qual': 0, 'playoff_spot': 0})

for draw_config in all_draw_configurations:
    groups = {
        "A": [],
        "B": [],
        "C": []
    }

    for i, pot_permutation in enumerate(draw_config):
        groups["A"].append(pot_permutation[0]) 
        groups["B"].append(pot_permutation[1])
        groups["C"].append(pot_permutation[2])

    second_place_contenders = []

    for group_name, group_teams_raw in groups.items():
        first_place_team, second_place_team_info = simulate_group_stage(group_teams_raw)
        
        overall_qualification_results[first_place_team]['direct_qual'] += 1
        second_place_contenders.append(second_place_team_info)

    # Determine the TWO inter-confederation playoff spots
    # Sort contenders by points (desc), then goal difference (desc), then goals for (desc)
    second_place_contenders.sort(key=lambda x: (x['points'], x['goal_difference'], x['goals_for']), reverse=True)
    
    # *** CHANGE APPLIED HERE: All 2nd place teams (1 from each group) get a playoff spot ***
    # Now, all three 2nd place teams get a playoff spot, as per the latest clarification.
    for contender_info in second_place_contenders:
        playoff_spot_winner_name = contender_info['name']
        overall_qualification_results[playoff_spot_winner_name]['playoff_spot'] += 1

# --- 6. Calculate and Print Final Percentages ---
print("## World Cup Qualification Likelihood (Simulated Results):\n")
print("--- Simulation Assumptions ---")
print("1.  **Group Stage:** Three groups of four teams, playing home-and-away (6 matches per team).")
print("2.  **Match Outcomes:** Probabilistic, based on FIFA rankings (higher ranking = higher strength). Strength influences win/draw/loss probability and goal scores.")
print("3.  **Points System:** Win = 3 points, Draw = 1 point, Loss = 0 points.")
print("4.  **Group Standings Tie-breakers:** Points, then Goal Difference, then Goals For, then Wins.")
print("5.  **Qualification Rules:**")
print("    * **Direct Qualification:** The 1st place team in each group qualifies automatically (3 spots).")
print("    * **Inter-Confederation Playoff:** The 2nd place team from *each* of the three groups advances to the Inter-Confederation Play-offs (3 spots).") # Updated assumption
print("\n")

final_percentages = {}
for team_name in teams_with_strength_map.keys():
    direct_qual_count = overall_qualification_results[team_name]['direct_qual']
    playoff_spot_count = overall_qualification_results[team_name]['playoff_spot']
    
    direct_percentage = (direct_qual_count / total_num_draws) * 100
    playoff_percentage = (playoff_spot_count / total_num_draws) * 100
    total_percentage = ((direct_qual_count + playoff_spot_count) / total_num_draws) * 100
    
    final_percentages[team_name] = {
        'direct_qual': direct_percentage,
        'playoff_spot': playoff_percentage,
        'total_chance': total_percentage
    }

sorted_final_percentages = sorted(final_percentages.items(), key=lambda item: item[1]['total_chance'], reverse=True)

print("| Team                  | Direct Qualification (%) | Playoff Spot Chance (%) | Total Qualification Chance (%) |")
print("|-----------------------|--------------------------|-------------------------|--------------------------------|")
for team, data in sorted_final_percentages:
    print(f"| {team:<21} | {data['direct_qual']:<24.2f} | {data['playoff_spot']:<23.2f} | {data['total_chance']:<30.2f} |")

