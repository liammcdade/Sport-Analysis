import numpy as np
from collections import defaultdict
from tqdm import tqdm
import itertools
from multiprocessing import Pool, cpu_count
import random

# --- Global Constants ---
# These are the teams in our simulation
TEAMS = [
    "Liverpool", "Arsenal", "Manchester City", "Newcastle United", "Chelsea",
    "Aston Villa", "Nottingham Forest", "Brighton & Hove Albion", "Brentford", "Fulham",
    "Bournemouth", "Crystal Palace", "Everton", "Wolverhampton Wanderers", "West Ham United",
    "Manchester United", "Tottenham Hotspur",
    "Leeds United", "Burnley", "Sunderland"
]

# Define league coefficients. Adjust these based on your data source's league context.
LEAGUE_COEFFICIENTS = {
    "Premier League": 1.0,
    "Championship": 0.7, # Example: Championship teams are 70% as strong as PL for direct comparisons
}

# --- Embedded Team Season Data (Manually Populated) ---
# This dictionary now holds all the historical data directly.
# Inferred values for xG, xAG, and Possession are placeholders based on common football stats.
# The 'GA' column is now directly used to calculate 'GA_per_90'.
TEAM_SEASON_DATA = {
    "Liverpool": [
        {"Season": "2024-2025", "Pld": 38, "GF": 86, "GA": 41, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 86/38, "GA_per_90": 41/38, "xG_per_90": (86/38)*0.95, "xAG_per_90": (86/38)*0.95*0.6, "xG_plus_xAG_per_90": (86/38)*0.95 + (86/38)*0.95*0.6, "Poss": 60.0},
        {"Season": "2023-2024", "Pld": 38, "GF": 86, "GA": 41, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 86/38, "GA_per_90": 41/38, "xG_per_90": (86/38)*0.95, "xAG_per_90": (86/38)*0.95*0.6, "xG_plus_xAG_per_90": (86/38)*0.95 + (86/38)*0.95*0.6, "Poss": 60.0},
        {"Season": "2022-2023", "Pld": 38, "GF": 75, "GA": 47, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 75/38, "GA_per_90": 47/38, "xG_per_90": (75/38)*0.95, "xAG_per_90": (75/38)*0.95*0.6, "xG_plus_xAG_per_90": (75/38)*0.95 + (75/38)*0.95*0.6, "Poss": 58.0},
    ],
    "Arsenal": [
        {"Season": "2024-2025", "Pld": 38, "GF": 69, "GA": 34, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 69/38, "GA_per_90": 34/38, "xG_per_90": (69/38)*0.95, "xAG_per_90": (69/38)*0.95*0.6, "xG_plus_xAG_per_90": (69/38)*0.95 + (69/38)*0.95*0.6, "Poss": 58.0},
        {"Season": "2023-2024", "Pld": 38, "GF": 91, "GA": 29, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 91/38, "GA_per_90": 29/38, "xG_per_90": (91/38)*0.95, "xAG_per_90": (91/38)*0.95*0.6, "xG_plus_xAG_per_90": (91/38)*0.95 + (91/38)*0.95*0.6, "Poss": 60.0},
        {"Season": "2022-2023", "Pld": 38, "GF": 88, "GA": 43, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 88/38, "GA_per_90": 43/38, "xG_per_90": (88/38)*0.95, "xAG_per_90": (88/38)*0.95*0.6, "xG_plus_xAG_per_90": (88/38)*0.95 + (88/38)*0.95*0.6, "Poss": 59.0},
    ],
    "Manchester City": [
        {"Season": "2024-2025", "Pld": 38, "GF": 72, "GA": 44, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 72/38, "GA_per_90": 44/38, "xG_per_90": (72/38)*0.95, "xAG_per_90": (72/38)*0.95*0.6, "xG_plus_xAG_per_90": (72/38)*0.95 + (72/38)*0.95*0.6, "Poss": 63.0},
        {"Season": "2023-2024", "Pld": 38, "GF": 96, "GA": 34, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 96/38, "GA_per_90": 34/38, "xG_per_90": (96/38)*0.95, "xAG_per_90": (96/38)*0.95*0.6, "xG_plus_xAG_per_90": (96/38)*0.95 + (96/38)*0.95*0.6, "Poss": 65.0},
        {"Season": "2022-2023", "Pld": 38, "GF": 94, "GA": 33, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 94/38, "GA_per_90": 33/38, "xG_per_90": (94/38)*0.95, "xAG_per_90": (94/38)*0.95*0.6, "xG_plus_xAG_per_90": (94/38)*0.95 + (94/38)*0.95*0.6, "Poss": 64.0},
    ],
    "Newcastle United": [
        {"Season": "2024-2025", "Pld": 38, "GF": 68, "GA": 47, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 68/38, "GA_per_90": 47/38, "xG_per_90": (68/38)*0.95, "xAG_per_90": (68/38)*0.95*0.6, "xG_plus_xAG_per_90": (68/38)*0.95 + (68/38)*0.95*0.6, "Poss": 52.0},
        {"Season": "2023-2024", "Pld": 38, "GF": 85, "GA": 62, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 85/38, "GA_per_90": 62/38, "xG_per_90": (85/38)*0.95, "xAG_per_90": (85/38)*0.95*0.6, "xG_plus_xAG_per_90": (85/38)*0.95 + (85/38)*0.95*0.6, "Poss": 50.0},
        {"Season": "2022-2023", "Pld": 38, "GF": 68, "GA": 33, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 68/38, "GA_per_90": 33/38, "xG_per_90": (68/38)*0.95, "xAG_per_90": (68/38)*0.95*0.6, "xG_plus_xAG_per_90": (68/38)*0.95 + (68/38)*0.95*0.6, "Poss": 53.0},
    ],
    "Chelsea": [
        {"Season": "2024-2025", "Pld": 38, "GF": 64, "GA": 43, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 64/38, "GA_per_90": 43/38, "xG_per_90": (64/38)*0.95, "xAG_per_90": (64/38)*0.95*0.6, "xG_plus_xAG_per_90": (64/38)*0.95 + (64/38)*0.95*0.6, "Poss": 55.0},
        {"Season": "2023-2024", "Pld": 38, "GF": 77, "GA": 63, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 77/38, "GA_per_90": 63/38, "xG_per_90": (77/38)*0.95, "xAG_per_90": (77/38)*0.95*0.6, "xG_plus_xAG_per_90": (77/38)*0.95 + (77/38)*0.95*0.6, "Poss": 54.0},
        {"Season": "2022-2023", "Pld": 38, "GF": 38, "GA": 47, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 38/38, "GA_per_90": 47/38, "xG_per_90": (38/38)*0.95, "xAG_per_90": (38/38)*0.95*0.6, "xG_plus_xAG_per_90": (38/38)*0.95 + (38/38)*0.95*0.6, "Poss": 56.0},
    ],
    "Aston Villa": [
        {"Season": "2024-2025", "Pld": 38, "GF": 58, "GA": 51, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 58/38, "GA_per_90": 51/38, "xG_per_90": (58/38)*0.95, "xAG_per_90": (58/38)*0.95*0.6, "xG_plus_xAG_per_90": (58/38)*0.95 + (58/38)*0.95*0.6, "Poss": 50.0},
        {"Season": "2023-2024", "Pld": 38, "GF": 76, "GA": 61, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 76/38, "GA_per_90": 61/38, "xG_per_90": (76/38)*0.95, "xAG_per_90": (76/38)*0.95*0.6, "xG_plus_xAG_per_90": (76/38)*0.95 + (76/38)*0.95*0.6, "Poss": 49.0},
        {"Season": "2022-2023", "Pld": 38, "GF": 51, "GA": 46, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 51/38, "GA_per_90": 46/38, "xG_per_90": (51/38)*0.95, "xAG_per_90": (51/38)*0.95*0.6, "xG_plus_xAG_per_90": (51/38)*0.95 + (51/38)*0.95*0.6, "Poss": 48.0},
    ],
    "Nottingham Forest": [
        {"Season": "2024-2025", "Pld": 38, "GF": 58, "GA": 46, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 58/38, "GA_per_90": 46/38, "xG_per_90": (58/38)*0.95, "xAG_per_90": (58/38)*0.95*0.6, "xG_plus_xAG_per_90": (58/38)*0.95 + (58/38)*0.95*0.6, "Poss": 42.0},
        {"Season": "2023-2024", "Pld": 38, "GF": 49, "GA": 67, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 49/38, "GA_per_90": 67/38, "xG_per_90": (49/38)*0.95, "xAG_per_90": (49/38)*0.95*0.6, "xG_plus_xAG_per_90": (49/38)*0.95 + (49/38)*0.95*0.6, "Poss": 40.0},
        {"Season": "2022-2023", "Pld": 38, "GF": 38, "GA": 68, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 38/38, "GA_per_90": 68/38, "xG_per_90": (38/38)*0.95, "xAG_per_90": (38/38)*0.95*0.6, "xG_plus_xAG_per_90": (38/38)*0.95 + (38/38)*0.95*0.6, "Poss": 41.0},
    ],
    "Brighton & Hove Albion": [
        {"Season": "2024-2025", "Pld": 38, "GF": 66, "GA": 59, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 66/38, "GA_per_90": 59/38, "xG_per_90": (66/38)*0.95, "xAG_per_90": (66/38)*0.95*0.6, "xG_plus_xAG_per_90": (66/38)*0.95 + (66/38)*0.95*0.6, "Poss": 55.0},
        {"Season": "2023-2024", "Pld": 38, "GF": 55, "GA": 62, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 55/38, "GA_per_90": 62/38, "xG_per_90": (55/38)*0.95, "xAG_per_90": (55/38)*0.95*0.6, "xG_plus_xAG_per_90": (55/38)*0.95 + (55/38)*0.95*0.6, "Poss": 53.0},
        {"Season": "2022-2023", "Pld": 38, "GF": 72, "GA": 53, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 72/38, "GA_per_90": 53/38, "xG_per_90": (72/38)*0.95, "xAG_per_90": (72/38)*0.95*0.6, "xG_plus_xAG_per_90": (72/38)*0.95 + (72/38)*0.95*0.6, "Poss": 57.0},
    ],
    "Brentford": [
        {"Season": "2024-2025", "Pld": 38, "GF": 66, "GA": 57, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 66/38, "GA_per_90": 57/38, "xG_per_90": (66/38)*0.95, "xAG_per_90": (66/38)*0.95*0.6, "xG_plus_xAG_per_90": (66/38)*0.95 + (66/38)*0.95*0.6, "Poss": 45.0},
        {"Season": "2023-2024", "Pld": 38, "GF": 56, "GA": 65, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 56/38, "GA_per_90": 65/38, "xG_per_90": (56/38)*0.95, "xAG_per_90": (56/38)*0.95*0.6, "xG_plus_xAG_per_90": (56/38)*0.95 + (56/38)*0.95*0.6, "Poss": 44.0},
        {"Season": "2022-2023", "Pld": 38, "GF": 58, "GA": 46, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 58/38, "GA_per_90": 46/38, "xG_per_90": (58/38)*0.95, "xAG_per_90": (58/38)*0.95*0.6, "xG_plus_xAG_per_90": (58/38)*0.95 + (58/38)*0.95*0.6, "Poss": 46.0},
    ],
    "Fulham": [
        {"Season": "2024-2025", "Pld": 38, "GF": 54, "GA": 54, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 54/38, "GA_per_90": 54/38, "xG_per_90": (54/38)*0.95, "xAG_per_90": (54/38)*0.95*0.6, "xG_plus_xAG_per_90": (54/38)*0.95 + (54/38)*0.95*0.6, "Poss": 47.0},
        {"Season": "2023-2024", "Pld": 38, "GF": 55, "GA": 61, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 55/38, "GA_per_90": 61/38, "xG_per_90": (55/38)*0.95, "xAG_per_90": (55/38)*0.95*0.6, "xG_plus_xAG_per_90": (55/38)*0.95 + (55/38)*0.95*0.6, "Poss": 46.0},
        {"Season": "2022-2023", "Pld": 38, "GF": 55, "GA": 53, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 55/38, "GA_per_90": 53/38, "xG_per_90": (55/38)*0.95, "xAG_per_90": (55/38)*0.95*0.6, "xG_plus_xAG_per_90": (55/38)*0.95 + (55/38)*0.95*0.6, "Poss": 48.0},
    ],
    "Bournemouth": [
        {"Season": "2024-2025", "Pld": 38, "GF": 58, "GA": 46, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 58/38, "GA_per_90": 46/38, "xG_per_90": (58/38)*0.95, "xAG_per_90": (58/38)*0.95*0.6, "xG_plus_xAG_per_90": (58/38)*0.95 + (58/38)*0.95*0.6, "Poss": 43.0},
        {"Season": "2023-2024", "Pld": 38, "GF": 54, "GA": 67, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 54/38, "GA_per_90": 67/38, "xG_per_90": (54/38)*0.95, "xAG_per_90": (54/38)*0.95*0.6, "xG_plus_xAG_per_90": (54/38)*0.95 + (54/38)*0.95*0.6, "Poss": 42.0},
        {"Season": "2022-2023", "Pld": 38, "GF": 37, "GA": 71, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 37/38, "GA_per_90": 71/38, "xG_per_90": (37/38)*0.95, "xAG_per_90": (37/38)*0.95*0.6, "xG_plus_xAG_per_90": (37/38)*0.95 + (37/38)*0.95*0.6, "Poss": 41.0},
    ],
    "Crystal Palace": [
        {"Season": "2024-2025", "Pld": 38, "GF": 51, "GA": 51, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 51/38, "GA_per_90": 51/38, "xG_per_90": (51/38)*0.95, "xAG_per_90": (51/38)*0.95*0.6, "xG_plus_xAG_per_90": (51/38)*0.95 + (51/38)*0.95*0.6, "Poss": 44.0},
        {"Season": "2023-2024", "Pld": 38, "GF": 57, "GA": 58, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 57/38, "GA_per_90": 58/38, "xG_per_90": (57/38)*0.95, "xAG_per_90": (57/38)*0.95*0.6, "xG_plus_xAG_per_90": (57/38)*0.95 + (57/38)*0.95*0.6, "Poss": 43.0},
        {"Season": "2022-2023", "Pld": 38, "GF": 40, "GA": 49, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 40/38, "GA_per_90": 49/38, "xG_per_90": (40/38)*0.95, "xAG_per_90": (40/38)*0.95*0.6, "xG_plus_xAG_per_90": (40/38)*0.95 + (40/38)*0.95*0.6, "Poss": 45.0},
    ],
    "Everton": [
        {"Season": "2024-2025", "Pld": 38, "GF": 42, "GA": 44, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 42/38, "GA_per_90": 44/38, "xG_per_90": (42/38)*0.95, "xAG_per_90": (42/38)*0.95*0.6, "xG_plus_xAG_per_90": (42/38)*0.95 + (42/38)*0.95*0.6, "Poss": 40.0},
        {"Season": "2023-2024", "Pld": 38, "GF": 40, "GA": 51, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 40/38, "GA_per_90": 51/38, "xG_per_90": (40/38)*0.95, "xAG_per_90": (40/38)*0.95*0.6, "xG_plus_xAG_per_90": (40/38)*0.95 + (40/38)*0.95*0.6, "Poss": 39.0},
        {"Season": "2022-2023", "Pld": 38, "GF": 34, "GA": 57, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 34/38, "GA_per_90": 57/38, "xG_per_90": (34/38)*0.95, "xAG_per_90": (34/38)*0.95*0.6, "xG_plus_xAG_per_90": (34/38)*0.95 + (34/38)*0.95*0.6, "Poss": 41.0},
    ],
    "Wolverhampton Wanderers": [
        {"Season": "2024-2025", "Pld": 38, "GF": 54, "GA": 69, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 54/38, "GA_per_90": 69/38, "xG_per_90": (54/38)*0.95, "xAG_per_90": (54/38)*0.95*0.6, "xG_plus_xAG_per_90": (54/38)*0.95 + (54/38)*0.95*0.6, "Poss": 45.0},
        {"Season": "2023-2024", "Pld": 38, "GF": 50, "GA": 65, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 50/38, "GA_per_90": 65/38, "xG_per_90": (50/38)*0.95, "xAG_per_90": (50/38)*0.95*0.6, "xG_plus_xAG_per_90": (50/38)*0.95 + (50/38)*0.95*0.6, "Poss": 44.0},
        {"Season": "2022-2023", "Pld": 38, "GF": 31, "GA": 58, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 31/38, "GA_per_90": 58/38, "xG_per_90": (31/38)*0.95, "xAG_per_90": (31/38)*0.95*0.6, "xG_plus_xAG_per_90": (31/38)*0.95 + (31/38)*0.95*0.6, "Poss": 46.0},
    ],
    "West Ham United": [
        {"Season": "2024-2025", "Pld": 38, "GF": 46, "GA": 62, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 46/38, "GA_per_90": 62/38, "xG_per_90": (46/38)*0.95, "xAG_per_90": (46/38)*0.95*0.6, "xG_plus_xAG_per_90": (46/38)*0.95 + (46/38)*0.95*0.6, "Poss": 40.0},
        {"Season": "2023-2024", "Pld": 38, "GF": 60, "GA": 74, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 60/38, "GA_per_90": 74/38, "xG_per_90": (60/38)*0.95, "xAG_per_90": (60/38)*0.95*0.6, "xG_plus_xAG_per_90": (60/38)*0.95 + (60/38)*0.95*0.6, "Poss": 38.0},
        {"Season": "2022-2023", "Pld": 38, "GF": 42, "GA": 55, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 42/38, "GA_per_90": 55/38, "xG_per_90": (42/38)*0.95, "xAG_per_90": (42/38)*0.95*0.6, "xG_plus_xAG_per_90": (42/38)*0.95 + (42/38)*0.95*0.6, "Poss": 41.0},
    ],
    "Manchester United": [
        {"Season": "2024-2025", "Pld": 38, "GF": 44, "GA": 54, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 44/38, "GA_per_90": 54/38, "xG_per_90": (44/38)*0.95, "xAG_per_90": (44/38)*0.95*0.6, "xG_plus_xAG_per_90": (44/38)*0.95 + (44/38)*0.95*0.6, "Poss": 52.0},
        {"Season": "2023-2024", "Pld": 38, "GF": 57, "GA": 58, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 57/38, "GA_per_90": 58/38, "xG_per_90": (57/38)*0.95, "xAG_per_90": (57/38)*0.95*0.6, "xG_plus_xAG_per_90": (57/38)*0.95 + (57/38)*0.95*0.6, "Poss": 50.0},
        {"Season": "2022-2023", "Pld": 38, "GF": 58, "GA": 43, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 58/38, "GA_per_90": 43/38, "xG_per_90": (58/38)*0.95, "xAG_per_90": (58/38)*0.95*0.6, "xG_plus_xAG_per_90": (58/38)*0.95 + (58/38)*0.95*0.6, "Poss": 54.0},
    ],
    "Tottenham Hotspur": [
        {"Season": "2024-2025", "Pld": 38, "GF": 64, "GA": 65, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 64/38, "GA_per_90": 65/38, "xG_per_90": (64/38)*0.95, "xAG_per_90": (64/38)*0.95*0.6, "xG_plus_xAG_per_90": (64/38)*0.95 + (64/38)*0.95*0.6, "Poss": 50.0},
        {"Season": "2023-2024", "Pld": 38, "GF": 74, "GA": 61, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 74/38, "GA_per_90": 61/38, "xG_per_90": (74/38)*0.95, "xAG_per_90": (74/38)*0.95*0.6, "xG_plus_xAG_per_90": (74/38)*0.95 + (74/38)*0.95*0.6, "Poss": 49.0},
        {"Season": "2022-2023", "Pld": 38, "GF": 70, "GA": 63, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 70/38, "GA_per_90": 63/38, "xG_per_90": (70/38)*0.95, "xAG_per_90": (70/38)*0.95*0.6, "xG_plus_xAG_per_90": (70/38)*0.95 + (70/38)*0.95*0.6, "Poss": 51.0},
    ],
    "Leeds United": [
        {"Season": "2024", "Pld": 28, "GF": 50, "GA": 46, "League": "Championship",
         "90s": 25.4, "Gls_per_90": 1.98, "GA_per_90": 46/25.4, "xG_per_90": 1.94, "xAG_per_90": 1.47, "xG_plus_xAG_per_90": 3.41, "Poss": 61.3},
        {"Season": "2023-2024", "Pld": 46, "GF": 81, "GA": 43, "League": "Championship",
         "90s": 46.0, "Gls_per_90": 81/46, "GA_per_90": 43/46, "xG_per_90": (81/46)*0.95, "xAG_per_90": (81/46)*0.95*0.6, "xG_plus_xAG_per_90": (81/46)*0.95 + (81/46)*0.95*0.6, "Poss": 58.0},
        {"Season": "2022-2023", "Pld": 38, "GF": 48, "GA": 78, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 48/38, "GA_per_90": 78/38, "xG_per_90": (48/38)*0.95, "xAG_per_90": (48/38)*0.95*0.6, "xG_plus_xAG_per_90": (48/38)*0.95 + (48/38)*0.95*0.6, "Poss": 45.0},
    ],
    "Burnley": [
        {"Season": "2024-2025", "Pld": 46, "GF": 69, "GA": 16, "League": "Championship",
         "90s": 46.0, "Gls_per_90": 69/46, "GA_per_90": 16/46, "xG_per_90": (69/46)*0.95, "xAG_per_90": (69/46)*0.95*0.6, "xG_plus_xAG_per_90": (69/46)*0.95 + (69/46)*0.95*0.6, "Poss": 55.0},
        {"Season": "2023-2024", "Pld": 38, "GF": 41, "GA": 78, "League": "Premier League",
         "90s": 38.0, "Gls_per_90": 41/38, "GA_per_90": 78/38, "xG_per_90": (41/38)*0.95, "xAG_per_90": (41/38)*0.95*0.6, "xG_plus_xAG_per_90": (41/38)*0.95 + (41/38)*0.95*0.6, "Poss": 40.0},
        {"Season": "2022-2023", "Pld": 46, "GF": 87, "GA": 35, "League": "Championship",
         "90s": 46.0, "Gls_per_90": 87/46, "GA_per_90": 35/46, "xG_per_90": (87/46)*0.95, "xAG_per_90": (87/46)*0.95*0.6, "xG_plus_xAG_per_90": (87/46)*0.95 + (87/46)*0.95*0.6, "Poss": 57.0},
    ],
    "Sunderland": [
        {"Season": "2024-2025", "Pld": 46, "GF": 58, "GA": 44, "League": "Championship",
         "90s": 46.0, "Gls_per_90": 58/46, "GA_per_90": 44/46, "xG_per_90": (58/46)*0.95, "xAG_per_90": (58/46)*0.95*0.6, "xG_plus_xAG_per_90": (58/46)*0.95 + (58/46)*0.95*0.6, "Poss": 50.0},
        {"Season": "2023-2024", "Pld": 46, "GF": 52, "GA": 54, "League": "Championship",
         "90s": 46.0, "Gls_per_90": 52/46, "GA_per_90": 54/46, "xG_per_90": (52/46)*0.95, "xAG_per_90": (52/46)*0.95*0.6, "xG_plus_xAG_per_90": (52/46)*0.95 + (52/46)*0.95*0.6, "Poss": 48.0},
        {"Season": "2022-2023", "Pld": 46, "GF": 68, "GA": 55, "League": "Championship",
         "90s": 46.0, "Gls_per_90": 68/46, "GA_per_90": 55/46, "xG_per_90": (68/46)*0.95, "xAG_per_90": (68/46)*0.95*0.6, "xG_plus_xAG_per_90": (68/46)*0.95 + (68/46)*0.95*0.6, "Poss": 51.0},
    ],
}

