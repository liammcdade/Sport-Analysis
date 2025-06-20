from fractions import Fraction

# --- ODDS-BASED MATCH WINNER PREDICTION ---
# Example odds dictionary: (You can fill in real odds here)
odds_dict = {
    # (home, away): (home_win_odds, draw_odds, away_win_odds)
    ("Liverpool", "Bournemouth"): (
        [
            "19/50",
            "2/5",
            "27/100",
            "2/5",
            "2/5",
            "2/5",
            "4/11",
            "27/100",
            "4/11",
            "31/100",
            "4/11",
            "2/5",
            "2/5",
            "1/3",
            "1/3",
            "1/4",
        ],
        [
            "17/4",
            "19/5",
            "17/4",
            "4/1",
            "19/5",
            "17/4",
            "4/1",
            "17/4",
            "15/4",
            "23/5",
            "4/1",
            "4/1",
            "17/4",
            "4/1",
            "4/1",
            "3/1",
        ],
        [
            "6/1",
            "11/2",
            "8/1",
            "13/2",
            "11/2",
            "6/1",
            "6/1",
            "8/1",
            "11/2",
            "7/1",
            "6/1",
            "5/1",
            "6/1",
            "13/2",
            "7/1",
            "647/100",
        ],
    ),
    ("Aston Villa", "Newcastle"): (
        [
            "29/20",
            "7/5",
            "29/20",
            "6/4",
            "7/5",
            "29/20",
            "7/5",
            "29/20",
            "7/5",
            "29/20",
            "7/5",
            "7/5",
            "29/20",
            "6/4",
            "6/4",
            "6/5",
        ],
        [
            "5/2",
            "5/2",
            "9/4",
            "13/5",
            "5/2",
            "13/5",
            "13/5",
            "9/4",
            "12/5",
            "49/20",
            "12/5",
            "5/2",
            "13/5",
            "5/2",
            "5/2",
            "2/1",
        ],
        [
            "17/10",
            "13/8",
            "17/10",
            "7/4",
            "13/8",
            "13/8",
            "13/8",
            "17/10",
            "17/10",
            "168/100",
            "8/5",
            "13/8",
            "13/8",
            "13/8",
            "13/8",
            "7/5",
        ],
    ),
    ("Brighton", "Fulham"): (
        [
            "10/11",
            "5/6",
            "17/20",
            "9/10",
            "5/6",
            "17/20",
            "17/20",
            "17/20",
            "4/5",
            "88/100",
            "5/6",
            "17/20",
            "17/20",
            "17/20",
            "17/20",
            "8/11",
        ],
        [
            "12/5",
            "13/5",
            "47/20",
            "13/5",
            "13/5",
            "13/5",
            "13/5",
            "13/5",
            "13/5",
            "11/4",
            "21/10",
            "13/5",
            "13/5",
            "13/5",
            "13/5",
            "11/4",
        ],
        [
            "3/1",
            "3/1",
            "29/10",
            "3/1",
            "3/1",
            "3/1",
            "14/5",
            "29/10",
            "3/1",
            "29/10",
            "14/5",
            "14/5",
            "3/1",
            "29/10",
            "14/5",
            "23/10",
        ],
    ),
    ("Nottm Forest", "Brentford"): (
        ["2/1", "21/10"],
        ["9/4", "12/5"],
        ["13/10", "6/5"],
    ),
    ("Sunderland", "West Ham"): (
        [
            "9/4",
            "21/10",
            "11/5",
            "21/10",
            "21/10",
            "21/10",
            "2/1",
            "11/5",
            "11/5",
            "11/5",
            "21/10",
            "21/10",
            "11/5",
            "21/10",
            "21/10",
            "9/5",
        ],
        [
            "23/10",
            "23/10",
            "9/4",
            "12/5",
            "23/10",
            "12/5",
            "5/2",
            "9/4",
            "23/10",
            "23/10",
            "9/4",
            "23/10",
            "12/5",
            "23/10",
            "23/10",
            "15/8",
        ],
        [
            "6/5",
            "6/5",
            "23/20",
            "13/10",
            "6/5",
            "6/5",
            "6/5",
            "23/20",
            "6/5",
            "6/5",
            "23/20",
            "6/5",
            "5/4",
            "5/4",
            "5/4",
            "20/21",
        ],
    ),
    ("Tottenham", "Burnley"): (["8/13", "4/7"], ["3/1", "10/3"], ["9/2", "5/1"]),
    ("Wolves", "Man City"): (["6/1", "13/2"], ["7/2", "4/1"], ["2/5", "1/3"]),
    ("Chelsea", "Crystal Palace"): (["8/11", "4/5"], ["11/4", "5/2"], ["7/2", "4/1"]),
    ("Man Utd", "Arsenal"): (["7/4", "15/8"], ["12/5", "5/2"], ["6/4", "13/8"]),
    ("Leeds", "Everton"): (["11/8", "6/5"], ["9/4", "5/2"], ["2/1", "21/10"]),
}


