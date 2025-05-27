import random
import numpy as np
from collections import defaultdict
from tqdm import tqdm

# Define the two teams for the Champions League Final
team_a = "Paris Saint-Germain"
team_b = "Inter Milan"
finalists = [team_a, team_b]

# Provided domestic league standings (assumed for a recent past season)
league_stats = {
    team_a: {"Pld": 34, "W": 26, "D": 6, "L": 2, "GF": 92, "GA": 35, "GD": 57, "Pts": 84, "League": "Ligue 1"},
    team_b: {"Pld": 38, "W": 24, "D": 9, "L": 5, "GF": 79, "GA": 35, "GD": 44, "Pts": 81, "League": "Serie A"}
}

# UEFA 5-Year League Coefficients (current as of May 2025, higher is stronger)
league_coefficients = {
    "Serie A": 97.231, # Italy
    "Ligue 1": 72.807  # France
}

# UEFA Club Coefficients (current as of May 2025, higher is stronger)
club_coefficients = {
    team_a: 116.500, # Paris Saint-Germain
    team_b: 116.250  # Inter Milan
}

# Calculate base average goals for and against from provided league stats
team_strengths = {}
for team, stats in league_stats.items():
    team_strengths[team] = {
        "GF_avg": stats["GF"] / stats["Pld"],
        "GA_avg": stats["GA"] / stats["Pld"],
        "League": stats["League"]
    }

# Counters for simulation results
win_counts = defaultdict(int)
total_simulations = 10000

def simulate_goals_poisson(lambda_val):
    """
    Simulates goals using a Poisson distribution.
    Ensures lambda is never too low to avoid issues.
    """
    return np.random.poisson(max(0.1, lambda_val))

def calculate_adjusted_strengths_combined(team_name, opponent_name, strengths, league_coeffs, club_coeffs):
    """
    Calculates adjusted GF_avg and GA_avg based on both league and club strength.
    """
    team_league = strengths[team_name]["League"]
    opponent_league = strengths[opponent_name]["League"]

    team_league_coeff = league_coeffs[team_league]
    opponent_league_coeff = league_coeffs[opponent_league]

    team_club_coeff = club_coeffs[team_name]
    opponent_club_coeff = club_coeffs[opponent_name]

    # Max league coeff for normalization (prevents over-boosting if one league is very dominant)
    max_overall_league_coeff = max(league_coeffs.values())

    # --- Adjustment 1: Normalize domestic stats by own league strength relative to highest league ---
    # If a team's league is weaker, its GF_avg is slightly reduced, GA_avg slightly increased.
    # Weaker league --> raw GF might be inflated, GA might be deflated.
    # Stronger league --> raw GF might be deflated, GA might be inflated.
    
    # Example: If Ligue 1 (72) vs Serie A (97), PSG's GF will be reduced (72/97 < 1), GA increased (97/72 > 1)
    # Inter's GF will be slightly increased (97/72 > 1), GA slightly reduced (72/97 < 1)
    
    # We use sqrt (power 0.5) to dampen the effect of the ratio.
    league_influence_gf = (team_league_coeff / opponent_league_coeff)**0.5 # For own attack
    league_influence_ga = (opponent_league_coeff / team_league_coeff)**0.5 # For own defense

    temp_adjusted_gf = strengths[team_name]["GF_avg"] * league_influence_gf
    temp_adjusted_ga = strengths[team_name]["GA_avg"] * league_influence_ga

    # --- Adjustment 2: Direct European strength comparison via Club Coefficients ---
    # This directly biases the outcome based on a team's proven European pedigree.
    # Higher club coeff means stronger overall, affecting both offense and defense.
    
    # We use a power of 0.25 for club coefficient impact, as it's a direct strength metric
    # applied to the *already* league-adjusted domestic stats.
    club_strength_ratio = (team_club_coeff / opponent_club_coeff)**0.25

    # Final adjusted values
    final_adjusted_gf = temp_adjusted_gf * club_strength_ratio
    final_adjusted_ga = temp_adjusted_ga / club_strength_ratio # Divide for defense, meaning lower GA if stronger

    return final_adjusted_gf, final_adjusted_ga

