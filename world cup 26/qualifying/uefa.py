import random
from collections import defaultdict
from tqdm import tqdm
import math

team_strengths = {
    'Argentina': 1886.16, 'Spain': 1854.64, 'France': 1852.71, 'England': 1819.20,
    'Brazil': 1776.03, 'Netherlands': 1752.44, 'Portugal': 1750.08, 'Belgium': 1735.75,
    'Italy': 1718.31, 'Germany': 1716.98, 'Croatia': 1698.66, 'Morocco': 1694.24,
    'Uruguay': 1679.49, 'Colombia': 1679.04, 'Japan': 1652.64, 'USA': 1648.81,
    'Mexico': 1646.94, 'Iran': 1637.39, 'Senegal': 1630.32, 'Switzerland': 1624.75,
    'Denmark': 1617.54, 'Austria': 1580.22, 'South Korea': 1574.93, 'Ecuador': 1567.95,
    'Ukraine': 1559.81, 'Australia': 1554.55, 'Türkiye': 1551.47, 'Sweden': 1536.05,
    'Wales': 1535.57, 'Canada': 1531.58, 'Serbia': 1523.91, 'Egypt': 1518.79,
    'Panama': 1517.66, 'Poland': 1517.35, 'Russia': 1516.27, 'Algeria': 1507.17,
    'Hungary': 1503.34, 'Norway': 1497.18, 'Czechia': 1491.43, 'Greece': 1489.82,
    'Slovakia': 1477.78, 'Romania': 1479.22, 'Scotland': 1480.30,
    'Slovenia': 1462.66, 'Republic of Ireland': 1412.23, 'Albania': 1375.95,
    'North Macedonia': 1375.58, 'Georgia': 1373.05, 'Finland': 1359.79,
    'Bosnia and Herzegovina': 1350.85, 'Northern Ireland': 1348.67, 'Montenegro': 1337.36,
    'Iceland': 1336.55, 'Israel': 1321.78, 'Bulgaria': 1289.03, 'Luxembourg': 1261.88,
    'Kosovo': 1238.38, 'Belarus': 1235.36, 'Armenia': 1208.31, 'Kazakhstan': 1177.66,
    'Azerbaijan': 1150.64, 'Estonia': 1144.48, 'Moldova': 1120.48,
    'Cyprus': 1090.73,
    'Faroe Islands': 1050.65,
    'Latvia': 1025.10,
    'Lithuania': 1000.55,
    'Andorra': 950.25,
    'Malta': 900.80,
    'Gibraltar': 800.15,
    'Liechtenstein': 750.30,
    'San Marino': 700.00
}

UNL_INTERIM_RANKING = [
    'Spain', 'Germany', 'Portugal', 'France',
    'Italy', 'Netherlands', 'Denmark', 'Croatia', 'Scotland', 'Serbia', 'Hungary', 'Belgium',
    'Poland', 'Israel', 'Switzerland', 'Bosnia and Herzegovina',
    'England', 'Norway', 'Wales', 'Czechia',
    'Greece', 'Austria', 'Türkiye', 'Ukraine', 'Slovenia', 'Georgia', 'Finland', 'Iceland', 'Northern Ireland', 'Montenegro', 'Bosnia and Herzegovina', 'Israel',
    'Romania', 'Sweden', 'North Macedonia', 'Northern Ireland',
    'Moldova', 'San Marino',
]

PROHIBITED_CLASHES = {
    frozenset({'Armenia', 'Azerbaijan'}),
    frozenset({'Belarus', 'Ukraine'}),
    frozenset({'Gibraltar', 'Spain'}),
    frozenset({'Kosovo', 'Bosnia and Herzegovina'}),
    frozenset({'Kosovo', 'Serbia'})
}

