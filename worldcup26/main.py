import random
import math
from collections import defaultdict
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

# FIFA_RANKINGS updated as of April 3, 2025, based on publicly available data.
# Note: This data is static and would need to be manually updated or fetched via web scraping
# if a live API or more advanced scraping tools were available.
FIFA_RANKINGS = {
    "Argentina": 1886.16, "Spain": 1854.64, "France": 1852.71, "England": 1819.2, "Brazil": 1776.03,
    "Netherlands": 1752.44, "Portugal": 1750.08, "Belgium": 1735.75, "Italy": 1718.31, "Germany": 1716.98,
    "Croatia": 1698.66, "Morocco": 1694.24, "Uruguay": 1679.49, "Colombia": 1679.04, "Japan": 1652.64,
    "USA": 1648.81, "Mexico": 1646.94, "IR Iran": 1637.39, "Senegal": 1630.32, "Switzerland": 1624.75,
    "Denmark": 1617.54, "Austria": 1580.22, "Korea Republic": 1574.93, "Ecuador": 1567.95, "Ukraine": 1559.81,
    "Australia": 1554.55, "Türkiye": 1551.47, "Sweden": 1536.05, "Wales": 1535.57, "Canada": 1531.58,
    "Serbia": 1523.91, "Egypt": 1518.79, "Panama": 1517.66, "Poland": 1517.35, "Russia": 1516.27,
    "Algeria": 1507.17, "Hungary": 1503.34, "Norway": 1497.18, "Czechia": 1491.43, "Greece": 1489.82,
    "Côte d'Ivoire": 1487.27, "Peru": 1483.48, "Nigeria": 1481.35, "Scotland": 1480.3, "Romania": 1479.22,
    "Slovakia": 1477.78, "Venezuela": 1476.84, "Paraguay": 1475.93, "Tunisia": 1474.1, "Cameroon": 1465.72,
    "Slovenia": 1462.66, "Chile": 1461.91, "Mali": 1460.23, "Costa Rica": 1459.13, "Qatar": 1456.58,
    "South Africa": 1445.01, "Uzbekistan": 1437.02, "Saudi Arabia": 1418.96, "Iraq": 1413.4, "Republic of Ireland": 1412.23,
    "North Macedonia": 1406.87, "Bosnia and Herzegovina": 1400.99, "Ghana": 1399.78, "DR Congo": 1395.2, "Finland": 1393.77,
    "Burkina Faso": 1385.61, "Iceland": 1383.07, "Albania": 1374.88, "Honduras": 1373.07, "United Arab Emirates": 1368.14,
    "Jordan": 1283.48, "New Zealand": 1221.75, "New Caledonia": 1058.0, "Kuwait": 1109.81, "India": 1132.03,
    "Afghanistan": 919.32, "Kyrgyz Republic": 1297.05, "Oman": 1307.72, "Palestine": 1269.83, "Indonesia": 1102.26,
    "China PR": 1275.25, "Bahrain": 1128.53, "Congo": 1204.68, "Tanzania": 1184.28, "Niger": 1072.07, "Zambia": 1241.65,
    "Cuba": 1291.68, "Bermuda": 1198.81, "Cayman Islands": 951.18, "Antigua and Barbuda": 1040.69,
    "Grenada": 1150.77, "Saint Kitts and Nevis": 998.67, "Bahamas": 872.2, "Aruba": 978.89, "Barbados": 940.33, "Saint Lucia": 1026.83,
    "Guyana": 1069.95, "Montserrat": 1061.5, "Belize": 1007.41, "Dominican Republic": 1181.82, "Dominica": 927.87, "British Virgin Islands": 809.8,
    "Saint Vincent and the Grenadines": 1039.67, "Anguilla": 786.9, "Puerto Rico": 1083.3,
    "Bolivia": 1302.2, "Chile": 1461.91, "Venezuela": 1476.84, # Chile and Venezuela are already in the main list, but keeping for clarity if they were intended to be distinct in certain contexts.
    "Mauritania": 1206.18, "Togo": 1162.77, "Sudan": 1120.35, "South Sudan": 948.33,
    "Benin": 1146.43, "Zimbabwe": 1092.36, "Rwanda": 1080.35, "Lesotho": 1047.88,
    "Cape Verde": 1435.32, "Angola": 1276.46, "Libya": 1182.26, "Eswatini": 966.86, "Mauritius": 903.07,
    "Gabon": 1290.35, "Kenya": 1166.19, "The Gambia": 1127.32, "Burundi": 1089.47, "Seychelles": 834.61,
    "Guinea": 1345.86, "Uganda": 1184.2, "Mozambique": 1166.7, "Botswana": 1083.56, "Somalia": 822.45,
    "Equatorial Guinea": 1238.19, "Namibia": 1152.06, "Malawi": 1109.84, "Liberia": 1039.69, "Sao Tome and Principe": 878.0,
    "Djibouti": 863.09, "Ethiopia": 1060.03, "Guinea-Bissau": 1218.4, "Sierra Leone": 1087.72,
    "North Korea": 1153.25,
    "Thailand": 1176.4, "Vietnam": 1169.96, "Syria": 1088.19, "Lebanon": 1010.42, "Tajikistan": 1100.91,
    "Bulgaria": 1365.17, "Israel": 1358.33, "Georgia": 1302.26, "Luxembourg": 1285.44, "Cyprus": 1155.24, "Kosovo": 1119.5, "Lithuania": 1062.24, "Estonia": 1007.41,
    "Latvia": 986.79, "Azerbaijan": 1159.26, "Kazakhstan": 1117.84, "Armenia": 1111.45, "Malta": 955.51, "Moldova": 909.11, "Gibraltar": 822.61,
    "San Marino": 743.08, "Liechtenstein": 724.87, "Andorra": 894.49, "Faroe Islands": 1037.13,
    "Madagascar": 1165.75, "Comoros": 1137.9, "Central African Republic": 1086.56, "Chad": 903.07,
    "Northern Ireland": 1300.0, # Placeholder, ranking not found in snippets, assuming average
    "Belarus": 1250.0, # Placeholder
    "Trinidad and Tobago": 1350.0, # Placeholder
    "Curacao": 1300.0, # Placeholder
    "Haiti": 1280.0, # Placeholder
    "Nicaragua": 1270.0, # Placeholder
    "Guatemala": 1320.0, # Placeholder
    "Jamaica": 1400.0, # Placeholder
    "Suriname": 1250.0, # Placeholder
    "El Salvador": 1200.0, # Placeholder
    "Greenland": 500.0 # Placeholder, if it ever appears
}


class Team:
    def __init__(self, name, confederation, ranking_points):
        self.name = name
        self.confederation = confederation
        self.ranking_points = ranking_points
        self.group_stats = {"Pld": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "Pts": 0}

    def __repr__(self):
        return f"Team({self.name}, {self.ranking_points:.2f})"

teams = {}


def get_team(name):
    """Retrieves a Team object by name, creating it if it doesn't exist."""
    if name not in teams:
        ranking_points = FIFA_RANKINGS.get(name, 500.0)
        teams[name] = Team(name, "Unknown", ranking_points)
    return teams[name]


def simulate_match(team1, team2):
    """Simulates a single football match between two teams based on their FIFA ranking points."""
    elo_diff = team1.ranking_points - team2.ranking_points
    base_expected_goals = 1.3
    scale_factor = 0.002
    expected_goals_team1 = base_expected_goals * math.exp(scale_factor * elo_diff)
    expected_goals_team2 = base_expected_goals * math.exp(scale_factor * -elo_diff)
    goals_team1 = max(0, int(random.gauss(expected_goals_team1, 1.0) + 0.5))
    goals_team2 = max(0, int(random.gauss(expected_goals_team2, 1.0) + 0.5))
    return goals_team1, goals_team2

def update_group_standings(standings, team_name, goals_for, goals_against):
    """Updates a team's statistics in a group standings dictionary after a match."""
    team_stats = standings[team_name]
    team_stats["Pld"] += 1
    team_stats["GF"] += goals_for
    team_stats["GA"] += goals_against
    team_stats["GD"] = team_stats["GF"] - team_stats["GA"]

    if goals_for > goals_against:
        team_stats["W"] += 1
        team_stats["Pts"] += 3
    elif goals_for == goals_against:
        team_stats["D"] += 1
        team_stats["Pts"] += 1
    else:
        team_stats["L"] += 1

def sort_group(standings_list):
    """Sorts a list of team standings based on points, goal difference, goals scored, and then FIFA ranking."""
    return sorted(standings_list, key=lambda x: (x["Pts"], x["GD"], x["GF"], get_team(x["Team"]).ranking_points), reverse=True)

