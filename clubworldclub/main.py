import random
import numpy as np
from tqdm import tqdm
from collections import defaultdict
import pandas as pd # For better date formatting in the report

# --- Step 1: Define Teams and their Informed Strength Ratings ---
# These ratings are estimated based on general global club football hierarchy,
# recent continental performance, and perceived squad quality.
# Higher rating indicates a stronger team.
team_strengths = {
    # UEFA (Europe) - 12 teams (Highest tier)
    "Real Madrid": 2.95,       # Consistent UCL winner, top tier
    "Manchester City": 2.90,   # UCL winner, dominant in England
    "Bayern Munich": 2.85,     # German giant, consistent UCL contender
    "Paris Saint-Germain": 2.75, # French dominant, UCL strong contender
    "Inter Milan": 2.65,       # Strong Italian side, UCL finalist
    "Chelsea": 2.50,           # Former UCL winner, currently rebuilding but still strong
    "Atletico Madrid": 2.45,   # Spanish strong, defensively solid
    "Borussia Dortmund": 2.40, # German strong, UCL finalist
    "Juventus": 2.35,          # Italian powerhouse
    "Porto": 2.20,             # Portuguese champion, consistent UCL presence
    "Benfica": 2.15,           # Portuguese champion, consistent UCL presence
    "Red Bull Salzburg": 1.95, # Austrian dominant, good UCL experience

    # CONMEBOL (South America) - 6 teams (Second tier globally)
    "Palmeiras": 2.30,         # Multiple Libertadores winner, very strong
    "Flamengo": 2.25,          # Multiple Libertadores winner, strong
    "Fluminense": 2.10,        # Current Libertadores holder
    "River Plate": 2.05,       # Argentine powerhouse, consistent contender
    "Boca Juniors": 2.00,      # Argentine powerhouse, consistent contender
    "Botafogo": 1.85,          # Qualifies via 2024 Libertadores (hypothetical win)

    # CONCACAF (North/Central America & Caribbean) - 4 Champions + 1 Host = 5 total (Third tier)
    "Monterrey": 1.60,         # Mexican top club, strong CCL performer
    "Pachuca": 1.55,           # Mexican top club, strong CCL performer
    "Seattle Sounders": 1.45,  # MLS champion, good CCL run
    "Club León": 1.40,         # Mexican champion, CCL winner
    "Inter Miami": 1.30,       # Host, strong but lower MLS tier than CCL winners

    # CAF (Africa) - 4 teams (Third tier)
    "Al Ahly": 1.50,           # Egyptian dominant, consistent CAF CL winner
    "Wydad AC": 1.45,          # Moroccan strong, CAF CL winner
    "Esperance de Tunis": 1.35,# Tunisian strong, CAF CL contender
    "Mamelodi Sundowns": 1.30, # South African dominant, CAF CL contender

    # AFC (Asia) - 4 teams (Third tier)
    "Al Hilal": 1.65,          # Saudi giant, Asian CL dominant
    "Urawa Red Diamonds": 1.35,# Japanese side, Asian CL winner
    "Al Ain": 1.25,            # UAE side, Asian CL winner
    "Ulsan HD": 1.20,          # South Korean side, Asian CL winner

    # OFC (Oceania) - 1 team (Lowest tier)
    "Auckland City": 0.80      # Consistent OFC CL winner, significantly weaker
}

# Ensure all 32 teams are present
assert len(team_strengths) == 32, f"Expected 32 teams, but got {len(team_strengths)}"

# --- Step 2: Define Groups (based on FIFA draw results) ---
# Note: Replaced "Club America" with "Club León" in Group D, assuming its placeholder role.
groups = {
    "Group A": ["Palmeiras", "Porto", "Al Ahly", "Inter Miami"],
    "Group B": ["Paris Saint-Germain", "Atletico Madrid", "Botafogo", "Seattle Sounders"],
    "Group C": ["Bayern Munich", "Auckland City", "Boca Juniors", "Benfica"],
    "Group D": ["Chelsea", "Flamengo", "Esperance de Tunis", "Club León"], # Corrected
    "Group E": ["River Plate", "Urawa Red Diamonds", "Monterrey", "Inter Milan"],
    "Group F": ["Fluminense", "Borussia Dortmund", "Ulsan HD", "Mamelodi Sundowns"],
    "Group G": ["Manchester City", "Wydad AC", "Al Ain", "Juventus"],
    "Group H": ["Real Madrid", "Al Hilal", "Pachuca", "Red Bull Salzburg"]
}