current_standings = {
    'Group A': {
        'Germany': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0},
        'Slovakia': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0},
        'Northern Ireland': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0},
        'Luxembourg': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0}
    },
    'Group B': {
        'Switzerland': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0},
        'Sweden': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0},
        'Slovenia': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0},
        'Kosovo': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0}
    },
    'Group C': {
        'Denmark': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0},
        'Greece': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0},
        'Scotland': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0},
        'Belarus': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0}
    },
    'Group D': {
        'France': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0},
        'Ukraine': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0},
        'Iceland': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0},
        'Azerbaijan': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0}
    },
    'Group E': {
        'Spain': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0},
        'Türkiye': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0},
        'Georgia': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0},
        'Bulgaria': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0}
    },
    'Group F': {
        'Portugal': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0},
        'Hungary': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0},
        'Republic of Ireland': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0},
        'Armenia': {'points': 0, 'gd': 0, 'gs': 0, 'matches_played': 0}
    },
    'Group G': {
        'Poland': {'points': 6, 'gd': 3, 'gs': 3, 'matches_played': 2},
        'Netherlands': {'points': 3, 'gd': 2, 'gs': 2, 'matches_played': 1},
        'Finland': {'points': 4, 'gd': 1, 'gs': 3, 'matches_played': 3},
        'Lithuania': {'points': 1, 'gd': -2, 'gs': 2, 'matches_played': 3},
        'Malta': {'points': 1, 'gd': -3, 'gs': 0, 'matches_played': 3}
    },
    'Group H': {
        'Bosnia and Herzegovina': {'points': 6, 'gd': 2, 'gs': 4, 'matches_played': 3},
        'Austria': {'points': 3, 'gd': 1, 'gs': 2, 'matches_played': 1},
        'Romania': {'points': 3, 'gd': -1, 'gs': 1, 'matches_played': 2},
        'Cyprus': {'points': 3, 'gd': 2, 'gs': 2, 'matches_played': 1},
        'San Marino': {'points': 0, 'gd': -5, 'gs': 0, 'matches_played': 3}
    },
    'Group I': {
        'Norway': {'points': 9, 'gd': 8, 'gs': 12, 'matches_played': 3},
        'Israel': {'points': 3, 'gd': -1, 'gs': 5, 'matches_played': 2},
        'Estonia': {'points': 3, 'gd': -1, 'gs': 4, 'matches_played': 2},
        'Italy': {'points': 0, 'gd': -3, 'gs': 0, 'matches_played': 1},
        'Moldova': {'points': 0, 'gd': -3, 'gs': 2, 'matches_played': 2}
    },
    'Group J': {
        'Wales': {'points': 7, 'gd': 5, 'gs': 7, 'matches_played': 3},
        'North Macedonia': {'points': 5, 'gd': 3, 'gs': 5, 'matches_played': 3},
        'Kazakhstan': {'points': 3, 'gd': 0, 'gs': 3, 'matches_played': 2},
        'Belgium': {'points': 1, 'gd': 0, 'gs': 1, 'matches_played': 1},
        'Liechtenstein': {'points': 0, 'gd': -8, 'gs': 0, 'matches_played': 3}
    },
    'Group K': {
        'England': {'points': 9, 'gd': 7, 'gs': 8, 'matches_played': 3},
        'Albania': {'points': 4, 'gd': 1, 'gs': 3, 'matches_played': 3},
        'Latvia': {'points': 2, 'gd': -2, 'gs': 1, 'matches_played': 3},
        'Serbia': {'points': 1, 'gd': 0, 'gs': 0, 'matches_played': 2},
        'Andorra': {'points': 1, 'gd': -2, 'gs': 0, 'matches_played': 3}
    },
    'Group L': {
        'Croatia': {'points': 6, 'gd': 11, 'gs': 11, 'matches_played': 2},
        'Czechia': {'points': 6, 'gd': 5, 'gs': 6, 'matches_played': 2},
        'Montenegro': {'points': 3, 'gd': 1, 'gs': 1, 'matches_played': 2},
        'Faroe Islands': {'points': 0, 'gd': -5, 'gs': 1, 'matches_played': 3},
        'Gibraltar': {'points': 0, 'gd': -11, 'gs': 0, 'matches_played': 3}
    }
}