def fractional_to_decimal(odds):
    """Convert fractional odds (as string or Fraction) to decimal odds."""
    if isinstance(odds, str):
        odds = Fraction(odds)
    return float(odds) + 1


def fractional_list_to_decimal_avg(odds_list):
    """Convert a list of fractional odds (strings or Fractions) to the average decimal odds."""
    if not isinstance(odds_list, (list, tuple)):
        odds_list = [odds_list]
    decimals = [float(Fraction(od)) + 1 for od in odds_list]
    return sum(decimals) / len(decimals)


def implied_probability(decimal_odds):
    """Convert decimal odds to implied probability (as a float between 0 and 1)."""
    return 1 / decimal_odds if decimal_odds > 0 else 0


def predict_winner_with_fractional_odds_avg(home, away, odds_dict):
    key = (home, away)
    if key not in odds_dict:
        return "NO ODDS AVAILABLE"
    home_odds, draw_odds, away_odds = odds_dict[key]
    home_dec = fractional_list_to_decimal_avg(home_odds)
    draw_dec = fractional_list_to_decimal_avg(draw_odds)
    away_dec = fractional_list_to_decimal_avg(away_odds)
    min_odds = min(home_dec, draw_dec, away_dec)
    if min_odds == home_dec:
        return home
    elif min_odds == away_dec:
        return away
    else:
        return "DRAW"


def predict_winner_with_fractional_odds_avg_and_probs(home, away, odds_dict):
    key = (home, away)
    if key not in odds_dict:
        return ("NO ODDS AVAILABLE", 0, 0, 0)
    home_odds, draw_odds, away_odds = odds_dict[key]
    home_dec = fractional_list_to_decimal_avg(home_odds)
    draw_dec = fractional_list_to_decimal_avg(draw_odds)
    away_dec = fractional_list_to_decimal_avg(away_odds)
    home_prob = implied_probability(home_dec)
    draw_prob = implied_probability(draw_dec)
    away_prob = implied_probability(away_dec)
    # Normalize to sum to 1 for display
    total = home_prob + draw_prob + away_prob
    if total > 0:
        home_prob /= total
        draw_prob /= total
        away_prob /= total
    # If all probabilities are within 0.12 (12%) of each other, classify as draw
    probs = [home_prob, draw_prob, away_prob]
    if max(probs) - min(probs) <= 0.12:
        return ("DRAW", home_prob, draw_prob, away_prob)
    probs_named = [(home, home_prob), ("DRAW", draw_prob), (away, away_prob)]
    probs_named.sort(key=lambda x: x[1], reverse=True)
    winner, win_prob = probs_named[0]
    return winner, home_prob, draw_prob, away_prob


def print_odds_predictions(fixtures, odds_dict):
    print("\n--- ODDS-BASED MATCH WINNER PREDICTIONS (Averaged Fractional Odds) ---")
    for home, away in fixtures:
        winner = predict_winner_with_fractional_odds_avg(home, away, odds_dict)
        print(f"{home} vs {away}: {winner}")
    print()


def print_odds_predictions_table(fixtures, odds_dict):
    print(
        "\n--- ODDS-BASED MATCH WINNER PREDICTIONS (Averaged Fractional Odds, with % Table) ---"
    )
    header = f"{'Fixture':35} | {'Home %':>7} | {'Draw %':>7} | {'Away %':>7} | {'Predicted':>12}"
    print(header)
    print("-" * len(header))
    for home, away in fixtures:
        winner, home_prob, draw_prob, away_prob = (
            predict_winner_with_fractional_odds_avg_and_probs(home, away, odds_dict)
        )
        print(
            f"{home} vs {away:20} | {home_prob*100:7.2f} | {draw_prob*100:7.2f} | {away_prob*100:7.2f} | {winner:12}"
        )
    print()


