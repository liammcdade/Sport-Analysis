import random
import math
import numpy as np
from tqdm import tqdm

def estimate_civilizations_monte_carlo():
    """
    Estimates the number and distribution of civilizations using a Monte Carlo simulation
    over the Drake Equation parameters.
    """
    # --- Simulation Control ---
    # The number of random scenarios to simulate.
    # 1,000,000 provides a good balance of speed and statistical accuracy.
    num_simulations = 1_000_000

    # --- Drake Parameter Ranges (min, max) ---
    # Define the plausible range for each parameter. We'll pick a random value from these
    # ranges in each simulation.
    R_star_range = (1.0, 10.0)      # Rate of star formation (stars/year)
    f_p_range = (0.5, 1.0)          # Fraction of stars with planets
    n_e_range = (0.1, 1.6)         # Habitable worlds per star (log-uniform)
    f_l_range = (1e-6, 1.0)         # Fraction where life arises (log-uniform)
    f_i_range = (1e-6, 1.0)         # Fraction with intelligence (log-uniform)
    f_c_range = (0.01, 0.5)         # Fraction developing detectable tech
    L_range = (100, 1e9)            # Lifetime of a civilization in years (log-uniform)

    # --- Constants ---
    galaxy_age = 13_600_000_000
    total_stars_mw = 200_000_000_000
    
    # Milky Way dimensions (using a 3D volume for distance approximation)
    radius_mw_ly = 50_000
    thickness_mw_ly = 1_000
    volume_mw_ly3 = math.pi * (radius_mw_ly ** 2) * thickness_mw_ly

    results_mw = [] # List to store the result (N) from each simulation

    print(f"Running {num_simulations:,} Monte Carlo simulations...")
    
    # --- Main Simulation Loop ---
    for _ in tqdm(range(num_simulations), desc="Simulating Scenarios"):
        # For each simulation, draw a new random value for each parameter.
        
        # Linear sampling for parameters with a narrow, well-defined range.
        R_star = random.uniform(*R_star_range)
        f_p = random.uniform(*f_p_range)
        f_c = random.uniform(*f_c_range)
        
        # Log-uniform sampling for parameters with high uncertainty spanning orders of magnitude.
        # This gives each order of magnitude an equal chance of being selected.
        n_e = 10**random.uniform(math.log10(n_e_range[0]), math.log10(n_e_range[1]))
        f_l = 10**random.uniform(math.log10(f_l_range[0]), math.log10(f_l_range[1]))
        f_i = 10**random.uniform(math.log10(f_i_range[0]), math.log10(f_i_range[1]))
        L = 10**random.uniform(math.log10(L_range[0]), math.log10(L_range[1]))
        
        # Calculate N for the Milky Way with this random set of parameters
        current_civs_mw = R_star * f_p * n_e * f_l * f_i * f_c * L
        
        results_mw.append(current_civs_mw)

    # --- Statistical Analysis of Results ---
    results_mw = np.array(results_mw)

    # Calculate key statistics. The median is often more telling than the mean
    # because a few wildly optimistic scenarios can skew the mean upwards.
    mean_civs = np.mean(results_mw)
    median_civs = np.median(results_mw)
    std_dev_civs = np.std(results_mw)
    
    # Calculate the probability of being "alone" in the galaxy (N < 1)
    # This is a key output of the Fermi Paradox debate.
    prob_alone_in_galaxy = np.sum(results_mw < 1) / num_simulations * 100
    prob_at_least_10 = np.sum(results_mw >= 10) / num_simulations * 100
    prob_at_least_1000 = np.sum(results_mw >= 1000) / num_simulations * 100

    print("\n--- MONTE CARLO SIMULATION RESULTS (MILKY WAY) ---")
    print(f"Based on {num_simulations:,} random scenarios:\n")
    
    print("[ Civilization Count Statistics ]")
    print(f"  Mean (Average) number of civilizations : {mean_civs:,.2f}")
    print(f"  Median number of civilizations         : {median_civs:,.2f} (This is often the most representative value)")
    print(f"  Standard Deviation                     : {std_dev_civs:,.2f}")
    
    print("\n[ Probabilistic Scenarios ]")
    print(f"  Probability we are effectively ALONE in the galaxy (N < 1)   : {prob_alone_in_galaxy:.2f}%")
    print(f"  Probability of at least 10 civilizations in the galaxy      : {prob_at_least_10:.2f}%")
    print(f"  Probability of at least 1,000 civilizations in the galaxy   : {prob_at_least_1000:.2f}%")

    # --- Distance Calculation based on the MEDIAN result ---
    # Using the median is more robust against outlier scenarios.
    print("\n[ Spatial Distribution based on MEDIAN result ]")
    if median_civs > 0:
        if median_civs > 1:
            # Assume 3D distribution for distance calculation
            dist_ly = (volume_mw_ly3 / median_civs) ** (1/3)
            print(f"  Median distance to nearest civilization: {dist_ly:,.0f} light years")
        else:
            # If N is between 0 and 1, the "average" distance is just the size of the galaxy
            print(f"  Median distance to nearest civilization: >{radius_mw_ly*2:,.0f} light years (as N < 1)")
            
        # Earth Surface Analogy
        earth_surface_area_km2 = 510.0e6
        # If we scaled the number of median civilizations down to the surface of the Earth:
        area_per_civ_on_earth = earth_surface_area_km2 / median_civs
        dist_on_earth_km = math.sqrt(area_per_civ_on_earth)
        print(f"  Earth Analogy: This density is like people being {dist_on_earth_km:,.1f} km apart from each other.")
    else:
        print("  Median number of civilizations is 0, distance is effectively infinite.")


# Run the simulation
estimate_civilizations_monte_carlo()