# Global league averages for normalization in goal simulation
LEAGUE_AVG_GLS_PER_90 = 0.0
LEAGUE_AVG_GA_PER_90 = 0.0
LEAGUE_AVG_XG_PLUS_XAG_PER_90 = 0.0 # Average for combined attack metric

# --- Helper Functions ---
def generate_weight_sets(num_sets=100, num_seasons=3):
    """Generates sets of decay weights for historical seasons."""
    weights = []
    for _ in range(num_sets):
        raw_weights = [random.random() for _ in range(num_seasons)]
        total_raw = sum(raw_weights)
        normalized_weights = [w / total_raw for w in raw_weights]
        normalized_weights.sort(reverse=True) # Most recent season gets highest weight
        weights.append(normalized_weights)
    return weights

# --- Compute Weighted Average for a Specific Metric ---
def weighted_avg_metric(team, metric_name, season_weights):
    """
    Compute weighted, normalized average for a specific metric for a team
    using provided season_weights and league coefficients.
    """
    seasons = TEAM_SEASON_DATA.get(team, [])
    if not seasons:
        print(f"Warning: No season data found for {team}. Returning 0.0 for {metric_name}.")
        return 0.0

    weighted_sum = 0.0
    total_weight = 0.0
    
    num_seasons_to_use = min(len(seasons), len(season_weights))

    for i in range(num_seasons_to_use):
        season = seasons[i]
        weight = season_weights[i]
        league_coeff = LEAGUE_COEFFICIENTS.get(season.get("League", "Premier League"), 1.0)
        
        metric_value = season.get(metric_name)
        if metric_value is None or not isinstance(metric_value, (int, float)):
            print(f"Warning: Missing or non-numeric '{metric_name}' for {team} in season {season.get('Season', 'N/A')}. Skipping this season for this metric.")
            continue
        
        weighted_sum += weight * metric_value * league_coeff
        total_weight += weight

    if total_weight == 0:
        return 0.0
    return weighted_sum / total_weight

