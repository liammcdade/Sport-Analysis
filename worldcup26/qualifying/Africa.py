import random
from collections import defaultdict
from tqdm import tqdm
import math

# --- Data Setup ---

# FIFA Ranking points for CAF teams (June 2024 FIFA World Ranking)
# This list is comprehensive but might not include all ~54 CAF nations if they are very low ranked
# or not actively participating. I will use a default for missing ones.
team_strengths = {
    'Morocco': 1676.99,
    'Senegal': 1623.34,
    'Egypt': 1515.1,
    'Tunisia': 1502.8,
    'Algeria': 1493.59,
    'Mali': 1475.29,
    'Ivory Coast': 1447.65,
    'Nigeria': 1445.69,
    'Burkina Faso': 1435.59,
    'Cameroon': 1421.93,
    'Ghana': 1399.79,
    'DR Congo': 1378.1,
    'South Africa': 1361.32,
    'Cape Verde': 1345.54,
    'Zambia': 1297.2,
    'Gabon': 1294.61,
    'Equatorial Guinea': 1269.83,
    'Uganda': 1238.16,
    'Benin': 1228.61,
    'Mauritania': 1226.54,
    'Madagascar': 1205.86,
    'Guinea-Bissau': 1184.28,
    'Namibia': 1179.94,
    'Angola': 1177.37,
    'Mozambique': 1168.04,
    'Gambia': 1166.5,
    'Sierra Leone': 1162.77,
    'Togo': 1150.14,
    'Tanzania': 1141.51,
    'Libya': 1133.09,
    'Zimbabwe': 1122.97,
    'Malawi': 1120.73,
    'Comoros': 1111.46,
    'Sudan': 1081.76,
    'Rwanda': 1060.03,
    'Burundi': 1050.21,
    'Ethiopia': 1032.54,
    'Botswana': 1021.93,
    'Eswatini': 1007.82,
    'Lesotho': 989.15,
    'Liberia': 982.72,
    'Central African Republic': 962.19,
    'Niger': 959.08,
    'Chad': 906.91,
    'Sao Tome and Principe': 864.03,
    'South Sudan': 841.48,
    'Djibouti': 821.57,
    'Seychelles': 800.74,
    'Somalia': 799.04,
    'Eritrea': 794.75, # Eritrea withdrew, but keeping for completeness
}