def simulate_group_with_initial_standings(group_name, group_teams_names, initial_standings_data, num_qualify_direct=0, num_to_playoff=0, total_matches_per_team=None, verbose=True):
    """Simulates a group stage, starting from provided initial standings."""
    if verbose: print(f"\n--- Simulating Group: {group_name} (from initial standings) ---")
    standings = {team_name: initial_standings_data.get(team_name, {
        "Pld": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "Pts": 0
    }).copy() for team_name in group_teams_names}

    if verbose:
        print(f"Initial Standings for {group_name}:")
        print("{:<20} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5}".format(
            "Team", "Pld", "W", "D", "L", "GF", "GA", "GD", "Pts"
        ))
        for team_name in group_teams_names:
            stats = standings[team_name]
            print("{:<20} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5}".format(
                team_name, stats["Pld"], stats["W"], stats["D"], stats["L"],
                stats["GF"], stats["GA"], stats["GD"], stats["Pts"]
            ))

    if len(group_teams_names) > 1:
        legs_per_pair = 2
        if group_name.startswith("CONCACAF_Second_Round_Group_") or group_name.startswith("AFC_Fourth_Round_Group_"):
            legs_per_pair = 1
        total_possible_matches_in_group = (len(group_teams_names) * (len(group_teams_names) - 1) // 2) * legs_per_pair
        current_total_matches_played = sum(s["Pld"] for s in standings.values()) // 2
        matches_to_simulate_count = total_possible_matches_in_group - current_total_matches_played
        if verbose:
            print(f"Total possible matches in group: {total_possible_matches_in_group}")
            print(f"Current total matches played: {current_total_matches_played}")
            print(f"Matches to simulate: {matches_to_simulate_count}")

        # Simulate remaining matches
        for _ in range(matches_to_simulate_count):
            eligible_teams = [t_name for t_name in group_teams_names if standings[t_name]["Pld"] < total_matches_per_team]
            if len(eligible_teams) < 2:
                if verbose: print("Not enough eligible teams to simulate remaining matches in this group.")
                break
            team1_name, team2_name = random.sample(eligible_teams, 2)
            t1 = get_team(team1_name)
            t2 = get_team(team2_name)
            goals1, goals2 = simulate_match(t1, t2)
            update_group_standings(standings, team1_name, goals1, goals2)
            update_group_standings(standings, team2_name, goals2, goals1)

    final_standings_list = [{"Team": team_name, **stats} for team_name, stats in standings.items()]
    sorted_standings = sort_group(final_standings_list)

    if verbose:
        print(f"--- {group_name} Final Standings (after simulation) ---")
        print("{:<20} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5}".format(
            "Team", "Pld", "W", "D", "L", "GF", "GA", "GD", "Pts"
        ))
        for team_stat in sorted_standings:
            print("{:<20} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5}".format(
                team_stat["Team"], team_stat["Pld"], team_stat["W"], team_stat["D"],
                team_stat["L"], team_stat["GF"], team_stat["GA"], team_stat["GD"], team_stat["Pts"]
            ))

    qualified = [t["Team"] for t in sorted_standings[:num_qualify_direct]]
    playoff = [t["Team"] for t in sorted_standings[num_qualify_direct:num_qualify_direct + num_to_playoff]]
    remaining = [t["Team"] for t in sorted_standings[num_qualify_direct + num_to_playoff:]]

    if verbose:
        print(f"\nQualified from {group_name}: {qualified}")
        if playoff:
            print(f"Advance to next round/playoff from {group_name}: {playoff}")
    return qualified, playoff, remaining, standings


def simulate_knockout(teams_for_knockout, round_name="Knockout Round", verbose=True):
    """
    Simulates a knockout tournament recursively.
    Teams are sorted by ranking for pairing (higher ranked plays lower ranked).
    """
    if verbose: print(f"\n--- Simulating {round_name} ---")
    
    if len(teams_for_knockout) < 2:
        if teams_for_knockout:
            if verbose: print(f"Only one team left in {round_name}: {teams_for_knockout[0]} advances by default.")
            return teams_for_knockout
        if verbose: print(f"Not enough teams for {round_name}.")
        return []

    # Sort teams by ranking points to ensure higher ranked teams play lower ranked teams in a typical bracket
    teams_for_knockout.sort(key=lambda x: get_team(x).ranking_points, reverse=True)
    
    current_round_winners = []
    
    num_matches = len(teams_for_knockout) // 2
    for i in range(num_matches):
        team1_name = teams_for_knockout[i] # Higher ranked
        team2_name = teams_for_knockout[len(teams_for_knockout) - 1 - i] # Lower ranked
        
        if verbose: print(f"Match: {team1_name} vs {team2_name}")
        
        t1 = get_team(team1_name)
        t2 = get_team(team2_name)
        
        goals1, goals2 = simulate_match(t1, t2)
        
        if verbose: print(f"  {t1.name} {goals1}-{goals2} {t2.name}")
        
        if goals1 == goals2:
            # If draw, simulate extra time and penalties by giving win to higher ranked team
            if verbose: print("  Match drawn, simulating extra time and penalties (higher ranked team wins).")
            if t1.ranking_points > t2.ranking_points:
                current_round_winners.append(t1.name)
                if verbose: print(f"  {t1.name} wins.")
            else:
                current_round_winners.append(t2.name)
                if verbose: print(f"  {t2.name} wins.")
        elif goals1 > goals2:
            current_round_winners.append(t1.name)
        else:
            current_round_winners.append(t2.name)
            
    # Handle odd number of teams (one team gets a bye)
    if len(teams_for_knockout) % 2 != 0:
        bye_team = teams_for_knockout[num_matches * 2]
        current_round_winners.append(bye_team)
        if verbose: print(f"  {bye_team} gets a bye to the next round.")

    # Recursively call for the next stage if more than one winner
    if len(current_round_winners) > 1:
        return simulate_knockout(current_round_winners, round_name=f"Next Stage of {round_name}", verbose=verbose)
    else:
        # Return the single winner (or empty list if no teams)
        return current_round_winners


# --- Static Qualification Data ---
# These represent teams that have already qualified or are in a known playoff spot.
STATIC_WORLD_CUP_QUALIFIED = {
    "CONCACAF": ["Canada", "Mexico", "USA"], # Host nations
    "CONMEBOL": ["Argentina"], # Example, assuming they might have qualified early
    "AFC": ["Japan", "IR Iran", "Uzbekistan", "Korea Republic", "Jordan"], # Example direct qualifiers
    "OFC": ["New Zealand"] # Example direct qualifier
}

STATIC_INTER_CONFED_PLAYOFF_TEAMS = {
    "OFC": "New Caledonia", # Example, a specific team pre-assigned to ICP
}


# --- LIVE STANDINGS DATA ---
# This dictionary holds the current (static) standings for various qualification stages.
# In a real-world application, this data would ideally be fetched dynamically from
# an API or through robust web scraping to ensure it's always up-to-date.
# As web scraping live sports data is complex and prone to breaking due to website changes,
# this serves as a manually updated snapshot.
LIVE_STANDINGS_DATA = {
    "CONMEBOL": {
        "Argentina": {"Pld": 15, "W": 11, "D": 1, "L": 3, "GF": 27, "GA": 8, "GD": 19, "Pts": 34},
        "Ecuador": {"Pld": 15, "W": 7, "D": 6, "L": 2, "GF": 13, "GA": 5, "GD": 8, "Pts": 24},
        "Paraguay": {"Pld": 15, "W": 6, "D": 6, "L": 3, "GF": 13, "GA": 9, "GD": 4, "Pts": 24},
        "Brazil": {"Pld": 15, "W": 6, "D": 4, "L": 5, "GF": 20, "GA": 16, "GD": 4, "Pts": 22},
        "Uruguay": {"Pld": 15, "W": 5, "D": 6, "L": 4, "GF": 17, "GA": 12, "GD": 5, "Pts": 21},
        "Colombia": {"Pld": 15, "W": 5, "D": 6, "L": 4, "GF": 18, "GA": 14, "GD": 4, "Pts": 21},
        "Venezuela": {"Pld": 15, "W": 4, "D": 6, "L": 5, "GF": 15, "GA": 17, "GD": -2, "Pts": 18},
        "Bolivia": {"Pld": 15, "W": 4, "D": 2, "L": 9, "GF": 14, "GA": 32, "GD": -18, "Pts": 14},
        "Peru": {"Pld": 15, "W": 2, "D": 5, "L": 8, "GF": 6, "GA": 17, "GD": -11, "Pts": 11},
        "Chile": {"Pld": 15, "W": 2, "D": 4, "L": 9, "GF": 9, "GA": 22, "GD": -13, "Pts": 10}
    },
    "CAF": {
        "CAF_Group_A": {
            "Egypt": {"Pld": 6, "W": 5, "D": 1, "L": 0, "GF": 14, "GA": 2, "GD": 12, "Pts": 16},
            "Burkina Faso": {"Pld": 6, "W": 3, "D": 2, "L": 1, "GF": 13, "GA": 7, "GD": 6, "Pts": 11},
            "Sierra Leone": {"Pld": 6, "W": 2, "D": 2, "L": 2, "GF": 7, "GA": 7, "GD": 0, "Pts": 8},
            "Ethiopia": {"Pld": 6, "W": 1, "D": 3, "L": 2, "GF": 7, "GA": 7, "GD": 0, "Pts": 6},
            "Guinea-Bissau": {"Pld": 6, "W": 1, "D": 3, "L": 2, "GF": 5, "GA": 7, "GD": -2, "Pts": 6},
            "Djibouti": {"Pld": 6, "W": 0, "D": 1, "L": 5, "GF": 4, "GA": 20, "GD": -16, "Pts": 1},
        },
        "CAF_Group_B": {
            "DR Congo": {"Pld": 6, "W": 4, "D": 1, "L": 1, "GF": 7, "GA": 2, "GD": 5, "Pts": 13},
            "Senegal": {"Pld": 6, "W": 3, "D": 3, "L": 0, "GF": 8, "GA": 1, "GD": 7, "Pts": 12},
            "Sudan": {"Pld": 6, "W": 3, "D": 3, "L": 0, "GF": 8, "GA": 2, "GD": 6, "Pts": 12},
            "Togo": {"Pld": 6, "W": 0, "D": 4, "L": 2, "GF": 4, "GA": 7, "GD": -3, "Pts": 4},
            "South Sudan": {"Pld": 6, "W": 0, "D": 3, "L": 3, "GF": 2, "GA": 10, "GD": -8, "Pts": 3},
            "Mauritania": {"Pld": 6, "W": 0, "D": 2, "L": 4, "GF": 2, "GA": 9, "GD": -7, "Pts": 2},
        },
        "CAF_Group_C": {
            "South Africa": {"Pld": 6, "W": 4, "D": 1, "L": 1, "GF": 10, "GA": 5, "GD": 5, "Pts": 13},
            "Rwanda": {"Pld": 6, "W": 2, "D": 2, "L": 2, "GF": 4, "GA": 4, "GD": 0, "Pts": 8},
            "Benin": {"Pld": 6, "W": 2, "D": 2, "L": 2, "GF": 6, "GA": 7, "GD": -1, "Pts": 8},
            "Nigeria": {"Pld": 6, "W": 1, "D": 4, "L": 1, "GF": 7, "GA": 6, "GD": 1, "Pts": 7},
            "Lesotho": {"Pld": 6, "W": 1, "D": 3, "L": 2, "GF": 4, "GA": 5, "GD": -1, "Pts": 6},
            "Zimbabwe": {"Pld": 6, "W": 0, "D": 4, "L": 2, "GF": 5, "GA": 9, "GD": -4, "Pts": 4},
        },
        "CAF_Group_D": {
            "Cape Verde": {"Pld": 6, "W": 4, "D": 1, "L": 1, "GF": 7, "GA": 5, "GD": 2, "Pts": 13},
            "Cameroon": {"Pld": 6, "W": 3, "D": 3, "L": 0, "GF": 12, "GA": 4, "GD": 8, "Pts": 12},
            "Libya": {"Pld": 6, "W": 2, "D": 2, "L": 2, "GF": 6, "GA": 7, "GD": -1, "Pts": 8},
            "Angola": {"Pld": 6, "W": 1, "D": 4, "L": 1, "GF": 4, "GA": 4, "GD": 0, "Pts": 7},
            "Mauritius": {"Pld": 6, "W": 1, "D": 2, "L": 3, "GF": 6, "GA": 10, "GD": -4, "Pts": 5},
            "Eswatini": {"Pld": 6, "W": 0, "D": 2, "L": 4, "GF": 4, "GA": 9, "GD": -5, "Pts": 2},
        },
        "CAF_Group_E": {
            "Morocco": {"Pld": 5, "W": 5, "D": 0, "L": 0, "GF": 14, "GA": 2, "GD": 12, "Pts": 15},
            "Tanzania": {"Pld": 4, "W": 2, "D": 0, "L": 2, "GF": 2, "GA": 4, "GD": -2, "Pts": 6},
            "Zambia": {"Pld": 4, "W": 1, "D": 0, "L": 3, "GF": 6, "GA": 7, "GD": -1, "Pts": 3},
            "Niger": {"Pld": 3, "W": 1, "D": 0, "L": 2, "GF": 3, "GA": 4, "GD": -1, "Pts": 3},
            "Congo": {"Pld": 2, "W": 0, "D": 0, "L": 2, "GF": 2, "GA": 10, "GD": -8, "Pts": 0},
        },
        "CAF_Group_F": {
            "Ivory Coast": {"Pld": 6, "W": 5, "D": 1, "L": 0, "GF": 14, "GA": 0, "GD": 14, "Pts": 16},
            "Gabon": {"Pld": 6, "W": 5, "D": 0, "L": 1, "GF": 12, "GA": 6, "GD": 6, "Pts": 15},
            "Burundi": {"Pld": 6, "W": 3, "D": 1, "L": 2, "GF": 13, "GA": 7, "GD": 6, "Pts": 10},
            "Kenya": {"Pld": 6, "W": 1, "D": 3, "L": 2, "GF": 11, "GA": 8, "GD": 3, "Pts": 6},
            "Gambia": {"Pld": 6, "W": 1, "D": 1, "L": 4, "GF": 12, "GA": 13, "GD": -1, "Pts": 4},
            "Seychelles": {"Pld": 6, "W": 0, "D": 0, "L": 6, "GF": 2, "GA": 30, "GD": -28, "Pts": 0},
        },
        "CAF_Group_G": {
            "Algeria": {"Pld": 6, "W": 5, "D": 0, "L": 1, "GF": 16, "GA": 6, "GD": 10, "Pts": 15},
            "Mozambique": {"Pld": 6, "W": 4, "D": 0, "L": 2, "GF": 10, "GA": 11, "GD": -1, "Pts": 12},
            "Botswana": {"Pld": 6, "W": 3, "D": 0, "L": 3, "GF": 9, "GA": 8, "GD": 1, "Pts": 9},
            "Uganda": {"Pld": 6, "W": 3, "D": 0, "L": 3, "GF": 6, "GA": 7, "GD": -1, "Pts": 9},
            "Guinea": {"Pld": 6, "W": 2, "D": 1, "L": 3, "GF": 4, "GA": 5, "GD": -1, "Pts": 7},
            "Somalia": {"Pld": 6, "W": 0, "D": 1, "L": 5, "GF": 3, "GA": 11, "GD": -8, "Pts": 1},
        },
        "CAF_Group_H": {
            "Tunisia": {"Pld": 6, "W": 5, "D": 1, "L": 0, "GF": 9, "GA": 0, "GD": 9, "Pts": 16},
            "Equatorial Guinea": {"Pld": 6, "W": 4, "D": 1, "L": 1, "GF": 6, "GA": 2, "GD": 4, "Pts": 13},
            "Namibia": {"Pld": 6, "W": 2, "D": 3, "L": 1, "GF": 5, "GA": 3, "GD": 2, "Pts": 9},
            "Liberia": {"Pld": 6, "W": 2, "D": 1, "L": 3, "GF": 4, "GA": 5, "GD": -1, "Pts": 7},
            "Malawi": {"Pld": 6, "W": 2, "D": 0, "L": 4, "GF": 4, "GA": 6, "GD": -2, "Pts": 6},
            "Sao Tome and Principe": {"Pld": 6, "W": 0, "D": 0, "L": 6, "GF": 2, "GA": 14, "GD": -12, "Pts": 0},
        },
        "CAF_Group_I": {
            "Ghana": {"Pld": 6, "W": 5, "D": 0, "L": 1, "GF": 15, "GA": 5, "GD": 10, "Pts": 15},
            "Comoros": {"Pld": 6, "W": 4, "D": 0, "L": 2, "GF": 9, "GA": 7, "GD": 2, "Pts": 12},
            "Madagascar": {"Pld": 6, "W": 3, "D": 1, "L": 2, "GF": 9, "GA": 6, "GD": 3, "Pts": 10},
            "Mali": {"Pld": 6, "W": 2, "D": 3, "L": 1, "GF": 8, "GA": 4, "GD": 4, "Pts": 9},
            "Central African Republic": {"Pld": 6, "W": 1, "D": 2, "L": 3, "GF": 8, "GA": 13, "GD": -5, "Pts": 5},
            "Chad": {"Pld": 6, "W": 0, "D": 0, "L": 6, "GF": 1, "GA": 15, "GD": -14, "Pts": 0},
        }
    },
    "AFC": {
        "AFC_Third_Round_Group_A": {
            "IR Iran": {"Pld": 9, "W": 6, "D": 2, "L": 1, "GF": 16, "GA": 8, "GD": 8, "Pts": 20},
            "Uzbekistan": {"Pld": 9, "W": 5, "D": 3, "L": 1, "GF": 11, "GA": 7, "GD": 4, "Pts": 18},
            "United Arab Emirates": {"Pld": 9, "W": 4, "D": 2, "L": 3, "GF": 14, "GA": 7, "GD": 7, "Pts": 14},
            "Qatar": {"Pld": 9, "W": 4, "D": 1, "L": 4, "GF": 17, "GA": 21, "GD": -4, "Pts": 13},
            "Kyrgyz Republic": {"Pld": 9, "W": 2, "D": 1, "L": 6, "GF": 11, "GA": 17, "GD": -6, "Pts": 7},
            "North Korea": {"Pld": 9, "W": 0, "D": 3, "L": 6, "GF": 9, "GA": 18, "GD": -9, "Pts": 3},
        },
        "AFC_Third_Round_Group_B": {
            "South Korea": {"Pld": 9, "W": 5, "D": 4, "L": 0, "GF": 16, "GA": 7, "GD": 9, "Pts": 19},
            "Jordan": {"Pld": 9, "W": 4, "D": 4, "L": 1, "GF": 16, "GA": 7, "GD": 9, "Pts": 16},
            "Iraq": {"Pld": 9, "W": 3, "D": 3, "L": 3, "GF": 8, "GA": 9, "GD": -1, "Pts": 12},
            "Oman": {"Pld": 9, "W": 3, "D": 1, "L": 5, "GF": 8, "GA": 13, "GD": -5, "Pts": 10},
            "Palestine": {"Pld": 9, "W": 2, "D": 3, "L": 4, "GF": 9, "GA": 12, "GD": -3, "Pts": 9},
            "Kuwait": {"Pld": 9, "W": 0, "D": 5, "L": 4, "GF": 7, "GA": 16, "GD": -9, "Pts": 5},
        },
        "AFC_Third_Round_Group_C": {
            "Japan": {"Pld": 9, "W": 6, "D": 2, "L": 1, "GF": 24, "GA": 3, "GD": 21, "Pts": 20},
            "Australia": {"Pld": 9, "W": 4, "D": 4, "L": 1, "GF": 14, "GA": 6, "GD": 8, "Pts": 16},
            "Saudi Arabia": {"Pld": 9, "W": 3, "D": 4, "L": 2, "GF": 6, "GA": 6, "GD": 0, "Pts": 13},
            "Indonesia": {"Pld": 9, "W": 3, "D": 3, "L": 3, "GF": 9, "GA": 14, "GD": -5, "Pts": 12},
            "Bahrain": {"Pld": 9, "W": 1, "D": 3, "L": 5, "GF": 5, "GA": 15, "GD": -10, "Pts": 6},
            "China PR": {"Pld": 9, "W": 2, "D": 0, "L": 7, "GF": 6, "GA": 20, "GD": -14, "Pts": 6},
        }
    },
    "CONCACAF_Second_Round": {
        "CONCACAF_Second_Round_Group_A": {
            "Honduras": {"Pld": 2, "W": 2, "D": 0, "L": 0, "GF": 7, "GA": 0, "GD": 7, "Pts": 6},
            "Cuba": {"Pld": 2, "W": 1, "D": 0, "L": 1, "GF": 1, "GA": 1, "GD": 0, "Pts": 3},
            "Cayman Islands": {"Pld": 2, "W": 1, "D": 0, "L": 1, "GF": 2, "GA": 2, "GD": 0, "Pts": 3},
            "Antigua and Barbuda": {"Pld": 2, "W": 0, "D": 1, "L": 1, "GF": 1, "GA": 2, "GD": -1, "Pts": 1},
            "Bermuda": {"Pld": 2, "W": 0, "D": 1, "L": 1, "GF": 2, "GA": 7, "GD": -5, "Pts": 1},
        },
        "CONCACAF_Second_Round_Group_B": {
            "Costa Rica": {"Pld": 2, "W": 2, "D": 0, "L": 0, "GF": 7, "GA": 0, "GD": 7, "Pts": 6},
            "Trinidad and Tobago": {"Pld": 2, "W": 1, "D": 1, "L": 0, "GF": 6, "GA": 0, "GD": 6, "Pts": 4},
            "Saint Kitts and Nevis": {"Pld": 2, "W": 1, "D": 0, "L": 1, "GF": 1, "GA": 3, "GD": -2, "Pts": 3},
            "Grenada": {"Pld": 2, "W": 0, "D": 1, "L": 1, "GF": 1, "GA": 3, "GD": -2, "Pts": 1},
            "Bahamas": {"Pld": 2, "W": 0, "D": 0, "L": 2, "GF": 0, "GA": 7, "GD": -7, "Pts": 0},
        },
        "CONCACAF_Second_Round_Group_C": {
            "Curacao": {"Pld": 2, "W": 2, "D": 0, "L": 0, "GF": 5, "GA": 0, "GD": 5, "Pts": 6},
            "Haiti": {"Pld": 2, "W": 2, "D": 0, "L": 0, "GF": 3, "GA": 0, "GD": 3, "Pts": 6},
            "Saint Lucia": {"Pld": 2, "W": 0, "D": 1, "L": 1, "GF": 0, "GA": 1, "GD": -1, "Pts": 1},
            "Aruba": {"Pld": 2, "W": 0, "D": 1, "L": 1, "GF": 0, "GA": 2, "GD": -2, "Pts": 1},
            "Barbados": {"Pld": 2, "W": 0, "D": 0, "L": 2, "GF": 0, "GA": 5, "GD": -5, "Pts": 0},
        },
        "CONCACAF_Second_Round_Group_D": {
            "Nicaragua": {"Pld": 2, "W": 2, "D": 0, "L": 0, "GF": 7, "GA": 0, "GD": 7, "Pts": 6},
            "Panama": {"Pld": 2, "W": 2, "D": 0, "L": 0, "GF": 4, "GA": 0, "GD": 4, "Pts": 6},
            "Guyana": {"Pld": 2, "W": 1, "D": 0, "L": 1, "GF": 1, "GA": 1, "GD": 0, "Pts": 3},
            "Montserrat": {"Pld": 2, "W": 0, "D": 0, "L": 2, "GF": 0, "GA": 5, "GD": -5, "Pts": 0},
            "Belize": {"Pld": 2, "W": 0, "D": 0, "L": 2, "GF": 0, "GA": 6, "GD": -6, "Pts": 0},
        },
        "CONCACAF_Second_Round_Group_E": {
            "Guatemala": {"Pld": 2, "W": 2, "D": 0, "L": 0, "GF": 9, "GA": 0, "GD": 9, "Pts": 6},
            "Jamaica": {"Pld": 2, "W": 2, "D": 0, "L": 0, "GF": 2, "GA": 0, "GD": 2, "Pts": 6},
            "Dominican Republic": {"Pld": 2, "W": 1, "D": 0, "L": 1, "GF": 3, "GA": 0, "GD": 3, "Pts": 3},
            "Dominica": {"Pld": 2, "W": 0, "D": 0, "L": 2, "GF": 0, "GA": 7, "GD": -7, "Pts": 0},
            "British Virgin Islands": {"Pld": 2, "W": 0, "D": 0, "L": 2, "GF": 0, "GA": 7, "GD": -7, "Pts": 0},
        },
        "CONCACAF_Second_Round_Group_F": {
            "Suriname": {"Pld": 2, "W": 2, "D": 0, "L": 0, "GF": 7, "GA": 0, "GD": 7, "Pts": 6},
            "Puerto Rico": {"Pld": 2, "W": 1, "D": 1, "L": 0, "GF": 8, "GA": 0, "GD": 8, "Pts": 4},
            "El Salvador": {"Pld": 2, "W": 1, "D": 1, "L": 0, "GF": 2, "GA": 0, "GD": 2, "Pts": 4},
            "Saint Vincent and the Grenadines": {"Pld": 2, "W": 0, "D": 0, "L": 2, "GF": 0, "GA": 5, "GD": -5, "Pts": 0},
            "Anguilla": {"Pld": 2, "W": 0, "D": 0, "L": 2, "GF": 0, "GA": 12, "GD": -12, "Pts": 0},
        },
    },
    "UEFA": {
        # UEFA group data from your original code remains, as live fetching was not possible.
        # These are placeholders and would need to be updated with actual data.
        "UEFA_Group_A": {},
        "UEFA_Group_B": {},
        "UEFA_Group_C": {},
        "UEFA_Group_D": {},
        "UEFA_Group_E": {},
        "UEFA_Group_F": {},
        "UEFA_Group_G": {
            "Poland": {"Pld": 2, "W": 2, "D": 0, "L": 0, "GF": 3, "GA": 0, "GD": 3, "Pts": 6},
            "Finland": {"Pld": 2, "W": 1, "D": 1, "L": 0, "GF": 1, "GA": 0, "GD": 1, "Pts": 4},
            "Lithuania": {"Pld": 2, "W": 0, "D": 1, "L": 1, "GF": 0, "GA": 1, "GD": -1, "Pts": 1},
            "Netherlands": {"Pld": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "Pts": 0},
            "Malta": {"Pld": 2, "W": 0, "D": 0, "L": 2, "GF": 0, "GA": 3, "GD": -3, "Pts": 0},
        },
        "UEFA_Group_H": {
            "Bosnia and Herzegovina": {"Pld": 2, "W": 2, "D": 0, "L": 0, "GF": 2, "GA": 0, "GD": 2, "Pts": 6},
            "Romania": {"Pld": 2, "W": 1, "D": 0, "L": 1, "GF": 3, "GA": 0, "GD": 3, "Pts": 3},
            "Cyprus": {"Pld": 2, "W": 1, "D": 0, "L": 1, "GF": 1, "GA": 0, "GD": 1, "Pts": 3},
            "Austria": {"Pld": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "Pts": 0},
            "San Marino": {"Pld": 2, "W": 0, "D": 0, "L": 2, "GF": 0, "GA": 6, "GD": -6, "Pts": 0},
        },
        "UEFA_Group_I": {
            "Norway": {"Pld": 2, "W": 2, "D": 0, "L": 0, "GF": 7, "GA": 0, "GD": 7, "Pts": 6},
            "Estonia": {"Pld": 2, "W": 1, "D": 0, "L": 1, "GF": 0, "GA": 0, "GD": 0, "Pts": 3},
            "Israel": {"Pld": 2, "W": 1, "D": 0, "L": 1, "GF": 0, "GA": 1, "GD": -1, "Pts": 3},
            "Italy": {"Pld": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "Pts": 0},
            "Moldova": {"Pld": 2, "W": 0, "D": 0, "L": 2, "GF": 0, "GA": 6, "GD": -6, "Pts": 0},
        },
        "UEFA_Group_J": {
            "North Macedonia": {"Pld": 2, "W": 1, "D": 1, "L": 0, "GF": 3, "GA": 0, "GD": 3, "Pts": 4},
            "Wales": {"Pld": 2, "W": 1, "D": 1, "L": 0, "GF": 2, "GA": 0, "GD": 2, "Pts": 4},
            "Kazakhstan": {"Pld": 2, "W": 1, "D": 0, "L": 1, "GF": 0, "GA": 0, "GD": 0, "Pts": 3},
            "Belgium": {"Pld": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "Pts": 0},
            "Liechtenstein": {"Pld": 2, "W": 0, "D": 0, "L": 2, "GF": 0, "GA": 5, "GD": -5, "Pts": 0},
        }
    }
}


def simulate_afc_qualifying(verbose=True):
    """
    Simulates the AFC (Asia) World Cup qualifying process.
    """
    if verbose: print(f"\n\n===== Simulating AFC World Cup Qualifying =====")
    afc_qualified_paths = []
    
    # Add statically qualified teams (if any)
    for team_name in STATIC_WORLD_CUP_QUALIFIED["AFC"]:
        afc_qualified_paths.append((team_name, "AFC Direct (Pre-qualified)"))

    # Define AFC Third Round groups with teams, excluding those already pre-qualified
    afc_third_round_groups = {
        "AFC_Third_Round_Group_A": [t for t in LIVE_STANDINGS_DATA["AFC"]["AFC_Third_Round_Group_A"].keys() if t not in [item[0] for item in afc_qualified_paths]],
        "AFC_Third_Round_Group_B": [t for t in LIVE_STANDINGS_DATA["AFC"]["AFC_Third_Round_Group_B"].keys() if t not in [item[0] for item in afc_qualified_paths]],
        "AFC_Third_Round_Group_C": [t for t in LIVE_STANDINGS_DATA["AFC"]["AFC_Third_Round_Group_C"].keys() if t not in [item[0] for item in afc_qualified_paths]],
    }
    
    afc_fourth_round_teams = []
    
    # Simulate each Third Round group
    for group_name, teams_in_group in afc_third_round_groups.items():
        if not teams_in_group:
            if verbose: print(f"Skipping empty group: {group_name}")
            continue
        
        # Get initial standings for the group from LIVE_STANDINGS_DATA
        initial_group_data = {t_name: LIVE_STANDINGS_DATA["AFC"][group_name][t_name] for t_name in teams_in_group}

        direct_qualifiers, playoff_teams, _, _ = simulate_group_with_initial_standings(
            group_name, teams_in_group, initial_group_data, num_qualify_direct=2, num_to_playoff=2,
            total_matches_per_team=10, verbose=verbose
        )
        for team in direct_qualifiers:
            afc_qualified_paths.append((team, "AFC Direct (Third Round)"))
        afc_fourth_round_teams.extend(playoff_teams) # Runners-up advance to Fourth Round

    if verbose: print("\n--- AFC Fourth Round ---")
    
    random.shuffle(afc_fourth_round_teams) # Randomize order for group assignment
    # Create Fourth Round groups (2 groups of 3)
    if len(afc_fourth_round_teams) >= 6:
        afc_fourth_round_groups = {
            "AFC_Fourth_Round_Group_X": afc_fourth_round_teams[0:3],
            "AFC_Fourth_Round_Group_Y": afc_fourth_round_teams[3:6],
        }
    else:
        # Handle cases with fewer than 6 teams (e.g., if simulation path led to less teams)
        if verbose: print(f"Not enough teams ({len(afc_fourth_round_teams)}) for AFC Fourth Round, proceeding with available.")
        if len(afc_fourth_round_teams) > 0:
            afc_fourth_round_groups = {"AFC_Fourth_Round_Group_X": afc_fourth_round_teams}
        else:
            afc_fourth_round_groups = {}
    
    afc_fifth_round_teams = []
    
    # Simulate each Fourth Round group
    for group_name, teams_in_group in afc_fourth_round_groups.items():
        if not teams_in_group: continue
        # For Fourth Round, assume starting fresh as no initial standings provided for it.
        direct_qualifiers, playoff_teams, _, _ = simulate_group_with_initial_standings(
            group_name, teams_in_group, {}, num_qualify_direct=1, num_to_playoff=1,
            total_matches_per_team=2, # Assuming 2 matches per team in this round
            verbose=verbose
        )
        for team in direct_qualifiers:
            afc_qualified_paths.append((team, "AFC Direct (Fourth Round)"))
        afc_fifth_round_teams.extend(playoff_teams) # Runners-up advance to Fifth Round

    afc_playoff_participant = None
    if verbose: print("\n--- AFC Fifth Round ---")
    
    # Simulate AFC Playoff (Fifth Round)
    if len(afc_fifth_round_teams) == 2:
        if verbose: print(f"AFC Playoff Match: {afc_fifth_round_teams[0]} vs {afc_fifth_round_teams[1]}")
        winner = simulate_knockout(afc_fifth_round_teams, round_name="AFC Playoff", verbose=verbose)
        if winner:
            afc_playoff_participant = winner[0]
            if verbose: print(f"AFC Inter-confederation Playoff participant: {afc_playoff_participant}")
    elif len(afc_fifth_round_teams) == 1:
        # If only one team remains, they advance by default
        afc_playoff_participant = afc_fifth_round_teams[0]
        if verbose: print(f"AFC Inter-confederation Playoff participant (by default): {afc_playoff_participant}")
    else:
        if verbose: print("Not enough teams for AFC Fifth Round playoff or unexpected number.")

    return afc_qualified_paths, afc_playoff_participant


def simulate_caf_qualifying(verbose=True):
    """
    Simulates the CAF (Africa) World Cup qualifying process.
    """
    if verbose: print(f"\n\n===== Simulating CAF World Cup Qualifying =====")
    caf_qualified_paths = []

    # Define CAF group initial teams (assuming these are fixed groups)
    caf_groups_initial_teams = {
        "CAF_Group_A": ["Egypt", "Burkina Faso", "Guinea-Bissau", "Sierra Leone", "Ethiopia", "Djibouti"],
        "CAF_Group_B": ["DR Congo", "Senegal", "Sudan", "Togo", "South Sudan", "Mauritania"],
        "CAF_Group_C": ["South Africa", "Rwanda", "Benin", "Nigeria", "Lesotho", "Zimbabwe"],
        "CAF_Group_D": ["Cape Verde", "Cameroon", "Libya", "Angola", "Mauritius", "Eswatini"],
        "CAF_Group_E": ["Morocco", "Tanzania", "Zambia", "Niger", "Congo"], # Note: Group E has 5 teams
        "CAF_Group_F": ["Ivory Coast", "Gabon", "Burundi", "Kenya", "Gambia", "Seychelles"],
        "CAF_Group_G": ["Algeria", "Mozambique", "Botswana", "Uganda", "Guinea", "Somalia"],
        "CAF_Group_H": ["Tunisia", "Equatorial Guinea", "Namibia", "Liberia", "Malawi", "Sao Tome and Principe"],
        "CAF_Group_I": ["Ghana", "Comoros", "Madagascar", "Mali", "Central African Republic", "Chad"]
    }
    
    group_runners_up_for_selection = [] # To select best runners-up for playoff

    # Simulate each CAF group
    for group_name, teams_in_group_list in caf_groups_initial_teams.items():
        if not teams_in_group_list: continue

        # Get initial standings for the group from LIVE_STANDINGS_DATA
        initial_group_data = LIVE_STANDINGS_DATA["CAF"].get(group_name, {})
        
        # Determine total matches per team based on group size
        if group_name == "CAF_Group_E":
            total_matches_per_team = 8 # (5 teams * 4 matches each / 2 matches per pair = 10 total matches, 8 matches per team)
        else:
            total_matches_per_team = 10 # (6 teams * 5 matches each / 2 matches per pair = 15 total matches, 10 matches per team)

        qualified_from_group, runner_up, _, _ = simulate_group_with_initial_standings(
            group_name, teams_in_group_list, initial_group_data, num_qualify_direct=1, num_to_playoff=1,
            total_matches_per_team=total_matches_per_team, verbose=verbose
        )
        for team in qualified_from_group:
            caf_qualified_paths.append((team, "CAF Direct (Group Winner)"))
        if runner_up:
            group_runners_up_for_selection.append({
                "team": runner_up[0],
                "ranking_points": get_team(runner_up[0]).ranking_points,
            })
            
    # Sort runners-up by ranking points to pick the top 4 for playoff
    group_runners_up_for_selection.sort(key=lambda x: x["ranking_points"], reverse=True)
    caf_playoff_candidates = [s["team"] for s in group_runners_up_for_selection[:4]]

    caf_playoff_participant = None
    if verbose: print("\n--- CAF Play-off Stage ---")

    # Simulate CAF Play-off (single knockout to determine one ICP participant)
    if len(caf_playoff_candidates) >= 2:
        if verbose: print(f"CAF Playoff participants (top 4 runners-up by ranking): {caf_playoff_candidates}")
        # Assuming a single knockout to determine the one ICP spot from these 4.
        # This will simulate a mini-tournament among the top 4.
        winner = simulate_knockout(caf_playoff_candidates, round_name="CAF Playoff", verbose=verbose)
        if winner:
            caf_playoff_participant = winner[0]
            if verbose: print(f"CAF Inter-confederation Playoff participant: {caf_playoff_participant}")
    elif len(caf_playoff_candidates) == 1:
        # If only one candidate, they advance by default
        caf_playoff_participant = caf_playoff_candidates[0]
        if verbose: print(f"CAF Inter-confederation Playoff participant (by default): {caf_playoff_participant}")
    else:
        if verbose: print("Not enough teams for CAF Playoff stage.")

    return caf_qualified_paths, caf_playoff_participant


def simulate_concacaf_qualifying(verbose=True):
    """
    Simulates the CONCACAF (North, Central America, and Caribbean) World Cup qualifying process.
    """
    if verbose: print(f"\n\n===== Simulating CONCACAF World Cup Qualifying =====")
    concacaf_qualified_paths = []

    # Host nations are pre-qualified
    for team_name in STATIC_WORLD_CUP_QUALIFIED["CONCACAF"]:
        concacaf_qualified_paths.append((team_name, "CONCACAF Host Nation"))

    # Define CONCACAF Second Round groups with teams
    concacaf_second_round_groups_teams = {
        "CONCACAF_Second_Round_Group_A": list(LIVE_STANDINGS_DATA["CONCACAF_Second_Round"]["CONCACAF_Second_Round_Group_A"].keys()),
        "CONCACAF_Second_Round_Group_B": list(LIVE_STANDINGS_DATA["CONCACAF_Second_Round"]["CONCACAF_Second_Round_Group_B"].keys()),
        "CONCACAF_Second_Round_Group_C": list(LIVE_STANDINGS_DATA["CONCACAF_Second_Round"]["CONCACAF_Second_Round_Group_C"].keys()),
        "CONCACAF_Second_Round_Group_D": list(LIVE_STANDINGS_DATA["CONCACAF_Second_Round"]["CONCACAF_Second_Round_Group_D"].keys()),
        "CONCACAF_Second_Round_Group_E": list(LIVE_STANDINGS_DATA["CONCACAF_Second_Round"]["CONCACAF_Second_Round_Group_E"].keys()),
        "CONCACAF_Second_Round_Group_F": list(LIVE_STANDINGS_DATA["CONCACAF_Second_Round"]["CONCACAF_Second_Round_Group_F"].keys()),
    }
    
    concacaf_third_round_teams = []

    # Simulate each Second Round group
    for group_name, teams_in_group_list in concacaf_second_round_groups_teams.items():
        if not teams_in_group_list: continue
        
        initial_group_data = LIVE_STANDINGS_DATA["CONCACAF_Second_Round"].get(group_name, {})

        # Top 1 from each group qualifies to Third Round (direct), 2nd place also advances (runner-up for simulation)
        qualified_from_group, runner_up, _, _ = simulate_group_with_initial_standings(
            group_name, teams_in_group_list, initial_group_data, num_qualify_direct=1, num_to_playoff=1,
            total_matches_per_team=4, # Each team plays 4 matches in Second Round
            verbose=verbose
        )
        concacaf_third_round_teams.extend(qualified_from_group)
        if runner_up:
            concacaf_third_round_teams.extend(runner_up) # Both winner and runner-up go to Third Round

    concacaf_icp_participants = []
    if verbose: print("\n--- CONCACAF Third Round ---")
    
    random.shuffle(concacaf_third_round_teams) # Randomize teams for Third Round group draw
    # Create Third Round groups (3 groups of 4 teams each)
    if len(concacaf_third_round_teams) >= 12:
        concacaf_third_round_groups = {
            "CONCACAF_Third_Round_Group_1": concacaf_third_round_teams[0:4],
            "CONCACAF_Third_Round_Group_2": concacaf_third_round_teams[4:8],
            "CONCACAF_Third_Round_Group_3": concacaf_third_round_teams[8:12],
        }
    else:
        # Handle cases with fewer than 12 teams
        if verbose: print(f"Not enough teams ({len(concacaf_third_round_teams)}) for CONCACAF Third Round, proceeding with available.")
        concacaf_third_round_groups = {}
        # Distribute available teams into groups of 4
        for i in range(len(concacaf_third_round_teams) // 4):
            concacaf_third_round_groups[f"CONCACAF_Third_Round_Group_{i+1}"] = concacaf_third_round_teams[i*4:(i+1)*4]
        # If there's a remainder, put them in a final partial group
        if len(concacaf_third_round_teams) % 4 != 0 and len(concacaf_third_round_teams) > 0:
            concacaf_third_round_groups[f"CONCACAF_Third_Round_Group_X_Remainder"] = concacaf_third_round_teams[-(len(concacaf_third_round_teams) % 4):]


    concacaf_runners_up_stats = []

    # Simulate each Third Round group
    for group_name, teams_in_group in concacaf_third_round_groups.items():
        if not teams_in_group: continue
        # Top 1 from each group qualifies directly to World Cup, 2nd place advances to ICP
        direct_qualifiers, runner_up, _, _ = simulate_group_with_initial_standings(
            group_name, teams_in_group, {}, num_qualify_direct=1, num_to_playoff=1,
            total_matches_per_team=6, # Each team plays 6 matches in Third Round
            verbose=verbose
        )
        for team in direct_qualifiers:
            concacaf_qualified_paths.append((team, "CONCACAF Direct (Group Winner)"))
        if runner_up:
            concacaf_runners_up_stats.append({
                "team": runner_up[0],
                "ranking_points": get_team(runner_up[0]).ranking_points,
            })
            
    # The two best runners-up advance to the Inter-confederation Playoff
    concacaf_runners_up_stats.sort(key=lambda x: x["ranking_points"], reverse=True)
    concacaf_icp_participants = [s["team"] for s in concacaf_runners_up_stats[:2]]
    
    if len(concacaf_icp_participants) >= 2:
        if verbose: print(f"CONCACAF Inter-confederation Playoff participants: {concacaf_icp_participants}")
    elif concacaf_icp_participants:
        if verbose: print(f"CONCACAF Inter-confederation Playoff participants (partial): {concacaf_icp_participants}")
    else:
        if verbose: print("Not enough CONCACAF teams for ICP slots.")

    return concacaf_qualified_paths, concacaf_icp_participants


def simulate_conmebol_qualifying(verbose=True):
    """
    Simulates the CONMEBOL (South America) World Cup qualifying process.
    """
    if verbose: print(f"\n\n===== Simulating CONMEBOL World Cup Qualifying =====")
    conmebol_qualified_paths = []
    conmebol_playoff_participant = None

    # Add statically qualified teams (if any)
    for team_name in STATIC_WORLD_CUP_QUALIFIED["CONMEBOL"]:
        conmebol_qualified_paths.append((team_name, "CONMEBOL Direct (Pre-qualified)"))

    conmebol_teams = list(LIVE_STANDINGS_DATA["CONMEBOL"].keys())
    
    if verbose:
        print("Simulating CONMEBOL league from current standings (15 matches per team played, 3 remaining).")

    initial_conmebol_standings = LIVE_STANDINGS_DATA["CONMEBOL"]

    # Simulate the CONMEBOL single league format
    _, _, _, final_conmebol_standings_dict = simulate_group_with_initial_standings(
        "CONMEBOL_League", conmebol_teams, initial_conmebol_standings,
        num_qualify_direct=0, num_to_playoff=0, # Direct and playoff spots are determined *after* the league
        total_matches_per_team=18, # Total matches in the league (home and away against 9 opponents)
        verbose=verbose
    )

    # Convert dictionary standings back to list for sorting
    conmebol_final_standings_list = []
    for team_name in conmebol_teams:
        conmebol_final_standings_list.append({"Team": team_name, **final_conmebol_standings_dict.get(team_name, {})})
    
    sorted_standings = sort_group(conmebol_final_standings_list)
    
    # Top 6 qualify directly
    for t in sorted_standings[:6]:
        conmebol_qualified_paths.append((t["Team"], "CONMEBOL Direct (Top 6)"))
    
    # 7th place goes to Inter-confederation Playoff
    if len(sorted_standings) >= 7:
        conmebol_playoff_participant = sorted_standings[6]["Team"]
        if verbose: print(f"CONMEBOL Inter-confederation Playoff participant: {conmebol_playoff_participant}")
    else:
        if verbose: print("Not enough teams in CONMEBOL league to determine 7th place for playoff spot.")

    return conmebol_qualified_paths, conmebol_playoff_participant


def simulate_ofc_qualifying(verbose=True):
    """
    Simulates the OFC (Oceania) World Cup qualifying process.
    Currently, this confederation typically has one direct ICP participant.
    """
    if verbose: print(f"\n\n===== Simulating OFC World Cup Qualifying =====")
    ofc_qualified_paths = []

    # Add statically qualified teams (if any, typically New Zealand is a strong candidate)
    for team_name in STATIC_WORLD_CUP_QUALIFIED["OFC"]:
        ofc_qualified_paths.append((team_name, "OFC Direct (Pre-qualified)"))
    
    # OFC's typical path is one team to the inter-confederation playoff
    ofc_playoff_participant = STATIC_INTER_CONFED_PLAYOFF_TEAMS.get("OFC", None)
    if ofc_playoff_participant:
        if verbose: print(f"OFC Inter-confederation Playoff participant (already known): {ofc_playoff_participant}")

    return ofc_qualified_paths, ofc_playoff_participant


def simulate_uefa_qualifying(verbose=True):
    """
    Simulates the UEFA (Europe) World Cup qualifying process.
    12 direct qualifiers (group winners) and 4 playoff qualifiers.
    """
    if verbose: print(f"\n\n===== Simulating UEFA World Cup Qualifying =====")
    uefa_qualified_paths = []
    
    # UEFA teams pool for group assignment (your original list, modified slightly for completeness)
    uefa_teams_pool = [
        "Spain", "France", "England", "Belgium", "Italy", "Germany",
        "Netherlands", "Portugal", "Croatia", "Switzerland", "Denmark", "Austria",
        "Ukraine", "Türkiye", "Sweden", "Wales", "Serbia", "Poland", "Russia",
        "Hungary", "Norway", "Czechia", "Greece", "Scotland", "Romania",
        "Slovakia", "Slovenia", "Republic of Ireland", "North Macedonia",
        "Bosnia and Herzegovina", "Finland", "Iceland", "Albania",
        "Bulgaria", "Israel", "Georgia", "Luxembourg", "Cyprus", "Kosovo", "Lithuania", "Estonia",
        "Latvia", "Azerbaijan", "Kazakhstan", "Armenia", "Malta", "Moldova", "Gibraltar",
        "San Marino", "Liechtenstein", "Andorra", "Faroe Islands",
        # Added teams from CONCACAF/CAF if they were in UEFA initially or for general pool:
        "Northern Ireland", "Belarus", "Trinidad and Tobago", "Curacao", "Haiti",
        "Nicaragua", "Guatemala", "Jamaica", "Suriname", "El Salvador"
    ]
    random.shuffle(uefa_teams_pool) # Shuffle to simulate random group draw

    # UEFA groups, some pre-filled, some to be filled from the pool
    uefa_groups_teams = {
        "UEFA_Group_A": ["Germany", "Luxembourg", "Northern Ireland", "Slovakia"],
        "UEFA_Group_B": ["Kosovo", "Slovenia", "Sweden", "Switzerland"],
        "UEFA_Group_C": ["Belarus", "Denmark", "Greece", "Scotland"],
        "UEFA_Group_D": ["Azerbaijan", "France", "Iceland", "Ukraine"],
        "UEFA_Group_E": ["Bulgaria", "Georgia", "Spain", "Türkiye"],
        "UEFA_Group_F": ["Armenia", "Hungary", "Portugal", "Republic of Ireland"],
        "UEFA_Group_G": ["Poland", "Finland", "Lithuania", "Netherlands", "Malta"],
        "UEFA_Group_H": ["Bosnia and Herzegovina", "Romania", "Cyprus", "Austria", "San Marino"],
        "UEFA_Group_I": ["Norway", "Estonia", "Israel", "Italy", "Moldova"],
        "UEFA_Group_J": ["North Macedonia", "Wales", "Kazakhstan", "Belgium", "Liechtenstein"],
        "UEFA_Group_K": [], # Will be filled dynamically
        "UEFA_Group_L": [], # Will be filled dynamically
    }

    # Track already assigned teams to avoid duplication
    assigned_teams = set()
    for group_teams in uefa_groups_teams.values():
        assigned_teams.update(group_teams)
    
    # Add unassigned teams from the general pool to new groups (K and L)
    unassigned_uefa_teams = [t for t in uefa_teams_pool if t not in assigned_teams]
    random.shuffle(unassigned_uefa_teams)

    # Distribute remaining teams into UEFA groups K and L (assuming groups of 4)
    if len(unassigned_uefa_teams) >= 4:
        uefa_groups_teams["UEFA_Group_K"] = unassigned_uefa_teams[0:4]
        unassigned_uefa_teams = unassigned_uefa_teams[4:]
    if len(unassigned_uefa_teams) >= 4:
        uefa_groups_teams["UEFA_Group_L"] = unassigned_uefa_teams[0:4]
        unassigned_uefa_teams = unassigned_uefa_teams[4:]
    elif len(unassigned_uefa_teams) > 0:
         # If less than 4 remain, add them to Group L (or K if L is empty)
         if not uefa_groups_teams["UEFA_Group_L"]:
             uefa_groups_teams["UEFA_Group_L"].extend(unassigned_uefa_teams)
         else:
             uefa_groups_teams["UEFA_Group_K"].extend(unassigned_uefa_teams) # Add to K if L is already started
         unassigned_uefa_teams = [] # Clear unassigned after distribution


    all_runners_up_stats = []

    # Simulate each UEFA group stage
    for group_name, teams_in_group_list in uefa_groups_teams.items():
        if not teams_in_group_list: continue # Skip empty groups

        initial_group_data = LIVE_STANDINGS_DATA["UEFA"].get(group_name, {}) # Get initial standings if available
        
        # Determine total matches based on group size
        if len(teams_in_group_list) == 4:
            total_matches_per_team = 6 # Each team plays 6 matches (home/away against 3 opponents)
        else: # Assuming 5 teams
            total_matches_per_team = 8 # Each team plays 8 matches (home/away against 4 opponents)

        # 1st place qualifies directly, 2nd place goes to playoff
        direct_qualifier, runner_up, _, _ = simulate_group_with_initial_standings(
            group_name, teams_in_group_list, initial_group_data, num_qualify_direct=1, num_to_playoff=1,
            total_matches_per_team=total_matches_per_team, verbose=verbose
        )
        for team in direct_qualifier:
            uefa_qualified_paths.append((team, "UEFA Direct (Group Winner)"))
        if runner_up:
            all_runners_up_stats.append({
                "team": runner_up[0],
                "ranking_points": get_team(runner_up[0]).ranking_points,
            })
    
    if verbose: print("\n--- UEFA Play-off Stage ---")

    # The 12 group runners-up are joined by the 4 best-ranked Nations League group winners
    # who have not qualified directly or finished as group runners-up.
    # For simulation, we'll pick 4 highest ranked teams from the remaining pool for UNL winners.
    unl_winners_candidates = [t for t in uefa_teams_pool if t not in [item[0] for item in uefa_qualified_paths] and t not in [s["team"] for s in all_runners_up_stats]]
    unl_winners_candidates.sort(key=lambda x: get_team(x).ranking_points, reverse=True)
    
    extra_playoff_teams = unl_winners_candidates[:4] # Top 4 remaining high-ranked teams
    
    uefa_playoff_pool = [s["team"] for s in all_runners_up_stats] + extra_playoff_teams
    
    if len(uefa_playoff_pool) < 16 and verbose:
        print(f"Warning: Not enough teams for UEFA playoff stage (expected 16, got {len(uefa_playoff_pool)}). Simulating with available teams.")
    
    random.shuffle(uefa_playoff_pool) # Shuffle for playoff draw

    final_uefa_qualifiers_from_playoffs = []
    
    # Simulate 4 playoff paths, each with 4 teams (semi-finals and a final)
    # Each path provides one qualifier.
    num_paths_to_simulate = min(4, len(uefa_playoff_pool) // 4)
    # If there are fewer than 4 full paths but at least 2 teams, simulate one path.
    if num_paths_to_simulate == 0 and len(uefa_playoff_pool) >= 2:
        num_paths_to_simulate = 1

    for i in range(num_paths_to_simulate):
        path_teams = uefa_playoff_pool[i*4 : min((i+1)*4, len(uefa_playoff_pool))]
        if not path_teams: continue
        if verbose: print(f"\nUEFA Playoff Path {i+1} teams: {path_teams}")
        path_winner = simulate_knockout(path_teams, round_name=f"UEFA Playoff Path {i+1}", verbose=verbose)
        if path_winner:
            for team in path_winner:
                final_uefa_qualifiers_from_playoffs.append((team, "UEFA Playoff Winner"))
            
    # Fallback if structured playoff paths are not possible due to insufficient teams
    if not final_uefa_qualifiers_from_playoffs and uefa_playoff_pool:
        if verbose: print(f"Not enough teams for structured UEFA Playoff paths. Assigning highest ranked remaining teams.")
        uefa_playoff_pool.sort(key=lambda x: get_team(x).ranking_points, reverse=True)
        # Take the top 4 remaining teams as playoff qualifiers if structure fails
        for team in uefa_playoff_pool[:min(4, len(uefa_playoff_pool))]:
             final_uefa_qualifiers_from_playoffs.append((team, "UEFA Playoff Winner (Fallback)"))


    uefa_qualified_paths.extend(final_uefa_qualifiers_from_playoffs)

    return uefa_qualified_paths, None # UEFA does not send teams to Inter-confederation Playoff


def simulate_inter_confederation_playoffs(icp_participants_dict, verbose=True):
    """
    Simulates the Inter-confederation Play-offs.
    This typically involves six teams competing for two World Cup spots.
    The structure is usually semi-finals and finals, with two seeded teams getting a bye to the finals.
    """
    if verbose: print(f"\n\n===== Simulating Inter-confederation Play-offs =====")
    icp_qualified_paths = []

    icp_teams_list = []
    for conf, teams_or_team in icp_participants_dict.items():
        if isinstance(teams_or_team, list):
            icp_teams_list.extend(teams_or_team)
        elif teams_or_team:
            icp_teams_list.append(teams_or_team)
            
    # Ensure there are 6 teams for the ICP structure, add dummies if necessary
    if len(icp_teams_list) < 6:
        if verbose: print(f"Warning: Not enough teams for Inter-confederation Play-offs (expected 6, got {len(icp_teams_list)}). Adding dummy teams if necessary for simulation structure.")
        num_dummies = 6 - len(icp_teams_list)
        for i in range(num_dummies):
            dummy_team_name = f"Dummy_ICP_Team_{i+1}"
            get_team(dummy_team_name) # Ensure dummy teams exist in 'teams' dictionary
            icp_teams_list.append(dummy_team_name)
            
    # Sort all ICP participants by ranking points
    icp_teams_list.sort(key=lambda x: get_team(x).ranking_points, reverse=True)
    
    # Identify seeded teams (top 2 usually get a bye to the final) and unseeded teams
    seeded_teams = icp_teams_list[:2]
    unseeded_teams = icp_teams_list[2:]

    if verbose:
        print(f"ICP Seeded teams (bye to final): {seeded_teams}")
        print(f"ICP Unseeded teams (play semi-finals): {unseeded_teams}")

    semi_final_winners = []
    # Simulate semi-finals among the unseeded teams (4 teams, 2 matches)
    if len(unseeded_teams) >= 4:
        if verbose: print("\n--- ICP Semi-finals ---")
        semi_final_winners.extend(simulate_knockout([unseeded_teams[0], unseeded_teams[3]], round_name="ICP Semi-final 1", verbose=verbose))
        semi_final_winners.extend(simulate_knockout([unseeded_teams[1], unseeded_teams[2]], round_name="ICP Semi-final 2", verbose=verbose))
    elif len(unseeded_teams) >= 2:
        # Handle cases with fewer than 4 unseeded teams for semi-finals
        if verbose: print("\n--- ICP Semi-finals (partial) ---")
        semi_final_winners.extend(simulate_knockout(unseeded_teams[:2], round_name="ICP Semi-final", verbose=verbose))
        if len(unseeded_teams) % 2 != 0 and len(unseeded_teams) > 0:
            semi_final_winners.append(unseeded_teams[-1]) # If odd number, one gets a bye
    else:
        if verbose: print("Not enough unseeded teams for semi-finals.")
        semi_final_winners.extend(unseeded_teams) # If 0 or 1, they just proceed

    # Combine seeded teams with semi-final winners for the finals
    final_contenders = seeded_teams + semi_final_winners
    
    # Simulate the two final matches (each winner qualifies)
    if len(final_contenders) >= 2:
        if verbose: print("\n--- ICP Finals ---")
        random.shuffle(final_contenders) # Shuffle for final pairing
        
        if len(final_contenders) >= 4:
            # Two final matches, each yielding one qualifier
            winner1 = simulate_knockout([final_contenders[0], final_contenders[1]], round_name="ICP Final Match 1", verbose=verbose)
            for team in winner1:
                icp_qualified_paths.append((team, "Inter-confederation Playoff Winner"))
            
            winner2 = simulate_knockout([final_contenders[2], final_contenders[3]], round_name="ICP Final Match 2", verbose=verbose)
            for team in winner2:
                icp_qualified_paths.append((team, "Inter-confederation Playoff Winner"))
        elif len(final_contenders) == 3:
             # If only 3, assume the top 2 ranked qualify for the two spots directly.
             if verbose: print(f"Only 3 contenders for 2 spots. The two highest ranked qualify directly.")
             final_contenders.sort(key=lambda x: get_team(x).ranking_points, reverse=True)
             for team in final_contenders[:2]:
                 icp_qualified_paths.append((team, "Inter-confederation Playoff Winner (Top Ranked)"))
        elif len(final_contenders) == 2:
             # If only 2, both qualify
             if verbose: print(f"Only 2 contenders for 2 spots. Both qualify.")
             for team in final_contenders:
                 icp_qualified_paths.append((team, "Inter-confederation Playoff Winner"))
        else:
            if verbose: print("Not enough contenders for ICP Finals to determine 2 qualifiers.")
            for team in final_contenders: # Qualify any remaining if less than 2
                icp_qualified_paths.append((team, "Inter-confederation Playoff Winner (Partial Path)"))

    return icp_qualified_paths


def run_single_world_cup_qualifying_simulation(verbose=True):
    """
    Runs a single full simulation of the FIFA World Cup 2026 qualifying process.
    Resets team data for each simulation.
    """
    global teams
    # Re-initialize teams for each simulation to ensure fresh start
    teams = {name: Team(name, "", points) for name, points in FIFA_RANKINGS.items()}

    qualified_paths_this_run = []
    
    if verbose: print("Starting FIFA World Cup 2026 Qualifying Simulation...")
    if verbose: print("Note: This simulation uses static table data as a starting point for ongoing group stages.")

    # Dictionary to hold participants for the Inter-confederation Play-offs
    current_icp_participants = {
        "OFC": STATIC_INTER_CONFED_PLAYOFF_TEAMS.get("OFC", None), # OFC typically sends one known team
        "AFC": None,
        "CAF": None,
        "CONCACAF": None,
        "CONMEBOL": None
    }

    # Simulate each confederation's qualifying path
    afc_q_paths, afc_icp_p = simulate_afc_qualifying(verbose=verbose)
    qualified_paths_this_run.extend(afc_q_paths)
    current_icp_participants["AFC"] = afc_icp_p
    
    caf_q_paths, caf_icp_p = simulate_caf_qualifying(verbose=verbose)
    qualified_paths_this_run.extend(caf_q_paths)
    current_icp_participants["CAF"] = caf_icp_p

    concacaf_q_paths, concacaf_icp_p = simulate_concacaf_qualifying(verbose=verbose)
    qualified_paths_this_run.extend(concacaf_q_paths)
    # CONCACAF can send multiple teams to ICP, so its participant is a list
    current_icp_participants["CONCACAF"] = concacaf_icp_p 

    conmebol_q_paths, conmebol_icp_p = simulate_conmebol_qualifying(verbose=verbose)
    qualified_paths_this_run.extend(conmebol_q_paths)
    current_icp_participants["CONMEBOL"] = conmebol_icp_p

    ofc_q_paths, ofc_icp_p = simulate_ofc_qualifying(verbose=verbose)
    qualified_paths_this_run.extend(ofc_q_paths)
    # OFC has a known ICP participant from STATIC_INTER_CONFED_PLAYOFF_TEAMS, no need to update current_icp_participants for it here again.

    # UEFA qualifying does not send teams to the inter-confederation playoffs.
    uefa_q_paths, _ = simulate_uefa_qualifying(verbose=verbose)
    qualified_paths_this_run.extend(uefa_q_paths)

    # Simulate the Inter-confederation Play-offs using all gathered participants
    icp_q_paths = simulate_inter_confederation_playoffs(current_icp_participants, verbose=verbose)
    qualified_paths_this_run.extend(icp_q_paths)

    return qualified_paths_this_run

def simulate_world_cup(qualified_teams, verbose=True):
    """
    Simulates the FIFA World Cup 2026 tournament for the top 48 qualified teams.
    This includes group stages (12 groups of 4), selecting best third-placed teams,
    and a knockout stage starting from the Round of 32.
    """
    if verbose: print("\n\n===== Simulating FIFA World Cup 2026 Tournament =====")

    # Ensure we have 48 teams for the World Cup draw.
    # If more, trim to 48. If less, fill with dummy teams (for simulation structure).
    if len(qualified_teams) > 48:
        qualified_teams = qualified_teams[:48]
        if verbose: print(f"Warning: More than 48 teams qualified for World Cup. Trimming to 48.")
    elif len(qualified_teams) < 48:
        if verbose: print(f"Warning: Less than 48 teams qualified for World Cup ({len(qualified_teams)}). Filling with dummy teams to reach 48 for simulation structure.")
        num_dummies = 48 - len(qualified_teams)
        for i in range(num_dummies):
            dummy_team_name = f"WC_Dummy_Team_{i+1}"
            get_team(dummy_team_name) # Ensure dummy teams exist in 'teams' dictionary
            qualified_teams.append(dummy_team_name)

    random.shuffle(qualified_teams) # Randomize teams for the World Cup group draw

    # Define 12 groups of 4 teams for the World Cup (FIFA 2026 format)
    world_cup_groups = {}
    group_letters = [chr(ord('A') + i) for i in range(12)] # Generates A, B, C... L
    teams_per_group = 4
    for i, group_letter in enumerate(group_letters):
        start_index = i * teams_per_group
        end_index = start_index + teams_per_group
        world_cup_groups[f"WC_Group_{group_letter}"] = qualified_teams[start_index:end_index]

    knockout_teams = []
    third_placed_teams_stats = []

    # Simulate World Cup group stages
    for group_name, teams_in_group in world_cup_groups.items():
        if not teams_in_group: continue
        # For World Cup groups, assume starting with fresh standings for each group simulation
        # num_qualify_direct=2 as top 2 from each group advance directly
        # num_to_playoff=1 to capture the 3rd placed team's stats for later consideration
        qualified_from_group, playoff_teams_placeholder, remaining_in_group, final_standings_dict = simulate_group_with_initial_standings(
            group_name, teams_in_group, {}, num_qualify_direct=2, num_to_playoff=1, 
            total_matches_per_team=3, # Each team plays 3 group matches (single round-robin)
            verbose=verbose
        )
        knockout_teams.extend(qualified_from_group) # Add top 2 from each group to knockout stage
        
        # Collect third-placed teams' statistics for comparison
        # The 'remaining_in_group' list actually contains all teams not directly qualified/playoff
        # So we need to sort the group's final standings to identify the 3rd place team.
        sorted_group_teams = sort_group([{"Team": t_name, **final_standings_dict[t_name]} for t_name in teams_in_group])
        if len(sorted_group_teams) >= 3:
            third_place_team_stat = sorted_group_teams[2] # 0-indexed, so index 2 is the third team
            third_placed_teams_stats.append(third_place_team_stat)

    if verbose: print(f"\nTeams qualified from group stage (Top 2s from each group): {len(knockout_teams)} teams - {knockout_teams}")
    
    # Determine the 8 best third-placed teams to advance to the Round of 32
    if verbose: print("\n--- Evaluating Best Third-Placed Teams for Knockout Stage ---")
    # Sort third-placed teams by points, then goal difference, then goals scored, then FIFA ranking
    sorted_third_placed = sorted(third_placed_teams_stats, key=lambda x: (x["Pts"], x["GD"], x["GF"], get_team(x["Team"]).ranking_points), reverse=True)
    best_third_placed = [t["Team"] for t in sorted_third_placed[:8]]
    if verbose: print(f"Best 8 third-placed teams (advancing): {best_third_placed}")

    knockout_teams.extend(best_third_placed) # Add these 8 teams to the knockout stage
    random.shuffle(knockout_teams) # Reshuffle for knockout bracket seeding (can be more sophisticated for actual seeding)

    if verbose: print(f"\nTotal teams for World Cup Round of 32: {len(knockout_teams)}")
    if verbose: print(f"World Cup Round of 32 teams: {knockout_teams}")

    # Simulate knockout stages (Round of 32, Round of 16, Quarter-finals, Semi-finals, Final)
    if len(knockout_teams) == 32: # A standard 32-team knockout bracket
        round_of_32_winners = simulate_knockout(knockout_teams, round_name="World Cup Round of 32", verbose=verbose)
        if round_of_32_winners:
            round_of_16_winners = simulate_knockout(round_of_32_winners, round_name="World Cup Round of 16", verbose=verbose)
            if round_of_16_winners:
                quarter_final_winners = simulate_knockout(round_of_16_winners, round_name="World Cup Quarter-finals", verbose=verbose)
                if quarter_final_winners:
                    semi_final_winners = simulate_knockout(quarter_final_winners, round_name="World Cup Semi-finals", verbose=verbose)
                    if semi_final_winners:
                        world_cup_winner = simulate_knockout(semi_final_winners, round_name="World Cup Final", verbose=verbose)
                        if world_cup_winner:
                            return world_cup_winner[0] # Return the single winner
    else:
        if verbose: print(f"Warning: Unexpected number of teams for World Cup knockout stage ({len(knockout_teams)}). Simulating a simpler knockout path.")
        # If the number of teams isn't a perfect power of 2, run a simpler knockout until one winner remains.
        if knockout_teams:
            return simulate_knockout(knockout_teams, round_name="World Cup Knockout (Adjusted Size)", verbose=verbose)[0]
    
    return None # Return None if no winner could be determined (e.g., empty list passed)


def generate_qualification_report_pdf(qualification_paths_summary, num_simulations, output_filename="world_cup_qualification_report.pdf"):
    """
    Generates a PDF report summarizing the qualification chances of each team
    and their qualification paths across multiple simulations.
    """
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("FIFA World Cup 2026 Qualification Report", styles['h1']))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"Based on {num_simulations} simulations.", styles['Normal']))
    elements.append(Spacer(1, 0.4 * inch))

    # Sort teams by their total qualification count in descending order
    sorted_teams = sorted(qualification_paths_summary.items(), key=lambda item: sum(item[1].values()), reverse=True)

    for team_name, paths_counts in sorted_teams:
        total_qualifications = sum(paths_counts.values())
        if total_qualifications == 0:
            continue # Skip teams that never qualified

        elements.append(Paragraph(f"<b>{team_name}</b>", styles['h2']))
        elements.append(Spacer(1, 0.1 * inch))

        path_data = [['Qualification Path', 'Frequency', 'Percentage']]
        for path, count in paths_counts.items():
            percentage = (count / num_simulations) * 100
            path_data.append([path, str(count), f"{percentage:.2f}%"])
        
        # Add a row for total qualifications for this team
        overall_percentage = (total_qualifications / num_simulations) * 100
        path_data.append(['<b>Overall Qualification</b>', f'<b>{total_qualifications}</b>', f'<b>{overall_percentage:.2f}%</b>'])

        # Define table style
        table_style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-2), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
        ])
        
        table = Table(path_data)
        table.setStyle(table_style)
        elements.append(table)
        elements.append(Spacer(1, 0.5 * inch))

    doc.build(elements)
    print(f"\nPDF report generated: {output_filename}")


