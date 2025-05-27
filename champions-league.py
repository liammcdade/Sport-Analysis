import random
import numpy as np
from collections import defaultdict
from tqdm import tqdm

# === Simulation Parameters ===
TOTAL_SIMULATIONS = 10000

# === Teams and Data ===
TEAM_A = "Paris Saint-Germain"
TEAM_B = "Inter Milan"

LEAGUE_STATS = {
    TEAM_A: {"Pld": 34, "W": 26, "D": 6, "L": 2, "GF": 92, "GA": 35, "GD": 57, "Pts": 84, "League": "Ligue 1"},
    TEAM_B: {"Pld": 38, "W": 24, "D": 9, "L": 5, "GF": 79, "GA": 35, "GD": 44, "Pts": 81, "League": "Serie A"}
}

LEAGUE_COEFFICIENTS = {
    "Serie A": 97.231,
    "Ligue 1": 72.807
}

CLUB_COEFFICIENTS = {
    TEAM_A: 116.500,
    TEAM_B: 116.250
}

# === Derived Stats ===
TEAM_STRENGTHS = {
    team: {
        "GF_avg": stats["GF"] / stats["Pld"],
        "GA_avg": stats["GA"] / stats["Pld"],
        "League": stats["League"]
    }
    for team, stats in LEAGUE_STATS.items()
}

# === Simulation Functions ===
def simulate_goals_poisson(lambda_val: float) -> int:
    """Simulates goals using a Poisson distribution (lambda min 0.1)."""
    return np.random.poisson(max(0.1, lambda_val))

def calculate_adjusted_strengths_combined(
    team_name: str,
    opponent_name: str,
    strengths: dict,
    league_coeffs: dict,
    club_coeffs: dict,
) -> tuple[float, float]:
    """
    Calculates adjusted GF_avg and GA_avg based on both league and club strength.
    """
    team_league = strengths[team_name]["League"]
    opponent_league = strengths[opponent_name]["League"]

    team_league_coeff = league_coeffs[team_league]
    opponent_league_coeff = league_coeffs[opponent_league]

    team_club_coeff = club_coeffs[team_name]
    opponent_club_coeff = club_coeffs[opponent_name]

    # Adjustment 1: Normalize league strength (sqrt dampening)
    league_influence_gf = (team_league_coeff / opponent_league_coeff) ** 0.5
    league_influence_ga = (opponent_league_coeff / team_league_coeff) ** 0.5

    temp_adjusted_gf = strengths[team_name]["GF_avg"] * league_influence_gf
    temp_adjusted_ga = strengths[team_name]["GA_avg"] * league_influence_ga

    # Adjustment 2: Club coefficient (quarter-root dampening)
    club_strength_ratio = (team_club_coeff / opponent_club_coeff) ** 0.25
    final_adjusted_gf = temp_adjusted_gf * club_strength_ratio
    final_adjusted_ga = temp_adjusted_ga / club_strength_ratio

    return final_adjusted_gf, final_adjusted_ga

def simulate_match(
    team1: str, team2: str, strengths: dict, league_coeffs: dict, club_coeffs: dict
) -> tuple[int, int]:
    """Simulates a single match between two teams."""
    team1_adj_gf, team1_adj_ga = calculate_adjusted_strengths_combined(team1, team2, strengths, league_coeffs, club_coeffs)
    team2_adj_gf, team2_adj_ga = calculate_adjusted_strengths_combined(team2, team1, strengths, league_coeffs, club_coeffs)

    lambda_team1 = (team1_adj_gf + team2_adj_ga) / 2
    lambda_team2 = (team2_adj_gf + team1_adj_ga) / 2

    team1_goals = simulate_goals_poisson(lambda_team1)
    team2_goals = simulate_goals_poisson(lambda_team2)
    return team1_goals, team2_goals