remaining_fixtures = [
    ('Kazakhstan', 'North Macedonia', 'Group J'),
    ('Belgium', 'Wales', 'Group J'),
    ('Croatia', 'Czechia', 'Group L'),
    ('Estonia', 'Norway', 'Group I'),
    ('Faroe Islands', 'Gibraltar', 'Group L'),
    ('Italy', 'Moldova', 'Group I'),
    ('Finland', 'Poland', 'Group G'),
    ('Latvia', 'Albania', 'Group K'),
    ('Netherlands', 'Malta', 'Group G'),
    ('Romania', 'Cyprus', 'Group H'),
    ('San Marino', 'Austria', 'Group H'),
    ('Serbia', 'Andorra', 'Group K'),

    ('Kazakhstan', 'Wales', 'Group J'),
    ('Georgia', 'Türkiye', 'Group E'),
    ('Lithuania', 'Malta', 'Group G'),
    ('Luxembourg', 'Northern Ireland', 'Group A'),
    ('Slovakia', 'Germany', 'Group A'),
    ('Bulgaria', 'Spain', 'Group E'),
    ('Netherlands', 'Poland', 'Group G'),
    ('Liechtenstein', 'Belgium', 'Group J'),
    ('Slovenia', 'Sweden', 'Group B'),
    ('Switzerland', 'Kosovo', 'Group B'),
    ('Greece', 'Belarus', 'Group C'),
    ('Denmark', 'Scotland', 'Group C'),
    ('Iceland', 'Azerbaijan', 'Group D'),
    ('Ukraine', 'France', 'Group D'),
    ('Moldova', 'Israel', 'Group I'),
    ('Italy', 'Estonia', 'Group I'),
    ('Faroe Islands', 'Croatia', 'Group L'),
    ('Montenegro', 'Czechia', 'Group L'),
    ('Latvia', 'Serbia', 'Group K'),
    ('Armenia', 'Portugal', 'Group F'),
    ('England', 'Andorra', 'Group K'),
    ('Republic of Ireland', 'Hungary', 'Group F'),
    ('Austria', 'Cyprus', 'Group H'),
    ('San Marino', 'Bosnia and Herzegovina', 'Group H'),

    ('Georgia', 'Bulgaria', 'Group E'),
    ('North Macedonia', 'Liechtenstein', 'Group J'),
    ('Luxembourg', 'Slovakia', 'Group A'),
    ('Germany', 'Northern Ireland', 'Group A'),
    ('Türkiye', 'Spain', 'Group E'),
    ('Lithuania', 'Netherlands', 'Group G'),
    ('Poland', 'Finland', 'Group G'),
    ('Belgium', 'Kazakhstan', 'Group J'),
    ('Kosovo', 'Sweden', 'Group B'),
    ('Switzerland', 'Slovenia', 'Group B'),
    ('Belarus', 'Scotland', 'Group C'),
    ('Greece', 'Denmark', 'Group C'),
    ('Israel', 'Italy', 'Group I'),
    ('Gibraltar', 'Faroe Islands', 'Group L'),
    ('Croatia', 'Montenegro', 'Group L'),
    ('Azerbaijan', 'Ukraine', 'Group D'),
    ('Armenia', 'Republic of Ireland', 'Group F'),
    ('France', 'Iceland', 'Group D'),
    ('Hungary', 'Portugal', 'Group F'),
    ('Bosnia and Herzegovina', 'Austria', 'Group H'),
    ('Cyprus', 'Romania', 'Group H'),
    ('Norway', 'Moldova', 'Group I'),
    ('Albania', 'Latvia', 'Group K'),
    ('Serbia', 'England', 'Group K'),

    ('Belarus', 'Denmark', 'Group C'),
    ('Scotland', 'Greece', 'Group C'),
    ('Finland', 'Lithuania', 'Group G'),
    ('Malta', 'Netherlands', 'Group G'),
    ('Austria', 'San Marino', 'Group H'),
    ('Cyprus', 'Bosnia and Herzegovina', 'Group H'),
    ('Czechia', 'Croatia', 'Group L'),
    ('Faroe Islands', 'Montenegro', 'Group L'),
    ('Kazakhstan', 'Liechtenstein', 'Group J'),
    ('Northern Ireland', 'Slovakia', 'Group A'),
    ('Germany', 'Luxembourg', 'Group A'),
    ('Kosovo', 'Slovenia', 'Group B'),
    ('Sweden', 'Switzerland', 'Group B'),
    ('Iceland', 'Ukraine', 'Group D'),
    ('France', 'Azerbaijan', 'Group D'),
    ('Belgium', 'North Macedonia', 'Group J'),
    ('Latvia', 'Andorra', 'Group K'),
    ('Hungary', 'Armenia', 'Group F'),
    ('Norway', 'Israel', 'Group I'),
    ('Bulgaria', 'Türkiye', 'Group E'),
    ('Spain', 'Georgia', 'Group E'),
    ('Portugal', 'Republic of Ireland', 'Group F'),
    ('Estonia', 'Italy', 'Group I'),
    ('Serbia', 'Albania', 'Group K'),

    ('San Marino', 'Cyprus', 'Group H'),
    ('Faroe Islands', 'Czechia', 'Group L'),
    ('Netherlands', 'Finland', 'Group G'),
    ('Scotland', 'Belarus', 'Group C'),
    ('Croatia', 'Gibraltar', 'Group L'),
    ('Denmark', 'Greece', 'Group C'),
    ('Lithuania', 'Poland', 'Group G'),
    ('Romania', 'Austria', 'Group H'),
    ('Iceland', 'France', 'Group D'),
    ('North Macedonia', 'Kazakhstan', 'Group J'),
    ('Northern Ireland', 'Germany', 'Group A'),
    ('Slovakia', 'Luxembourg', 'Group A'),
    ('Slovenia', 'Switzerland', 'Group B'),
    ('Sweden', 'Kosovo', 'Group B'),
    ('Ukraine', 'Azerbaijan', 'Group D'),
    ('Wales', 'Belgium', 'Group J'),
    ('Estonia', 'Moldova', 'Group I'),
    ('Andorra', 'Serbia', 'Group K'),
    ('Republic of Ireland', 'Armenia', 'Group F'),
    ('Italy', 'Israel', 'Group I'),
    ('Latvia', 'England', 'Group K'),
    ('Portugal', 'Hungary', 'Group F'),
    ('Spain', 'Bulgaria', 'Group E'),
    ('Türkiye', 'Georgia', 'Group E'),

    ('Armenia', 'Hungary', 'Group F'),
    ('Azerbaijan', 'Iceland', 'Group D'),
    ('Norway', 'Estonia', 'Group I'),
    ('Andorra', 'Albania', 'Group K'),
    ('England', 'Serbia', 'Group K'),
    ('France', 'Ukraine', 'Group D'),
    ('Republic of Ireland', 'Portugal', 'Group F'),
    ('Moldova', 'Italy', 'Group I'),
    ('Finland', 'Malta', 'Group G'),
    ('Croatia', 'Faroe Islands', 'Group L'),
    ('Gibraltar', 'Montenegro', 'Group L'),
    ('Luxembourg', 'Germany', 'Group A'),
    ('Poland', 'Netherlands', 'Group G'),
    ('Slovakia', 'Northern Ireland', 'Group A'),
    ('Kazakhstan', 'Belgium', 'Group J'),
    ('Cyprus', 'Austria', 'Group H'),
    ('Georgia', 'Spain', 'Group E'),
    ('Liechtenstein', 'Wales', 'Group J'),
    ('Türkiye', 'Bulgaria', 'Group E'),
    ('Bosnia and Herzegovina', 'Romania', 'Group H'),
    ('Denmark', 'Belarus', 'Group C'),
    ('Greece', 'Scotland', 'Group C'),
    ('Slovenia', 'Kosovo', 'Group B'),
    ('Switzerland', 'Sweden', 'Group B'),

    ('Hungary', 'Republic of Ireland', 'Group F'),
    ('Portugal', 'Armenia', 'Group F'),
    ('Albania', 'England', 'Group K'),
    ('Azerbaijan', 'France', 'Group D'),
    ('Serbia', 'Latvia', 'Group K'),
    ('Ukraine', 'Iceland', 'Group D'),
    ('Israel', 'Moldova', 'Group I'),
    ('Italy', 'Norway', 'Group I'),
    ('Northern Ireland', 'Luxembourg', 'Group A'),
    ('Germany', 'Slovakia', 'Group A'),
    ('Belarus', 'Greece', 'Group C'),
    ('Scotland', 'Denmark', 'Group C'),
    ('Sweden', 'Slovenia', 'Group B'),
    ('Kosovo', 'Switzerland', 'Group B'),
    ('Wales', 'North Macedonia', 'Group J'),
    ('Belgium', 'Liechtenstein', 'Group J'),
    ('Austria', 'San Marino', 'Group H'),
    ('Romania', 'Bosnia and Herzegovina', 'Group H'),
    ('Bulgaria', 'Georgia', 'Group E'),
    ('Spain', 'Türkiye', 'Group E'),
    ('Lithuania', 'Malta', 'Group G'),
    ('Finland', 'Poland', 'Group G'),
    ('Montenegro', 'Gibraltar', 'Group L'),
    ('Czechia', 'Faroe Islands', 'Group L'),
]