# Current Group Standings after Matchday 6 (June 2025 matches have completed)
# Source: Primarily NBC Sports, BBC Sport, Wikipedia, FIFA.com (as of June 9, 2025)
# Note: Some groups have played 5 matches for some teams, 6 for others.
# I've used the data with 6 matches where available, and adjusted for Eritrea's withdrawal.
current_group_standings = {
    'Group A': {
        'Egypt': {'points': 16, 'gd': 12, 'gs': 14, 'matches_played': 6},
        'Burkina Faso': {'points': 11, 'gd': 6, 'gs': 13, 'matches_played': 6},
        'Sierra Leone': {'points': 8, 'gd': 0, 'gs': 7, 'matches_played': 6},
        'Ethiopia': {'points': 6, 'gd': 0, 'gs': 7, 'matches_played': 6},
        'Guinea-Bissau': {'points': 6, 'gd': -2, 'gs': 5, 'matches_played': 6},
        'Djibouti': {'points': 1, 'gd': -16, 'gs': 4, 'matches_played': 6},
    },
    'Group B': {
        'DR Congo': {'points': 13, 'gd': 5, 'gs': 7, 'matches_played': 6},
        'Senegal': {'points': 12, 'gd': 7, 'gs': 8, 'matches_played': 6},
        'Sudan': {'points': 12, 'gd': 6, 'gs': 8, 'matches_played': 6},
        'Togo': {'points': 4, 'gd': -3, 'gs': 4, 'matches_played': 6},
        'South Sudan': {'points': 3, 'gd': -8, 'gs': 2, 'matches_played': 6},
        'Mauritania': {'points': 2, 'gd': -7, 'gs': 2, 'matches_played': 6},
    },
    'Group C': {
        'South Africa': {'points': 13, 'gd': 5, 'gs': 10, 'matches_played': 6},
        'Rwanda': {'points': 8, 'gd': 0, 'gs': 4, 'matches_played': 6},
        'Benin': {'points': 8, 'gd': -1, 'gs': 6, 'matches_played': 6},
        'Nigeria': {'points': 7, 'gd': 1, 'gs': 7, 'matches_played': 6},
        'Lesotho': {'points': 6, 'gd': -1, 'gs': 4, 'matches_played': 6},
        'Zimbabwe': {'points': 4, 'gd': -4, 'gs': 5, 'matches_played': 6},
    },
    'Group D': {
        'Cape Verde': {'points': 13, 'gd': 2, 'gs': 7, 'matches_played': 6},
        'Cameroon': {'points': 12, 'gd': 8, 'gs': 12, 'matches_played': 6},
        'Libya': {'points': 8, 'gd': -1, 'gs': 6, 'matches_played': 6},
        'Angola': {'points': 7, 'gd': 0, 'gs': 4, 'matches_played': 6},
        'Mauritius': {'points': 5, 'gd': -4, 'gs': 6, 'matches_played': 6},
        'Eswatini': {'points': 2, 'gd': -5, 'gs': 4, 'matches_played': 6},
    },
    'Group E': { # Eritrea withdrew, so this group has 5 teams. All teams will play 8 matches.
        'Morocco': {'points': 15, 'gd': 12, 'gs': 14, 'matches_played': 5}, # Morocco played 5
        'Tanzania': {'points': 9, 'gd': 1, 'gs': 5, 'matches_played': 5},   # Tanzania played 5
        'Zambia': {'points': 6, 'gd': 2, 'gs': 9, 'matches_played': 5},
        'Niger': {'points': 6, 'gd': 2, 'gs': 6, 'matches_played': 4}, # Niger played 4, others 5
        'Congo': {'points': 0, 'gd': -17, 'gs': 2, 'matches_played': 5},
    },
    'Group F': {
        'Ivory Coast': {'points': 16, 'gd': 14, 'gs': 14, 'matches_played': 6},
        'Gabon': {'points': 15, 'gd': 6, 'gs': 12, 'matches_played': 6},
        'Burundi': {'points': 10, 'gd': 6, 'gs': 13, 'matches_played': 6},
        'Kenya': {'points': 6, 'gd': 3, 'gs': 11, 'matches_played': 6},
        'Gambia': {'points': 4, 'gd': -1, 'gs': 12, 'matches_played': 6},
        'Seychelles': {'points': 0, 'gd': -28, 'gs': 2, 'matches_played': 6},
    },
    'Group G': {
        'Algeria': {'points': 15, 'gd': 10, 'gs': 16, 'matches_played': 6},
        'Mozambique': {'points': 12, 'gd': -1, 'gs': 10, 'matches_played': 6},
        'Botswana': {'points': 9, 'gd': 1, 'gs': 9, 'matches_played': 6},
        'Uganda': {'points': 9, 'gd': -1, 'gs': 9, 'matches_played': 6},
        'Guinea': {'points': 7, 'gd': -1, 'gs': 8, 'matches_played': 6},
        'Somalia': {'points': 1, 'gd': -8, 'gs': 3, 'matches_played': 6},
    },
    'Group H': {
        'Tunisia': {'points': 16, 'gd': 9, 'gs': 11, 'matches_played': 6},
        'Namibia': {'points': 12, 'gd': 6, 'gs': 9, 'matches_played': 6},
        'Liberia': {'points': 10, 'gd': 3, 'gs': 7, 'matches_played': 6},
        'Equatorial Guinea': {'points': 7, 'gd': -4, 'gs': 3, 'matches_played': 6},
        'Malawi': {'points': 6, 'gd': -2, 'gs': 6, 'matches_played': 6},
        'Sao Tome and Principe': {'points': 0, 'gd': -12, 'gs': 0, 'matches_played': 6},
    },
    'Group I': {
        'Ghana': {'points': 15, 'gd': 10, 'gs': 15, 'matches_played': 6},
        'Comoros': {'points': 12, 'gd': 2, 'gs': 9, 'matches_played': 6},
        'Madagascar': {'points': 10, 'gd': 3, 'gs': 9, 'matches_played': 6},
        'Mali': {'points': 9, 'gd': 4, 'gs': 8, 'matches_played': 6},
        'Central African Republic': {'points': 5, 'gd': -5, 'gs': 8, 'matches_played': 6},
        'Chad': {'points': 0, 'gd': -14, 'gs': 1, 'matches_played': 6},
    }
}