def simulate_champions_league_final(
    team1: str, team2: str, strengths: dict, league_coeffs: dict, club_coeffs: dict
) -> str:
    """
    Simulates a Champions League final, including extra time and penalties if needed.
    Returns the winner as a string.
    """
    t1_goals, t2_goals = simulate_match(team1, team2, strengths, league_coeffs, club_coeffs)

    if t1_goals > t2_goals:
        return team1
    elif t2_goals > t1_goals:
        return team2
    else:
        # Extra Time
        et_multiplier = 0.5
        team1_adj_gf, team1_adj_ga = calculate_adjusted_strengths_combined(team1, team2, strengths, league_coeffs, club_coeffs)
        team2_adj_gf, team2_adj_ga = calculate_adjusted_strengths_combined(team2, team1, strengths, league_coeffs, club_coeffs)

        lambda_team1_et = (team1_adj_gf + team2_adj_ga) / 2 * et_multiplier
        lambda_team2_et = (team2_adj_gf + team1_adj_ga) / 2 * et_multiplier

        et_t1_goals = simulate_goals_poisson(lambda_team1_et)
        et_t2_goals = simulate_goals_poisson(lambda_team2_et)

        total_t1_goals_et = t1_goals + et_t1_goals
        total_t2_goals_et = t2_goals + et_t2_goals

        if total_t1_goals_et > total_t2_goals_et:
            return team1
        elif total_t2_goals_et > total_t1_goals_et:
            return team2
        else:
            # Penalties: 50/50 chance
            return team1 if random.random() < 0.5 else team2

# === Main Execution ===
if __name__ == "__main__":
    win_counts = defaultdict(int)

    print(f"Simulating Champions League Final between {TEAM_A} and {TEAM_B}...")
    print("-" * 60)
    print(f"Using {TEAM_A} stats: Pld={LEAGUE_STATS[TEAM_A]['Pld']}, GF_avg={TEAM_STRENGTHS[TEAM_A]['GF_avg']:.2f}, GA_avg={TEAM_STRENGTHS[TEAM_A]['GA_avg']:.2f}")
    print(f"  League: {TEAM_STRENGTHS[TEAM_A]['League']} (Coeff: {LEAGUE_COEFFICIENTS[TEAM_STRENGTHS[TEAM_A]['League']]}), Club Coeff: {CLUB_COEFFICIENTS[TEAM_A]}")
    print(f"Using {TEAM_B} stats: Pld={LEAGUE_STATS[TEAM_B]['Pld']}, GF_avg={TEAM_STRENGTHS[TEAM_B]['GF_avg']:.2f}, GA_avg={TEAM_STRENGTHS[TEAM_B]['GA_avg']:.2f}")
    print(f"  League: {TEAM_STRENGTHS[TEAM_B]['League']} (Coeff: {LEAGUE_COEFFICIENTS[TEAM_STRENGTHS[TEAM_B]['League']]}), Club Coeff: {CLUB_COEFFICIENTS[TEAM_B]}")
    print("-" * 60)

    print("\n--- Adjusted Strengths for this specific match (example): ---")
    adj_gf_a, adj_ga_a = calculate_adjusted_strengths_combined(TEAM_A, TEAM_B, TEAM_STRENGTHS, LEAGUE_COEFFICIENTS, CLUB_COEFFICIENTS)
    adj_gf_b, adj_ga_b = calculate_adjusted_strengths_combined(TEAM_B, TEAM_A, TEAM_STRENGTHS, LEAGUE_COEFFICIENTS, CLUB_COEFFICIENTS)
    print(f"{TEAM_A} Adjusted GF: {adj_gf_a:.2f}, Adjusted GA: {adj_ga_a:.2f}")
    print(f"{TEAM_B} Adjusted GF: {adj_gf_b:.2f}, Adjusted GA: {adj_ga_b:.2f}")
    print("-----------------------------------------------------------\n")

    for _ in tqdm(range(TOTAL_SIMULATIONS), desc="Simulating Final"):
        winner = simulate_champions_league_final(TEAM_A, TEAM_B, TEAM_STRENGTHS, LEAGUE_COEFFICIENTS, CLUB_COEFFICIENTS)
        win_counts[winner] += 1

    print("\n" + "="*80)
    print("              CHAMPIONS LEAGUE FINAL SIMULATION RESULTS")
    print("   (Adjusted for Domestic League & Club Strength Coefficients - Combined)")
    print("="*80 + "\n")

    print(f"Total simulations: {TOTAL_SIMULATIONS}\n")
    team_a_win_prob = win_counts[TEAM_A] / TOTAL_SIMULATIONS
    team_b_win_prob = win_counts[TEAM_B] / TOTAL_SIMULATIONS

    print(f"{TEAM_A} Win Probability: {team_a_win_prob:.2%}")
    print(f"{TEAM_B} Win Probability: {team_b_win_prob:.2%}")
    print("\nThese probabilities include outcomes from regular time, extra time, and penalties,\nwith adjustments made for the relative strength of their domestic leagues AND their club coefficients.")
    print("\n" + "="*80)
    print("Simulation Complete!")
    print("="*80)