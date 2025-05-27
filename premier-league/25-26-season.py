import numpy as np
from collections import defaultdict
from tqdm import tqdm
import itertools
from multiprocessing import Pool, cpu_count
import random

TEAMS = [
    "Liverpool", "Arsenal", "Manchester City", "Newcastle United", "Chelsea",
    "Aston Villa", "Nottingham Forest", "Brighton & Hove Albion", "Brentford", "Fulham",
    "Bournemouth", "Crystal Palace", "Everton", "Wolverhampton Wanderers", "West Ham United",
    "Manchester United", "Tottenham Hotspur", "Leeds United", "Burnley", "Sunderland"
]

# Example: fill in with real recent performance data (Pld, GF, GA, League)
# Each entry is a list of dicts, most recent season first
TEAM_SEASON_DATA = {
    "Liverpool": [
        {"Pld": 38, "GF": 86, "GA": 41, "League": "Premier League"}, # 2024/25 (User provided)
        {"Pld": 38, "GF": 86, "GA": 41, "League": "Premier League"}, # 2023/24 (User provided)
        {"Pld": 38, "GF": 75, "GA": 47, "League": "Premier League"}, # 2022/23 (User provided)
    ],
    "Arsenal": [
        {"Pld": 38, "GF": 69, "GA": 34, "League": "Premier League"}, # 2024/25 (User provided)
        {"Pld": 38, "GF": 91, "GA": 29, "League": "Premier League"}, # 2023/24 (User provided)
        {"Pld": 38, "GF": 88, "GA": 43, "League": "Premier League"}, # 2022/23 (User provided)
    ],
    "Manchester City": [
        {"Pld": 38, "GF": 72, "GA": 44, "League": "Premier League"}, # 2024/25 (User provided)
        {"Pld": 38, "GF": 96, "GA": 34, "League": "Premier League"}, # 2023/24 (User provided)
        {"Pld": 38, "GF": 94, "GA": 33, "League": "Premier League"}, # 2022/23 (User provided)
    ],
    "Newcastle United": [
        {"Pld": 38, "GF": 68, "GA": 47, "League": "Premier League"}, # 2024/25 (User provided)
        {"Pld": 38, "GF": 85, "GA": 62, "League": "Premier League"}, # 2023/24 (User provided)
        {"Pld": 38, "GF": 68, "GA": 33, "League": "Premier League"}, # 2022/23 (User provided)
    ],
    "Chelsea": [
        {"Pld": 38, "GF": 64, "GA": 43, "League": "Premier League"}, # 2024/25 (User provided)
        {"Pld": 38, "GF": 77, "GA": 63, "League": "Premier League"}, # 2023/24 (User provided)
        {"Pld": 38, "GF": 38, "GA": 47, "League": "Premier League"}, # 2022/23 (User provided)
    ],
    "Aston Villa": [
        {"Pld": 38, "GF": 58, "GA": 51, "League": "Premier League"}, # 2024/25 (User provided)
        {"Pld": 38, "GF": 76, "GA": 61, "League": "Premier League"}, # 2023/24 (User provided)
        {"Pld": 38, "GF": 51, "GA": 46, "League": "Premier League"}, # 2022/23 (User provided)
    ],
    "Nottingham Forest": [
        {"Pld": 38, "GF": 58, "GA": 46, "League": "Premier League"}, # 2024/25 (User provided)
        {"Pld": 38, "GF": 49, "GA": 67, "League": "Premier League"}, # 2023/24 (User provided)
        {"Pld": 38, "GF": 38, "GA": 68, "League": "Premier League"}, # 2022/23 (User provided)
    ],
    "Brighton & Hove Albion": [
        {"Pld": 38, "GF": 66, "GA": 59, "League": "Premier League"}, # 2024/25 (User provided)
        {"Pld": 38, "GF": 55, "GA": 62, "League": "Premier League"}, # 2023/24 (User provided)
        {"Pld": 38, "GF": 72, "GA": 53, "League": "Premier League"}, # 2022/23 (User provided)
    ],
    "Brentford": [
        {"Pld": 38, "GF": 66, "GA": 57, "League": "Premier League"}, # 2024/25 (User provided)
        {"Pld": 38, "GF": 56, "GA": 65, "League": "Premier League"}, # 2023/24 (User provided)
        {"Pld": 38, "GF": 58, "GA": 46, "League": "Premier League"}, # 2022/23 (User provided)
    ],
    "Fulham": [
        {"Pld": 38, "GF": 54, "GA": 54, "League": "Premier League"}, # 2024/25 (User provided)
        {"Pld": 38, "GF": 55, "GA": 61, "League": "Premier League"}, # 2023/24 (User provided)
        {"Pld": 38, "GF": 55, "GA": 53, "League": "Premier League"}, # 2022/23 (User provided)
    ],
    "Bournemouth": [
        {"Pld": 38, "GF": 58, "GA": 46, "League": "Premier League"}, # 2024/25 (User provided)
        {"Pld": 38, "GF": 54, "GA": 67, "League": "Premier League"}, # 2023/24 (User provided)
        {"Pld": 38, "GF": 37, "GA": 71, "League": "Premier League"}, # 2022/23 (User provided)
    ],
    "Crystal Palace": [
        {"Pld": 38, "GF": 51, "GA": 51, "League": "Premier League"}, # 2024/25 (User provided)
        {"Pld": 38, "GF": 57, "GA": 58, "League": "Premier League"}, # 2023/24 (User provided)
        {"Pld": 38, "GF": 40, "GA": 49, "League": "Premier League"}, # 2022/23 (User provided)
    ],
    "Everton": [
        {"Pld": 38, "GF": 42, "GA": 44, "League": "Premier League"}, # 2024/25 (User provided)
        {"Pld": 38, "GF": 40, "GA": 51, "League": "Premier League"}, # 2023/24 (User provided)
        {"Pld": 38, "GF": 34, "GA": 57, "League": "Premier League"}, # 2022/23 (User provided)
    ],
    "Wolverhampton Wanderers": [
        {"Pld": 38, "GF": 54, "GA": 69, "League": "Premier League"}, # 2024/25 (User provided)
        {"Pld": 38, "GF": 50, "GA": 65, "League": "Premier League"}, # 2023/24 (User provided)
        {"Pld": 38, "GF": 31, "GA": 58, "League": "Premier League"}, # 2022/23 (User provided)
    ],
    "West Ham United": [
        {"Pld": 38, "GF": 46, "GA": 62, "League": "Premier League"}, # 2024/25 (User provided)
        {"Pld": 38, "GF": 60, "GA": 74, "League": "Premier League"}, # 2023/24 (User provided)
        {"Pld": 38, "GF": 42, "GA": 55, "League": "Premier League"}, # 2022/23 (User provided)
    ],
    "Manchester United": [
        {"Pld": 38, "GF": 44, "GA": 54, "League": "Premier League"}, # 2024/25 (User provided)
        {"Pld": 38, "GF": 57, "GA": 58, "League": "Premier League"}, # 2023/24 (User provided)
        {"Pld": 38, "GF": 58, "GA": 43, "League": "Premier League"}, # 2022/23 (User provided)
    ],
    "Tottenham Hotspur": [
        {"Pld": 38, "GF": 64, "GA": 65, "League": "Premier League"}, # 2024/25 (User provided)
        {"Pld": 38, "GF": 74, "GA": 61, "League": "Premier League"}, # 2023/24 (User provided)
        {"Pld": 38, "GF": 70, "GA": 63, "League": "Premier League"}, # 2022/23 (User provided)
    ],
    "Leeds United": [
        {"Pld": 46, "GF": 95, "GA": 30, "League": "Championship"},   # 2024/25 (User provided)
        {"Pld": 46, "GF": 81, "GA": 43, "League": "Championship"},   # 2023/24 (User provided)
        {"Pld": 38, "GF": 48, "GA": 78, "League": "Premier League"}, # 2022/23 (User provided, Relegated)
    ],
    "Burnley": [
        {"Pld": 46, "GF": 69, "GA": 16, "League": "Championship"},   # 2024/25 (User provided)
        {"Pld": 38, "GF": 41, "GA": 78, "League": "Premier League"}, # 2023/24 (User provided, Relegated)
        {"Pld": 46, "GF": 87, "GA": 35, "League": "Championship"}, # 2022/23 (User provided, Promoted)
    ],
    "Sunderland": [
        {"Pld": 46, "GF": 58, "GA": 44, "League": "Championship"},   # 2024/25 (User provided)
        {"Pld": 46, "GF": 52, "GA": 54, "League": "Championship"}, # 2023/24 (User provided)
        {"Pld": 46, "GF": 68, "GA": 55, "League": "Championship"}, # 2022/23 (User provided)
    ],
}

