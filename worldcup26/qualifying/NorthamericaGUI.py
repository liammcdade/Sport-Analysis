import random
import math
from itertools import permutations, product
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time 

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

# --- 3. Group Stage Simulation Function for a single draw (to be called by animation) ---
# This version will yield group standings after each matchday for animation purposes.
def simulate_group_stage_for_animation(group_teams_raw):
    # Initialize standings for all teams in the group
    group_standings = {
        team_name: {
            'points': 0, 'wins': 0, 'draws': 0, 'losses': 0,
            'goals_for': 0, 'goals_against': 0, 'goal_difference': 0
        } for team_name, _ in group_teams_raw
    }
    # Prepare team info with strength for match simulation
    group_teams_info = [(team_name, teams_with_strength_map[team_name]["strength"]) for team_name, _ in group_teams_raw]
    
    # Define a fixed match schedule for 4 teams to ensure consistent matchdays for visualization
    # This ensures that for each "matchday" (frame in the animation), a set of relevant matches is played.
    # Total 12 matches (home and away) over 6 matchdays.
    if len(group_teams_info) == 4:
        T1, T2, T3, T4 = group_teams_info[0], group_teams_info[1], group_teams_info[2], group_teams_info[3]
        match_schedule_by_matchday = [
            [(T1, T2), (T3, T4)], # Matchday 1: T1 vs T2, T3 vs T4
            [(T1, T3), (T2, T4)], # Matchday 2: T1 vs T3, T2 vs T4
            [(T1, T4), (T2, T3)], # Matchday 3: T1 vs T4, T2 vs T3
            [(T2, T1), (T4, T3)], # Matchday 4: T2 vs T1, T4 vs T3
            [(T3, T1), (T4, T2)], # Matchday 5: T3 vs T1, T4 vs T2
            [(T4, T1), (T3, T2)]  # Matchday 6: T4 vs T1, T3 vs T2
        ]
    else:
        # Fallback for other group sizes (though problem specifies 4 teams)
        match_schedule_by_matchday = []
        # For simplicity, if not 4 teams, just list all home-and-away pairs sequentially
        # Each pair will be its own 'matchday'
        for i in range(len(group_teams_info)):
            for j in range(i + 1, len(group_teams_info)):
                match_schedule_by_matchday.append([
                    (group_teams_info[i], group_teams_info[j]),
                    (group_teams_info[j], group_teams_info[i])
                ])

    # Yield initial standings before any matches are played (Frame 0)
    yield "Initial Standings", group_standings, [] # No match results yet

    for i, matchday_fixtures in enumerate(match_schedule_by_matchday):
        matchday_results_display = []
        for (team1_name, team1_strength), (team2_name, team2_strength) in matchday_fixtures:
            p1, p2, g1, g2 = simulate_match(team1_name, team1_strength, team2_name, team2_strength)
            
            # Record match result for display in the animation
            match_result_str = f"{team1_name} {g1}-{g2} {team2_name}"
            matchday_results_display.append(match_result_str)

            # Update standings for Team 1
            group_standings[team1_name]['points'] += p1
            group_standings[team1_name]['goals_for'] += g1
            group_standings[team1_name]['goals_against'] += g2
            if p1 == 3: group_standings[team1_name]['wins'] += 1
            elif p1 == 1: group_standings[team1_name]['draws'] += 1
            else: group_standings[team1_name]['losses'] += 1

            # Update standings for Team 2
            group_standings[team2_name]['points'] += p2
            group_standings[team2_name]['goals_for'] += g2
            group_standings[team2_name]['goals_against'] += g1
            if p2 == 3: group_standings[team2_name]['wins'] += 1
            elif p2 == 1: group_standings[team2_name]['draws'] += 1
            else: group_standings[team2_name]['losses'] += 1

        # Calculate goal difference after each matchday for display
        for team_name, stats in group_standings.items():
            stats['goal_difference'] = stats['goals_for'] - stats['goals_against']

        # Yield current standings and match results for the animation (Matchday X Frame)
        yield f"Matchday {i+1}", group_standings, matchday_results_display

    # After all matchdays, determine final ranks for qualification highlighting
    final_sorted_standings_list = []
    for team, stats in group_standings.items():
        final_sorted_standings_list.append((
            team, 
            stats['points'], 
            stats['goal_difference'], 
            stats['goals_for'],
            stats['wins']
        ))
    # Sort standings based on tie-breakers
    final_sorted_standings_list.sort(key=lambda x: (x[1], x[2], x[3], x[4]), reverse=True)
    
    first_place_team = final_sorted_standings_list[0][0]
    second_place_team_info = {
        'name': final_sorted_standings_list[1][0],
        'points': final_sorted_standings_list[1][1],
        'goal_difference': final_sorted_standings_list[1][2],
        'goals_for': final_sorted_standings_list[1][3]
    }
    # Yield final results, including qualifiers for highlighting (Final Frame)
    yield "Final Results", group_standings, first_place_team, second_place_team_info

