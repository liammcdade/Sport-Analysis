
import random
from collections import defaultdict
from tqdm import tqdm
import math

# --- Data Setup ---

# Updated team strengths based on CONCACAF Ranking Index (May 2025 data from Concacaf.com)
# Using these rankings for seeding in the 3rd Round draw as well, as they are specific to CONCACAF
team_strengths = {
    'Mexico': 1946,
    'Canada': 1837,
    'Panama': 1778,
    'USA': 1712, # Note: USA is ranked 4th in CONCACAF by CONCACAF's own index, despite being host. Still a host.
    'Costa Rica': 1668,
    'Jamaica': 1552,
    'Honduras': 1534,
    'Haiti': 1481,
    'Guatemala': 1377,
    'Trinidad and Tobago': 1360,
    'El Salvador': 1243,
    'Suriname': 1223,
    'Guadeloupe': 1222, # Not part of WC Qualifiers generally
    'Martinique': 1202, # Not part of WC Qualifiers generally
    'Curaçao': 1130,
    'Nicaragua': 1115,
    'Guyana': 1069,
    'Cuba': 1057,
    'Dominican Republic': 1050,
    'French Guiana': 950, # Not part of WC Qualifiers generally
    'Saint Vincent and the Grenadines': 892,
    'Bermuda': 864,
    'Puerto Rico': 846,
    'Saint Kitts and Nevis': 833,
    'Belize': 781,
    'Saint Lucia': 774,
    'Grenada': 739,
    'Montserrat': 690,
    'Dominica': 622,
    'Sint Maarten': 603, # Not part of WC Qualifiers generally
    'Barbados': 591,
    'Saint Martin': 584, # Not part of WC Qualifiers generally
    'Antigua and Barbuda': 581,
    'Bonaire': 554, # Not part of WC Qualifiers generally
    'Aruba': 520,
    'Cayman Islands': 456,
    'Bahamas': 427,
    'Turks and Caicos Islands': 272, # Not part of WC Qualifiers generally
    'British Virgin Islands': 150,
    'Anguilla': 149,
    'US Virgin Islands': 110 # Not part of WC Qualifiers generally
}

# Current Second Round Standings (as of June 9, 2025 - prior to June 10 matches)
# Updated to reflect recent match results (June 7/8) and current state
second_round_standings = {
    'Group A': {
        'Honduras': {'points': 9, 'gd': 8, 'gs': 10, 'matches_played': 3},
        'Cuba': {'points': 6, 'gd': 2, 'gs': 5, 'matches_played': 3},
        'Bermuda': {'points': 4, 'gd': 0, 'gs': 7, 'matches_played': 3},
        'Antigua and Barbuda': {'points': 1, 'gd': -2, 'gs': 1, 'matches_played': 3},
        'Cayman Islands': {'points': 3, 'gd': -8, 'gs': 1, 'matches_played': 4}, # Played all matches
    },
    'Group B': {
        'Costa Rica': {'points': 9, 'gd': 15, 'gs': 15, 'matches_played': 3},
        'Trinidad and Tobago': {'points': 7, 'gd': 10, 'gs': 15, 'matches_played': 3},
        'Grenada': {'points': 4, 'gd': 3, 'gs': 8, 'matches_played': 3},
        'Saint Kitts and Nevis': {'points': 3, 'gd': -7, 'gs': 3, 'matches_played': 3},
        'Bahamas': {'points': 0, 'gd': -21, 'gs': 1, 'matches_played': 4}, # Played all matches
    },
    'Group C': {
        'Curaçao': {'points': 9, 'gd': 9, 'gs': 10, 'matches_played': 3},
        'Haiti': {'points': 9, 'gd': 8, 'gs': 10, 'matches_played': 3},
        'Aruba': {'points': 2, 'gd': -7, 'gs': 3, 'matches_played': 4}, # Played all matches
        'Barbados': {'points': 1, 'gd': -5, 'gs': 3, 'matches_played': 3},
        'Saint Lucia': {'points': 1, 'gd': -5, 'gs': 3, 'matches_played': 3},
    },
    'Group D': {
        'Nicaragua': {'points': 9, 'gd': 6, 'gs': 7, 'matches_played': 3},
        'Panama': {'points': 9, 'gd': 6, 'gs': 6, 'matches_played': 3},
        'Guyana': {'points': 3, 'gd': 0, 'gs': 3, 'matches_played': 3},
        'Montserrat': {'points': 0, 'gd': -7, 'gs': 1, 'matches_played': 3},
        'Belize': {'points': 0, 'gd': -8, 'gs': 0, 'matches_played': 3},
    },
    'Group E': {
        'Guatemala': {'points': 9, 'gd': 11, 'gs': 13, 'matches_played': 3},
        'Jamaica': {'points': 9, 'gd': 4, 'gs': 4, 'matches_played': 3},
        'Dominican Republic': {'points': 3, 'gd': 3, 'gs': 7, 'matches_played': 3},
        'Dominica': {'points': 0, 'gd': -10, 'gs': 0, 'matches_played': 3},
        'British Virgin Islands': {'points': 0, 'gd': -7, 'gs': 0, 'matches_played': 3},
    },
    'Group F': {
        'Suriname': {'points': 9, 'gd': 9, 'gs': 10, 'matches_played': 3},
        'Puerto Rico': {'points': 4, 'gd': 7, 'gs': 8, 'matches_played': 3},
        'El Salvador': {'points': 4, 'gd': 2, 'gs': 3, 'matches_played': 3},
        'Saint Vincent and the Grenadines': {'points': 0, 'gd': -9, 'gs': 1, 'matches_played': 3},
        'Anguilla': {'points': 0, 'gd': -15, 'gs': 0, 'matches_played': 3},
    }
}

