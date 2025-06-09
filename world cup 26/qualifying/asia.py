import random
from collections import defaultdict
from tqdm import tqdm
import math

# --- Data Setup ---

# FIFA Ranking points for AFC teams (approximate based on June 5, 2025 data where available, otherwise April 2025)
# Using more precise values from a reliable source if available for simulation accuracy.
# Adjusted based on latest FIFA ranking provided in search results for June 5, 2025 where possible.
team_strengths = {
    'Japan': 1652.64,        # Rank 15
    'Iran': 1637.39,         # Rank 18
    'South Korea': 1575.0,   # Rank 23 (approx, from search result)
    'Australia': 1488.89,    # Rank 23 (approx, from search result for 3rd round group C)
    'Qatar': 1445.01,        # Rank 35 (approx, from search result for 3rd round group A)
    'Saudi Arabia': 1418.96, # Rank 58
    'Iraq': 1413.40,         # Rank 59
    'Uzbekistan': 1437.02,   # Rank 57
    'Jordan': 1389.15,       # Rank 62
    'United Arab Emirates': 1382.70, # Rank 65
    'Oman': 1332.96,         # Rank 76 (approx, from search result for 3rd round groups)
    'Bahrain': 1290.00,      # Rank 84
    'China PR': 1250.95,     # Rank 94
    'Palestine': 1224.65,    # Rank 101
    'Kyrgyzstan': 1205.68,   # Rank 103
    'North Korea': 1153.38,  # Rank 118
    'Indonesia': 1142.92,    # Rank 123
    'Kuwait': 1109.91,       # Approx from context, not in provided list for June 5th
}

# Teams already qualified directly (as of June 5, 2025 results)
# These teams will have 100% direct qualification probability in the final output.
ALREADY_QUALIFIED_DIRECTLY = ['Iran', 'Uzbekistan', 'South Korea', 'Jordan', 'Japan', 'Australia']

# Third Round Groups and Matchday 10 fixtures (June 10, 2025)
third_round_groups = {
    'Group A': {
        'teams': ['Iran', 'Uzbekistan', 'United Arab Emirates', 'Qatar', 'Kyrgyzstan', 'North Korea'],
        'standings': { # Points, GD, GF from June 5, 2025 (after MD9)
            'Iran': {'points': 20, 'gd': 8, 'gs': 16, 'matches_played': 9},
            'Uzbekistan': {'points': 18, 'gd': 4, 'gs': 11, 'matches_played': 9},
            'United Arab Emirates': {'points': 14, 'gd': 7, 'gs': 14, 'matches_played': 9},
            'Qatar': {'points': 13, 'gd': -4, 'gs': 17, 'matches_played': 9},
            'Kyrgyzstan': {'points': 7, 'gd': -6, 'gs': 11, 'matches_played': 9},
            'North Korea': {'points': 3, 'gd': -9, 'gs': 9, 'matches_played': 9},
        },
        'fixtures_md10': [
            ('Uzbekistan', 'Qatar'),
            ('Kyrgyzstan', 'United Arab Emirates'),
            ('Iran', 'North Korea'),
        ]
    },
    'Group B': {
        'teams': ['South Korea', 'Jordan', 'Iraq', 'Oman', 'Palestine', 'Kuwait'],
        'standings': { # Points, GD, GF from June 5, 2025 (after MD9)
            'South Korea': {'points': 16, 'gd': 7, 'gs': 18, 'matches_played': 9},
            'Jordan': {'points': 13, 'gd': 6, 'gs': 14, 'matches_played': 9},
            'Iraq': {'points': 12, 'gd': 1, 'gs': 13, 'matches_played': 9},
            'Oman': {'points': 10, 'gd': -2, 'gs': 10, 'matches_played': 9},
            'Palestine': {'points': 6, 'gd': -5, 'gs': 8, 'matches_played': 9},
            'Kuwait': {'points': 5, 'gd': -7, 'gs': 5, 'matches_played': 9},
        },
        'fixtures_md10': [
            ('South Korea', 'Kuwait'),
            ('Jordan', 'Iraq'),
            ('Palestine', 'Oman'),
        ]
    },
    'Group C': {
        'teams': ['Japan', 'Australia', 'Saudi Arabia', 'Indonesia', 'Bahrain', 'China PR'],
        'standings': { # Points, GD, GF from June 5, 2025 (after MD9)
            'Japan': {'points': 20, 'gd': 22, 'gs': 27, 'matches_played': 9},
            'Australia': {'points': 13, 'gd': 7, 'gs': 15, 'matches_played': 9},
            'Saudi Arabia': {'points': 10, 'gd': -2, 'gs': 10, 'matches_played': 9},
            'Indonesia': {'points': 9, 'gd': -6, 'gs': 9, 'matches_played': 9},
            'Bahrain': {'points': 6, 'gd': -8, 'gs': 6, 'matches_played': 9},
            'China PR': {'points': 6, 'gd': -13, 'gs': 5, 'matches_played': 9},
        },
        'fixtures_md10': [
            ('Japan', 'Indonesia'),
            ('China PR', 'Bahrain'),
            ('Saudi Arabia', 'Australia'),
        ]
    }
}

