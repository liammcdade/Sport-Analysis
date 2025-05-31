import pandas as pd
import numpy as np
import random

# Example manually input team stats (normally from CSVs)
psg_team_data = {
    'xG': 88.9,
    'npxG': 83.3,
    'xAG': 70.8,
    'npxG+xAG': 154.1,
    'Gls': 89,
    'Ast': 69,
    'MP': 34

}

inter_team_data = {
    'xG': 66.9,
    'npxG': 60.1,
    'xAG': 48.3,
    'npxG+xAG': 108.5,
    'Gls': 79,
    'Ast': 57,
    'MP': 38
}

# Preprocess per-match values
def team_strength(team):
    mp = team['MP']
    return {
        'gls_per_game': team['Gls'] / mp,
        'xg_per_game': team['xG'] / mp,
        'xag_per_game': team['xAG'] / mp,
        'npxg_per_game': team['npxG'] / mp,
        'npxgxag_per_game': team['npxG+xAG'] / mp,
    }

psg_strength = team_strength(psg_team_data)
inter_strength = team_strength(inter_team_data)

# Minute and score
minute = 86
score_psg = 5
score_inter = 0

# Weighted average goal scoring probability per minute
psg_goal_rate = (psg_strength['npxgxag_per_game']) / 90
inter_goal_rate = (inter_strength['npxgxag_per_game']) / 90

# Monte Carlo simulation
psg_wins = 0
inter_wins = 0
draws = 0
simulations = 1000

for _ in range(simulations):
    psg_goals = score_psg
    inter_goals = score_inter
    for m in range(minute, 90):
        if random.random() < psg_goal_rate:
            psg_goals += 1
        if random.random() < inter_goal_rate:
            inter_goals += 1
    if psg_goals > inter_goals:
        psg_wins += 1
    elif inter_goals > psg_goals:
        inter_wins += 1
    else:
        draws += 1

# Final probabilities
total = psg_wins + inter_wins + draws
psg_percent = round(psg_wins / total * 100, 6)
inter_percent = round(inter_wins / total * 100, 6)
draw_percent = round(draws / total * 100, 6)

psg_percent, inter_percent, draw_percent

print(f"PSG Win Probability: {psg_percent}%")
print(f"Inter Win Probability: {inter_percent}%")
print(f"Draw Probability: {draw_percent}%")