# --- Original Group Stage Simulation Function (for aggregate results) ---
# This function is used to calculate the overall qualification percentages by running all permutations.
def simulate_group_stage_aggregate(group_teams_raw):
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
        first_place_team, second_place_team_info = simulate_group_stage_aggregate(group_teams_raw)
        
        overall_qualification_results[first_place_team]['direct_qual'] += 1
        second_place_contenders.append(second_place_team_info)

    # Determine the THREE inter-confederation playoff spots
    # Sort contenders by points (desc), then goal difference (desc), then goals for (desc)
    second_place_contenders.sort(key=lambda x: (x['points'], x['goal_difference'], x['goals_for']), reverse=True)
    
    # All three 2nd place teams get a playoff spot.
    for contender_info in second_place_contenders:
        playoff_spot_winner_name = contender_info['name']
        overall_qualification_results[playoff_spot_winner_name]['playoff_spot'] += 1

# --- 6. Calculate and Print Final Percentages ---
print("## World Cup Qualification Likelihood (Simulated Results):\n")
print("--- Simulation Assumptions ---")
print("1.  **Group Stage:** Three groups of four teams, playing home-and-away (6 matches per team).")
print("2.  **Match Outcomes:** Probabilistic, based on FIFA rankings (higher ranking = higher strength). Strength influences win/draw/loss probability and goal scores.")
print("3.  **Points System:** Win = 3 points, Draw = 1 point, Loss = 0 points.")
print("4.  **Group Standings Tie-breakers:** Points, then Goal Difference, then Goals For, then Wins.")
print("5.  **Qualification Rules:**")
print("    * **Direct Qualification:** The 1st place team in each group qualifies automatically (3 spots).")
print("    * **Inter-Confederation Playoff:** The 2nd place team from *each* of the three groups advances to the Inter-Confederation Play-offs (3 spots).")
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

# --- GUI / Video Simulation (New Part) ---

print("\n--- Visualizing a Single World Cup Draw Simulation ---")
print("A random draw configuration will be simulated match by match.")
print("The simulation will run slower to demonstrate the progression.")
print("You can save the animation as a video file (e.g., .mp4, .gif) by running this script locally and uncommenting the save line at the end of the code.")

# Select a random draw configuration for visualization
random_draw_config = random.choice(all_draw_configurations)
visual_groups = {
    "A": [],
    "B": [],
    "C": []
}

# Distribute teams into groups based on the random draw configuration
for i, pot_permutation in enumerate(random_draw_config):
    visual_groups["A"].append(pot_permutation[0]) 
    visual_groups["B"].append(pot_permutation[1])
    visual_groups["C"].append(pot_permutation[2])

# Prepare simulation generators for each group
group_simulations = {}
for group_name, group_teams_raw in visual_groups.items():
    group_simulations[group_name] = simulate_group_stage_for_animation(group_teams_raw)

# Setup matplotlib figure and axes for the GUI
fig, axes = plt.subplots(1, 3, figsize=(20, 10)) # 1 row, 3 columns for 3 groups
fig.suptitle("World Cup Qualification Simulation: Matchday by Matchday", fontsize=18, weight='bold', y=0.98)

tables = {}
match_result_texts = {} # To display results of current matchday
current_frame_number = 0 # To track progress for the status text