# --- Helper Functions ---

def get_team_rank_points(team_name):
    return team_strengths.get(team_name, 1000) # Default if team not found

def predict_match_outcome(home_team, away_team, is_knockout=False):
    home_rank_points = get_team_rank_points(home_team)
    away_rank_points = get_team_rank_points(away_team)

    # Elo-like probability calculation
    prob_home_win = 1 / (1 + 10**((away_rank_points - home_rank_points + 60) / 400)) # Home advantage of ~60 points
    prob_draw = 0.22 # AFC often has draws, slightly higher than OFC
    prob_away_win = 1 - prob_home_win - prob_draw

    # Ensure probabilities are valid and sum to 1
    if prob_away_win < 0: prob_draw += prob_away_win; prob_away_win = 0
    if prob_home_win < 0: prob_draw += prob_home_win; prob_home_win = 0
    total_prob = prob_home_win + prob_draw + prob_away_win
    if total_prob <= 0: prob_home_win, prob_draw, prob_away_win = 1/3, 1/3, 1/3
    else: prob_home_win /= total_prob; prob_draw /= total_prob; prob_away_win /= total_prob

    outcome = random.choices(['home_win', 'draw', 'away_win'],
                             weights=[prob_home_win, prob_draw, prob_away_win], k=1)[0]

    home_goals, away_goals = 0, 0
    strength_diff = home_rank_points - away_rank_points

    # Simplified goal prediction with some randomness
    if outcome == 'home_win':
        home_goals = random.randint(1, 3) + max(0, round(strength_diff / 300))
        away_goals = random.randint(0, home_goals - 1)
        home_goals = max(1, home_goals) # At least 1 goal for winner
        away_goals = max(0, away_goals)
    elif outcome == 'away_win':
        away_goals = random.randint(1, 3) + max(0, round(-strength_diff / 300))
        home_goals = random.randint(0, away_goals - 1)
        away_goals = max(1, away_goals)
        home_goals = max(0, home_goals)
    else: # Draw
        goals = random.randint(0, 2) + round((home_rank_points + away_rank_points) / 3000)
        home_goals = max(0, goals)
        away_goals = max(0, goals)
        if home_goals != away_goals: home_goals = away_goals = max(home_goals, away_goals)
        if home_goals == 0: home_goals = away_goals = random.randint(1,2) # Avoid too many 0-0

    # For knockout matches, force a winner
    if is_knockout and home_goals == away_goals:
        # Simulate extra time and penalties based on higher rank
        if home_rank_points > away_rank_points:
            home_goals += 1
        else:
            away_goals += 1

    return home_goals, away_goals

def calculate_group_standings(group_data):
    # Sort by points, then goal difference, then goals scored, then FIFA ranking
    sorted_teams = sorted(group_data.items(),
                          key=lambda item: (item[1]['points'], item[1]['gd'], item[1]['gs'], get_team_rank_points(item[0])),
                          reverse=True)
    return sorted_teams