def predict_match_outcome(home_team, away_team, match_type='group_stage'):
    home_rank_points = team_strengths.get(home_team, 1000)
    away_rank_points = team_strengths.get(away_team, 1000)

    strength_diff = home_rank_points - away_rank_points

    base_home_win_prob = 0.45
    base_draw_prob = 0.25
    base_away_win_prob = 0.30

    if match_type == 'knockout':
        base_draw_prob *= 0.8
        diff_for_wins = (0.25 - base_draw_prob) / 2
        base_home_win_prob += diff_for_wins
        base_away_win_prob += diff_for_wins

    # Explicitly initialize to avoid UnboundLocalError in very rare cases
    home_win_prob = 0.0
    away_win_prob = 0.0
    draw_prob = 0.0

    home_win_prob = base_home_win_prob + (strength_diff * 0.0005)
    away_win_prob = base_away_win_prob - (strength_diff * 0.0005)
    draw_prob = base_draw_prob - abs(strength_diff) * 0.00025

    home_win_prob = max(0.05, min(0.95, home_win_prob))
    away_win_prob = max(0.05, min(0.95, away_win_prob))
    draw_prob = max(0.05, min(0.95, draw_prob))

    total_prob = home_win_prob + draw_prob + away_win_prob
    if total_prob == 0:
        home_win_prob = draw_prob = away_win_prob = 1/3
    else:
        home_win_prob /= total_prob
        draw_prob /= total_prob
        away_win_prob /= total_prob

    outcome = random.choices(['home_win', 'draw', 'away_win'],
                             weights=[home_win_prob, draw_prob, away_win_prob], k=1)[0]

    if outcome == 'home_win':
        home_goals = random.randint(1, 4) + round((home_rank_points - away_rank_points) / 500)
        away_goals = random.randint(0, max(0, home_goals - 1))
        home_goals = max(1, home_goals)
        away_goals = max(0, away_goals)
        if home_goals <= away_goals:
            home_goals = away_goals + 1
    elif outcome == 'away_win':
        away_goals = random.randint(1, 4) + round((away_rank_points - home_rank_points) / 500)
        home_goals = random.randint(0, max(0, away_goals - 1))
        away_goals = max(1, away_goals)
        home_goals = max(0, home_goals)
        if away_goals <= home_goals:
            away_goals = home_goals + 1
    else:
        goals = random.randint(0, 3) + round((home_rank_points + away_rank_points) / 2000)
        home_goals = max(0, goals)
        away_goals = max(0, goals)
        if home_goals != away_goals:
            home_goals = away_goals = max(home_goals, away_goals)

    if match_type == 'knockout' and home_goals == away_goals:
        if random.random() < 0.5:
            home_goals += 1
        else:
            away_goals += 1

    return home_goals, away_goals

