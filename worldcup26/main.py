import random
import math
from collections import defaultdict

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
    "Jordan": 1283.48,
    "New Zealand": 1221.75,
    "New Caledonia": 1058.0,
    "Kuwait": 1109.81,
    "India": 1132.03,
    "Afghanistan": 919.32,
    "Kyrgyz Republic": 1297.05,
    "Oman": 1307.72,
    "Palestine": 1269.83,
    "Indonesia": 1102.26,
    "China PR": 1275.25,
    "Bahrain": 1128.53,
    "Congo": 1204.68,
    "Tanzania": 1184.28, "Niger": 1072.07, "Zambia": 1241.65,
    "Cuba": 1291.68, "Bermuda": 1198.81, "Cayman Islands": 951.18, "Antigua and Barbuda": 1040.69,
    "Grenada": 1150.77, "Saint Kitts and Nevis": 998.67, "Bahamas": 872.2,
    "Aruba": 978.89, "Barbados": 940.33, "Saint Lucia": 1026.83,
    "Guyana": 1069.95, "Montserrat": 1061.5, "Belize": 1007.41,
    "Dominican Republic": 1181.82, "Dominica": 927.87, "British Virgin Islands": 809.8,
    "Saint Vincent and the Grenadines": 1039.67, "Anguilla": 786.9,
    "Puerto Rico": 1083.3,
    "Bolivia": 1302.2, "Chile": 1461.91, "Venezuela": 1476.84,
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
    "Madagascar": 1165.75, "Comoros": 1137.9, "Central African Republic": 1086.56, "Chad": 903.07
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
    if name not in teams:
        ranking_points = FIFA_RANKINGS.get(name, 500.0)
        teams[name] = Team(name, "Unknown", ranking_points)
    return teams[name]


def simulate_match(team1, team2):
    elo_diff = team1.ranking_points - team2.ranking_points
    
    base_expected_goals = 1.3
    scale_factor = 0.002

    expected_goals_team1 = base_expected_goals * math.exp(scale_factor * elo_diff)
    expected_goals_team2 = base_expected_goals * math.exp(scale_factor * -elo_diff)

    goals_team1 = int(random.gauss(expected_goals_team1, 1.0) + 0.5)
    goals_team2 = int(random.gauss(expected_goals_team2, 1.0) + 0.5)

    goals_team1 = max(0, goals_team1)
    goals_team2 = max(0, goals_team2)
            
    return goals_team1, goals_team2

def update_group_standings(standings, team_name, goals_for, goals_against):
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
    return sorted(standings_list, key=lambda x: (x["Pts"], x["GD"], x["GF"], get_team(x["Team"]).ranking_points), reverse=True)