def simulate_group_matches(group_info, current_standings):
    # Create a copy of current standings for this simulation run
    sim_standings = {team: data.copy() for team, data in current_standings.items()}

    for home_team, away_team in group_info['fixtures_md10']:
        home_goals, away_goals = predict_match_outcome(home_team, away_team, is_knockout=False)

        # Update standings
        if home_goals > away_goals:
            sim_standings[home_team]['points'] += 3
        elif home_goals < away_goals:
            sim_standings[away_team]['points'] += 3
        else:
            sim_standings[home_team]['points'] += 1
            sim_standings[away_team]['points'] += 1

        sim_standings[home_team]['gd'] += (home_goals - away_goals)
        sim_standings[away_team]['gd'] += (away_goals - home_goals)
        sim_standings[home_team]['gs'] += home_goals
        sim_standings[away_team]['gs'] += away_goals
        sim_standings[home_team]['matches_played'] += 1
        sim_standings[away_team]['matches_played'] += 1

    return sim_standings

def simulate_two_legged_tie(team1, team2):
    # Leg 1: Team 1 home
    goals1_leg1, goals2_leg1 = predict_match_outcome(team1, team2, is_knockout=False)

    # Leg 2: Team 2 home
    goals2_leg2, goals1_leg2 = predict_match_outcome(team2, team1, is_knockout=False) # Note: Team2 is "home"

    # Aggregate score
    agg_team1 = goals1_leg1 + goals1_leg2
    agg_team2 = goals2_leg1 + goals2_leg2

    if agg_team1 > agg_team2:
        return team1
    elif agg_team2 > agg_team1:
        return team2
    else: # Aggregate score is tied, apply away goals rule (simplified: whoever scored more away goals wins)
        if goals1_leg2 > goals2_leg1: # Team 1 scored more away goals (in Leg 2)
            return team1
        elif goals2_leg1 > goals1_leg2: # Team 2 scored more away goals (in Leg 1)
            return team2
        else: # Still tied (e.g., 0-0, 0-0 or 1-1, 1-1). Simulate penalties by higher rank.
            return team1 if get_team_rank_points(team1) > get_team_rank_points(team2) else team2

# --- Main Simulation Function ---