# Remaining First Round Fixtures (Matchday 7, 8, 9, 10 - September, October 2025)
# This is a large list. I will try to be as accurate as possible based on the search results.
# NOTE: The provided search results list September 3rd and September 6th fixtures.
# I'll add the remaining fixtures for October based on the standard home/away pattern if not explicit.
remaining_group_fixtures = [
    # September 3, 2025
    ('Algeria', 'Botswana'), ('Angola', 'Libya'), ('Benin', 'Zimbabwe'), ('Cameroon', 'Eswatini'),
    ('Chad', 'Ghana'), ('Congo', 'Tanzania'), ('Djibouti', 'Burkina Faso'), ('Egypt', 'Ethiopia'),
    ('Guinea-Bissau', 'Sierra Leone'), ('Ivory Coast', 'Burundi'), ('Kenya', 'Gambia'),
    ('Lesotho', 'South Africa'), ('Madagascar', 'Central African Republic'), ('Mali', 'Comoros'),
    ('Mauritania', 'Togo'), ('Mauritius', 'Cape Verde'), ('Morocco', 'Niger'),
    ('Namibia', 'Malawi'), ('Nigeria', 'Rwanda'), ('Sao Tome and Principe', 'Equatorial Guinea'),
    ('Senegal', 'Sudan'), ('Seychelles', 'Gabon'), ('Somalia', 'Guinea'),
    ('South Sudan', 'DR Congo'), ('Tunisia', 'Liberia'), ('Uganda', 'Mozambique'),
    # September 6, 2025 (or similar window)
    ('Angola', 'Mauritius'), ('Benin', 'Lesotho'), ('Burkina Faso', 'Egypt'), ('Cape Verde', 'Cameroon'),
    ('Central African Republic', 'Comoros'), ('DR Congo', 'Senegal'), ('Equatorial Guinea', 'Tunisia'),
    ('Gabon', 'Ivory Coast'), ('Gambia', 'Burundi'), ('Ghana', 'Mali'), ('Guinea', 'Algeria'),
    ('Guinea-Bissau', 'Djibouti'), ('Kenya', 'Seychelles'), ('Libya', 'Eswatini'),
    ('Madagascar', 'Chad'), ('Malawi', 'Liberia'), ('Mauritania', 'South Sudan'),
    ('Mozambique', 'Botswana'), ('Namibia', 'Sao Tome and Principe'), ('Sierra Leone', 'Ethiopia'),
    ('South Africa', 'Nigeria'), ('Tanzania', 'Niger'), ('Togo', 'Sudan'),
    ('Uganda', 'Somalia'), ('Zambia', 'Morocco'), ('Zimbabwe', 'Rwanda'),
    # October 2025 - Matchdays 9 & 10 (reverse fixtures of initial matchdays)
    # This part requires making assumptions about how matchdays 9 and 10 will play out.
    # The format is home-and-away round-robin. Matchdays 1-6 are done.
    # Matchdays 7-8 are Sept. Matchdays 9-10 are Oct.
    # It's likely that Oct matches are simply the reverse of earlier ones not yet played in Sept.
    # Or, the fixtures for Oct 2025 are specific. The searches did not provide October fixtures.
    # For a full simulation, I'll assume the reverse of the remaining September fixtures, or the reverse of earlier unseen matches
    # to complete the round robin.
    # A more robust solution would require explicit fixture lists for Oct.
    # For now, let's create a full list of all possible matches in the groups (10 per team for 6-team groups, 8 for 5-team group)
    # and filter out the ones already played. Then simulate the remaining.

]

# Generate all possible group matches to compare against already played matches
all_group_matches = []
for group_name, teams_data in current_group_standings.items():
    teams_in_group = list(teams_data.keys())
    for i in range(len(teams_in_group)):
        for j in range(i + 1, len(teams_in_group)):
            team1 = teams_in_group[i]
            team2 = teams_in_group[j]
            all_group_matches.append(tuple(sorted((team1, team2)))) # Use sorted tuple for unique match pair