def simulate_group_with_initial_standings(group_name, group_teams_names, initial_standings_data, num_qualify_direct=0, num_to_playoff=0, total_matches_per_team=None, verbose=True):
    if verbose: print(f"\n--- Simulating Group: {group_name} (from initial standings) ---")

    standings = {}
    for team_name in group_teams_names:
        standings[team_name] = initial_standings_data.get(team_name, {
            "Pld": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "Pts": 0
        }).copy()

    if verbose: print(f"Initial Standings for {group_name}:")
    if verbose:
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
        if group_name.startswith("CONCACAF_Second_Round_Group_") or \
           group_name.startswith("AFC_Fourth_Round_Group_"):
            legs_per_pair = 1

        total_possible_matches_in_group = (len(group_teams_names) * (len(group_teams_names) - 1) // 2) * legs_per_pair
        
        current_total_matches_played = sum(s["Pld"] for s in standings.values()) // 2
        
        matches_to_simulate_count = total_possible_matches_in_group - current_total_matches_played
        
        if verbose: print(f"Total possible matches in group: {total_possible_matches_in_group}")
        if verbose: print(f"Current total matches played: {current_total_matches_played}")
        if verbose: print(f"Matches to simulate: {matches_to_simulate_count}")

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

    final_standings_list = []
    for team_name, stats in standings.items():
        final_standings_list.append({"Team": team_name, **stats})

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
    if verbose: print(f"\n--- Simulating {round_name} ---")
    
    if len(teams_for_knockout) < 2:
        if teams_for_knockout:
            if verbose: print(f"Only one team left in {round_name}: {teams_for_knockout[0]} advances by default.")
            return teams_for_knockout
        if verbose: print(f"Not enough teams for {round_name}.")
        return []

    teams_for_knockout.sort(key=lambda x: get_team(x).ranking_points, reverse=True)
    
    current_round_winners = []
    
    num_matches = len(teams_for_knockout) // 2
    for i in range(num_matches):
        team1_name = teams_for_knockout[i]
        team2_name = teams_for_knockout[len(teams_for_knockout) - 1 - i]
        
        if verbose: print(f"Match: {team1_name} vs {team2_name}")
        
        t1 = get_team(team1_name)
        t2 = get_team(team2_name)
        
        goals1, goals2 = simulate_match(t1, t2)
        
        if verbose: print(f"  {t1.name} {goals1}-{goals2} {t2.name}")
        
        if goals1 == goals2:
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
            
    if len(teams_for_knockout) % 2 != 0:
        bye_team = teams_for_knockout[num_matches * 2]
        current_round_winners.append(bye_team)
        if verbose: print(f"  {bye_team} gets a bye to the next round.")

    if len(current_round_winners) > 1:
        return simulate_knockout(current_round_winners, round_name=f"Next Stage of {round_name}", verbose=verbose)
    else:
        return current_round_winners


STATIC_WORLD_CUP_QUALIFIED = {
    "CONCACAF": ["Canada", "Mexico", "USA"],
    "CONMEBOL": ["Argentina"],
    "AFC": ["Japan", "IR Iran", "Uzbekistan", "Korea Republic", "Jordan"],
    "OFC": ["New Zealand"]
}

STATIC_INTER_CONFED_PLAYOFF_TEAMS = {
    "OFC": "New Caledonia",
}

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
    if verbose: print("\n\n===== Simulating AFC World Cup Qualifying =====")
    afc_qualified = list(STATIC_WORLD_CUP_QUALIFIED["AFC"])
    afc_playoff_participant = None

    if verbose: print(f"AFC Teams already qualified (before simulation of remaining rounds): {afc_qualified}")

    afc_third_round_groups = {
        "AFC_Third_Round_Group_A": [t for t in LIVE_STANDINGS_DATA["AFC"]["AFC_Third_Round_Group_A"].keys() if t not in afc_qualified],
        "AFC_Third_Round_Group_B": [t for t in LIVE_STANDINGS_DATA["AFC"]["AFC_Third_Round_Group_B"].keys() if t not in afc_qualified],
        "AFC_Third_Round_Group_C": [t for t in LIVE_STANDINGS_DATA["AFC"]["AFC_Third_Round_Group_C"].keys() if t not in afc_qualified],
    }
    
    afc_fourth_round_teams = []
    
    for group_name, teams_in_group in afc_third_round_groups.items():
        if not teams_in_group:
            if verbose: print(f"Skipping empty group: {group_name}")
            continue
        
        initial_group_data = {t_name: LIVE_STANDINGS_DATA["AFC"][group_name][t_name] for t_name in teams_in_group}

        direct_qualifiers, playoff_teams, _, _ = simulate_group_with_initial_standings(
            group_name, teams_in_group, initial_group_data, num_qualify_direct=2, num_to_playoff=2,
            total_matches_per_team=10, verbose=verbose
        )
        afc_qualified.extend(direct_qualifiers)
        afc_fourth_round_teams.extend(playoff_teams)

    if verbose: print("\n--- AFC Fourth Round ---")
    
    random.shuffle(afc_fourth_round_teams)
    if len(afc_fourth_round_teams) >= 6:
        afc_fourth_round_groups = {
            "AFC_Fourth_Round_Group_X": afc_fourth_round_teams[0:3],
            "AFC_Fourth_Round_Group_Y": afc_fourth_round_teams[3:6],
        }
    else:
        if verbose: print(f"Not enough teams ({len(afc_fourth_round_teams)}) for AFC Fourth Round, proceeding with available.")
        if len(afc_fourth_round_teams) > 0:
            afc_fourth_round_groups = {"AFC_Fourth_Round_Group_X": afc_fourth_round_teams}
        else:
            afc_fourth_round_groups = {}
    
    afc_fifth_round_teams = []
    
    for group_name, teams_in_group in afc_fourth_round_groups.items():
        if not teams_in_group: continue
        direct_qualifiers, playoff_teams, _, _ = simulate_group_with_initial_standings(
            group_name, teams_in_group, {}, num_qualify_direct=1, num_to_playoff=1,
            total_matches_per_team=2,
            verbose=verbose
        )
        afc_qualified.extend(direct_qualifiers)
        afc_fifth_round_teams.extend(playoff_teams)

    if verbose: print("\n--- AFC Fifth Round ---")
    
    if len(afc_fifth_round_teams) == 2:
        if verbose: print(f"AFC Playoff Match: {afc_fifth_round_teams[0]} vs {afc_fifth_round_teams[1]}")
        winner = simulate_knockout(afc_fifth_round_teams, round_name="AFC Playoff", verbose=verbose)
        if winner:
            afc_playoff_participant = winner[0]
            if verbose: print(f"AFC Inter-confederation Playoff participant: {afc_playoff_participant}")
    elif len(afc_fifth_round_teams) == 1:
        afc_playoff_participant = afc_fifth_round_teams[0]
        if verbose: print(f"AFC Inter-confederation Playoff participant (by default): {afc_playoff_participant}")
    else:
        if verbose: print("Not enough teams for AFC Fifth Round playoff or unexpected number.")

    if verbose: print("\n===== AFC Qualification Complete =====")
    if verbose: print(f"AFC Direct Qualifiers: {sorted(afc_qualified, key=lambda x: get_team(x).ranking_points, reverse=True)}")
    if verbose: print(f"AFC Inter-confederation Playoff: {afc_playoff_participant if afc_playoff_participant else 'N/A'}")
    return afc_qualified, afc_playoff_participant


def simulate_caf_qualifying(verbose=True):
    if verbose: print("\n\n===== Simulating CAF World Cup Qualifying =====")
    caf_qualified = []
    caf_playoff_participant = None

    caf_groups_initial_teams = {
        "CAF_Group_A": ["Egypt", "Burkina Faso", "Guinea-Bissau", "Sierra Leone", "Ethiopia", "Djibouti"],
        "CAF_Group_B": ["DR Congo", "Senegal", "Sudan", "Togo", "South Sudan", "Mauritania"],
        "CAF_Group_C": ["South Africa", "Rwanda", "Benin", "Nigeria", "Lesotho", "Zimbabwe"],
        "CAF_Group_D": ["Cape Verde", "Cameroon", "Libya", "Angola", "Mauritius", "Eswatini"],
        "CAF_Group_E": ["Morocco", "Tanzania", "Zambia", "Niger", "Congo"],
        "CAF_Group_F": ["Ivory Coast", "Gabon", "Burundi", "Kenya", "Gambia", "Seychelles"],
        "CAF_Group_G": ["Algeria", "Mozambique", "Botswana", "Uganda", "Guinea", "Somalia"],
        "CAF_Group_H": ["Tunisia", "Equatorial Guinea", "Namibia", "Liberia", "Malawi", "Sao Tome and Principe"],
        "CAF_Group_I": ["Ghana", "Comoros", "Madagascar", "Mali", "Central African Republic", "Chad"]
    }
    
    group_runners_up_for_selection = []

    for group_name, teams_in_group_list in caf_groups_initial_teams.items():
        if not teams_in_group_list: continue

        initial_group_data = LIVE_STANDINGS_DATA["CAF"].get(group_name, {})
        
        if group_name == "CAF_Group_E":
            total_matches_per_team = 8
        else:
            total_matches_per_team = 10

        qualified_from_group, runner_up, _, _ = simulate_group_with_initial_standings(
            group_name, teams_in_group_list, initial_group_data, num_qualify_direct=1, num_to_playoff=1,
            total_matches_per_team=total_matches_per_team, verbose=verbose
        )
        caf_qualified.extend(qualified_from_group)
        if runner_up:
            group_runners_up_for_selection.append({
                "team": runner_up[0],
                "ranking_points": get_team(runner_up[0]).ranking_points,
            })
            
    group_runners_up_for_selection.sort(key=lambda x: x["ranking_points"], reverse=True)
    caf_playoff_candidates = [s["team"] for s in group_runners_up_for_selection[:4]]

    if verbose: print("\n--- CAF Play-off Stage ---")

    if len(caf_playoff_candidates) >= 2:
        if verbose: print(f"CAF Playoff participants (top 4 runners-up by ranking): {caf_playoff_candidates}")
        winner = simulate_knockout(caf_playoff_candidates, round_name="CAF Playoff", verbose=verbose)
        if winner:
            caf_playoff_participant = winner[0]
            if verbose: print(f"CAF Inter-confederation Playoff participant: {caf_playoff_participant}")
    elif len(caf_playoff_candidates) == 1:
        caf_playoff_participant = caf_playoff_candidates[0]
        if verbose: print(f"CAF Inter-confederation Playoff participant (by default): {caf_playoff_participant}")
    else:
        if verbose: print("Not enough teams for CAF Playoff stage.")

    if verbose: print("\n===== CAF Qualification Complete =====")
    if verbose: print(f"CAF Direct Qualifiers: {sorted(caf_qualified, key=lambda x: get_team(x).ranking_points, reverse=True)}")
    if verbose: print(f"CAF Inter-confederation Playoff: {caf_playoff_participant if caf_playoff_participant else 'N/A'}")
    return caf_qualified, caf_playoff_participant


def simulate_concacaf_qualifying(verbose=True):
    if verbose: print("\n\n===== Simulating CONCACAF World Cup Qualifying =====")
    concacaf_qualified = list(STATIC_WORLD_CUP_QUALIFIED["CONCACAF"])
    concacaf_icp_participants = []

    if verbose: print(f"CONCACAF Host Qualifiers: {concacaf_qualified}")

    concacaf_second_round_groups_teams = {
        "CONCACAF_Second_Round_Group_A": list(LIVE_STANDINGS_DATA["CONCACAF_Second_Round"]["CONCACAF_Second_Round_Group_A"].keys()),
        "CONCACAF_Second_Round_Group_B": list(LIVE_STANDINGS_DATA["CONCACAF_Second_Round"]["CONCACAF_Second_Round_Group_B"].keys()),
        "CONCACAF_Second_Round_Group_C": list(LIVE_STANDINGS_DATA["CONCACAF_Second_Round"]["CONCACAF_Second_Round_Group_C"].keys()),
        "CONCACAF_Second_Round_Group_D": list(LIVE_STANDINGS_DATA["CONCACAF_Second_Round"]["CONCACAF_Second_Round_Group_D"].keys()),
        "CONCACAF_Second_Round_Group_E": list(LIVE_STANDINGS_DATA["CONCACAF_Second_Round"]["CONCACAF_Second_Round_Group_E"].keys()),
        "CONCACAF_Second_Round_Group_F": list(LIVE_STANDINGS_DATA["CONCACAF_Second_Round"]["CONCACAF_Second_Round_Group_F"].keys()),
    }
    
    concacaf_third_round_teams = []

    for group_name, teams_in_group_list in concacaf_second_round_groups_teams.items():
        if not teams_in_group_list: continue
        
        initial_group_data = LIVE_STANDINGS_DATA["CONCACAF_Second_Round"].get(group_name, {})

        qualified_from_group, runner_up, _, _ = simulate_group_with_initial_standings(
            group_name, teams_in_group_list, initial_group_data, num_qualify_direct=1, num_to_playoff=1,
            total_matches_per_team=4,
            verbose=verbose
        )
        concacaf_third_round_teams.extend(qualified_from_group)
        if runner_up:
            concacaf_third_round_teams.extend(runner_up)

    if verbose: print("\n--- CONCACAF Third Round ---")
    
    random.shuffle(concacaf_third_round_teams)
    if len(concacaf_third_round_teams) >= 12:
        concacaf_third_round_groups = {
            "CONCACAF_Third_Round_Group_1": concacaf_third_round_teams[0:4],
            "CONCACAF_Third_Round_Group_2": concacaf_third_round_teams[4:8],
            "CONCACAF_Third_Round_Group_3": concacaf_third_round_teams[8:12],
        }
    else:
        if verbose: print(f"Not enough teams ({len(concacaf_third_round_teams)}) for CONCACAF Third Round, proceeding with available.")
        concacaf_third_round_groups = {}
        for i in range(len(concacaf_third_round_teams) // 4):
            concacaf_third_round_groups[f"CONCACAF_Third_Round_Group_{i+1}"] = concacaf_third_round_teams[i*4:(i+1)*4]
        if len(concacaf_third_round_teams) % 4 != 0 and len(concacaf_third_round_teams) > 0:
            concacaf_third_round_groups[f"CONCACAF_Third_Round_Group_X_Remainder"] = concacaf_third_round_teams[-(len(concacaf_third_round_teams) % 4):]


    concacaf_runners_up_stats = []

    for group_name, teams_in_group in concacaf_third_round_groups.items():
        if not teams_in_group: continue
        direct_qualifiers, runner_up, _, _ = simulate_group_with_initial_standings(
            group_name, teams_in_group, {}, num_qualify_direct=1, num_to_playoff=1,
            total_matches_per_team=6,
            verbose=verbose
        )
        concacaf_qualified.extend(direct_qualifiers)
        if runner_up:
            concacaf_runners_up_stats.append({
                "team": runner_up[0],
                "ranking_points": get_team(runner_up[0]).ranking_points,
            })
            
    concacaf_runners_up_stats.sort(key=lambda x: x["ranking_points"], reverse=True)
    concacaf_icp_participants = [s["team"] for s in concacaf_runners_up_stats[:2]]
    
    if len(concacaf_icp_participants) >= 2:
        if verbose: print(f"CONCACAF Inter-confederation Playoff participants: {concacaf_icp_participants}")
    elif concacaf_icp_participants:
        if verbose: print(f"CONCACAF Inter-confederation Playoff participants (partial): {concacaf_icp_participants}")
    else:
        if verbose: print("Not enough CONCACAF teams for ICP slots.")


    if verbose: print("\n===== CONCACAF Qualification Complete =====")
    if verbose: print(f"CONCACAF Direct Qualifiers (including hosts): {sorted(concacaf_qualified, key=lambda x: get_team(x).ranking_points, reverse=True)}")
    if verbose: print(f"CONCACAF Inter-confederation Playoff: {concacaf_icp_participants if concacaf_icp_participants else 'N/A'}")
    return concacaf_qualified, concacaf_icp_participants


def simulate_conmebol_qualifying(verbose=True):
    if verbose: print("\n\n===== Simulating CONMEBOL World Cup Qualifying =====")
    conmebol_qualified = []
    conmebol_playoff_participant = None

    conmebol_teams = list(LIVE_STANDINGS_DATA["CONMEBOL"].keys())
    
    if verbose:
        print("Simulating CONMEBOL league from current standings (15 matches per team played, 3 remaining).")

    initial_conmebol_standings = LIVE_STANDINGS_DATA["CONMEBOL"]

    _, _, _, final_conmebol_standings_dict = simulate_group_with_initial_standings(
        "CONMEBOL_League", conmebol_teams, initial_conmebol_standings,
        num_qualify_direct=0, num_to_playoff=0,
        total_matches_per_team=18,
        verbose=verbose
    )

    conmebol_final_standings_list = []
    for team_name in conmebol_teams:
        conmebol_final_standings_list.append({"Team": team_name, **final_conmebol_standings_dict.get(team_name, {})})
    
    sorted_standings = sort_group(conmebol_final_standings_list)

    if verbose:
        print("\n--- CONMEBOL Final League Standings (Simulated) ---")
        print("{:<20} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5}".format(
            "Team", "Pld", "W", "D", "L", "GF", "GA", "GD", "Pts"
        ))
        for team_stat in sorted_standings:
            print("{:<20} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5}".format(
                team_stat["Team"], team_stat["Pld"], team_stat["W"], team_stat["D"],
                team_stat["L"], team_stat["GF"], team_stat["GA"], team_stat["GD"], team_stat["Pts"]
            ))
    
    conmebol_qualified = [t["Team"] for t in sorted_standings[:6]]
    
    if len(sorted_standings) >= 7:
        conmebol_playoff_participant = sorted_standings[6]["Team"]
        if verbose: print(f"CONMEBOL Inter-confederation Playoff participant: {conmebol_playoff_participant}")
    else:
        if verbose: print("Not enough teams in CONMEBOL league to determine 7th place for playoff spot.")

    if verbose: print("\n===== CONMEBOL Qualification Complete =====")
    if verbose: print(f"CONMEBOL Direct Qualifiers: {sorted(conmebol_qualified, key=lambda x: get_team(x).ranking_points, reverse=True)}")
    if verbose: print(f"CONMEBOL Inter-confederation Playoff: {conmebol_playoff_participant if conmebol_playoff_participant else 'N/A'}")
    return conmebol_qualified, conmebol_playoff_participant


def simulate_ofc_qualifying(verbose=True):
    if verbose: print("\n\n===== Simulating OFC World Cup Qualifying =====")
    ofc_qualified = list(STATIC_WORLD_CUP_QUALIFIED["OFC"])
    ofc_playoff_participant = STATIC_INTER_CONFED_PLAYOFF_TEAMS.get("OFC", None)

    if verbose:
        print(f"OFC Direct Qualifier (already known): {ofc_qualified[0] if ofc_qualified else 'N/A'}")
        print(f"OFC Inter-confederation Playoff participant (already known): {ofc_playoff_participant if ofc_playoff_participant else 'N/A'}")

    if verbose: print("\n===== OFC Qualification Complete =====")
    return ofc_qualified, ofc_playoff_participant


def simulate_uefa_qualifying(verbose=True):
    if verbose: print("\n\n===== Simulating UEFA World Cup Qualifying =====")
    uefa_qualified = []
    
    uefa_teams_pool = [
        "Spain", "France", "England", "Belgium", "Italy", "Germany",
        "Netherlands", "Portugal", "Croatia", "Switzerland", "Denmark", "Austria",
        "Ukraine", "Türkiye", "Sweden", "Wales", "Serbia", "Poland", "Russia",
        "Hungary", "Norway", "Czechia", "Greece", "Scotland", "Romania",
        "Slovakia", "Slovenia", "Republic of Ireland", "North Macedonia",
        "Bosnia and Herzegovina", "Finland", "Iceland", "Albania",
        "Bulgaria", "Israel", "Georgia", "Luxembourg", "Cyprus", "Kosovo", "Lithuania", "Estonia",
        "Latvia", "Azerbaijan", "Kazakhstan", "Armenia", "Malta", "Moldova", "Gibraltar",
        "San Marino", "Liechtenstein", "Andorra", "Faroe Islands"
    ]
    random.shuffle(uefa_teams_pool)
    
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
        "UEFA_Group_K": [],
        "UEFA_Group_L": [],
    }

    assigned_teams = set()
    for group_teams in uefa_groups_teams.values():
        assigned_teams.update(group_teams)
    
    unassigned_uefa_teams = [t for t in uefa_teams_pool if t not in assigned_teams]
    random.shuffle(unassigned_uefa_teams)

    if len(unassigned_uefa_teams) >= 4:
        uefa_groups_teams["UEFA_Group_K"] = unassigned_uefa_teams[0:4]
        unassigned_uefa_teams = unassigned_uefa_teams[4:]
    if len(unassigned_uefa_teams) >= 4:
        uefa_groups_teams["UEFA_Group_L"] = unassigned_uefa_teams[0:4]
        unassigned_uefa_teams = unassigned_uefa_teams[4:]
    elif len(unassigned_uefa_teams) > 0:
         uefa_groups_teams["UEFA_Group_L"].extend(unassigned_uefa_teams)
         unassigned_uefa_teams = []


    all_runners_up_stats = []

    for group_name, teams_in_group_list in uefa_groups_teams.items():
        if not teams_in_group_list: continue

        initial_group_data = LIVE_STANDINGS_DATA["UEFA"].get(group_name, {})
        
        if len(teams_in_group_list) == 4:
            total_matches_per_team = 6
        else:
            total_matches_per_team = 8

        direct_qualifier, runner_up, _, _ = simulate_group_with_initial_standings(
            group_name, teams_in_group_list, initial_group_data, num_qualify_direct=1, num_to_playoff=1,
            total_matches_per_team=total_matches_per_team, verbose=verbose
        )
        uefa_qualified.extend(direct_qualifier)
        if runner_up:
            all_runners_up_stats.append({
                "team": runner_up[0],
                "ranking_points": get_team(runner_up[0]).ranking_points,
            })
    
    if verbose: print("\n--- UEFA Play-off Stage ---")

    unl_winners_candidates = [t for t in uefa_teams_pool if t not in uefa_qualified and t not in [s["team"] for s in all_runners_up_stats]]
    unl_winners_candidates.sort(key=lambda x: get_team(x).ranking_points, reverse=True)
    
    extra_playoff_teams = unl_winners_candidates[:4]
    
    uefa_playoff_pool = [s["team"] for s in all_runners_up_stats] + extra_playoff_teams
    
    if len(uefa_playoff_pool) < 16 and verbose:
        print(f"Warning: Not enough teams for UEFA playoff stage (expected 16, got {len(uefa_playoff_pool)}). Simulating with available teams.")
    
    random.shuffle(uefa_playoff_pool)

    final_uefa_qualifiers_from_playoffs = []
    
    num_paths_to_simulate = min(4, len(uefa_playoff_pool) // 4)
    if num_paths_to_simulate == 0 and len(uefa_playoff_pool) >= 2:
        num_paths_to_simulate = 1

    for i in range(num_paths_to_simulate):
        path_teams = uefa_playoff_pool[i*4 : min((i+1)*4, len(uefa_playoff_pool))]
        if not path_teams: continue
        if verbose: print(f"\nUEFA Playoff Path {i+1} teams: {path_teams}")
        path_winner = simulate_knockout(path_teams, round_name=f"UEFA Playoff Path {i+1}", verbose=verbose)
        if path_winner:
            final_uefa_qualifiers_from_playoffs.extend(path_winner)
            
    if not final_uefa_qualifiers_from_playoffs and uefa_playoff_pool:
        if verbose: print(f"Not enough teams for structured UEFA Playoff paths. Assigning highest ranked remaining teams.")
        uefa_playoff_pool.sort(key=lambda x: get_team(x).ranking_points, reverse=True)
        final_uefa_qualifiers_from_playoffs.extend(uefa_playoff_pool[:min(4, len(uefa_playoff_pool))])

    uefa_qualified.extend(final_uefa_qualifiers_from_playoffs)

    if verbose: print("\n===== UEFA Qualification Complete =====")
    if verbose: print(f"UEFA Direct Qualifiers: {sorted(uefa_qualified, key=lambda x: get_team(x).ranking_points, reverse=True)}")
    return uefa_qualified, None


def simulate_inter_confederation_playoffs(icp_participants_dict, verbose=True):
    if verbose: print("\n\n===== Simulating Inter-confederation Play-offs =====")
    icp_qualified = []

    icp_teams_list = []
    for conf, teams_or_team in icp_participants_dict.items():
        if isinstance(teams_or_team, list):
            icp_teams_list.extend(teams_or_team)
        elif teams_or_team:
            icp_teams_list.append(teams_or_team)
            
    if len(icp_teams_list) < 6:
        if verbose: print(f"Warning: Not enough teams for Inter-confederation Play-offs (expected 6, got {len(icp_teams_list)}). Adding dummy teams if necessary for simulation structure.")
        num_dummies = 6 - len(icp_teams_list)
        for i in range(num_dummies):
            dummy_team_name = f"Dummy_ICP_Team_{i+1}"
            get_team(dummy_team_name)
            icp_teams_list.append(dummy_team_name)
            
    icp_teams_list.sort(key=lambda x: get_team(x).ranking_points, reverse=True)
    
    seeded_teams = icp_teams_list[:2]
    unseeded_teams = icp_teams_list[2:]

    if verbose:
        print(f"ICP Seeded teams (bye to final): {seeded_teams}")
        print(f"ICP Unseeded teams (play semi-finals): {unseeded_teams}")

    semi_final_winners = []
    if len(unseeded_teams) >= 4:
        if verbose: print("\n--- ICP Semi-finals ---")
        semi_final_winners.extend(simulate_knockout([unseeded_teams[0], unseeded_teams[3]], round_name="ICP Semi-final 1", verbose=verbose))
        semi_final_winners.extend(simulate_knockout([unseeded_teams[1], unseeded_teams[2]], round_name="ICP Semi-final 2", verbose=verbose))
    elif len(unseeded_teams) >= 2:
        if verbose: print("\n--- ICP Semi-finals (partial) ---")
        semi_final_winners.extend(simulate_knockout(unseeded_teams[:2], round_name="ICP Semi-final", verbose=verbose))
        if len(unseeded_teams) % 2 != 0 and len(unseeded_teams) > 0:
            semi_final_winners.append(unseeded_teams[-1])
    else:
        if verbose: print("Not enough unseeded teams for semi-finals.")
        semi_final_winners.extend(unseeded_teams)

    final_contenders = seeded_teams + semi_final_winners
    
    if len(final_contenders) >= 2:
        if verbose: print("\n--- ICP Finals ---")
        random.shuffle(final_contenders)
        
        if len(final_contenders) >= 4:
            if verbose: print(f"Final 1: {final_contenders[0]} vs {final_contenders[1]}")
            icp_qualified.extend(simulate_knockout([final_contenders[0], final_contenders[1]], round_name="ICP Final Match 1", verbose=verbose))
            
            if verbose: print(f"Final 2: {final_contenders[2]} vs {final_contenders[3]}")
            icp_qualified.extend(simulate_knockout([final_contenders[2], final_contenders[3]], round_name="ICP Final Match 2", verbose=verbose))
        elif len(final_contenders) == 3:
             if verbose: print(f"Only 3 contenders for 2 spots. The two highest ranked qualify directly.")
             final_contenders.sort(key=lambda x: get_team(x).ranking_points, reverse=True)
             icp_qualified.extend(final_contenders[:2])
        elif len(final_contenders) == 2:
             if verbose: print(f"Only 2 contenders for 2 spots. Both qualify.")
             icp_qualified.extend(final_contenders)
        else:
            if verbose: print("Not enough contenders for ICP Finals to determine 2 qualifiers.")
            icp_qualified.extend(final_contenders)

    if verbose: print("\n===== Inter-confederation Play-offs Complete =====")
    if verbose: print(f"Teams qualified from Inter-confederation Play-offs: {sorted(icp_qualified, key=lambda x: get_team(x).ranking_points, reverse=True)}")
    return icp_qualified


def run_single_world_cup_qualifying_simulation(verbose=True):
    global teams
    teams = {name: Team(name, "", points) for name, points in FIFA_RANKINGS.items()}

    all_direct_qualifiers = set()
    
    if verbose: print("Starting FIFA World Cup 2026 Qualifying Simulation...")
    if verbose: print("Note: This simulation uses live table data as a starting point for ongoing group stages.")

    current_icp_participants = {
        "OFC": STATIC_INTER_CONFED_PLAYOFF_TEAMS.get("OFC", None),
        "AFC": None,
        "CAF": None,
        "CONCACAF": None,
        "CONMEBOL": None
    }

    for conf_teams in STATIC_WORLD_CUP_QUALIFIED.values():
        all_direct_qualifiers.update(conf_teams)

    afc_q, afc_icp_p = simulate_afc_qualifying(verbose=verbose)
    all_direct_qualifiers.update(afc_q)
    current_icp_participants["AFC"] = afc_icp_p
    
    caf_q, caf_icp_p = simulate_caf_qualifying(verbose=verbose)
    all_direct_qualifiers.update(caf_q)
    current_icp_participants["CAF"] = caf_icp_p

    concacaf_q, concacaf_icp_p = simulate_concacaf_qualifying(verbose=verbose)
    all_direct_qualifiers.update(concacaf_q)
    current_icp_participants["CONCACAF"] = concacaf_icp_p

    conmebol_q, conmebol_icp_p = simulate_conmebol_qualifying(verbose=verbose)
    all_direct_qualifiers.update(conmebol_q)
    current_icp_participants["CONMEBOL"] = conmebol_icp_p

    ofc_q, ofc_icp_p = simulate_ofc_qualifying(verbose=verbose)
    all_direct_qualifiers.update(ofc_q)

    uefa_q, _ = simulate_uefa_qualifying(verbose=verbose)
    all_direct_qualifiers.update(uefa_q)

    icp_q = simulate_inter_confederation_playoffs(current_icp_participants, verbose=verbose)
    all_direct_qualifiers.update(icp_q)

    return all_direct_qualifiers

def run_multiple_simulations(num_simulations=1000):
    qualification_counts = defaultdict(int)
    
    print(f"\n\nRunning {num_simulations} World Cup 2026 Qualification Simulations...")
    print("This may take a moment, detailed output for individual simulations is suppressed.")

    for i in range(num_simulations):
        qualified_teams_this_run = run_single_world_cup_qualifying_simulation(verbose=False)
        for team in qualified_teams_this_run:
            qualification_counts[team] += 1
        
        if (i + 1) % (num_simulations // 10 if num_simulations >= 10 else 1) == 0:
            print(f"Completed {i + 1}/{num_simulations} simulations...")

    print("\n\n############################################")
    print("##### FIFA World Cup 2026 Qualification Chances #####")
    print("############################################")

    sorted_chances = sorted(qualification_counts.items(), key=lambda item: item[1], reverse=True)

    print("\n--- Top 48 Teams by Qualification Frequency (out of {} simulations) ---".format(num_simulations))
    for i, (team_name, count) in enumerate(sorted_chances[:48]):
        percentage = (count / num_simulations) * 100
        print(f"{i+1}. {team_name}: {count}/{num_simulations} ({percentage:.2f}%)")

    print(f"\nTotal unique teams that qualified at least once: {len(sorted_chances)}")
    print("This list reflects the 'overall chance' based on repeated simulations.")

if __name__ == "__main__":
    run_multiple_simulations(num_simulations=1000)