# --- Calculate Global League Averages (needed for normalization in goal simulation) ---
def calculate_league_averages():
    """
    Calculates global league averages for goals for/against per 90 and xG+xAG per 90
    from all loaded team data, adjusted by league coefficients.
    These are used as baselines in goal simulation.
    """
    global LEAGUE_AVG_GLS_PER_90, LEAGUE_AVG_GA_PER_90, LEAGUE_AVG_XG_PLUS_XAG_PER_90
    
    total_gls_sum = 0.0
    total_ga_sum = 0.0
    total_xg_plus_xag_sum = 0.0
    total_90s_played = 0.0

    for team_seasons in TEAM_SEASON_DATA.values():
        for season_data in team_seasons:
            if all(k in season_data for k in ['Gls_per_90', 'GA_per_90', 'xG_plus_xAG_per_90', '90s']):
                
                league_coeff = LEAGUE_COEFFICIENTS.get(season_data.get("League", "Premier League"), 1.0)
                
                total_gls_sum += season_data['Gls_per_90'] * season_data['90s'] * league_coeff
                total_ga_sum += season_data['GA_per_90'] * season_data['90s'] * league_coeff
                total_xg_plus_xag_sum += season_data['xG_plus_xAG_per_90'] * season_data['90s'] * league_coeff
                total_90s_played += season_data['90s']

    if total_90s_played > 0:
        LEAGUE_AVG_GLS_PER_90 = total_gls_sum / total_90s_played
        LEAGUE_AVG_GA_PER_90 = total_ga_sum / total_90s_played
        LEAGUE_AVG_XG_PLUS_XAG_PER_90 = total_xg_plus_xag_sum / total_90s_played
    else:
        print("Warning: Could not calculate league averages. No valid season data found with '90s'. "
              "Setting default averages.")
        LEAGUE_AVG_GLS_PER_90 = 1.4
        LEAGUE_AVG_GA_PER_90 = 1.4
        LEAGUE_AVG_XG_PLUS_XAG_PER_90 = 2.5 # A reasonable default for xG+xAG