# This set stores matches already implicitly played (or those in the fixed September fixtures)
# Based on the given standings, each team has played 6 matches (or 4-5 in Group E).
# A 6-team group plays 10 matches total per team. A 5-team group plays 8 matches total per team.
# This means for a 6-team group, each team still has 4 matches left (10 total - 6 played).
# For Group E (5 teams), Morocco/Tanzania/Zambia/Congo played 5, Niger played 4.
# So, Morocco/Tanzania/Zambia/Congo have 3 matches left (8 total - 5 played). Niger has 4 matches left (8 total - 4 played).

# Let's generate the complete set of fixtures required for the round robin and then filter.
full_round_robin_fixtures = []
for group_name, teams_data in current_group_standings.items():
    teams = list(teams_data.keys())
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            full_round_robin_fixtures.append((teams[i], teams[j])) # Home fixture
            full_round_robin_fixtures.append((teams[j], teams[i])) # Away fixture

# The `remaining_group_fixtures` from search results are specific for Sept 3/6.
# We need to consider all matches required to get to 10 (or 8) matches per team.
# This part is the most complex as I don't have explicit MD7-10 fixtures.
# I will simulate the "remaining" matches by iterating until all teams have played 10 (or 8) matches.

# --- Helper Functions (same as CONCACAF, generally applicable) ---

def predict_match_outcome(home_team, away_team):
    home_rank_points = team_strengths.get(home_team, 800) # Default lower value for unranked teams
    away_rank_points = team_strengths.get(away_team, 800)

    strength_diff = home_rank_points - away_rank_points

    # Probabilities adjusted for home advantage and strength difference
    prob_home_win = 1 / (1 + 10**((away_rank_points - home_rank_points + 50) / 400)) # Add 50 for home advantage
    prob_draw = 0.25
    prob_away_win = 1 - prob_home_win - prob_draw

    # Ensure probabilities are positive and sum to 1
    if prob_away_win < 0:
        prob_draw += prob_away_win
        prob_away_win = 0
    if prob_home_win < 0:
        prob_draw += prob_home_win
        prob_home_win = 0

    total_prob = prob_home_win + prob_draw + prob_away_win
    if total_prob <= 0:
        prob_home_win, prob_draw, prob_away_win = 1/3, 1/3, 1/3
    else:
        prob_home_win /= total_prob
        prob_draw /= total_prob
        prob_away_win /= total_prob

    outcome = random.choices(['home_win', 'draw', 'away_win'],
                             weights=[prob_home_win, prob_draw, prob_away_win], k=1)[0]

    home_goals, away_goals = 0, 0

    # More nuanced goal prediction
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
        if home_goals != away_goals:
            home_goals = away_goals = max(home_goals, away_goals)
            if home_goals == 0:
                home_goals = away_goals = random.randint(1,2)

    return home_goals, away_goals

def calculate_group_standings(group_data):
    sorted_teams = sorted(group_data.items(),
                          key=lambda item: (item[1]['points'], item[1]['gd'], item[1]['gs'], team_strengths.get(item[0], 0)),
                          reverse=True)
    return sorted_teams

def get_team_rank_points(team_name):
    return team_strengths.get(team_name, 0) # Use 0 for unranked teams, they'd be lowest