def calculate_group_standings(group_data):
    sorted_teams = sorted(group_data.items(),
                          key=lambda item: (item[1]['points'], item[1]['gd'], item[1]['gs'], team_strengths.get(item[0], 0)),
                          reverse=True)
    return sorted_teams

def determine_nations_league_playoff_teams(simulated_group_results, num_needed=4):
    nations_league_playoff_candidates = []
    
    wcq_top_two = set()
    for group_name, teams_data in simulated_group_results.items():
        sorted_teams = calculate_group_standings(teams_data)
        if len(sorted_teams) >= 2:
            wcq_top_two.add(sorted_teams[0][0])
            wcq_top_two.add(sorted_teams[1][0])

    for team in UNL_INTERIM_RANKING:
        is_in_wcq = False
        for group_data in simulated_group_results.values():
            if team in group_data:
                is_in_wcq = True
                break
        
        if not is_in_wcq:
            continue

        if team not in wcq_top_two:
            nations_league_playoff_candidates.append(team)
            if len(nations_league_playoff_candidates) >= num_needed:
                break

    return nations_league_playoff_candidates[:num_needed]

def simulate_playoffs(runners_up, nations_league_teams):
    playoff_participants = list(runners_up)
    
    for nl_team in nations_league_teams:
        if nl_team not in playoff_participants:
            playoff_participants.append(nl_team)

    if len(playoff_participants) > 16:
        playoff_participants = sorted(playoff_participants, key=lambda x: team_strengths.get(x, 0), reverse=True)[:16]
    elif len(playoff_participants) < 16:
        pass

    runners_up_for_potting = []
    nl_teams_for_potting = []
    for team in playoff_participants:
        if team in nations_league_teams:
            nl_teams_for_potting.append(team)
        else:
            runners_up_for_potting.append(team)
    
    runners_up_for_potting = sorted(runners_up_for_potting, key=lambda x: team_strengths.get(x, 0), reverse=True)

    pots = {
        'Pot1': runners_up_for_potting[0:4] if len(runners_up_for_potting) >=4 else [],
        'Pot2': runners_up_for_potting[4:8] if len(runners_up_for_potting) >=8 else [],
        'Pot3': runners_up_for_potting[8:12] if len(runners_up_for_potting) >=12 else [],
        'Pot4': nl_teams_for_potting
    }

    for pot in pots.values():
        random.shuffle(pot)

    playoff_paths = []
    
    used_teams = set()
    draw_attempts = 0
    max_draw_attempts = 1000

    while len(playoff_paths) < 4 and draw_attempts < max_draw_attempts:
        draw_attempts += 1
        
        available_pot1 = [t for t in pots['Pot1'] if t not in used_teams]
        available_pot2 = [t for t in pots['Pot2'] if t not in used_teams]
        available_pot3 = [t for t in pots['Pot3'] if t not in used_teams]
        available_pot4 = [t for t in pots['Pot4'] if t not in used_teams]

        if not (len(available_pot1) >= (4 - len(playoff_paths)) and \
                len(available_pot2) >= (4 - len(playoff_paths)) and \
                len(available_pot3) >= (4 - len(playoff_paths)) and \
                len(available_pot4) >= (4 - len(playoff_paths))):
            break
            
        try:
            p1_team = random.choice(available_pot1)
            p2_team = random.choice(available_pot2)
            p3_team = random.choice(available_pot3)
            p4_team = random.choice(available_pot4)
            
            sf1_pairing = frozenset({p1_team, p4_team})
            sf2_pairing = frozenset({p2_team, p3_team})

            clash_found = False
            for clash_set in PROHIBITED_CLASHES:
                if clash_set.issubset(sf1_pairing) or clash_set.issubset(sf2_pairing):
                    clash_found = True
                    break
            
            if (p1_team in used_teams or p2_team in used_teams or
                p3_team in used_teams or p4_team in used_teams):
                clash_found = True

            if not clash_found:
                used_teams.add(p1_team)
                used_teams.add(p2_team)
                used_teams.add(p3_team)
                used_teams.add(p4_team)

                path_name = chr(ord('A') + len(playoff_paths))
                playoff_paths.append({
                    'path_name': path_name,
                    'semis': [
                        (p1_team, p4_team),
                        (p2_team, p3_team)
                    ],
                    'final_winner': None
                })

        except IndexError:
            pass


    qualified_from_playoffs = set()
    for path in playoff_paths:
        sf_winners = []
        for home_team, away_team in path['semis']:
            home_goals, away_goals = predict_match_outcome(home_team, away_team, match_type='knockout')
            if home_goals > away_goals:
                sf_winners.append(home_team)
            else:
                sf_winners.append(away_team)
        
        if len(sf_winners) == 2:
            finalists = list(sf_winners)
            random.shuffle(finalists)
            final_home = finalists[0]
            final_away = finalists[1]

            final_home_goals, final_away_goals = predict_match_outcome(final_home, final_away, match_type='knockout')

            if final_home_goals > final_away_goals:
                path['final_winner'] = final_home
            else:
                path['final_winner'] = final_away
            
            qualified_from_playoffs.add(path['final_winner'])
        else:
            pass

    return qualified_from_playoffs


