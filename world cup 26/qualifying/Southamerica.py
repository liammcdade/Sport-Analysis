import random
from collections import defaultdict

from tqdm import tqdm

# Updated team strengths based on FIFA rankings (May 6, 2025 data from Sofascore/FIFA)
team_strengths = {
    'Argentina': 1886.16,
    'Brazil': 1776.03,
    'Uruguay': 1679.49,
    'Colombia': 1679.04,
    'Ecuador': 1567.95,
    'Peru': 1483.48,
    'Venezuela': 1476.84,
    'Paraguay': 1475.93,
    'Chile': 1461.91,
    'Bolivia': 1308.12
}

# Current standings after 15 rounds of matches (based on NBC Sports/Sportstar as of June 8, 2025)
current_standings = {
    'Argentina': {'points': 34, 'gd': 19, 'gs': 27, 'matches_played': 15},
    'Ecuador': {'points': 24, 'gd': 8, 'gs': 13, 'matches_played': 15},
    'Paraguay': {'points': 24, 'gd': 4, 'gs': 13, 'matches_played': 15},
    'Brazil': {'points': 22, 'gd': 4, 'gs': 20, 'matches_played': 15},
    'Uruguay': {'points': 21, 'gd': 5, 'gs': 17, 'matches_played': 15},
    'Colombia': {'points': 21, 'gd': 4, 'gs': 18, 'matches_played': 15},
    'Venezuela': {'points': 18, 'gd': -2, 'gs': 15, 'matches_played': 15},
    'Bolivia': {'points': 14, 'gd': -18, 'gs': 14, 'matches_played': 15},
    'Peru': {'points': 11, 'gd': -11, 'gs': 6, 'matches_played': 15},
    'Chile': {'points': 10, 'gd': -13, 'gs': 9, 'matches_played': 15}
}

# Remaining fixtures (Matchday 16, 17, 18 - based on NBC Sports/Wikipedia)
remaining_fixtures = [
    # Matchday 16 (June 10, 2025)
    ('Bolivia', 'Chile'),
    ('Uruguay', 'Venezuela'),
    ('Argentina', 'Colombia'),
    ('Brazil', 'Paraguay'),
    ('Peru', 'Ecuador'),

    # Matchday 17 (September 9, 2025)
    ('Paraguay', 'Ecuador'),
    ('Argentina', 'Venezuela'),
    ('Uruguay', 'Peru'),
    ('Colombia', 'Bolivia'),
    ('Brazil', 'Chile'),

    # Matchday 18 (September 14, 2025)
    ('Ecuador', 'Argentina'),
    ('Chile', 'Uruguay'),
    ('Bolivia', 'Brazil'),
    ('Venezuela', 'Colombia'),
    ('Peru', 'Paraguay')
]

def predict_match_outcome(home_team, away_team):
    home_rank_points = team_strengths.get(home_team, 1000)
    away_rank_points = team_strengths.get(away_team, 1000)

    strength_diff = home_rank_points - away_rank_points

    base_home_win_prob = 0.45
    base_draw_prob = 0.25
    base_away_win_prob = 0.30

    home_win_prob = base_home_win_prob + (strength_diff * 0.0005)
    away_win_prob = base_away_win_prob - (strength_diff * 0.0005)
    draw_prob = base_draw_prob - abs(strength_diff) * 0.00025

    # Clip probabilities to be within a reasonable range and re-normalize
    home_win_prob = max(0.05, min(0.95, home_win_prob))
    away_win_prob = max(0.05, min(0.95, away_win_prob))
    draw_prob = max(0.05, min(0.95, draw_prob))

    total_prob = home_win_prob + draw_prob + away_win_prob
    if total_prob == 0: # Avoid division by zero in extreme cases
        home_win_prob = draw_prob = away_win_prob = 1/3
    else:
        home_win_prob /= total_prob
        draw_prob /= total_prob
        away_win_prob /= total_prob

    outcome = random.choices(['home_win', 'draw', 'away_win'],
                             weights=[home_win_prob, draw_prob, away_win_prob], k=1)[0]

    # Goal prediction (simplified)
    # Stronger team gets a higher chance of scoring more goals
    home_goals = 0
    away_goals = 0

    if outcome == 'home_win':
        home_goals = random.randint(1, 3) + max(0, round(strength_diff / 400))
        away_goals = random.randint(0, max(0, home_goals - 1))
        home_goals = max(1, home_goals)
        away_goals = max(0, away_goals)
        if home_goals <= away_goals: # Ensure home team wins
            home_goals = away_goals + random.choice([1,2])
    elif outcome == 'away_win':
        away_goals = random.randint(1, 3) + max(0, round(-strength_diff / 400))
        home_goals = random.randint(0, max(0, away_goals - 1))
        away_goals = max(1, away_goals)
        home_goals = max(0, home_goals)
        if away_goals <= home_goals: # Ensure away team wins
            away_goals = home_goals + random.choice([1,2])
    else:  # Draw
        goals = random.randint(0, 2) + round((home_rank_points + away_rank_points) / 3000)
        home_goals = max(0, goals)
        away_goals = max(0, goals)
        if home_goals != away_goals: # Ensure it's a draw
            home_goals = away_goals = max(home_goals, away_goals)
            if home_goals == 0: # Avoid 0-0 for every draw, ensure some variety
                home_goals = away_goals = random.randint(1,2)


    return home_goals, away_goals