def generate_league_table_from_predictions(fixtures, odds_dict, teams):
    # Initialize league table
    table = {team: {"MP": 0, "W": 0, "D": 0, "L": 0, "Pts": 0} for team in teams}
    for home, away in fixtures:
        winner, home_prob, draw_prob, away_prob = (
            predict_winner_with_fractional_odds_avg_and_probs(home, away, odds_dict)
        )
        table[home]["MP"] += 1
        table[away]["MP"] += 1
        if winner == home:
            table[home]["W"] += 1
            table[home]["Pts"] += 3
            table[away]["L"] += 1
        elif winner == away:
            table[away]["W"] += 1
            table[away]["Pts"] += 3
            table[home]["L"] += 1
        elif winner == "DRAW":
            table[home]["D"] += 1
            table[away]["D"] += 1
            table[home]["Pts"] += 1
            table[away]["Pts"] += 1
    # Convert to sorted list
    table_rows = [
        (team, stats["MP"], stats["W"], stats["D"], stats["L"], stats["Pts"])
        for team, stats in table.items()
    ]
    table_rows.sort(key=lambda x: (x[5], x[2], -x[3]), reverse=True)
    return table_rows


def print_league_table(table_rows):
    print("\n--- Predicted League Table (Based on Odds Predictions) ---")
    header = f"{'Rk':>2} {'Team':20} {'MP':>3} {'W':>3} {'D':>3} {'L':>3} {'Pts':>4}"
    print(header)
    print("-" * len(header))
    for idx, row in enumerate(table_rows, 1):
        team, mp, w, d, l, pts = row
        print(f"{idx:2} {team:20} {mp:3} {w:3} {d:3} {l:3} {pts:4}")
    print()


def generate_league_table_with_xg(fixtures, odds_dict, teams):
    # Initialize league table
    table = {
        team: {"MP": 0, "W": 0, "D": 0, "L": 0, "Pts": 0, "xGF": 0.0, "xGA": 0.0}
        for team in teams
    }
    for home, away in fixtures:
        winner, home_prob, draw_prob, away_prob = (
            predict_winner_with_fractional_odds_avg_and_probs(home, away, odds_dict)
        )
        # xG: Use implied probabilities as a proxy for expected goals (higher prob = more likely to score)
        # Home xGF: 2.0 * home_prob + 1.0 * draw_prob
        # Away xGF: 2.0 * away_prob + 1.0 * draw_prob
        # (You can adjust these weights for realism)
        home_xg = 2.0 * home_prob + 1.0 * draw_prob
        away_xg = 2.0 * away_prob + 1.0 * draw_prob
        table[home]["MP"] += 1
        table[away]["MP"] += 1
        table[home]["xGF"] += home_xg
        table[home]["xGA"] += away_xg
        table[away]["xGF"] += away_xg
        table[away]["xGA"] += home_xg
        if winner == home:
            table[home]["W"] += 1
            table[home]["Pts"] += 3
            table[away]["L"] += 1
        elif winner == away:
            table[away]["W"] += 1
            table[away]["Pts"] += 3
            table[home]["L"] += 1
        elif winner == "DRAW":
            table[home]["D"] += 1
            table[away]["D"] += 1
            table[home]["Pts"] += 1
            table[away]["Pts"] += 1
    # Convert to sorted list by xGD (xGF - xGA), then points, then wins
    table_rows = [
        (
            team,
            stats["MP"],
            stats["W"],
            stats["D"],
            stats["L"],
            stats["Pts"],
            stats["xGF"],
            stats["xGA"],
            stats["xGF"] - stats["xGA"],
        )
        for team, stats in table.items()
    ]
    table_rows.sort(key=lambda x: (x[8], x[5], x[2]), reverse=True)
    return table_rows