# Headers for the table (Shortened for brevity)
table_headers = ["Team", "P", "W", "D", "L", "GF", "GA", "GD"]
col_widths = [0.4, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08] # Proportionate widths

for i, group_name in enumerate(visual_groups.keys()):
    # Get initial standings data from the generator
    try:
        _, initial_standings, _ = next(group_simulations[group_name]) # Get the initial state (discarding status string and empty results)
    except StopIteration:
        print(f"Error: Group {group_name} simulation yielded no initial state for animation.")
        continue
    
    # Prepare table data for initial display
    table_data = []
    for team_name, stats in initial_standings.items():
        table_data.append([
            team_name, stats['points'], stats['wins'], stats['draws'], stats['losses'],
            stats['goals_for'], stats['goals_against'], stats['goal_difference']
        ])
    
    # Sort for initial display (by points, then GD, etc.)
    table_data.sort(key=lambda x: (x[1], x[7], x[5], x[2]), reverse=True)

    axes[i].set_title(f"Group {group_name}", fontsize=14, weight='bold')
    axes[i].axis('off') # Hide axes to display only the table
    
    # Create the table
    table = axes[i].table(cellText=table_data, colLabels=table_headers, loc='center', cellLoc='center', colWidths=col_widths)
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 1.8) # Scale table vertically for better readability

    # Style table cells: header, alternating rows
    for (row, col), cell in table.cells.items():
        cell.set_height(0.1) # Adjust cell height
        if row == 0: # Header row
            cell.set_facecolor("#4CAF50") # Green header
            cell.set_text_props(weight='bold', color='white')
        elif row % 2 == 1: # Odd rows (first data row, third, etc.)
            cell.set_facecolor("#f2f2f2") # Light grey
        else: # Even rows
            cell.set_facecolor("#ffffff") # White
        cell.set_edgecolor("#cccccc") # Light border

    tables[group_name] = table

    # Add text for match results below each group table
    match_result_texts[group_name] = axes[i].text(0.5, -0.15, '', transform=axes[i].transAxes, fontsize=11, 
                                                  ha='center', va='top', wrap=True,
                                                  bbox=dict(boxstyle="round,pad=0.3", fc="#E0F7FA", ec="#00ACC1", lw=1)) # Light blue box


# Overall status text at the top
status_text = fig.text(0.5, 0.92, 'Starting Simulation...', ha='center', va='top', fontsize=16, weight='bold', 
                       bbox=dict(boxstyle="round,pad=0.5", fc="#FFF9C4", ec="#FDD835", lw=1)) # Yellow box