def simulate_match(team1, team2, strengths, league_coeffs, club_coeffs):
    """
    Simulates a single match between two teams, adjusting for both league and club strength.
    Returns (team1_goals, team2_goals).
    """
    # Calculate adjusted strengths for each team when playing the other
    team1_adj_gf, team1_adj_ga = calculate_adjusted_strengths_combined(team1, team2, strengths, league_coeffs, club_coeffs)
    team2_adj_gf, team2_adj_ga = calculate_adjusted_strengths_combined(team2, team1, strengths, league_coeffs, club_coeffs)

    # Calculate lambda for Poisson distribution for each team
    # This combines the attacking team's adjusted offense with the defending team's adjusted defense
    lambda_team1 = (team1_adj_gf + team2_adj_ga) / 2
    lambda_team2 = (team2_adj_gf + team1_adj_ga) / 2

    team1_goals = simulate_goals_poisson(lambda_team1)
    team2_goals = simulate_goals_poisson(lambda_team2)
    
    return team1_goals, team2_goals

def simulate_champions_league_final(team1, team2, strengths, league_coeffs, club_coeffs):
    """
    Simulates a Champions League final, including extra time and penalties if needed.
    Returns the winner of the final.
    """
    # Simulate regular time
    t1_goals, t2_goals = simulate_match(team1, team2, strengths, league_coeffs, club_coeffs)

    if t1_goals > t2_goals:
        return team1
    elif t2_goals > t1_goals:
        return team2
    else: # Draw in regular time, go to Extra Time
        # Simulate Extra Time (goals are typically lower due to fatigue/caution)
        et_multiplier = 0.5 # Represents reduction factor for goals in ET (e.g., 50% of regular goals per 30 mins)

        # Recalculate adjusted strengths for ET, applying the fatigue multiplier
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
        else: # Still a draw after Extra Time, go to Penalties
            # Penalties: Simulating a penalty shootout, assuming a 50/50 chance for now
            if random.random() < 0.5:
                return team1
            else:
                return team2


print(f"Simulating Champions League Final between {team_a} and {team_b}...")
print("-" * 60)
print(f"Using {team_a} stats: Pld={league_stats[team_a]['Pld']}, GF_avg={team_strengths[team_a]['GF_avg']:.2f}, GA_avg={team_strengths[team_a]['GA_avg']:.2f}")
print(f"  League: {team_strengths[team_a]['League']} (Coeff: {league_coefficients[team_strengths[team_a]['League']]}), Club Coeff: {club_coefficients[team_a]}")
print(f"Using {team_b} stats: Pld={league_stats[team_b]['Pld']}, GF_avg={team_strengths[team_b]['GF_avg']:.2f}, GA_avg={team_strengths[team_b]['GA_avg']:.2f}")
print(f"  League: {team_strengths[team_b]['League']} (Coeff: {league_coefficients[team_strengths[team_b]['League']]}), Club Coeff: {club_coefficients[team_b]}")
print("-" * 60)

# Show adjusted strengths for transparency before simulation
print("\n--- Adjusted Strengths for this specific match (example): ---")
psg_adj_gf, psg_adj_ga = calculate_adjusted_strengths_combined(team_a, team_b, team_strengths, league_coefficients, club_coefficients)
inter_adj_gf, inter_adj_ga = calculate_adjusted_strengths_combined(team_b, team_a, team_strengths, league_coefficients, club_coefficients)
print(f"{team_a} Adjusted GF: {psg_adj_gf:.2f}, Adjusted GA: {psg_adj_ga:.2f}")
print(f"{team_b} Adjusted GF: {inter_adj_gf:.2f}, Adjusted GA: {inter_adj_ga:.2f}")
print("-----------------------------------------------------------\n")


for _ in tqdm(range(total_simulations), desc="Simulating Final"):
    winner = simulate_champions_league_final(team_a, team_b, team_strengths, league_coefficients, club_coefficients)
    win_counts[winner] += 1

print("\n" + "="*80)
print("              CHAMPIONS LEAGUE FINAL SIMULATION RESULTS")
print("   (Adjusted for Domestic League & Club Strength Coefficients - Combined)")
print("="*80 + "\n")

print(f"Total simulations: {total_simulations}\n")

# Calculate probabilities
team_a_win_prob = win_counts[team_a] / total_simulations
team_b_win_prob = win_counts[team_b] / total_simulations

print(f"{team_a} Win Probability: {team_a_win_prob:.2%}")
print(f"{team_b} Win Probability: {team_b_win_prob:.2%}")
print("\n")
print("These probabilities include outcomes from regular time, extra time, and penalties,")
print("with adjustments made for the relative strength of their domestic leagues AND their club coefficients.")
print("\n" + "="*80)
print("Simulation Complete!")
print("="*80)