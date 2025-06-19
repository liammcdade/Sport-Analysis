import numpy as np
import sys

# Settings
num_simulations = 50000  # More simulations

# Initialize list to store results
results = []

print("Running Monte Carlo simulations... (Live updates below)\n")

for i in range(1, num_simulations + 1):
    R_star = 1  # Only one star per solar system
    # All other variables are random
    f_p = np.random.uniform(0.1, 1.0)
    n_e = np.random.uniform(0.05, 0.6)
    f_l = 10 ** np.random.uniform(np.log10(0.005), np.log10(1))
    f_i = 10 ** np.random.uniform(np.log10(0.0005), np.log10(1))
    f_c = 10 ** np.random.uniform(np.log10(0.005), np.log10(0.3))
    L = 10 ** np.random.uniform(np.log10(50), np.log10(20000))

    # Compute N
    N = R_star * f_p * n_e * f_l * f_i * f_c * L
    results.append(N)

    if i % 1 == 0 or i == num_simulations:
        avg_N = np.mean(results)
        prob_N_ge_1 = np.mean(np.array(results) >= 1)
        sys.stdout.write(f"\rSimulation {i} / {num_simulations} | Avg N: {avg_N:.2f} | P(N ≥ 1): {prob_N_ge_1:.2%}")
        sys.stdout.flush()

results = np.array(results)
print("\n\n--- Simulation Complete ---")
print(f"Simulations: {num_simulations}")
print(f"Average N: {results.mean():.2f}")
print(f"Median N: {np.median(results):.2f}")
print(f"Probability N ≥ 1: {(results >= 1).mean():.2%}")
print(f"Probability N ≥ 10: {(results >= 10).mean():.2%}")
print(f"Probability N = 0: {(results == 0).mean():.2%}")