def simulate_caf_qualifiers(initial_group_standings, remaining_fixtures_list, num_simulations=10000):
    direct_qual_counts = defaultdict(int)
    playoff_qual_counts = defaultdict(int)
    interconf_playoff_counts = defaultdict(int) # This is the final CAF spot for inter-confed playoff

    for _ in tqdm(range(num_simulations), desc="Simulating CAF Qualifiers"):
        simulated_standings = {group: {team: data.copy() for team, data in group_data.items()}
                               for group, group_data in initial_group_standings.items()}

        # Simulate remaining group matches
        for home_team, away_team in remaining_fixtures_list:
            group_name = None
            for g_name, teams_in_group in simulated_standings.items():
                if home_team in teams_in_group and away_team in teams_in_group:
                    group_name = g_name
                    break
            if not group_name:
                continue

            # Ensure match is actually remaining for these teams based on matches_played
            team_count_in_group = len(simulated_standings[group_name])
            max_matches = (team_count_in_group - 1) * 2 # Round robin, home & away

            if simulated_standings[group_name][home_team]['matches_played'] < max_matches and \
               simulated_standings[group_name][away_team]['matches_played'] < max_matches:

                home_goals, away_goals = predict_match_outcome(home_team, away_team)

                if home_goals > away_goals:
                    simulated_standings[group_name][home_team]['points'] += 3
                elif home_goals < away_goals:
                    simulated_standings[group_name][away_team]['points'] += 3
                else:
                    simulated_standings[group_name][home_team]['points'] += 1
                    simulated_standings[group_name][away_team]['points'] += 1

                simulated_standings[group_name][home_team]['gd'] += (home_goals - away_goals)
                simulated_standings[group_name][away_team]['gd'] += (away_goals - home_goals)
                simulated_standings[group_name][home_team]['gs'] += home_goals
                simulated_standings[group_name][away_team]['gs'] += away_goals
                simulated_standings[group_name][home_team]['matches_played'] += 1
                simulated_standings[group_name][away_team]['matches_played'] += 1


        # Determine 9 Group Winners (Direct Qualifiers)
        group_winners = []
        for group_name, data in simulated_standings.items():
            final_group_order = calculate_group_standings(data)
            if final_group_order:
                group_winners.append(final_group_order[0][0])
                direct_qual_counts[final_group_order[0][0]] += 1

        # Determine 4 Best Runners-Up for CAF Playoff
        all_runners_up = []
        for group_name, data in simulated_standings.items():
            final_group_order = calculate_group_standings(data)
            if len(final_group_order) > 1: # Ensure there's a runner-up
                runner_up_team = final_group_order[1][0]
                runner_up_data = final_group_order[1][1].copy()
                runner_up_data['team'] = runner_up_team
                all_runners_up.append(runner_up_data)

        # Sort runners-up by points, then GD, then GS, then rank
        sorted_runners_up = sorted(all_runners_up,
                                   key=lambda x: (x['points'], x['gd'], x['gs'], get_team_rank_points(x['team'])),
                                   reverse=True)

        caf_playoff_teams = [ru['team'] for ru in sorted_runners_up[:4]] # Top 4 runners-up

        # Simulate CAF Play-off Tournament
        if len(caf_playoff_teams) == 4:
            # Semi-finals (Random draw among them, or based on ranking? Let's do random for simplicity)
            random.shuffle(caf_playoff_teams)
            sf1_teams = (caf_playoff_teams[0], caf_playoff_teams[3]) # Higher vs lower based on shuffled list
            sf2_teams = (caf_playoff_teams[1], caf_playoff_teams[2])

            sf1_home_goals, sf1_away_goals = predict_match_outcome(*sf1_teams)
            sf2_home_goals, sf2_away_goals = predict_match_outcome(*sf2_teams)

            sf1_winner = sf1_teams[0] if sf1_home_goals > sf1_away_goals else sf1_teams[1]
            sf2_winner = sf2_teams[0] if sf2_home_goals > sf2_away_goals else sf2_teams[1]

            # If draws are possible, they'd go to extra time/penalties. For simulation, a draw means the higher-ranked team wins.
            if sf1_home_goals == sf1_away_goals:
                sf1_winner = sf1_teams[0] if get_team_rank_points(sf1_teams[0]) > get_team_rank_points(sf1_teams[1]) else sf1_teams[1]
            if sf2_home_goals == sf2_away_goals:
                sf2_winner = sf2_teams[0] if get_team_rank_points(sf2_teams[0]) > get_team_rank_points(sf2_teams[1]) else sf2_teams[1]

            # Final
            final_teams = (sf1_winner, sf2_winner)
            final_home_goals, final_away_goals = predict_match_outcome(*final_teams)
            caf_playoff_winner = final_teams[0] if final_home_goals > final_away_goals else final_teams[1]
            if final_home_goals == final_away_goals:
                caf_playoff_winner = final_teams[0] if get_team_rank_points(final_teams[0]) > get_team_rank_points(final_teams[1]) else final_teams[1]

            interconf_playoff_counts[caf_playoff_winner] += 1

            for team in caf_playoff_teams:
                playoff_qual_counts[team] += 1 # Count participation in CAF playoff

    print(f"\n--- CAF World Cup 2026 Qualification Simulation Results ({num_simulations} runs) ---")
    print(f"**Note:** This simulation uses current Group Stage standings (Matchday 6 completed) and simulates remaining group matches (MD 7-10) and CAF Playoff.")
    print(f"9 Group Winners qualify directly. 4 Best Runners-Up enter CAF Playoff. Winner of CAF Playoff enters Inter-confederation Playoff.")

    print("\nProbability of Direct Qualification (Group Winner):")
    sorted_direct = sorted(direct_qual_counts.items(), key=lambda item: (-item[1], item[0]))
    for team, count in sorted_direct:
        print(f"{team}: {count / num_simulations:.2%}")

    print("\nProbability of entering CAF Playoff (Top 4 Runners-Up):")
    sorted_playoff_entry = sorted(playoff_qual_counts.items(), key=lambda item: (-item[1], item[0]))
    for team, count in sorted_playoff_entry:
        print(f"{team}: {count / num_simulations:.2%}")

    print("\nProbability of advancing to Inter-confederation Playoff (Winner of CAF Playoff):")
    sorted_interconf_playoff = sorted(interconf_playoff_counts.items(), key=lambda item: (-item[1], item[0]))
    for team, count in sorted_interconf_playoff:
        print(f"{team}: {count / num_simulations:.2%}")

    print("\nOverall Probability of Qualification (Direct OR Inter-confederation Playoff spot):")
    overall_qual_probabilities = defaultdict(float)
    for team, count in direct_qual_counts.items():
        overall_qual_probabilities[team] += count / num_simulations
    for team, count in interconf_playoff_counts.items():
        overall_qual_probabilities[team] += count / num_simulations

    sorted_overall = sorted(overall_qual_probabilities.items(), key=lambda item: (-item[1], item[0]))
    for team, chance in sorted_overall:
        print(f"{team}: {chance:.2%}")