def print_league_table_with_xg(table_rows):
    print("\n--- Predicted League Table (Based on Odds, xGF-xGA Order) ---")
    header = f"{'Rk':>2} {'Team':20} {'MP':>3} {'W':>3} {'D':>3} {'L':>3} {'Pts':>4} {'xGF':>6} {'xGA':>6} {'xGD':>6}"
    print(header)
    print("-" * len(header))
    for idx, row in enumerate(table_rows, 1):
        team, mp, w, d, l, pts, xgf, xga, xgd = row
        print(
            f"{idx:2} {team:20} {mp:3} {w:3} {d:3} {l:3} {pts:4} {xgf:6.2f} {xga:6.2f} {xgd:6.2f}"
        )
    print()


def calculate_league_win_probabilities(fixtures, odds_dict, teams):
    # For each team, count how many times they are predicted to win a match
    win_counts = {team: 0 for team in teams}
    total_matches = {team: 0 for team in teams}
    for home, away in fixtures:
        winner, home_prob, draw_prob, away_prob = (
            predict_winner_with_fractional_odds_avg_and_probs(home, away, odds_dict)
        )
        if winner == home:
            win_counts[home] += 1
        elif winner == away:
            win_counts[away] += 1
        # Count matches played
        total_matches[home] += 1
        total_matches[away] += 1
    # League win chance: proportion of matches predicted as wins for each team
    win_probs = {
        team: (win_counts[team] / total_matches[team] if total_matches[team] > 0 else 0)
        for team in teams
    }
    return win_probs


def print_league_table_points_with_win_prob(table_rows, win_probs):
    print("\n--- Predicted League Table (Points Order, with Avg Win % per Team) ---")
    header = f"{'Rk':>2} {'Team':20} {'MP':>3} {'W':>3} {'D':>3} {'L':>3} {'Pts':>4} {'xGF':>6} {'xGA':>6} {'xGD':>6} {'Win%':>7}"
    print(header)
    print("-" * len(header))
    # Sort by points, then xGD, then wins
    table_rows_sorted = sorted(
        table_rows, key=lambda x: (x[5], x[8], x[2]), reverse=True
    )
    for idx, row in enumerate(table_rows_sorted, 1):
        team, mp, w, d, l, pts, xgf, xga, xgd = row
        win_pct = win_probs.get(team, 0) * 100
        print(
            f"{idx:2} {team:20} {mp:3} {w:3} {d:3} {l:3} {pts:4} {xgf:6.2f} {xga:6.2f} {xgd:6.2f} {win_pct:7.2f}"
        )
    print()


def print_league_table_points_gd_winprob(table_rows, win_probs):
    print("\n--- Predicted League Table (Points, GD, Win%, Draw%, Loss%) ---")
    header = f"{'Rk':>2} {'Team':20} {'MP':>3} {'W':>3} {'D':>3} {'L':>3} {'Pts':>4} {'xGF':>6} {'xGA':>6} {'xGD':>6} {'Win%':>7} {'Draw%':>7} {'Loss%':>7}"
    print(header)
    print("-" * len(header))
    # Sort by points, then xGD, then win probability
    table_rows_sorted = sorted(
        table_rows, key=lambda x: (x[5], x[8], win_probs.get(x[0], 0)), reverse=True
    )
    for idx, row in enumerate(table_rows_sorted, 1):
        team, mp, w, d, l, pts, xgf, xga, xgd = row
        win_pct = (w / mp * 100) if mp else 0
        draw_pct = (d / mp * 100) if mp else 0
        loss_pct = (l / mp * 100) if mp else 0
        print(
            f"{idx:2} {team:20} {mp:3} {w:3} {d:3} {l:3} {pts:4} {xgf:6.2f} {xga:6.2f} {xgd:6.2f} {win_pct:7.2f} {draw_pct:7.2f} {loss_pct:7.2f}"
        )
    print()


def get_fixture_result(home, away, odds_dict):
    """Accepts either odds or a final score for each fixture."""
    key = (home, away)
    value = odds_dict.get(key)
    if value is None:
        return None, None, None, None  # No data
    # If value is a tuple of two ints or strings that can be cast to int, treat as score
    if isinstance(value, (list, tuple)) and len(value) == 2:
        try:
            score_home = int(value[0])
            score_away = int(value[1])
            if score_home > score_away:
                return home, 1.0, 0.0, 0.0  # Home win
            elif score_away > score_home:
                return away, 0.0, 0.0, 1.0  # Away win
            else:
                return "DRAW", 0.0, 1.0, 0.0  # Draw
        except Exception:
            pass  # Not a score, fall through to odds
    # Otherwise, treat as odds
    return predict_winner_with_fractional_odds_avg_and_probs(home, away, odds_dict)