def simulate_tournament(initial_standings, all_fixtures, num_simulations=5000):
    group_winner_counts = defaultdict(int)
    runner_up_counts = defaultdict(int)
    qualified_counts = defaultdict(int)
    joint_qualification_count = 0 

    specific_16_teams = set([
        'Germany', 'France', 'Portugal', 'Spain',
        'Netherlands', 'England', 'Italy', 'Belgium',
        'Denmark', 'Croatia', 'Switzerland', 'Serbia',
        'Ukraine', 'Sweden', 'Norway', 'Scotland'
    ])

    all_simulated_group_results = []
    all_runners_up = []

    for _ in tqdm(range(num_simulations), desc="Simulating World Cup Qualifiers"):
        simulated_standings = {group: {team: data.copy() for team, data in teams.items()}
                               for group, teams in initial_standings.items()}

        for home_team, away_team, group in all_fixtures:
            if home_team not in simulated_standings[group] or away_team not in simulated_standings[group]:
                continue

            home_goals, away_goals = predict_match_outcome(home_team, away_team, match_type='group_stage')

            if home_goals > away_goals:
                simulated_standings[group][home_team]['points'] += 3
            elif home_goals < away_goals:
                simulated_standings[group][away_team]['points'] += 3
            else:
                simulated_standings[group][home_team]['points'] += 1
                simulated_standings[group][away_team]['points'] += 1

            simulated_standings[group][home_team]['gd'] += (home_goals - away_goals)
            simulated_standings[group][away_team]['gd'] += (away_goals - home_goals)
            simulated_standings[group][home_team]['gs'] += home_goals
            simulated_standings[group][away_team]['gs'] += away_goals
            simulated_standings[group][home_team]['matches_played'] += 1
            simulated_standings[group][away_team]['matches_played'] += 1

        direct_qualifiers = set()
        current_runners_up_list = []

        for group, data in simulated_standings.items():
            final_group_order = calculate_group_standings(data)
            if final_group_order:
                group_winner = final_group_order[0][0]
                group_winner_counts[group_winner] += 1
                direct_qualifiers.add(group_winner)

                if len(final_group_order) > 1:
                    runner_up = final_group_order[1][0]
                    runner_up_counts[runner_up] += 1
                    current_runners_up_list.append(runner_up)
        
        all_runners_up.append(current_runners_up_list)

        nations_league_playoff_teams = determine_nations_league_playoff_teams(simulated_standings)
        playoff_winners = simulate_playoffs(current_runners_up_list, nations_league_playoff_teams)
        
        all_qualified_this_sim = direct_qualifiers.union(playoff_winners)
        for team in all_qualified_this_sim:
            qualified_counts[team] += 1

        if specific_16_teams.issubset(all_qualified_this_sim):
            if len(all_qualified_this_sim) == len(specific_16_teams):
                joint_qualification_count += 1


    print(f"\n--- Monte Carlo Simulation Results ({num_simulations} runs) ---")
    print("\nProbability of winning group (Direct Qualification):")
    sorted_winners = sorted(group_winner_counts.items(), key=lambda item: (-item[1], item[0]))
    for team, wins in sorted_winners:
        if num_simulations > 0:
            print(f"{team}: {wins / num_simulations:.2%}")

    print("\nProbability of finishing as group runner-up (Potential Playoff Spot):")
    sorted_runners_up = sorted(runner_up_counts.items(), key=lambda item: (-item[1], item[0]))
    for team, wins in sorted_runners_up:
        if num_simulations > 0:
            print(f"{team}: {wins / num_simulations:.2%}")

    print("\nOverall Probability of Qualification (Direct or Playoff):")
    overall_probabilities = {}
    for team, qualified_times in qualified_counts.items():
        if num_simulations > 0:
            overall_probabilities[team] = qualified_times / num_simulations
    
    sorted_qualified = sorted(overall_probabilities.items(), key=lambda item: (-item[1], item[0]))
    for team, prob in sorted_qualified:
        print(f"{team}: {prob:.2%}")

    if num_simulations > 0 and len(specific_16_teams) == 16:
        joint_prob = joint_qualification_count / num_simulations
    elif num_simulations > 0:
        joint_prob
    else:
        joint_prob = 0.0


if __name__ == "__main__":
    simulate_tournament(current_standings, remaining_fixtures, num_simulations=100)