def update(frame):
    global current_frame_number # Use global to modify it
    current_frame_number = frame
    
    current_matchday_status = []
    updated_artists = []

    if frame == 0: # Initial state (already handled, just ensure status text updates)
        status_text.set_text('Simulation Ready: Initial Standings')
        updated_artists.append(status_text)
        # Ensure all tables are marked for update for the first frame
        for group_table in tables.values():
            updated_artists.extend([cell._text for cell in group_table.cells.values()])
            updated_artists.extend(group_table.collections) # Add rectangles for cells and lines
        updated_artists.extend(match_result_texts.values()) # Add match result text objects
        return updated_artists

    # Advance each group's simulation
    for group_name, sim_generator in group_simulations.items():
        try:
            # Get the next state from the generator
            status, standings_data, *extra_info = next(sim_generator)
            
            # Prepare data for the table for the current frame
            table_data = []
            for team_name, stats in standings_data.items():
                table_data.append([
                    team_name, stats['points'], stats['wins'], stats['draws'], stats['losses'],
                    stats['goals_for'], stats['goals_against'], stats['goal_difference']
                ])
            
            # Sort current standings for display
            table_data.sort(key=lambda x: (x[1], x[7], x[5], x[2]), reverse=True)

            # Update table cells with new data
            for row_idx, row_data in enumerate(table_data):
                for col_idx, cell_value in enumerate(row_data):
                    cell = tables[group_name]._cells[(row_idx + 1, col_idx)]
                    cell._text.set_text(str(cell_value))
                    # Reset colors before highlighting, for dynamic changes
                    if row_idx % 2 == 0: cell.set_facecolor("#ffffff")
                    else: cell.set_facecolor("#f2f2f2")
                    cell._text.set_color('black')
                    cell._text.set_weight('normal')
                    updated_artists.append(cell._text) # Mark text for update
                    updated_artists.append(cell) # Mark cell for update (background)


            # Update match results text for the current matchday
            if status.startswith("Matchday") and extra_info and isinstance(extra_info[0], list):
                match_results = "\n".join(extra_info[0])
                match_result_texts[group_name].set_text(f"Match Results for {status}:\n{match_results}")
                updated_artists.append(match_result_texts[group_name])
            elif status == "Final Results": # Final frame
                first_place_team = extra_info[0]
                second_place_team_info = extra_info[1]
                second_place_team = second_place_team_info['name']

                # Highlight 1st and 2nd place teams in the table
                for row_idx, row_data in enumerate(table_data):
                    cell_team_name_text = tables[group_name]._cells[(row_idx + 1, 0)]._text # Team Name cell text
                    cell_team_name_rect = tables[group_name]._cells[(row_idx + 1, 0)] # Team Name cell rectangle
                    if row_data[0] == first_place_team:
                        cell_team_name_rect.set_facecolor('lightgreen')
                        cell_team_name_text.set_color('black')
                        cell_team_name_text.set_weight('bold')
                        updated_artists.append(cell_team_name_text)
                        updated_artists.append(cell_team_name_rect)
                    elif row_data[0] == second_place_team:
                        cell_team_name_rect.set_facecolor('lightblue')
                        cell_team_name_text.set_color('black')
                        cell_team_name_text.set_weight('bold')
                        updated_artists.append(cell_team_name_text)
                        updated_artists.append(cell_team_name_rect)
                
                # Update match results text to show qualifiers
                match_result_texts[group_name].set_text(f"Group {group_name}:\n1st: {first_place_team} (Direct Qual)\n2nd: {second_place_team} (Playoff Spot)")
                updated_artists.append(match_result_texts[group_name])

            else: # For 'Initial Standings' or if no matches played
                match_result_texts[group_name].set_text('')
                updated_artists.append(match_result_texts[group_name])
            
            current_matchday_status.append(f"Group {group_name}: {status}")

        except StopIteration:
            # If a generator is exhausted, it means that group's simulation is complete
            current_matchday_status.append(f"Group {group_name}: Final")
            # Ensure final state (colors, text) remains if already set
            # Re-add all artists from the final state to ensure they are drawn
            for row_idx, row_data in enumerate(table_data): # Use the last known table data
                cell_team_name_text = tables[group_name]._cells[(row_idx + 1, 0)]._text
                cell_team_name_rect = tables[group_name]._cells[(row_idx + 1, 0)]
                updated_artists.append(cell_team_name_text)
                updated_artists.append(cell_team_name_rect)
            updated_artists.append(match_result_texts[group_name])
            
    # Update overall status text
    status_text.set_text(" | ".join(current_matchday_status))
    updated_artists.append(status_text)
    
    return updated_artists # Return all artists that were potentially modified


# Total frames: 1 (initial) + 6 (matchdays) + 1 (final results) = 8 frames
# Interval: 2000 ms (2 seconds) per frame to make it slower
ani = animation.FuncAnimation(fig, update, frames=8, interval=2000, blit=True, repeat=False)

plt.tight_layout(rect=[0, 0.05, 1, 0.95]) # Adjust layout to make space for suptitle and bottom texts
plt.show()

# To save the animation as a video (requires ffmpeg or imagemagick)
# Uncomment the line below and install necessary software if you want to save the video.
# print("\nTo save the animation as a video, you will need to run this script locally.")
# print("Ensure you have 'ffmpeg' installed and accessible in your system's PATH.")
# print("Then, uncomment the following line:")
# # ani.save('world_cup_simulation.mp4', writer='ffmpeg', fps=0.5, dpi=200) 
# print("A lower 'fps' (frames per second) value will make the video playback slower.")
# print("A higher 'dpi' (dots per inch) will result in better video quality.")