# --- Goal Simulation Function (using full data, NO ELO) ---
def simulate_score_data_only(home_attack_rating, away_defense_rating, away_attack_rating, home_defense_rating):
    """
    Simulates goals for home and away teams using derived attack and defense ratings
    from weighted historical data. Uses Poisson distribution.
    
    Attack_Rating = Team_xG_plus_xAG_per_90 / LEAGUE_AVG_XG_PLUS_XAG_PER_90
    Defense_Rating = LEAGUE_AVG_GA_PER_90 / Team_GA_per_90 (inverted, higher is better defense)
    
    lambda = Attack_Rating * Defense_Rating * LEAGUE_AVG_GLS_PER_90
    """
    
    # Ensure no division by zero or very small numbers for ratings
    # If league averages are 0, this indicates a data issue.
    if LEAGUE_AVG_XG_PLUS_XAG_PER_90 == 0 or LEAGUE_AVG_GA_PER_90 == 0:
        print("Error: League averages are zero. Cannot accurately simulate goals. Check data.")
        return 0, 0 # Return 0 goals to prevent errors, but indicates a problem.

    # Ensure defense ratings are not zero to prevent division by zero in next step
    away_defense_rating = max(0.01, away_defense_rating)
    home_defense_rating = max(0.01, home_defense_rating)

    # Calculate actual attack and defense ratings for the specific match
    # Home team's attack rating relative to league average
    home_att_rating = home_attack_rating / LEAGUE_AVG_XG_PLUS_XAG_PER_90
    # Away team's defense rating (inverted: lower GA_per_90 means better defense, so higher rating)
    away_def_rating = LEAGUE_AVG_GA_PER_90 / away_defense_rating
    
    # Away team's attack rating relative to league average
    away_att_rating = away_attack_rating / LEAGUE_AVG_XG_PLUS_XAG_PER_90
    # Home team's defense rating (inverted)
    home_def_rating = LEAGUE_AVG_GA_PER_90 / home_defense_rating

    # Calculate Poisson lambdas for each team
    # Home team's expected goals: their attack strength * opponent's defensive weakness * league average goal rate
    home_lambda = home_att_rating * away_def_rating * LEAGUE_AVG_GLS_PER_90
    # Away team's expected goals: their attack strength * opponent's defensive weakness * league average goal rate
    away_lambda = away_att_rating * home_def_rating * LEAGUE_AVG_GLS_PER_90

    # Ensure lambdas are reasonable and positive for Poisson distribution
    home_lambda = max(0.1, home_lambda)
    away_lambda = max(0.1, away_lambda)
    
    return np.random.poisson(home_lambda), np.random.poisson(away_lambda)