def simulate_afc_qualifiers(num_simulations=1000):
    direct_qualifiers_counts = defaultdict(int)
    playoff_tournament_qual_counts = defaultdict(int)

    for _ in tqdm(range(num_simulations), desc="Simulating AFC Qualifiers"):

        # 1. Third Round (Simulate Matchday 10)
        third_round_final_standings = {}
        third_round_third_place = []
        third_round_fourth_place = []

        for group_name, group_data in third_round_groups.items():
            final_group_standings = simulate_group_matches(group_data, group_data['standings'])
            sorted_group = calculate_group_standings(final_group_standings)
            third_round_final_standings[group_name] = sorted_group

            # Top 2 qualify directly
            for i in range(2):
                team = sorted_group[i][0]
                if team not in ALREADY_QUALIFIED_DIRECTLY: # Only add if not already confirmed
                    direct_qualifiers_counts[team] += 1
            # 3rd and 4th go to Fourth Round
            third_round_third_place.append(sorted_group[2][0])
            third_round_fourth_place.append(sorted_group[3][0])

        # Combine 3rd and 4th placed teams for Fourth Round
        fourth_round_teams = third_round_third_place + third_round_fourth_place
        # Sort by rank for semi-random group assignment (higher ranked teams try to avoid each other)
        fourth_round_teams.sort(key=get_team_rank_points, reverse=True)
        random.shuffle(fourth_round_teams) # Add some randomness to group formation

        # 2. Fourth Round (Two groups of three, single-leg round-robin)
        # 8 direct slots for AFC. 6 are known. 2 more come from Fourth Round.
        # 6 teams from 3rd/4th place (A3, A4, B3, B4, C3, C4)
        # Groups of 3. Play once.
        fourth_round_group_a_teams = fourth_round_teams[0:3]
        fourth_round_group_b_teams = fourth_round_teams[3:6]

        fourth_round_group_winners = []
        fourth_round_group_runners_up = []

        # Simulate Group A
        group_a_standings = {team: {'points': 0, 'gd': 0, 'gs': 0} for team in fourth_round_group_a_teams}
        group_a_fixtures = [
            (fourth_round_group_a_teams[0], fourth_round_group_a_teams[1]),
            (fourth_round_group_a_teams[0], fourth_round_group_a_teams[2]),
            (fourth_round_group_a_teams[1], fourth_round_group_a_teams[2]),
        ]
        random.shuffle(group_a_fixtures)

        for team1, team2 in group_a_fixtures:
            home_goals, away_goals = predict_match_outcome(team1, team2, is_knockout=False) # Neutral venue implied, but function uses "home" for consistency

            if home_goals > away_goals:
                group_a_standings[team1]['points'] += 3
            elif home_goals < away_goals:
                group_a_standings[team2]['points'] += 3
            else:
                group_a_standings[team1]['points'] += 1
                group_a_standings[team2]['points'] += 1

            group_a_standings[team1]['gd'] += (home_goals - away_goals)
            group_a_standings[team2]['gd'] += (away_goals - home_goals)
            group_a_standings[team1]['gs'] += home_goals
            group_a_standings[team2]['gs'] += away_goals

        sorted_group_a = calculate_group_standings(group_a_standings)
        fourth_round_group_winners.append(sorted_group_a[0][0])
        fourth_round_group_runners_up.append(sorted_group_a[1][0])

        # Simulate Group B (similar logic)
        group_b_standings = {team: {'points': 0, 'gd': 0, 'gs': 0} for team in fourth_round_group_b_teams}
        group_b_fixtures = [
            (fourth_round_group_b_teams[0], fourth_round_group_b_teams[1]),
            (fourth_round_group_b_teams[0], fourth_round_group_b_teams[2]),
            (fourth_round_group_b_teams[1], fourth_round_group_b_teams[2]),
        ]
        random.shuffle(group_b_fixtures)

        for team1, team2 in group_b_fixtures:
            home_goals, away_goals = predict_match_outcome(team1, team2, is_knockout=False)

            if home_goals > away_goals:
                group_b_standings[team1]['points'] += 3
            elif home_goals < away_goals:
                group_b_standings[team2]['points'] += 3
            else:
                group_b_standings[team1]['points'] += 1
                group_b_standings[team2]['points'] += 1

            group_b_standings[team1]['gd'] += (home_goals - away_goals)
            group_b_standings[team2]['gd'] += (away_goals - home_goals)
            group_b_standings[team1]['gs'] += home_goals
            group_b_standings[team2]['gs'] += away_goals

        sorted_group_b = calculate_group_standings(group_b_standings)
        fourth_round_group_winners.append(sorted_group_b[0][0])
        fourth_round_group_runners_up.append(sorted_group_b[1][0])

        # Add Fourth Round group winners to direct qualifiers
        for team in fourth_round_group_winners:
            direct_qualifiers_counts[team] += 1

        # 3. Fifth Round (Playoff for Inter-confederation Playoff spot)
        # The two runners-up from the Fourth Round (fourth_round_group_runners_up) play a two-legged tie.
        fifth_round_contenders = fourth_round_group_runners_up
        # Ensure only 2 teams for the tie
        if len(fifth_round_contenders) == 2:
            interconf_playoff_team = simulate_two_legged_tie(fifth_round_contenders[0], fifth_round_contenders[1])
            playoff_tournament_qual_counts[interconf_playoff_team] += 1

    print(f"\n--- AFC World Cup 2026 Qualification Simulation Results ({num_simulations} runs) ---")
    print(f"**Note:** This simulation covers the remaining Third Round matches, Fourth Round, and Fifth Round.")
    print(f"AFC has 8 direct World Cup slots and 1 Inter-confederation Play-off slot.")

    print("\n--- Direct World Cup Qualifiers ---")
    # Add already qualified teams with 100% chance for reporting
    for team in ALREADY_QUALIFIED_DIRECTLY:
        direct_qualifiers_counts[team] = num_simulations # Mark as 100% qualified

    sorted_direct_qualifiers = sorted(direct_qualifiers_counts.items(), key=lambda item: (-item[1], item[0]))
    for team, count in sorted_direct_qualifiers:
        print(f"{team}: {count / num_simulations:.2%}")

    print("\n--- Teams Advancing to FIFA Inter-confederation Play-off Tournament ---")
    sorted_playoff_qualifiers = sorted(playoff_tournament_qual_counts.items(), key=lambda item: (-item[1], item[0]))
    for team, count in sorted_playoff_qualifiers:
        print(f"{team}: {count / num_simulations:.2%}")

# --- Main Execution ---
if __name__ == "__main__":
    simulate_afc_qualifiers(num_simulations=1000)