def run_multiple_simulations(num_simulations=1000):
    """
    Runs multiple World Cup qualification simulations and aggregates the results
    to show qualification probabilities and paths.
    """
    qualification_counts = defaultdict(int) # Counts total qualifications per team
    qualification_paths_summary = defaultdict(lambda: defaultdict(int)) # Counts qualifications per team by path
    
    print(f"\n\nRunning {num_simulations} World Cup 2026 Qualification Simulations...")
    print("This may take a moment, detailed output for individual simulations is suppressed.")

    for i in range(num_simulations):
        qualified_teams_and_paths = run_single_world_cup_qualifying_simulation(verbose=False)
        for team, path in qualified_teams_and_paths:
            qualification_counts[team] += 1
            qualification_paths_summary[team][path] += 1
        
        # Print progress update
        if (i + 1) % (num_simulations // 10 if num_simulations >= 10 else 1) == 0:
            print(f"Completed {i + 1}/{num_simulations} simulations...")

    print("\n\n############################################")
    print("##### FIFA World Cup 2026 Qualification Chances #####")
    print("############################################")

    # Sort teams by their total qualification count
    sorted_chances = sorted(qualification_counts.items(), key=lambda item: item[1], reverse=True)
    top_48_qualified_teams = [team_name for team_name, count in sorted_chances[:48]] # Get the top 48 teams

    print("\n--- Top 48 Teams by Qualification Frequency (out of {} simulations) ---".format(num_simulations))
    # Print qualification chances for the top 48 teams
    for i, (team_name, count) in enumerate(sorted_chances[:48]):
        percentage = (count / num_simulations) * 100
        print(f"{i+1}. {team_name}: {count}/{num_simulations} ({percentage:.2f}%)")

    print(f"\nTotal unique teams that qualified at least once: {len(sorted_chances)}")
    print("This list reflects the 'overall chance' based on repeated simulations.")

    # Generate the PDF report
    generate_qualification_report_pdf(qualification_paths_summary, num_simulations)

    # --- World Cup Tournament Simulation for the top 48 teams ---
    print("\n\n############################################")
    print("##### World Cup 2026 Tournament Simulation #####")
    print("############################################")
    
    # Run a single World Cup simulation using the overall top 48 teams identified.
    # If you want to track World Cup winners across multiple qualification simulations,
    # you would move this call inside the 'for i in range(num_simulations):' loop
    # and aggregate the World Cup winner results similarly to qualification paths.
    world_cup_winner = simulate_world_cup(top_48_qualified_teams, verbose=True)
    if world_cup_winner:
        print(f"\n\n--- FIFA World Cup 2026 Winner: {world_cup_winner} ---")
    else:
        print("\n\n--- Could not determine World Cup 2026 winner in this simulation. ---")

if __name__ == "__main__":
    # Run multiple simulations when the script is executed
    run_multiple_simulations(num_simulations=1000)

