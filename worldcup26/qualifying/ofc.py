import random

def print_ofc_world_cup_chances():
    """
    Prints the World Cup 2026 qualification chances for New Zealand and New Caledonia
    based on the confirmed OFC qualification outcomes.
    """

    # --- Confirmed Qualification Status ---
    # New Zealand has directly qualified for the FIFA World Cup 2026.
    new_zealand_chance_percent = 100.0

    # New Caledonia has advanced to the Inter-confederation Playoff.
    # The 50% chance is as per your specific request for a hypothetical scenario.
    new_caledonia_playoff_chance_percent = 50.0

    print("--- OFC World Cup 2026 Qualification Chances ---")
    print("\nBased on confirmed OFC Qualification results:")

    print(f"\nNew Zealand's World Cup 2026 Qualification Chance: {new_zealand_chance_percent:.2f}%")
    print(f"   (New Zealand has directly qualified for the World Cup as OFC's automatic slot winner.)")

    print(f"\nNew Caledonia's World Cup 2026 Qualification Chance (via Inter-confederation Playoff): {new_caledonia_playoff_chance_percent:.2f}%")
    print(f"   (New Caledonia will compete in the Inter-confederation Playoff for one of the remaining World Cup spots.")
    print(f"   Note: The {new_caledonia_playoff_chance_percent}% chance for New Caledonia is a specific value you requested for a hypothetical scenario,")
    print(f"   and not an official probability from FIFA for the inter-confederation playoff.)")

    # Optional: A very simple "simulation" for New Caledonia if you want to see outcomes based on 50%
    print("\n--- Illustrative Micro-Simulation for New Caledonia's Playoff (based on 50% chance) ---")
    num_micro_sims = 1000 # A small number just to show outcomes

    qualified_count = 0
    not_qualified_count = 0

    for _ in range(num_micro_sims):
        if random.random() < (new_caledonia_playoff_chance_percent / 100.0):
            qualified_count += 1
        else:
            not_qualified_count += 1

    print(f"Out of {num_micro_sims} hypothetical playoff attempts for New Caledonia:")
    print(f"- Qualified: {qualified_count} times ({qualified_count / num_micro_sims:.2%})")
    print(f"- Did Not Qualify: {not_qualified_count} times ({not_qualified_count / num_micro_sims:.2%})")


# --- Main Execution ---
if __name__ == "__main__":
    print_ofc_world_cup_chances()