# Remaining Second Round Fixtures (June 10, 2025)
second_round_fixtures = [
    ('Cuba', 'Bermuda'),
    ('Honduras', 'Antigua and Barbuda'),
    ('Saint Kitts and Nevis', 'Grenada'),
    ('Costa Rica', 'Trinidad and Tobago'),
    ('Saint Lucia', 'Barbados'),
    ('Haiti', 'Curaçao'),
    ('Guyana', 'Montserrat'),
    ('Panama', 'Nicaragua'),
    ('Dominican Republic', 'Dominica'),
    ('Jamaica', 'Guatemala'),
    ('Puerto Rico', 'Saint Vincent and the Grenadines'),
    ('El Salvador', 'Suriname')
]

# Host nations who automatically qualify
HOST_NATIONS = ['Canada', 'Mexico', 'USA']

# --- Helper Functions ---

def predict_match_outcome(home_team, away_team):
    home_rank_points = team_strengths.get(home_team, 1000)
    away_rank_points = team_strengths.get(away_team, 1000)

    strength_diff = home_rank_points - away_rank_points

    # Probabilities adjusted for home advantage and strength difference
    # Using a logistic-like function for probability mapping based on Elo difference
    # 400 Elo point difference ~ 3x odds
    prob_home_win = 1 / (1 + 10**((away_rank_points - home_rank_points + 50) / 400)) # Add 50 for home advantage
    prob_draw = 0.25 # Base draw probability, can be adjusted
    prob_away_win = 1 - prob_home_win - prob_draw

    # Ensure probabilities are positive and sum to 1, adjust draw if needed
    if prob_away_win < 0:
        prob_draw += prob_away_win # Reduce draw prob
        prob_away_win = 0
    if prob_home_win < 0:
        prob_draw += prob_home_win # Reduce draw prob
        prob_home_win = 0

    # Renormalize if sum is not 1 (due to clipping or initial approximation)
    total_prob = prob_home_win + prob_draw + prob_away_win
    if total_prob <= 0: # Fallback for extreme cases
        prob_home_win, prob_draw, prob_away_win = 1/3, 1/3, 1/3
    else:
        prob_home_win /= total_prob
        prob_draw /= total_prob
        prob_away_win /= total_prob

    outcome = random.choices(['home_win', 'draw', 'away_win'],
                             weights=[prob_home_win, prob_draw, prob_away_win], k=1)[0]

    home_goals, away_goals = 0, 0

    # More nuanced goal prediction based on strength and outcome
    if outcome == 'home_win':
        home_goals = random.randint(1, 3) + max(0, round(strength_diff / 300))
        away_goals = random.randint(0, max(0, home_goals - 1))
        home_goals = max(1, home_goals)
        away_goals = max(0, away_goals)
        if home_goals <= away_goals: home_goals = away_goals + random.choice([1, 2])
    elif outcome == 'away_win':
        away_goals = random.randint(1, 3) + max(0, round(-strength_diff / 300))
        home_goals = random.randint(0, max(0, away_goals - 1))
        away_goals = max(1, away_goals)
        home_goals = max(0, home_goals)
        if away_goals <= home_goals: away_goals = home_goals + random.choice([1, 2])
    else:  # Draw
        max_goals = random.randint(0, 2) + round((home_rank_points + away_rank_points) / 3000)
        home_goals = max(0, max_goals)
        away_goals = max(0, max_goals)
        if home_goals != away_goals: # Ensure it's a draw
            home_goals = away_goals = max(home_goals, away_goals)
            if home_goals == 0: # Avoid too many 0-0 draws, ensure some variety
                home_goals = away_goals = random.randint(1,2)

    return home_goals, away_goals