LEAGUE_COEFFICIENTS = {
    "Premier League": 1.0,
    "Championship": 0.7,  # Scale as appropriate
    # Add more leagues if needed
}

def generate_weight_sets(num_sets=100, num_seasons=3):
    """
    Generates multiple sets of season weights. Each set sums to 1 and
    weights are sorted in descending order to prioritize more recent seasons.
    """
    weights = []
    for _ in range(num_sets):
        # Generate random numbers for each season, then normalize
        raw_weights = [random.random() for _ in range(num_seasons)]
        total_raw = sum(raw_weights)
        normalized_weights = [w / total_raw for w in raw_weights]
        # Sort in descending order to represent more recent seasons mattering more
        normalized_weights.sort(reverse=True)
        weights.append(normalized_weights)
    return weights

# Generate 10 different sets of weights for the 3 seasons
WEIGHT_SETS = generate_weight_sets(100, 3)

def weighted_avg_stats(team, season_weights):
    """Compute weighted, normalized averages for a team using provided season_weights."""
    seasons = TEAM_SEASON_DATA[team]
    gf, ga = 0.0, 0.0
    total_weight = 0.0
    for i, season in enumerate(seasons):
        # Ensure we don't go out of bounds for season_weights
        if i >= len(season_weights):
            break
        weight = season_weights[i]
        league_coeff = LEAGUE_COEFFICIENTS.get(season["League"], 1.0)
        games = season["Pld"]
        # Avoid division by zero if Pld is 0 (though unlikely with real data)
        if games == 0:
            continue
        gf += weight * (season["GF"] / games) * league_coeff
        ga += weight * (season["GA"] / games) * league_coeff
        total_weight += weight
    # Avoid division by zero if total_weight is 0
    if total_weight == 0:
        return 0.0, 0.0
    return gf / total_weight, ga / total_weight

