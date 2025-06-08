def fifa_ranking_update(P_team, P_opponent, result, importance=25):
    """
    Calculates the new FIFA ranking for a team after a match.
    
    Parameters:
    - P_team (float): Team's rating before the match
    - P_opponent (float): Opponent's rating before the match
    - result (float): Match result (1=win, 0.5=draw, 0=loss)
    - importance (int): Match importance coefficient (default 25 for WC qualifiers)
    
    Returns:
    - float: New FIFA rating
    """
    dr = P_team - P_opponent
    E = 1 / (1 + 10 ** (-dr / 600))  # Expected result
    P_new = P_team + importance * (result - E)
    return round(P_new, 2), E  # Return both new rating and expected result for transparency

# --- Input Data ---
P_england_before = 1819.2
P_andorra_before = 957.41
importance = 25

# England wins, Andorra loses
result_england = 1
result_andorra = 0

# --- Calculations ---
P_england_after, E_england = fifa_ranking_update(P_england_before, P_andorra_before, result_england, importance)
P_andorra_after, E_andorra = fifa_ranking_update(P_andorra_before, P_england_before, result_andorra, importance)

# --- Output ---

print(f"")

print(f"England expected result: {E_england:.6f}")
print(f"England new rating: {P_england_after}")
print(f"Andorra expected result: {E_andorra:.6f}")
print(f"Andorra new rating: {P_andorra_after}")