def calculate_group_standings(group_data):
    sorted_teams = sorted(group_data.items(),
                          key=lambda item: (item[1]['points'], item[1]['gd'], item[1]['gs'], team_strengths.get(item[0], 0)),
                          reverse=True)
    return sorted_teams

def generate_third_round_fixtures(teams_in_group):
    fixtures = []
    for i in range(len(teams_in_group)):
        for j in range(i + 1, len(teams_in_group)):
            team1 = teams_in_group[i]
            team2 = teams_in_group[j]
            # Home and away matches
            fixtures.append((team1, team2))
            fixtures.append((team2, team1))
    return fixtures

def get_team_rank_points(team_name):
    return team_strengths.get(team_name, 0) # Use 0 for unranked teams, they'd be lowest

def simulate_concacaf_qualifiers_full(initial_second_round_standings, second_round_fixtures_list, num_simulations=10000):
    direct_qual_counts = defaultdict(int)
    playoff_qual_counts = defaultdict(int)
    total_qual_counts = defaultdict(int)

    # Host nations are always qualified
    for host in HOST_NATIONS:
        direct_qual_counts[host] = num_simulations
        total_qual_counts[host] = num_simulations

    for _ in tqdm(range(num_simulations), desc="Simulating CONCACAF Qualifiers"):
        # --- Simulate Second Round ---
        simulated_second_round_standings = {group: {team: data.copy() for team, data in group_data.items()}
                                            for group, group_data in initial_second_round_standings.items()}

        for home_team, away_team in second_round_fixtures_list:
            # Find the group for the match
            group_name = None
            for g_name, teams_in_group in simulated_second_round_standings.items():
                if home_team in teams_in_group and away_team in teams_in_group:
                    group_name = g_name
                    break
            if not group_name:
                continue # Should not happen with correct data

            home_goals, away_goals = predict_match_outcome(home_team, away_team)

            # Update standings
            if home_goals > away_goals:
                simulated_second_round_standings[group_name][home_team]['points'] += 3
            elif home_goals < away_goals:
                simulated_second_round_standings[group_name][away_team]['points'] += 3
            else:
                simulated_second_round_standings[group_name][home_team]['points'] += 1
                simulated_second_round_standings[group_name][away_team]['points'] += 1

            simulated_second_round_standings[group_name][home_team]['gd'] += (home_goals - away_goals)
            simulated_second_round_standings[group_name][away_team]['gd'] += (away_goals - home_goals)
            simulated_second_round_standings[group_name][home_team]['gs'] += home_goals
            simulated_second_round_standings[group_name][away_team]['gs'] += away_goals
            simulated_second_round_standings[group_name][home_team]['matches_played'] += 1
            simulated_second_round_standings[group_name][away_team]['matches_played'] += 1

        # Determine the 12 teams for the Third Round
        third_round_qualifiers_list = []
        for group_name, data in simulated_second_round_standings.items():
            final_group_order = calculate_group_standings(data)
            # Take top 2 from each group if available and they haven't played all matches (some eliminated teams did)
            # Ensure only teams with matches_played == 4 (finished their round) are considered, or those confirmed to advance
            valid_qualifiers_in_group = [team_info[0] for team_info in final_group_order if team_info[1]['matches_played'] == 4]

            if len(valid_qualifiers_in_group) >= 2:
                third_round_qualifiers_list.append(valid_qualifiers_in_group[0]) # Group winner
                third_round_qualifiers_list.append(valid_qualifiers_in_group[1]) # Group runner-up

        # This check is crucial: ensure exactly 12 teams before proceeding to 3rd round draw
        if len(third_round_qualifiers_list) != 12:
            # This handles edge cases where the simulation logic for advancing teams might not perfectly match
            # the exact 2-per-group outcome if a group is very tight with goal difference and strength.
            # In a real scenario, this would ideally mean all teams advance.
            # For robust simulation, if it's less than 12, it indicates a flaw in advancing logic or data.
            # For now, let's just skip this simulation run if it doesn't result in 12 qualifiers.
            continue


        # --- Third Round Draw ---
        # Sort qualifiers by FIFA ranking for seeding
        third_round_qualifiers_list.sort(key=get_team_rank_points, reverse=True)

        # Create pots based on rankings
        pot1 = third_round_qualifiers_list[0:3]
        pot2 = third_round_qualifiers_list[3:6]
        pot3 = third_round_qualifiers_list[6:9]
        pot4 = third_round_qualifiers_list[9:12]

        # Shuffle pots
        random.shuffle(pot1)
        random.shuffle(pot2)
        random.shuffle(pot3)
        random.shuffle(pot4)

        # Draw into groups (A, B, C)
        third_round_groups = {
            'Group A': [pot1[0], pot2[0], pot3[0], pot4[0]],
            'Group B': [pot1[1], pot2[1], pot3[1], pot4[1]],
            'Group C': [pot1[2], pot2[2], pot3[2], pot4[2]]
        }

        # --- Simulate Third Round ---
        simulated_third_round_results = {}
        for group_name, teams_in_group in third_round_groups.items():
            initial_group_standings = {team: {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0}
                                       for team in teams_in_group}
            group_fixtures = generate_third_round_fixtures(teams_in_group)

            current_sim_standings = {team: data.copy() for team, data in initial_group_standings.items()}

            for home_team, away_team in group_fixtures:
                home_goals, away_goals = predict_match_outcome(home_team, away_team)

                if home_goals > away_goals:
                    current_sim_standings[home_team]['points'] += 3
                elif home_goals < away_goals:
                    current_sim_standings[away_team]['points'] += 3
                else:
                    current_sim_standings[home_team]['points'] += 1
                    current_sim_standings[away_team]['points'] += 1

                current_sim_standings[home_team]['gd'] += (home_goals - away_goals)
                current_sim_standings[away_team]['gd'] += (away_goals - home_goals)
                current_sim_standings[home_team]['gs'] += home_goals
                current_sim_standings[away_team]['gs'] += away_goals
                current_sim_standings[home_team]['matches_played'] += 1
                current_sim_standings[away_team]['matches_played'] += 1

            simulated_third_round_results[group_name] = current_sim_standings

        # Determine direct qualifiers and playoff contenders from Third Round
        group_winners = []
        group_runners_up_info = [] # Store full data for tie-breaking

        for group_name, data in simulated_third_round_results.items():
            final_group_order = calculate_group_standings(data)
            if final_group_order:
                group_winners.append(final_group_order[0][0])
                if len(final_group_order) > 1:
                    runner_up_data = final_group_order[1][1]
                    runner_up_data['team'] = final_group_order[1][0]
                    group_runners_up_info.append(runner_up_data)

        # 3 Group Winners qualify directly
        for winner in group_winners:
            direct_qual_counts[winner] += 1
            total_qual_counts[winner] += 1

        # 2 Best Runners-Up go to Inter-Confederation Playoff
        # Sort runners-up by points, then GD, then GS, then strength
        sorted_runners_up = sorted(group_runners_up_info,
                                   key=lambda x: (x['points'], x['gd'], x['gs'], get_team_rank_points(x['team'])),
                                   reverse=True)

        for i in range(min(2, len(sorted_runners_up))):
            playoff_qual_counts[sorted_runners_up[i]['team']] += 1
            total_qual_counts[sorted_runners_up[i]['team']] += 1

    print(f"\n--- CONCACAF World Cup 2026 Qualification Simulation Results ({num_simulations} runs) ---")
    print(f"**Note:** This simulation uses real Second Round standings and simulates remaining matches.")
    print(f"Third Round groups are drawn randomly based on CONCACAF May 2025 rankings for seeding.")
    print(f"Automatic Qualifiers (Hosts): {', '.join(HOST_NATIONS)}")

    print("\nOverall Probability of Qualification (Direct, Playoff, or Host):")
    # Combine all teams that appeared in direct, playoff, or are hosts
    all_teams_in_results = set(total_qual_counts.keys()).union(set(HOST_NATIONS))

    final_overall_chances = {}
    for team in all_teams_in_results:
        final_overall_chances[team] = total_qual_counts[team] / num_simulations

    sorted_overall = sorted(final_overall_chances.items(), key=lambda item: (-item[1], item[0]))

    for team, chance in sorted_overall:
        print(f"{team}: {chance:.2%}")

if __name__ == "__main__":
    simulate_concacaf_qualifiers_full(second_round_standings, second_round_fixtures, num_simulations=10000)