def generate_league_table_with_xg_flexible(fixtures, odds_dict, teams):
    table = {
        team: {"MP": 0, "W": 0, "D": 0, "L": 0, "Pts": 0, "xGF": 0.0, "xGA": 0.0}
        for team in teams
    }
    for home, away in fixtures:
        winner, home_prob, draw_prob, away_prob = get_fixture_result(
            home, away, odds_dict
        )
        if winner is None:
            continue  # Skip if no data
        # xG: Use implied probabilities as a proxy for expected goals (or 1 for actual win, 0.5 for draw)
        if home_prob + draw_prob + away_prob == 1.0 and (
            home_prob in [1.0, 0.0] or away_prob in [1.0, 0.0]
        ):
            # This was a real score, so use 2 for win, 1 for draw
            home_xg = 2.0 * home_prob + 1.0 * draw_prob
            away_xg = 2.0 * away_prob + 1.0 * draw_prob
        else:
            home_xg = 2.0 * home_prob + 1.0 * draw_prob
            away_xg = 2.0 * away_prob + 1.0 * draw_prob
        table[home]["MP"] += 1
        table[away]["MP"] += 1
        table[home]["xGF"] += home_xg
        table[home]["xGA"] += away_xg
        table[away]["xGF"] += away_xg
        table[away]["xGA"] += home_xg
        if winner == home:
            table[home]["W"] += 1
            table[home]["Pts"] += 3
            table[away]["L"] += 1
        elif winner == away:
            table[away]["W"] += 1
            table[away]["Pts"] += 3
            table[home]["L"] += 1
        elif winner == "DRAW":
            table[home]["D"] += 1
            table[away]["D"] += 1
            table[home]["Pts"] += 1
            table[away]["Pts"] += 1
    table_rows = [
        (
            team,
            stats["MP"],
            stats["W"],
            stats["D"],
            stats["L"],
            stats["Pts"],
            stats["xGF"],
            stats["xGA"],
            stats["xGF"] - stats["xGA"],
        )
        for team, stats in table.items()
    ]
    table_rows.sort(key=lambda x: (x[5], x[8], x[2]), reverse=True)
    return table_rows


def main():
    # Week 1 fixtures
    fixtures_to_predict = [
        ("Liverpool", "Bournemouth"),
        ("Aston Villa", "Newcastle"),
        ("Brighton", "Fulham"),
        ("Nottm Forest", "Brentford"),
        ("Sunderland", "West Ham"),
        ("Tottenham", "Burnley"),
        ("Wolves", "Man City"),
        ("Chelsea", "Crystal Palace"),
        ("Man Utd", "Arsenal"),
        ("Leeds", "Everton"),
    ]
    print_odds_predictions(fixtures_to_predict, odds_dict)
    print_odds_predictions_table(fixtures_to_predict, odds_dict)

    # List all teams in week 1 fixtures
    teams = set()
    for home, away in fixtures_to_predict:
        teams.add(home)
        teams.add(away)
    teams = sorted(teams)
    # Generate and print league table
#     league_table = generate_league_table_from_predictions(
        fixtures_to_predict, odds_dict, teams
    )

    # Generate and print league table with xGF/xGA
    league_table_xg = generate_league_table_with_xg(
        fixtures_to_predict, odds_dict, teams
    )

    # Generate and print league table with xGF/xGA/xGD ordering
    league_table_xg = generate_league_table_with_xg(
        fixtures_to_predict, odds_dict, teams
    )

    # Print league table in order of points, then in order of xGD
    win_probs = calculate_league_win_probabilities(
        fixtures_to_predict, odds_dict, teams
    )

    # Print only one league table: points, then xGD, then win probability
    print_league_table_points_gd_winprob(league_table_xg, win_probs)


if __name__ == "__main__":
    main()
