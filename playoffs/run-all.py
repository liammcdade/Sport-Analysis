import random
import numpy as np
from tqdm import tqdm

# --- Team Statistics for all three finals ---
all_teams_stats = {
    # Championship Play-Off Final: Sheffield United vs Sunderland
    "Sheffield United": {"Pld": 46, "GF": 63, "GA": 36, "Pts": 90},
    "Sunderland": {"Pld": 46, "GF": 58, "GA": 44, "Pts": 76},
    
    # League One Play-Off Final: Charlton Athletic vs Leyton Orient
    "Charlton Athletic": {"Pld": 46, "GF": 67, "GA": 43, "Pts": 85},
    "Leyton Orient": {"Pld": 46, "GF": 72, "GA": 48, "Pts": 78},
    
    # League Two Play-Off Final: Walsall vs AFC Wimbledon
    "Walsall": {"Pld": 46, "GF": 75, "GA": 54, "Pts": 77},
    "AFC Wimbledon": {"Pld": 46, "GF": 56, "GA": 35, "Pts": 73}
}

# --- Simulation Parameters ---
runs = 100000  # Number of times to simulate each match

# --- Generic Goal Simulation Function ---
def simulate_goals_for_team(team_avg_gf, opponent_avg_ga):
    """
    Simulates goals scored by a team in a match using a Poisson distribution.
    The expected goals are influenced by the team's average goals for and the opponent's average goals against.
    """
    lambda_val = max(0, (team_avg_gf + opponent_avg_ga) / 2)
    return np.random.poisson(lambda_val)

# --- Function to run a single match simulation and return results ---
def run_match_simulation(team1_name, team2_name, all_stats, num_runs):
    team1_wins = 0
    team2_wins = 0
    draws = 0

    team1_stats = all_stats[team1_name]
    team2_stats = all_stats[team2_name]

    team1_avg_gf = team1_stats["GF"] / team1_stats["Pld"]
    team1_avg_ga = team1_stats["GA"] / team1_stats["Pld"]
    
    team2_avg_gf = team2_stats["GF"] / team2_stats["Pld"]
    team2_avg_ga = team2_stats["GA"] / team2_stats["Pld"]

    for _ in tqdm(range(num_runs), desc=f"Simulating {team1_name} vs {team2_name}"):
        team1_goals = simulate_goals_for_team(team1_avg_gf, team2_avg_ga)
        team2_goals = simulate_goals_for_team(team2_avg_gf, team1_avg_ga)

        if team1_goals > team2_goals:
            team1_wins += 1
        elif team2_goals > team1_goals:
            team2_wins += 1
        else:
            draws += 1
            
    team1_win_percent = (team1_wins / num_runs) * 100
    team2_win_percent = (team2_wins / num_runs) * 100
    draw_percent = (draws / num_runs) * 100
    
    return {
        "team1_name": team1_name,
        "team2_name": team2_name,
        "team1_wins": team1_wins,
        "team2_wins": team2_wins,
        "draws": draws,
        "team1_win_percent": team1_win_percent,
        "team2_win_percent": team2_win_percent,
        "draw_percent": draw_percent,
        "total_runs": num_runs
    }

# --- Main Simulation Execution ---
print("Starting Play-Off Finals Simulations...\n")

# Championship Play-Off Final
championship_results = run_match_simulation(
    "Sheffield United", "Sunderland", all_teams_stats, runs
)

# League One Play-Off Final
league_one_results = run_match_simulation(
    "Charlton Athletic", "Leyton Orient", all_teams_stats, runs
)

# League Two Play-Off Final
league_two_results = run_match_simulation(
    "Walsall", "AFC Wimbledon", all_teams_stats, runs
)

# --- Display All Results ---
print("\n" + "="*80)
print("=== ALL EFL PLAY-OFF FINAL SIMULATION RESULTS (90 MINUTES) ===")
print("="*80 + "\n")

def print_results(results, final_type):
    print(f"--- {final_type} Play-Off Final: {results['team1_name']} vs {results['team2_name']} ---")
    print(f"Total simulations: {results['total_runs']}\n")
    print(f"{results['team1_name']} wins: {results['team1_wins']} ({results['team1_win_percent']:.2f}%)")
    print(f"{results['team2_name']} wins: {results['team2_wins']} ({results['team2_win_percent']:.2f}%)")
    print(f"Draws (after 90 mins): {results['draws']} ({results['draw_percent']:.2f}%)")
    print("\n")

print_results(championship_results, "Championship")
print_results(league_one_results, "League One")
print_results(league_two_results, "League Two")

# --- Summary Report ---
print("\n" + "="*80)
print("=== PLAY-OFF FINALS SIMULATION REPORT ===")
print("="*80)
print(f"Date of Report: Friday, May 23, 2025\n")

print("This report summarizes the results of 100,000 simulations for each of the upcoming EFL Play-Off Finals, based on the teams' full regular season statistics.\n")

# Championship Summary
championship_winner = championship_results['team1_name'] if championship_results['team1_win_percent'] > championship_results['team2_win_percent'] else championship_results['team2_name']
championship_likelihood = max(championship_results['team1_win_percent'], championship_results['team2_win_percent'])
print(f"**Championship Play-Off Final: {championship_results['team1_name']} vs {championship_results['team2_name']}**")
print(f"- Based on stats, {championship_winner} has the highest likelihood of winning in 90 minutes ({championship_likelihood:.2f}%).")
print(f"- There is a {championship_results['draw_percent']:.2f}% chance this high-stakes match will go to extra time.")
print("-" * 40)

# League One Summary
league_one_winner = league_one_results['team1_name'] if league_one_results['team1_win_percent'] > league_one_results['team2_win_percent'] else league_one_results['team2_name']
league_one_likelihood = max(league_one_results['team1_win_percent'], league_one_results['team2_win_percent'])
print(f"**League One Play-Off Final: {league_one_results['team1_name']} vs {league_one_results['team2_name']}**")
print(f"- The simulation suggests {league_one_winner} is more likely to secure victory within 90 minutes ({league_one_likelihood:.2f}%).")
print(f"- A draw after 90 minutes, leading to extra time, occurs in {league_one_results['draw_percent']:.2f}% of simulations.")
print("-" * 40)

# League Two Summary
league_two_winner = league_two_results['team1_name'] if league_two_results['team1_win_percent'] > league_two_results['team2_win_percent'] else league_two_results['team2_name']
league_two_likelihood = max(league_two_results['team1_win_percent'], league_two_results['team2_win_percent'])
print(f"**League Two Play-Off Final: {league_two_results['team1_name']} vs {league_two_results['team2_name']}**")
print(f"- {league_two_winner} shows a statistical edge to win in regulation time ({league_two_likelihood:.2f}%).")
print(f"- There's a {league_two_results['draw_percent']:.2f}% probability of this match proceeding to extra time.")
print("-" * 40)