FIXTURES = []
for team1, team2 in itertools.combinations(TEAMS, 2):
    FIXTURES.append((team1, team2))
    FIXTURES.append((team2, team1))
np.random.shuffle(FIXTURES)

def simulate_score(avg_for, avg_against):
    """
    Simulates a score for a single team in a match using Poisson distribution.
    The average goals for a team are influenced by their attacking strength (avg_for)
    and the opponent's defensive weakness (avg_against).
    """
    # Simple model: average of team's attacking strength and opponent's defensive weakness.
    # Ensure the lambda for Poisson is non-negative and not too small to avoid issues.
    lambda_val = max(0.1, (avg_for + avg_against) / 2)
    return np.random.poisson(lambda_val)

def simulate_season(weight_set_idx):
    """
    Simulates a single football league season using a specific set of weights
    and returns the European qualification, title winners, and final team stats.
    Each fixture is played as a "best of 3" series.
    """
    current_season_weights = WEIGHT_SETS[weight_set_idx]

    team_indices = {team: idx for idx, team in enumerate(TEAMS)}
    n = len(TEAMS)
    # Initialize stats: Pld, W, D, L, GF, GA, Pts, GD
    stats = np.zeros((n, 8), dtype=np.int32)

    # Precompute per-team attack/defense from weighted averages using the current weight set
    gf_avgs = [weighted_avg_stats(team, current_season_weights)[0] for team in TEAMS]
    ga_avgs = [weighted_avg_stats(team, current_season_weights)[1] for team in TEAMS]

    for home, away in FIXTURES:
        i, j = team_indices[home], team_indices[away]

        home_series_wins = 0
        away_series_wins = 0
        series_draws = 0
        total_home_goals_in_series = 0
        total_away_goals_in_series = 0

        # Play 3 individual matches for each fixture
        for _ in range(7):
            home_goals_match = simulate_score(gf_avgs[i], ga_avgs[j])
            away_goals_match = simulate_score(gf_avgs[j], ga_avgs[i])

            total_home_goals_in_series += home_goals_match
            total_away_goals_in_series += away_goals_match

            if home_goals_match > away_goals_match:
                home_series_wins += 1
            elif away_goals_match > home_goals_match:
                away_series_wins += 1
            else:
                series_draws += 1

        # Update played games (each fixture counts as 1 played game in the league table)
        stats[i,0] += 1
        stats[j,0] += 1

        # Update goals for and against based on the aggregated goals from the 3 matches
        stats[i,4] += total_home_goals_in_series
        stats[j,4] += total_away_goals_in_series
        stats[i,5] += total_away_goals_in_series
        stats[j,5] += total_home_goals_in_series

        # Update goal difference based on the aggregated goals from the 3 matches
        stats[i,7] += total_home_goals_in_series - total_away_goals_in_series
        stats[j,7] += total_away_goals_in_series - total_home_goals_in_series

        # Determine the outcome of the "best of 3" series and award points
        if home_series_wins > away_series_wins:
            stats[i,1] += 1; stats[i,6] += 3; stats[j,3] += 1 # Home team wins series
        elif away_series_wins > home_series_wins:
            stats[j,1] += 1; stats[j,6] += 3; stats[i,3] += 1 # Away team wins series
        else:
            stats[i,2] += 1; stats[j,2] += 1; stats[i,6] += 1; stats[j,6] += 1 # Series is a draw

    # Sort the table based on Points, then Goal Difference, then Goals For
    table = sorted(((team, stats[idx]) for team, idx in team_indices.items()),
                   key=lambda x: (x[1][6], x[1][7], x[1][4]), reverse=True)

    # Determine final league positions
    final_league_positions = {team: i+1 for i, (team, _) in enumerate(table)}

    # Determine European qualification spots
    cl, el, ecl = set(), set(), set()
    NUM_CL_LEAGUE_SPOTS = 5 # As per the prompt, assuming 5 CL spots from league position

    # Champions League spots
    for i in range(min(NUM_CL_LEAGUE_SPOTS, len(table))):
        cl.add(table[i][0])

    # Europa League and Europa Conference League spots
    for team, pos in final_league_positions.items():
        if team not in cl and pos == NUM_CL_LEAGUE_SPOTS + 1:
            el.add(team)
        if team not in cl and team not in el and pos == NUM_CL_LEAGUE_SPOTS + 2:
            ecl.add(team)

    all_eur = cl | el | ecl
    title = table[0][0] # The team at the top of the table is the champion

    # Return final stats for each team to calculate average league table
    final_team_stats = {team: stats[team_indices[team]].tolist() for team in TEAMS}
    return cl, el, ecl, all_eur, title, final_team_stats