# --- Simulation Parameters ---
num_tournaments_simulated = 1000 # Number of times to simulate the entire tournament

# --- Generic Goal Simulation Function (adapted for strength rating) ---
def simulate_goals(attacking_strength, defending_strength):
    """
    Simulates goals scored by a team in a match using a Poisson distribution.
    The expected goals (lambda) are derived from the attacking team's strength
    and the opponent's strength.

    Adjusted lambda:
    - Base rate: 1.0 (average goals in a match)
    - Attacking contribution: attacking_strength * 0.5 (stronger attack = more goals)
    - Defensive opposition contribution: (4.0 - defending_strength) * 0.25
      (weaker defense = more goals conceded by them)
    - Ensure lambda is never too low (e.g., min 0.1 for very weak vs strong)
    """
    lambda_val = max(0.1, 0.5 + (attacking_strength * 0.5) + ((4.0 - defending_strength) * 0.15))
    return np.random.poisson(lambda_val)

# --- Tournament Simulation Logic ---

def run_single_cwc_simulation(teams_data, tournament_groups):
    group_standings = defaultdict(lambda: {})

    # Initialize group standings for each team
    for group_name, teams_in_group in tournament_groups.items():
        for team_name in teams_in_group:
            group_standings[group_name][team_name] = {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0}

    # --- Group Stage Simulation ---
    for group_name, teams_in_group in tournament_groups.items():
        for i in range(len(teams_in_group)):
            for j in range(i + 1, len(teams_in_group)):
                team1 = teams_in_group[i]
                team2 = teams_in_group[j]

                team1_strength = teams_data[team1]
                team2_strength = teams_data[team2]

                team1_goals = simulate_goals(team1_strength, team2_strength)
                team2_goals = simulate_goals(team2_strength, team1_strength)

                # Update stats for team1
                group_standings[group_name][team1]['P'] += 1
                group_standings[group_name][team1]['GF'] += team1_goals
                group_standings[group_name][team1]['GA'] += team2_goals

                # Update stats for team2
                group_standings[group_name][team2]['P'] += 1
                group_standings[group_name][team2]['GF'] += team2_goals
                group_standings[group_name][team2]['GA'] += team1_goals

                if team1_goals > team2_goals:
                    group_standings[group_name][team1]['W'] += 1
                    group_standings[group_name][team1]['Pts'] += 3
                    group_standings[group_name][team2]['L'] += 1
                elif team2_goals > team1_goals:
                    group_standings[group_name][team2]['W'] += 1
                    group_standings[group_name][team2]['Pts'] += 3
                    group_standings[group_name][team1]['L'] += 1
                else:
                    group_standings[group_name][team1]['D'] += 1
                    group_standings[group_name][team2]['D'] += 1
                    group_standings[group_name][team1]['Pts'] += 1
                    group_standings[group_name][team2]['Pts'] += 1
        
        # Calculate GD after all games in the group for final sorting
        for team_name in teams_in_group:
            group_standings[group_name][team_name]['GD'] = \
                group_standings[group_name][team_name]['GF'] - group_standings[group_name][team_name]['GA']


    # --- Determine Group Qualifiers ---
    all_group_qualifiers = []
    for group_name in sorted(tournament_groups.keys()):
        teams_for_sorting = []
        for team_name in tournament_groups[group_name]:
            teams_for_sorting.append((team_name, group_standings[group_name][team_name]))
        
        # Sort teams by Pts, then GD, then GF
        sorted_teams = sorted(
            teams_for_sorting,
            key=lambda item: (item[1]['Pts'], item[1]['GD'], item[1]['GF']),
            reverse=True
        )
        
        all_group_qualifiers.append(sorted_teams[0][0]) # Group Winner
        all_group_qualifiers.append(sorted_teams[1][0]) # Group Runner-up

    # --- Knockout Stage Simulation ---
    # Extract winners and runners-up in order (W_A, R_A, W_B, R_B, ...)
    W = {chr(ord('A') + i): all_group_qualifiers[i*2] for i in range(8)}
    R = {chr(ord('A') + i): all_group_qualifiers[i*2 + 1] for i in range(8)}

    round_of_16_pairings = [
        (W['A'], R['B']), (W['C'], R['D']), (W['E'], R['F']), (W['G'], R['H']),
        (W['B'], R['A']), (W['D'], R['C']), (W['F'], R['E']), (W['H'], R['G'])
    ]
    
    # Generic knockout match simulation
    def play_knockout_match(teamA, teamB, teams_data):
        teamA_strength = teams_data[teamA]
        teamB_strength = teams_data[teamB]

        teamA_goals = simulate_goals(teamA_strength, teamB_strength)
        teamB_goals = simulate_goals(teamB_strength, teamA_strength)

        if teamA_goals > teamB_goals:
            return teamA
        elif teamB_goals > team1_goals:
            return teamB
        else:
            # Draw in knockout -> simulate extra time/penalties
            # For simplicity: higher strength has a slight edge, otherwise random
            if teamA_strength > teamB_strength:
                return teamA if random.random() < 0.6 else teamB
            elif teamB_strength > teamA_strength:
                return teamB if random.random() < 0.6 else teamA
            else:
                return random.choice([teamA, teamB])

    # Round of 16
    r16_winners = []
    for team1, team2 in round_of_16_pairings:
        winner = play_knockout_match(team1, team2, teams_data)
        r16_winners.append(winner)
    
    # Quarter-finals pairings based on bracket
    quarter_final_pairings = [
        (r16_winners[0], r16_winners[1]), (r16_winners[2], r16_winners[3]),
        (r16_winners[4], r16_winners[5]), (r16_winners[6], r16_winners[7])
    ]
    
    quarter_final_winners = []
    for team1, team2 in quarter_final_pairings:
        winner = play_knockout_match(team1, team2, teams_data)
        quarter_final_winners.append(winner)
    
    # Semi-finals pairings
    semi_final_pairings = [
        (quarter_final_winners[0], quarter_final_winners[1]),
        (quarter_final_winners[2], quarter_final_winners[3])
    ]

    semi_final_winners = []
    for team1, team2 in semi_final_pairings:
        winner = play_knockout_match(team1, team2, teams_data)
        semi_final_winners.append(winner)

    # Final
    final_winner = play_knockout_match(semi_final_winners[0], semi_final_winners[1], teams_data)
    
    return final_winner