# --- Simulation Execution (NO ELO) ---
def simulate_season_data_only(weight_set_idx):
    """
    Simulates a full league season for one weight set, using weighted historical
    squad data (xG+xAG for attack, GA for defense), without any ELO system.
    """
    current_season_weights = WEIGHT_SETS[weight_set_idx]
    team_indices = {team: idx for idx, team in enumerate(TEAMS)}
    
    # Stats array: MP, Wins, Draws, Losses, GF, GA, Pts, GD
    stats = np.zeros((len(TEAMS), 8), dtype=np.int32) 

    # Precompute weighted averages for xG_plus_xAG_per_90 (attack) and GA_per_90 (defense)
    # These are their 'strength' values for the current season based on past performance
    team_attack_ratings = {team: weighted_avg_metric(team, 'xG_plus_xAG_per_90', current_season_weights) for team in TEAMS}
    team_defense_ratings = {team: weighted_avg_metric(team, 'GA_per_90', current_season_weights) for team in TEAMS}

    # Generate fixtures (all vs all, home and away)
    FIXTURES = list(itertools.permutations(TEAMS, 2)) # Each team plays each other home & away
    random.shuffle(FIXTURES) # Randomize fixture order for each simulation

    for home, away in FIXTURES:
        i, j = team_indices[home], team_indices[away]

        # Simulate one match per fixture using the data-driven model
        home_goals_match, away_goals_match = simulate_score_data_only(
            team_attack_ratings[home], team_defense_ratings[away], # Home's attack vs Away's defense
            team_attack_ratings[away], team_defense_ratings[home]  # Away's attack vs Home's defense
        )
        
        # Update season statistics (Matches Played, Goals For, Goals Against, Goal Difference)
        stats[i,0] += 1; stats[j,0] += 1 # MP
        stats[i,4] += home_goals_match; stats[j,4] += away_goals_match # GF
        stats[i,5] += away_goals_match; stats[j,5] += home_goals_match # GA
        stats[i,7] += home_goals_match - away_goals_match # GD
        stats[j,7] += away_goals_match - home_goals_match # GD

        # Update Wins, Draws, Losses, and Points
        if home_goals_match > away_goals_match:
            stats[i,1] += 1; stats[i,6] += 3; stats[j,3] += 1 # Home Win
        elif away_goals_match > home_goals_match:
            stats[j,1] += 1; stats[j,6] += 3; stats[i,3] += 1 # Away Win
        else:
            stats[i,2] += 1; stats[j,2] += 1; stats[i,6] += 1; stats[j,6] += 1 # Draw

    # Sort final league table
    table = sorted(((team, stats[idx]) for team, idx in team_indices.items()),
                   key=lambda x: (x[1][6], x[1][7], x[1][4]), reverse=True) # Points, GD, GF

    # Determine European qualification and title winner
    final_league_positions = {team: i+1 for i, (team, _) in enumerate(table)}
    cl, el, ecl = set(), set(), set()
    NUM_CL_LEAGUE_SPOTS = 5 # Example: Top 5 qualify for Champions League
    
    for i in range(min(NUM_CL_LEAGUE_SPOTS, len(table))): 
        cl.add(table[i][0])
    
    for team, pos in final_league_positions.items():
        if team not in cl and pos == NUM_CL_LEAGUE_SPOTS + 1: # Next spot for EL
            el.add(team)
        if team not in cl and team not in el and pos == NUM_CL_LEAGUE_SPOTS + 2: # Next spot for ECL
            ecl.add(team)
    
    all_eur = cl | el | ecl
    title = table[0][0] # League winner

    final_team_stats = {team: stats[team_indices[team]].tolist() for team in TEAMS}
    
    # Return results without ELO
    return cl, el, ecl, all_eur, title, final_team_stats