if __name__ == "__main__":
    RUNS = 10000 # Number of simulations to run
    print(f"Starting simulation of {RUNS} seasons...")

    # Prepare arguments for multiprocessing: cycle through weight set indices
    pool_args = [i % len(WEIGHT_SETS) for i in range(RUNS)]

    # Use multiprocessing Pool to run simulations in parallel
    with Pool(cpu_count()) as pool:
        results = list(tqdm(pool.imap_unordered(simulate_season, pool_args), total=RUNS, desc="Simulating Seasons"))

    # Initialize dictionaries to store qualification counts and summed stats for average table
    qual_counts = {team: {"CL":0,"EL":0,"ECL":0,"Overall":0,"Title":0} for team in TEAMS}
    total_cl = total_el = total_ecl = 0
    # Summed stats for average league table: Pld, W, D, L, GF, GA, Pts, GD
    summed_team_stats = defaultdict(lambda: np.zeros(8, dtype=np.float64))

    # Aggregate results from all simulations
    for cl, el, ecl, all_eur, title, final_team_stats in results:
        for t in cl: qual_counts[t]["CL"] += 1
        for t in el: qual_counts[t]["EL"] += 1
        for t in ecl: qual_counts[t]["ECL"] += 1
        for t in all_eur: qual_counts[t]["Overall"] += 1
        qual_counts[title]["Title"] += 1
        total_cl += len(cl)
        total_el += len(el)
        total_ecl += len(ecl)

        for team, stats_list in final_team_stats.items():
            summed_team_stats[team] += np.array(stats_list)

    # Calculate average European slots assigned
    avg_cl = total_cl / RUNS
    avg_el = total_el / RUNS
    avg_ecl = total_ecl / RUNS
    avg_total = avg_cl + avg_el + avg_ecl

    print("\n--- Average European Slots Assigned Per Season ---")
    print(f"Average Champions League (CL) slots: {avg_cl:.2f}")
    print(f"Average Europa League (EL) slots: {avg_el:.2f}")
    print(f"Average Europa Conference League (ECL) slots: {avg_ecl:.2f}")
    print(f"Average Total European slots: {avg_total:.2f}\n" + "-"*60)

    print(f"\nQualification chances over {RUNS} simulations (weighted, last 3 seasons):")
    # Print header for the results table
    print(f"{'Team':20} | {'CL':<7} | {'EL':<7} | {'ECL':<7} | {'Overall':<9} | {'Title':<7}")
    print("-"*80)

    # Sort teams for display: by overall European chance, then CL, EL, ECL, then Title
    sorted_teams_qual = sorted(TEAMS, key=lambda t: (
        -qual_counts[t]["Overall"],
        -qual_counts[t]["CL"],
        -qual_counts[t]["EL"],
        -qual_counts[t]["ECL"],
        -qual_counts[t]["Title"]
    ))

    # Print results for each team
    for team in sorted_teams_qual:
        c = qual_counts[team]
        print(f"{team:20} | {c['CL']/RUNS:.2%} | {c['EL']/RUNS:.2%} | {c['ECL']/RUNS:.2%} | {c['Overall']/RUNS:.2%} | {c['Title']/RUNS:.2%}")

    # --- Predicted League Table ---
    print("\n--- Predicted League Table (Average over all simulations) ---")
    print(f"{'Pos':<4} | {'Team':20} | {'Pld':<4} | {'W':<4} | {'D':<4} | {'L':<4} | {'GF':<4} | {'GA':<4} | {'GD':<4} | {'Pts':<4}")
    print("-" * 90)

    # Calculate average stats for each team
    avg_team_stats = {}
    for team, stats_arr in summed_team_stats.items():
        avg_team_stats[team] = (stats_arr / RUNS).astype(int) # Convert to int for display

    # Sort teams for the predicted league table
    # Sort by average points, then average GD, then average GF
    predicted_table = sorted(avg_team_stats.items(),
                             key=lambda x: (x[1][6], x[1][7], x[1][4]), # Pts, GD, GF
                             reverse=True)

    for i, (team, stats_arr) in enumerate(predicted_table):
        pld, w, d, l, gf, ga, pts, gd = stats_arr
        print(f"{i+1:<4} | {team:20} | {pld:<4} | {w:<4} | {d:<4} | {l:<4} | {gf:<4} | {ga:<4} | {gd:<4} | {pts:<4}")