# --- Run Multiple Tournament Simulations ---
tournament_winners_counts = defaultdict(int)

print(f"Simulating {num_tournaments_simulated} FIFA Club World Cup 2025 tournaments...\n")

for i in tqdm(range(num_tournaments_simulated), desc="Running Tournaments"):
    winner = run_single_cwc_simulation(team_strengths, groups)
    tournament_winners_counts[winner] += 1

# --- Display Results ---
print("\n" + "="*80)
print("=== FIFA CLUB WORLD CUP 2025 SIMULATION RESULTS ===")
print("="*80 + "\n")

print(f"Total tournaments simulated: {num_tournaments_simulated}\n")
print("--- Predicted Tournament Winners (by percentage) ---\n")

sorted_winners = sorted(tournament_winners_counts.items(), key=lambda item: item[1], reverse=True)

for team, count in sorted_winners:
    percentage = (count / num_tournaments_simulated) * 100
    print(f"{team}: {count} wins ({percentage:.2f}%)")

print("\n" + "="*80)
print("=== FIFA CLUB WORLD CUP 2025 SIMULATION REPORT (INFORMED STRENGTHS) ===")
print("="*80)
print(f"Date of Report: {pd.Timestamp.now().strftime('%A, %B %d, %Y')}\n")

print(f"This report presents the outcomes of {num_tournaments_simulated} simulated FIFA Club World Cup 2025 tournaments, utilizing **informed 'strength ratings'** for each participating team.\n")

