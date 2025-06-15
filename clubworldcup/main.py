import random
import json
import re
import pandas as pd
import io
import numpy as np
from collections import defaultdict
from tqdm.auto import tqdm

# --- Configuration ---
NUM_SIMULATIONS = 50  # Define the number of Monte Carlo simulations to run
# --- IMPORTANT: Set your player data CSV file path here ---
# Make sure 'player_data.csv' is in the same directory as this script,
# or provide the full path, e.g., 'C:/Users/YourUser/Documents/player_data.csv'
PLAYER_CSV_FILE_PATH = 'clubworldcup/player_data.csv'

# --- Initial Team Data ---
# This data structure is designed to be easily extensible.
# You can modify SofaScore averages or add new teams/groups if the tournament format changes.
initial_teams_data = [
    # Group A - Initial data reflecting Al Ahly vs Inter Miami 0-0 draw (Match 1 in this group)
    {'id': 1, 'name': 'Palmeiras', 'group': 'A', 'sofaScoreAverage': 7.6, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 2, 'name': 'FC Porto', 'group': 'A', 'sofaScoreAverage': 7.5, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 3, 'name': 'Al Ahly SC', 'group': 'A', 'sofaScoreAverage': 6.99, 'matchesPlayed': 1, 'wins': 0, 'draws': 1, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 1},
    {'id': 4, 'name': 'Inter Miami CF', 'group': 'A', 'sofaScoreAverage': 7.10, 'matchesPlayed': 1, 'wins': 0, 'draws': 1, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 1},

    # Group B
    {'id': 5, 'name': 'Paris Saint-Germain', 'group': 'B', 'sofaScoreAverage': 8.0, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 6, 'name': 'Atletico Madrid', 'group': 'B', 'sofaScoreAverage': 7.8, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 7, 'name': 'Botafogo', 'group': 'B', 'sofaScoreAverage': 7.0, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 8, 'name': 'Seattle Sounders', 'group': 'B', 'sofaScoreAverage': 6.8, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},

    # Group C
    {'id': 9, 'name': 'Bayern Munich', 'group': 'C', 'sofaScoreAverage': 8.23, 'matchesPlayed': 1, 'wins': 1, 'draws': 0, 'losses': 0, 'goalsFor': 10, 'goalsAgainst': 0, 'points': 3},
    {'id': 10, 'name': 'Benfica', 'group': 'C', 'sofaScoreAverage': 7.6, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 11, 'name': 'Boca Juniors', 'group': 'C', 'sofaScoreAverage': 7.1, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 12, 'name': 'Auckland City', 'group': 'C', 'sofaScoreAverage': 5.85, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 1, 'goalsFor': 0, 'goalsAgainst': 10, 'points': 0},

    # Group D
    {'id': 13, 'name': 'Flamengo', 'group': 'D', 'sofaScoreAverage': 7.5, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 14, 'name': 'Chelsea FC', 'group': 'D', 'sofaScoreAverage': 7.6, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 15, 'name': 'Espérance Sportive de Tunis', 'group': 'D', 'sofaScoreAverage': 6.7, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 16, 'name': 'Los Angeles FC', 'group': 'D', 'sofaScoreAverage': 7.0, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},

    # Group E
    {'id': 17, 'name': 'River Plate', 'group': 'E', 'sofaScoreAverage': 7.4, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 18, 'name': 'Inter Milan', 'group': 'E', 'sofaScoreAverage': 7.9, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 19, 'name': 'CF Monterrey', 'group': 'E', 'sofaScoreAverage': 7.0, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 20, 'name': 'Urawa Red Diamonds', 'group': 'E', 'sofaScoreAverage': 6.5, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},

    # Group F
    {'id': 21, 'name': 'Fluminense', 'group': 'F', 'sofaScoreAverage': 7.3, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 22, 'name': 'Borussia Dortmund', 'group': 'F', 'sofaScoreAverage': 7.7, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 23, 'name': 'Ulsan HD FC', 'group': 'F', 'sofaScoreAverage': 6.8, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 24, 'name': 'Mamelodi Sundowns', 'group': 'F', 'sofaScoreAverage': 6.6, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},

    # Group G
    {'id': 25, 'name': 'Manchester City', 'group': 'G', 'sofaScoreAverage': 8.1, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 26, 'name': 'Juventus', 'group': 'G', 'sofaScoreAverage': 7.5, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 27, 'name': 'Wydad AC', 'group': 'G', 'sofaScoreAverage': 6.7, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 28, 'name': 'Al Ain FC', 'group': 'G', 'sofaScoreAverage': 6.6, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},

    # Group H
    {'id': 29, 'name': 'Real Madrid', 'group': 'H', 'sofaScoreAverage': 8.3, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 30, 'name': 'Al Hilal SFC', 'group': 'H', 'sofaScoreAverage': 7.0, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 31, 'name': 'Pachuca', 'group': 'H', 'sofaScoreAverage': 6.9, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
    {'id': 32, 'name': 'Red Bull Salzburg', 'group': 'H', 'sofaScoreAverage': 7.3, 'matchesPlayed': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'goalsFor': 0, 'goalsAgainst': 0, 'points': 0},
]

# Generate all possible group stage matches based on initial_teams_data
def generate_all_group_matches_template(teams):
    matches = []
    groups = sorted(list(set(team['group'] for team in teams)))
    for group_name in groups:
        teams_in_group = [team for team in teams if team['group'] == group_name]
        for i in range(len(teams_in_group)):
            for j in range(i + 1, len(teams_in_group)):
                match = {
                    'id': f"{teams_in_group[i]['id']}-{teams_in_group[j]['id']}",
                    'homeTeamId': teams_in_group[i]['id'],
                    'awayTeamId': teams_in_group[j]['id'],
                    'played': False,
                    'homeGoals': None,
                    'awayGoals': None,
                }
                # Pre-set the result for Al Ahly vs Inter Miami CF
                if (match['homeTeamId'] == 3 and match['awayTeamId'] == 4) or \
                   (match['homeTeamId'] == 4 and match['awayTeamId'] == 3):
                    match['played'] = True
                    match['homeGoals'] = 0
                    match['awayGoals'] = 0
                matches.append(match)
    return matches

# This template is used to create deep copies for each simulation
all_group_matches_template = generate_all_group_matches_template(initial_teams_data)

# --- Player Data Loading ---
def load_player_data(csv_path):
    """Load player data from CSV file path and return as DataFrame."""
    try:
        df = pd.read_csv(csv_path)
        return df
    except FileNotFoundError:
        print(f"Error: Player data CSV file not found at '{csv_path}'. Please ensure the path is correct.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading player data from '{csv_path}': {e}")
        return pd.DataFrame()

# --- Team-country mapping for robust player-team matching ---
TEAM_COUNTRY_MAP = {
    'Al Ahly SC': ['Al Ahly', 'eg Al Ahly', 'eg EGY Al Ahly'],
    'Inter Miami CF': ['Inter Miami', 'us Inter Miami', 'us USA Inter Miami' ],
    'Paris Saint-Germain': ['Paris Saint-Germain', 'fr Paris Saint-Germain'],
    'Atletico Madrid': ['Atletico Madrid', 'es Atletico Madrid', 'es ESP Atletico Madrid'],
    'Botafogo': ['Botafogo', 'br Botafogo'],
    'Seattle Sounders': ['Seattle Sounders', 'us Seattle Sounders'],
    'Bayern Munich': ['Bayern Munich', 'de Bayern Munich'],
    'Benfica': ['Benfica', 'pt Benfica'],
    'Boca Juniors': ['Boca Juniors', 'ar Boca Juniors'],
    'Auckland City': ['Auckland City', 'nz Auckland City'],
    'Flamengo': ['Flamengo', 'br Flamengo'],
    'Chelsea FC': ['Chelsea FC', 'en Chelsea FC'],
    'Espérance Sportive de Tunis': ['Espérance Sportive de Tunis', 'tn Espérance Sportive de Tunis'],
    'Los Angeles FC': ['Los Angeles FC', 'us Los Angeles FC'],
    'River Plate': ['River Plate', 'ar River Plate'],
    'Inter Milan': ['Inter Milan', 'it Inter Milan'],
    'CF Monterrey': ['CF Monterrey', 'mx CF Monterrey'],
    'Urawa Red Diamonds': ['Urawa Red Diamonds', 'jp Urawa Red Diamonds'],
    'Fluminense': ['Fluminense', 'br Fluminense'],
    'Borussia Dortmund': ['Borussia Dortmund', 'de Borussia Dortmund'],
    'Ulsan HD FC': ['Ulsan HD FC', 'kr Ulsan HD FC'],
    'Mamelodi Sundowns': ['Mamelodi Sundowns', 'za Mamelodi Sundowns'],
    'Manchester City': ['Manchester City', 'en Manchester City'],
    'Juventus': ['Juventus', 'it Juventus'],
    'Wydad AC': ['Wydad AC', 'ma Wydad AC'],
    'Al Ain FC': ['Al Ain FC', 'ae Al Ain FC'],
    'Real Madrid': ['Real Madrid', 'es Real Madrid'],
    'Al Hilal SFC': ['Al Hilal SFC', 'sa Al Hilal SFC'],
    'Pachuca': ['Pachuca', 'mx Pachuca'],
    'Red Bull Salzburg': ['Red Bull Salzburg', 'at Red Bull Salzburg'],
    'Palmeiras': ['Palmeiras', 'br Palmeiras'],
    # Add more mappings as needed
}

# Load player data
player_df = load_player_data(PLAYER_CSV_FILE_PATH)

# --- Streamy Score Calculation (Randomized Weights Averaged Over Simulations) ---
def compute_team_streamy_score_with_weights(team, player_df, weights):
    """
    Compute a 'Streamy Score' for a team using provided weights (which sum to 1),
    and scale the result to be out of 10.
    """
    def normalize_name(name):
        return str(name).replace(' ', '').lower()
    team_name_norm = normalize_name(team['name'])
    possible_names = [normalize_name(team['name'])]
    if team['name'] in TEAM_COUNTRY_MAP:
        possible_names += [normalize_name(n) for n in TEAM_COUNTRY_MAP[team['name']]]
    def player_team_match(row):
        teams = [normalize_name(t) for t in str(row['Teams']).split(',')]
        return any(n in teams or any(n in t for t in teams) for n in possible_names)
    team_players = player_df[player_df.apply(player_team_match, axis=1)]
    for col in ['Rating', 'Goals', 'Assists', 'Gls', 'Ast']:
        if col in team_players:
            team_players[col] = pd.to_numeric(team_players[col], errors='coerce').fillna(0)
    player_score = team_players['Rating'].mean() if 'Rating' in team_players else 0
    player_goals = (
        team_players['Goals'].sum() if 'Goals' in team_players else
        team_players['Gls'].sum() if 'Gls' in team_players else 0
    )
    player_assists = (
        team_players['Assists'].sum() if 'Assists' in team_players else
        team_players['Ast'].sum() if 'Ast' in team_players else 0
    )
    if team_players.empty:
        pass  # Don't print warnings during 5000x runs
    perf_score = (
        team['points'] * 2 +
        (team['goalsFor'] - team['goalsAgainst']) +
        team['wins'] * 1.5 +
        team['draws'] * 0.5
    )
    # Weighted sum, then scale to 10
    raw_score = (
        weights['sofa'] * team['sofaScoreAverage'] +
        weights['player'] * player_score +
        weights['goals'] * player_goals +
        weights['assists'] * player_assists +
        weights['perf'] * perf_score
    )
    # Scale to 10 (assuming max possible is 10, min is 0)
    return min(max(raw_score, 0), 10)

def compute_team_streamy_score(team, player_df):
    # Fallback: just use SofaScoreAverage or default 7.0
    return team.get('sofaScoreAverage', 7.0) or 7.0

# --- Calculate Streamy Score for each team by averaging over 5000 random weight runs ---
if not player_df.empty:
    print("\nCalculating Streamy Scores for all teams (averaged over random weights)...")
    team_streamy_scores = {team['id']: [] for team in initial_teams_data}
    for _ in tqdm(range(NUM_SIMULATIONS), desc="Streamy Score Weight Runs"):
        # Generate random weights for each stat, sum to 1
        w = [random.random() for _ in range(5)]
        wsum = sum(w)
        weights = {
            'sofa': w[0]/wsum,
            'player': w[1]/wsum,
            'goals': w[2]/wsum,
            'assists': w[3]/wsum,
            'perf': w[4]/wsum
        }
        for team in initial_teams_data:
            score = compute_team_streamy_score_with_weights(team, player_df, weights)
            team_streamy_scores[team['id']].append(score)
    # Average the scores for each team
    for team in initial_teams_data:
        scores = team_streamy_scores[team['id']]
        team['streamyScore'] = sum(scores) / len(scores) if scores else 0
else:
    print("Warning: Player data not loaded. Streamy Scores will not be accurately computed. Using only SofaScoreAverage (or default 7.0 if zero games played) for match prediction.")
    for team in initial_teams_data:
        team['streamyScore'] = compute_team_streamy_score(team, pd.DataFrame())

# --- Match Outcome Prediction ---
def predict_match_outcome(team_a, team_b):
    """
    Predicts the goals for a match based on the teams' 'streamyScore'.
    Adds a random element to simulate game variability.
    """
    # Use the pre-calculated streamyScore as the basis for match prediction
    a_strength = team_a['streamyScore']
    b_strength = team_b['streamyScore']

    # Add randomness to the strength for a single match to simulate variability
    a_effective_strength = a_strength + (random.random() - 0.5) * 1.0 # Smaller random range
    b_effective_strength = b_strength + (random.random() - 0.5) * 1.0

    strength_diff = a_effective_strength - b_effective_strength
    
    home_goals, away_goals = 0, 0

    # Probabilistic goal scoring based on strength difference
    if strength_diff > 1.5:  # Strong favorite home
        home_goals = random.choices([2, 3, 4], weights=[0.4, 0.4, 0.2])[0]
        away_goals = random.choices([0, 1], weights=[0.7, 0.3])[0]
    elif strength_diff < -1.5: # Strong favorite away
        home_goals = random.choices([0, 1], weights=[0.7, 0.3])[0]
        away_goals = random.choices([2, 3, 4], weights=[0.4, 0.4, 0.2])[0]
    elif strength_diff > 0.5: # Moderate favorite home
        home_goals = random.choices([1, 2, 3], weights=[0.4, 0.4, 0.2])[0]
        away_goals = random.choices([0, 1, 2], weights=[0.5, 0.3, 0.2])[0]
    elif strength_diff < -0.5: # Moderate favorite away
        home_goals = random.choices([0, 1, 2], weights=[0.5, 0.3, 0.2])[0]
        away_goals = random.choices([1, 2, 3], weights=[0.4, 0.4, 0.2])[0]
    else: # Evenly matched or slight difference
        home_goals = random.choices([0, 1, 2], weights=[0.3, 0.4, 0.3])[0]
        away_goals = random.choices([0, 1, 2], weights=[0.3, 0.4, 0.3])[0]

    return home_goals, away_goals

# Simulate all matches in the group stage
def simulate_group_stage(matches, teams_dict):
    """
    Simulates all group stage matches and updates team statistics.
    teams_dict is used for efficient lookup.
    """
    for match in matches:
        if not match['played']: # Only simulate unplayed matches
            home_team = teams_dict[match['homeTeamId']]
            away_team = teams_dict[match['awayTeamId']]
            home_goals, away_goals = predict_match_outcome(home_team, away_team)

            # Update match results
            match['homeGoals'] = home_goals
            match['awayGoals'] = away_goals
            match['played'] = True # Mark as played

            # Update team stats
            home_team['matchesPlayed'] += 1
            away_team['matchesPlayed'] += 1
            home_team['goalsFor'] += home_goals
            home_team['goalsAgainst'] += away_goals
            away_team['goalsFor'] += away_goals
            away_team['goalsAgainst'] += home_goals

            if home_goals > away_goals:
                home_team['wins'] += 1
                away_team['losses'] += 1
            elif home_goals < away_goals:
                home_team['losses'] += 1
                away_team['wins'] += 1
            else:
                home_team['draws'] += 1
                away_team['draws'] += 1

            # Update points
            home_team['points'] = home_team['wins'] * 3 + home_team['draws']
            away_team['points'] = away_team['wins'] * 3 + away_team['draws']

def get_group_standings(teams_list):
    """
    Calculates group standings and returns a dictionary of lists.
    Each list contains teams sorted by points, then goal difference, then goals for, then name.
    """
    group_standings = defaultdict(list)
    for team in teams_list:
        group_standings[team['group']].append(team)

    for group_name in group_standings:
        # Sort by points (desc), then goal difference (desc), then goals for (desc), then team name (asc)
        group_standings[group_name].sort(
            key=lambda x: (x['points'], x['goalsFor'] - x['goalsAgainst'], x['goalsFor'], x['name']),
            reverse=True
        )
    return group_standings

def simulate_tournament_group_stage_only(initial_teams_data_copy, all_group_matches_template_copy):
    """
    Simulates only the group stage of the tournament.
    Returns the final standings of all teams after the group stage.
    """
    # Create a dictionary for efficient team lookup during simulation
    teams_dict = {team['id']: team for team in initial_teams_data_copy}

    # Simulate group stage
    simulate_group_stage(all_group_matches_template_copy, teams_dict)
    
    # Return the updated list of teams (their current standings)
    return list(teams_dict.values())

# --- Main Execution ---
if __name__ == "__main__":
    group_winner_counts = defaultdict(int)
    qualified_counts = defaultdict(int) # Counts how many times a team qualified from group stage

    # Store a list of final group standings from each simulation
    all_simulation_group_standings = []
    # For averaging streamy scores
    streamy_score_runs = {team['name']: [] for team in initial_teams_data}
    
    print(f"Running {NUM_SIMULATIONS} Monte Carlo simulations (Group Stage Only)...")

    for sim_num in tqdm(range(NUM_SIMULATIONS), desc="Simulations"):
        # Generate random weights for each stat, sum to 1
        w = [random.random() for _ in range(5)]
        wsum = sum(w)
        weights = {
            'sofa': w[0]/wsum,
            'player': w[1]/wsum,
            'goals': w[2]/wsum,
            'assists': w[3]/wsum,
            'perf': w[4]/wsum
        }
        # Deep copy teams and matches
        teams_for_sim = json.loads(json.dumps(initial_teams_data))
        matches_for_sim = json.loads(json.dumps(all_group_matches_template))

        # Compute streamy score for each team for this run
        for team in teams_for_sim:
            team['streamyScore'] = compute_team_streamy_score_with_weights(team, player_df, weights)
            streamy_score_runs[team['name']].append(team['streamyScore'])

        # Run one tournament simulation (group stage only)
        final_teams_in_sim = simulate_tournament_group_stage_only(teams_for_sim, matches_for_sim)

        # Aggregate group stage qualification and winner data
        sim_group_standings = get_group_standings(final_teams_in_sim)
        all_simulation_group_standings.append(sim_group_standings)

        for group_name, standings in sim_group_standings.items():
            if standings:
                group_winner_counts[standings[0]['name']] += 1
                # Top 2 teams from each group qualify
                for i in range(min(2, len(standings))):
                    qualified_counts[standings[i]['name']] += 1

    # After all runs, set each team's streamyScore to the average
    for team in initial_teams_data:
        scores = streamy_score_runs[team['name']]
        team['streamyScore'] = np.mean(scores) if scores else 0

    print("\n=== Monte Carlo Simulation Results (Group Stage Only) ===")

    # Calculate and print Group Winner Probabilities
    print("\n--- Group Winner Probabilities ---")
    all_groups = sorted(list(set(team['group'] for team in initial_teams_data)))

    for group in all_groups:
        print(f"\nGroup {group}:")
        
        group_specific_winner_counts = defaultdict(int)
        for sim_standings in all_simulation_group_standings:
            if group in sim_standings and sim_standings[group]:
                group_specific_winner_counts[sim_standings[group][0]['name']] += 1

        total_group_wins = sum(group_specific_winner_counts.values())
        if total_group_wins > 0:
            sorted_group_winners = sorted(group_specific_winner_counts.items(), key=lambda item: item[1], reverse=True)
            for team_name, count in sorted_group_winners:
                probability = (count / total_group_wins) * 100
                print(f"  {team_name:<26}: {probability:>6.2f}%")
        else:
            print(f"  No group winners recorded for Group {group}.")


    # Calculate and print Qualification Probabilities (now explicitly labeled as Top 2 Finish Probability)
    print("\n--- Top 2 Finish Probability (Group Stage Qualification) ---")
    if NUM_SIMULATIONS > 0:
        sorted_qualifiers = sorted(qualified_counts.items(), key=lambda item: item[1], reverse=True)
        for team_name, count in sorted_qualifiers:
            probability = (count / NUM_SIMULATIONS) * 100
            print(f"{team_name:<28}: {probability:>6.2f}%")
    else:
        print("No qualifications recorded (NUM_SIMULATIONS is 0).")


    # --- Example Final Table from one simulation ---
    print("\n=== Example Group Stage Results from ONE Simulation ===")
    if all_simulation_group_standings:
        example_standings = all_simulation_group_standings[-1] # Take the last one

        for group in sorted(example_standings.keys()):
            group_teams = example_standings[group]
            
            # Need original data for this part, as streamyScore isn't updated during simulation run.
            original_group_teams_data = [team for team in initial_teams_data if team['group'] == group]
            
            # Ensure these lists are not empty before calculating min/max
            sofa_scores = [t['sofaScoreAverage'] for t in original_group_teams_data]
            streamy_scores = [t['streamyScore'] for t in original_group_teams_data]

            sofa_min = min(sofa_scores) if sofa_scores else 0
            sofa_max = max(sofa_scores) if sofa_scores else 0
            streamy_min = min(streamy_scores) if streamy_scores else 0
            streamy_max = max(streamy_scores) if streamy_scores else 0

            def norm(val, vmin, vmax):
                if vmax == vmin: # Avoid division by zero if all scores are the same
                    return 100.0
                return 100 * (val - vmin) / (vmax - vmin)

            print(f"\nGroup {group}")
            print(f"{'Team':<28} {'Pts':>3} {'W':>2} {'D':>2} {'L':>2} {'GF':>3} {'GA':>3} {'GD':>3} {'Sofa':>5} {'StreamyScore':>12}")
            print("-" * 100)
            for idx, team in enumerate(group_teams):
                original_team_data = next(t for t in initial_teams_data if t['id'] == team['id'])
                sofa_pct = norm(original_team_data['sofaScoreAverage'], sofa_min, sofa_max)
                streamy_pct = norm(original_team_data['streamyScore'], streamy_min, streamy_max)
                
                # Check for qualification based on actual standings
                qualifies_status = 'YES' if idx < 2 else '' # Top 2 qualify

                print(f"{team['name']:<28} {team['points']:>3} {team['wins']:>2} {team['draws']:>2} {team['losses']:>2} {team['goalsFor']:>3} {team['goalsAgainst']:>3} {team['goalsFor']-team['goalsAgainst']:>3} {original_team_data['sofaScoreAverage']:>5.2f} {original_team_data['streamyScore']:>12.2f} {qualifies_status:>7}")

    else:
        print("\nNo simulation results to display an example table.")