# --- Main Execution ---
if __name__ == "__main__":
    # To handle the remaining fixtures dynamically for 10 (or 8) matches per team:
    # We first calculate how many matches each team still needs to play.
    # Then we generate all possible remaining home-away pairs within each group.
    # We shuffle these to simulate matchday progression.

    dynamic_remaining_fixtures = []
    for group_name, teams_data in current_group_standings.items():
        teams_in_group = list(teams_data.keys())
        expected_matches = (len(teams_in_group) - 1) * 2 # Total matches for a round-robin

        # Create all home-away pairs for the group
        group_possible_fixtures = []
        for i in range(len(teams_in_group)):
            for j in range(len(teams_in_group)):
                if i != j:
                    group_possible_fixtures.append((teams_in_group[i], teams_in_group[j]))

        # For simulation, we need to add the *remaining* fixtures.
        # Given the current standings, matches_played goes up to 6.
        # We know there are 4 more matchdays (7, 8, 9, 10). Each matchday involves 2 games per team in a 6-team group.
        # So each team should play 4 more matches. This means 4 * 0.5 * (N teams in group) = 4 * 0.5 * 6 = 12 matches per group remaining.
        # In a 6-team group, there are 15 unique match pairings. Each pair plays twice (home/away) = 30 total matches.
        # If 6 matchdays have passed, each team played 6 games. This means 6 * 0.5 * 6 = 18 matches played per group.
        # So 30 - 18 = 12 matches remain per group.
        # For a 5-team group, (5-1)*2 = 8 matches per team total. (5*4)/2 = 10 unique match pairings. 20 total matches.
        # Group E: Morocco/Tanzania/Zambia/Congo played 5. Niger played 4.
        # This implies: 5*0.5*5 = 12.5 matches (rounded, approx 12-13) played.
        # Total matches in 5-team group = 20. Remaining = 7-8.

        # A simpler way to handle remaining fixtures without exact dates:
        # For each group, determine all possible match pairs.
        # Simulate matches until each team in the group has played the `expected_matches`.
        # This approach ensures the full round-robin is completed.

        # This will be done *inside* the simulation loop for each group to ensure random order of remaining games.

    # Reworking `simulate_caf_qualifiers` to dynamically determine remaining matches per simulation.
    # The `remaining_fixtures_list` parameter will no longer be pre-populated for ALL groups.
    # Instead, each simulation will track `matches_played` for each team and determine which fixtures are outstanding.

    def simulate_caf_qualifiers_dynamic_fixtures(initial_group_standings, num_simulations=10000):
        direct_qual_counts = defaultdict(int)
        playoff_qual_counts = defaultdict(int)
        interconf_playoff_counts = defaultdict(int)

        for _ in tqdm(range(num_simulations), desc="Simulating CAF Qualifiers"):
            simulated_standings = {group: {team: data.copy() for team, data in group_data.items()}
                                   for group, group_data in initial_group_standings.items()}

            # Track matches played for each team within the current simulation
            current_matches_played = {group: {team: data['matches_played'] for team, data in group_data.items()}
                                      for group, group_data in simulated_standings.items()}

            # Simulate remaining group matches for all groups
            for group_name, teams_data in simulated_standings.items():
                teams_in_group = list(teams_data.keys())
                max_group_matches_per_team = (len(teams_in_group) - 1) * 2

                # Generate all possible home-away fixtures for this group
                all_possible_group_fixtures = []
                for i in range(len(teams_in_group)):
                    for j in range(len(teams_in_group)):
                        if i != j:
                            all_possible_group_fixtures.append((teams_in_group[i], teams_in_group[j]))
                random.shuffle(all_possible_group_fixtures) # Shuffle order of matches

                # Simulate until each team has played their full complement of matches
                for home_team, away_team in all_possible_group_fixtures:
                    if current_matches_played[group_name][home_team] < max_group_matches_per_team and \
                       current_matches_played[group_name][away_team] < max_group_matches_per_team:

                        home_goals, away_goals = predict_match_outcome(home_team, away_team)

                        if home_goals > away_goals:
                            simulated_standings[group_name][home_team]['points'] += 3
                        elif home_goals < away_goals:
                            simulated_standings[group_name][away_team]['points'] += 3
                        else:
                            simulated_standings[group_name][home_team]['points'] += 1
                            simulated_standings[group_name][away_team]['points'] += 1

                        simulated_standings[group_name][home_team]['gd'] += (home_goals - away_goals)
                        simulated_standings[group_name][away_team]['gd'] += (away_goals - home_goals)
                        simulated_standings[group_name][home_team]['gs'] += home_goals
                        simulated_standings[group_name][away_team]['gs'] += away_goals
                        simulated_standings[group_name][home_team]['matches_played'] += 1
                        simulated_standings[group_name][away_team]['matches_played'] += 1

                        # Update the tracker for this simulation
                        current_matches_played[group_name][home_team] += 1
                        current_matches_played[group_name][away_team] += 1

            # Determine 9 Group Winners (Direct Qualifiers)
            group_winners = []
            for group_name, data in simulated_standings.items():
                final_group_order = calculate_group_standings(data)
                if final_group_order:
                    group_winners.append(final_group_order[0][0])
                    direct_qual_counts[final_group_order[0][0]] += 1

            # Determine 4 Best Runners-Up for CAF Playoff
            all_runners_up = []
            for group_name, data in simulated_standings.items():
                final_group_order = calculate_group_standings(data)
                if len(final_group_order) > 1:
                    runner_up_team = final_group_order[1][0]
                    runner_up_data = final_group_order[1][1].copy()
                    runner_up_data['team'] = runner_up_team
                    all_runners_up.append(runner_up_data)

            # Sort runners-up by points, then GD, then GS, then rank
            sorted_runners_up = sorted(all_runners_up,
                                       key=lambda x: (x['points'], x['gd'], x['gs'], get_team_rank_points(x['team'])),
                                       reverse=True)

            caf_playoff_teams = [ru['team'] for ru in sorted_runners_up[:4]]

            # Simulate CAF Play-off Tournament
            if len(caf_playoff_teams) == 4:
                # Random draw for semi-finals from the 4 teams
                random.shuffle(caf_playoff_teams)
                sf_pairings = [(caf_playoff_teams[0], caf_playoff_teams[3]), (caf_playoff_teams[1], caf_playoff_teams[2])]

                sf_winners = []
                for team1, team2 in sf_pairings:
                    # To determine home/away for this 1-off match, let's use the higher ranked team as home
                    if get_team_rank_points(team1) >= get_team_rank_points(team2):
                        home_sf_team, away_sf_team = team1, team2
                    else:
                        home_sf_team, away_sf_team = team2, team1

                    home_goals, away_goals = predict_match_outcome(home_sf_team, away_sf_team)

                    if home_goals > away_goals:
                        sf_winners.append(home_sf_team)
                    elif home_goals < away_goals:
                        sf_winners.append(away_sf_team)
                    else: # Draw, higher ranked team wins
                        sf_winners.append(home_sf_team if get_team_rank_points(home_sf_team) > get_team_rank_points(away_sf_team) else away_sf_team)

                # Final
                final_teams_for_match = (sf_winners[0], sf_winners[1])
                # Again, higher ranked team as home
                if get_team_rank_points(final_teams_for_match[0]) >= get_team_rank_points(final_teams_for_match[1]):
                    home_final_team, away_final_team = final_teams_for_match[0], final_teams_for_match[1]
                else:
                    home_final_team, away_final_team = final_teams_for_match[1], final_teams_for_match[0]

                final_home_goals, final_away_goals = predict_match_outcome(home_final_team, away_final_team)

                if final_home_goals > final_away_goals:
                    caf_playoff_winner = home_final_team
                elif final_home_goals < final_away_goals:
                    caf_playoff_winner = away_final_team
                else: # Draw, higher ranked team wins
                    caf_playoff_winner = home_final_team if get_team_rank_points(home_final_team) > get_team_rank_points(away_final_team) else away_final_team

                interconf_playoff_counts[caf_playoff_winner] += 1

                for team in caf_playoff_teams:
                    playoff_qual_counts[team] += 1 # Count participation in CAF playoff

        print(f"\n--- CAF World Cup 2026 Qualification Simulation Results ({num_simulations} runs) ---")
        print(f"**Note:** This simulation uses current Group Stage standings (after Matchday 6) and dynamically simulates remaining group matches (MD 7-10) and the CAF Playoff.")
        print(f"9 Group Winners qualify directly. 4 Best Runners-Up enter CAF Playoff. Winner of CAF Playoff enters Inter-confederation Playoff.")

        print("\nProbability of Direct Qualification (Group Winner):")
        sorted_direct = sorted(direct_qual_counts.items(), key=lambda item: (-item[1], item[0]))
        for team, count in sorted_direct:
            print(f"{team}: {count / num_simulations:.2%}")

        print("\nProbability of entering CAF Playoff (Top 4 Runners-Up):")
        sorted_playoff_entry = sorted(playoff_qual_counts.items(), key=lambda item: (-item[1], item[0]))
        for team, count in sorted_playoff_entry:
            print(f"{team}: {count / num_simulations:.2%}")

        print("\nProbability of advancing to Inter-confederation Playoff (Winner of CAF Playoff):")
        sorted_interconf_playoff = sorted(interconf_playoff_counts.items(), key=lambda item: (-item[1], item[0]))
        for team, count in sorted_interconf_playoff:
            print(f"{team}: {count / num_simulations:.2%}")

        print("\nOverall Probability of Qualification (Direct OR Inter-confederation Playoff spot):")
        overall_qual_probabilities = defaultdict(float)
        for team, count in direct_qual_counts.items():
            overall_qual_probabilities[team] += count / num_simulations
        for team, count in interconf_playoff_counts.items():
            overall_qual_probabilities[team] += count / num_simulations

        sorted_overall = sorted(overall_qual_probabilities.items(), key=lambda item: (-item[1], item[0]))
        for team, chance in sorted_overall:
            print(f"{team}: {chance:.2%}")


    # Call the main simulation function
    simulate_caf_qualifiers_dynamic_fixtures(current_group_standings, num_simulations=10000)