# --- Aggregation and Display Functions ---
def aggregate_results(results):
    """Aggregates results from multiple season simulations."""
    qual_counts = {team: {"CL":0,"EL":0,"ECL":0,"Overall":0,"Title":0} for team in TEAMS}
    summed_team_stats = defaultdict(lambda: np.zeros(8, dtype=np.float64)) # Use float for averages

    for cl, el, ecl, all_eur, title, final_team_stats in results:

        for t in cl: qual_counts[t]["CL"] += 1
        for t in el: qual_counts[t]["EL"] += 1
        for t in ecl: qual_counts[t]["ECL"] += 1
        for t in all_eur: qual_counts[t]["Overall"] += 1
        qual_counts[title]["Title"] += 1

        for team, stats_list in final_team_stats.items():
            summed_team_stats[team] += np.array(stats_list)
            
    return qual_counts, summed_team_stats

def display_results(qual_counts, summed_team_stats, RUNS):
    """Displays aggregated simulation results."""
    
    # Calculate average European slots (for general idea, not per team)
    total_cl = sum(qc["CL"] for qc in qual_counts.values())
    total_el = sum(qc["EL"] for qc in qual_counts.values())
    total_ecl = sum(qc["ECL"] for qc in qual_counts.values())

    avg_cl = total_cl / RUNS
    avg_el = total_el / RUNS
    avg_ecl = total_ecl / RUNS
    avg_total = avg_cl + avg_el + avg_ecl

    print(f"\n--- Average European Slots Assigned Per Season ({RUNS} Simulations) ---")
    print(f"Average Champions League (CL) slots: {avg_cl:.2f}")
    print(f"Average Europa League (EL) slots: {avg_el:.2f}")
    print(f"Average Europa Conference League (ECL) slots: {avg_ecl:.2f}")
    print(f"Average Total European slots: {avg_total:.2f}\n" + "-"*60)

    print("\n--- European Qualification & Title Probabilities ---")
    # Sort teams by their probability of winning the title
    sorted_qual_counts = sorted(qual_counts.items(), key=lambda item: item[1]["Title"], reverse=True)
    
    header = f"{'Team':<20} | {'Title %':>9} | {'CL %':>7} | {'EL %':>7} | {'ECL %':>8} | {'Euro %':>8}"
    print(header)
    print("-" * len(header))
    for team, counts in sorted_qual_counts:
        title_pct = (counts["Title"] / RUNS) * 100
        cl_pct = (counts["CL"] / RUNS) * 100
        el_pct = (counts["EL"] / RUNS) * 100
        ecl_pct = (counts["ECL"] / RUNS) * 100
        overall_pct = (counts["Overall"] / RUNS) * 100
        print(f"{team:<20} | {title_pct:>8.2f}% | {cl_pct:>6.2f}% | {el_pct:>6.2f}% | {ecl_pct:>7.2f}% | {overall_pct:>7.2f}%")

    print("\n--- Average Season Statistics per Team ---")
    header_stats = f"{'Team':<20} | {'MP':>4} | {'W':>4} | {'D':>4} | {'L':>4} | {'GF':>4} | {'GA':>4} | {'GD':>4} | {'Pts':>4}"
    print(header_stats)
    print("-" * len(header_stats))
    
    # Prepare average stats for display
    avg_stats_display = []
    for team in TEAMS:
        avg_s = summed_team_stats[team] / RUNS
        avg_stats_display.append((team, avg_s))
        
    # Sort average stats by average points
    sorted_avg_stats = sorted(avg_stats_display, key=lambda x: x[1][6], reverse=True) # Sort by Pts
    
    for team, avg_s in sorted_avg_stats:
        print(f"{team:<20} | {int(avg_s[0]):>4} | {int(avg_s[1]):>4} | {int(avg_s[2]):>4} | {int(avg_s[3]):>4} | {int(avg_s[4]):>4} | {int(avg_s[5]):>4} | {int(avg_s[7]):>4} | {int(avg_s[6]):>4}")