print("**Simulation Methodology Highlights:**")
print("- Each team is assigned an 'strength rating' based on general football hierarchy, recent continental performance, and perceived squad quality. These are not direct raw stats but informed estimates of overall team quality.")
print("- Goal outcomes for individual matches are generated using a Poisson distribution, where the expected goals are influenced by the attacking team's strength and the opponent's defensive strength.")
print("- The tournament follows the official FIFA Club World Cup 2025 format: a group stage followed by knockout rounds (Round of 16, Quarter-Finals, Semi-Finals, Final).")
print("- In knockout matches, draws are resolved by a simplified extra-time/penalty shootout simulation, favoring the stronger team slightly or by coin-flip if strengths are equal.\n")

print("**Key Findings:**\n")

if sorted_winners:
    top_contender = sorted_winners[0][0]
    top_contender_chance = sorted_winners[0][1] / num_tournaments_simulated * 100
    print(f"**Most Likely Winner:**")
    print(f"  - Our simulations predict **{top_contender}** as the most likely champion, winning approximately **{top_contender_chance:.2f}%** of the simulated tournaments.")

    if len(sorted_winners) > 1:
        second_contender = sorted_winners[1][0]
        second_contender_chance = sorted_winners[1][1] / num_tournaments_simulated * 100
        print(f"**Other Strong Contenders:**")
        print(f"  - Teams like **{second_contender}** also show significant chances of lifting the trophy, indicating a competitive field among the top clubs.")

    print("\n**Regional Dominance:**")
    uefa_teams = ["Real Madrid", "Manchester City", "Bayern Munich", "Paris Saint-Germain", "Inter Milan", "Chelsea", "Atletico Madrid", "Borussia Dortmund", "Juventus", "Porto", "Benfica", "Red Bull Salzburg"]
    conmebol_teams = ["Palmeiras", "Flamengo", "Fluminense", "River Plate", "Boca Juniors", "Botafogo"]
    
    uefa_wins = sum(tournament_winners_counts[team] for team in uefa_teams if team in tournament_winners_counts)
    conmebol_wins = sum(tournament_winners_counts[team] for team in conmebol_teams if team in tournament_winners_counts)
    
    # Calculate wins for other confederations
    other_confed_wins = num_tournaments_simulated - uefa_wins - conmebol_wins

    print(f"  - European clubs (UEFA) secured victory in approximately {uefa_wins / num_tournaments_simulated * 100:.2f}% of simulations.")
    print(f"  - South American clubs (CONMEBOL) won around {conmebol_wins / num_tournaments_simulated * 100:.2f}% of the time.")
    print(f"  - Clubs from other confederations collectively won {other_confed_wins / num_tournaments_simulated * 100:.2f}% of tournaments, which, while smaller, showcases the competitive nature of the tournament beyond the traditional two dominant continents.")
else:
    print("No winners recorded in simulations (this should not happen with proper setup).")

print("\n**Limitations & Disclaimer:**")
print("This simulation uses **informed strength ratings** to estimate team capabilities, as direct, universally comparable 'real stats' (like raw GF/GA across different leagues) are not suitable for inter-continental comparisons. While these ratings are more realistic than arbitrary numbers, they remain *estimates* based on general football knowledge and recent form.")
print("The model does not account for dynamic factors such as specific player injuries leading up to the tournament, current team form fluctuations, tactical nuances, individual player brilliance, or the psychological pressures of specific matches. Therefore, this simulation serves as a probabilistic forecast based on a defined set of team strengths, not a definitive prediction.")
print("Enjoy the spectacle of the FIFA Club World Cup 2025!")
print("="*80)