def calculate_standings(standings):
    sorted_teams = sorted(standings.items(),
                          key=lambda item: (item[1]['points'], item[1]['gd'], item[1]['gs'], team_strengths.get(item[0], 0)),
                          reverse=True)
    return sorted_teams

def simulate_tournament(initial_standings, all_fixtures, num_simulations=10000):
    direct_qual_counts = defaultdict(int)
    playoff_qual_counts = defaultdict(int)
    total_qual_counts = defaultdict(int)

    for _ in tqdm(range(num_simulations), desc="Simulating CONMEBOL Qualifiers"):
        simulated_standings = {team: data.copy() for team, data in initial_standings.items()}

        for home_team, away_team in all_fixtures:
            # Skip if either team is not in our standings (shouldn't happen with CONMEBOL)
            if home_team not in simulated_standings or away_team not in simulated_standings:
                continue

            home_goals, away_goals = predict_match_outcome(home_team, away_team)

            if home_goals > away_goals:
                simulated_standings[home_team]['points'] += 3
            elif home_goals < away_goals:
                simulated_standings[away_team]['points'] += 3
            else:
                simulated_standings[home_team]['points'] += 1
                simulated_standings[away_team]['points'] += 1

            simulated_standings[home_team]['gd'] += (home_goals - away_goals)
            simulated_standings[away_team]['gd'] += (away_goals - home_goals)
            simulated_standings[home_team]['gs'] += home_goals
            simulated_standings[away_team]['gs'] += away_goals
            simulated_standings[home_team]['matches_played'] += 1
            simulated_standings[away_team]['matches_played'] += 1

        final_order = calculate_standings(simulated_standings)

        # Top 6 directly qualify
        for i in range(6):
            if i < len(final_order):
                direct_qual_counts[final_order[i][0]] += 1
                total_qual_counts[final_order[i][0]] += 1

        # 7th place goes to inter-confederation playoff
        if len(final_order) >= 7:
            playoff_team = final_order[6][0]
            playoff_qual_counts[playoff_team] += 1
            total_qual_counts[playoff_team] += 1 # Count for total chance to qualify

    print(f"\n--- CONMEBOL World Cup 2026 Qualification Simulation Results ({num_simulations} runs) ---")

    print("\nProbability of Direct Qualification (Top 6):")
    sorted_direct = sorted(direct_qual_counts.items(), key=lambda item: (-item[1], item[0]))
    for team, count in sorted_direct:
        print(f"{team}: {count / num_simulations:.2%}")

    print("\nProbability of Playoff Spot (7th Place):")
    sorted_playoff = sorted(playoff_qual_counts.items(), key=lambda item: (-item[1], item[0]))
    for team, count in sorted_playoff:
        print(f"{team}: {count / num_simulations:.2%}")

    print("\nOverall Probability of Qualification (Direct or Playoff):")
    sorted_total = sorted(total_qual_counts.items(), key=lambda item: (-item[1], item[0]))
    for team, count in sorted_total:
        print(f"{team}: {count / num_simulations:.2%}")

if __name__ == "__main__":
    simulate_tournament(current_standings, remaining_fixtures, num_simulations=10000)