# --- Main Execution ---
if __name__ == "__main__":
    # --- Step 1: Data Setup ---
    # No CSV loading needed as data is embedded
    print("Using embedded squad season data. Calculating league averages...")
    calculate_league_averages() # Populate global league averages
    print(f"League Averages: Gls/90={LEAGUE_AVG_GLS_PER_90:.2f}, GA/90={LEAGUE_AVG_GA_PER_90:.2f}, xG+xAG/90={LEAGUE_AVG_XG_PLUS_XAG_PER_90:.2f}")

    # Determine the number of historical seasons available for weighting
    num_historical_seasons = 0
    if TEAM_SEASON_DATA:
        # Find the max number of seasons available for any team that has data
        num_historical_seasons = max(len(seasons) for seasons in TEAM_SEASON_DATA.values())
        if num_historical_seasons == 0:
            print("Error: No historical seasons found for any team. Cannot generate weight sets.")
            exit()
    else:
        print("Error: TEAM_SEASON_DATA is empty. Please check the embedded data.")
        exit()

    # Generate weight sets for the number of available historical seasons
    WEIGHT_SETS = generate_weight_sets(num_sets=100, num_seasons=num_historical_seasons)
    
    NUM_SIMULATIONS = 10000 # Number of times to simulate the league season

    print(f"\nStarting {NUM_SIMULATIONS} season simulations (using weighted historical squad data only, NO ELO)...")
    
    # Prepare parameters for multiprocessing: only weight_set_idx is needed
    sim_params = [i % len(WEIGHT_SETS) for i in range(NUM_SIMULATIONS)]

    # Use multiprocessing to run simulations in parallel
    with Pool(processes=cpu_count()) as pool:
        # Using tqdm for a progress bar
        all_results = list(tqdm(pool.imap(simulate_season_data_only, sim_params), total=NUM_SIMULATIONS))

    print("\nAggregating results...")
    qual_counts, summed_team_stats = aggregate_results(all_results)

    print("\n--- Weighted Historical Squad Data Only Model Results (NO ELO) ---")
    display_results(qual_counts, summed_team_stats, NUM_SIMULATIONS)