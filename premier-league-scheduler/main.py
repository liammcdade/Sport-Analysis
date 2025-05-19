import itertools
import random

def get_premier_league_teams():
    """
    Returns a list of dictionaries, where each dictionary contains
    information about a team in the 2024-2025 Premier League.
    """
    teams = [
        {"team": "Arsenal", "location": "London (Holloway)", "stadium": "Emirates Stadium", "capacity": 60704},
        {"team": "Aston Villa", "location": "Birmingham", "stadium": "Villa Park", "capacity": 42918},
        {"team": "Bournemouth", "location": "Bournemouth", "stadium": "Vitality Stadium", "capacity": 11307},
        {"team": "Brentford", "location": "London (Brentford)", "stadium": "Gtech Community Stadium", "capacity": 17250},
        {"team": "Brighton & Hove Albion", "location": "Falmer", "stadium": "American Express Stadium", "capacity": 31876},
        {"team": "Burnley", "location": "Burnley", "stadium": "Turf Moor", "capacity": 21944},
        {"team": "Chelsea", "location": "London (Fulham)", "stadium": "Stamford Bridge", "capacity": 40173},
        {"team": "Crystal Palace", "location": "London (Selhurst)", "stadium": "Selhurst Park", "capacity": 25194},
        {"team": "Everton", "location": "Liverpool (Vauxhall)", "stadium": "Hill Dickinson Stadium", "capacity": 52888},
        {"team": "Fulham", "location": "London (Fulham)", "stadium": "Craven Cottage", "capacity": 29589},
        {"team": "Leeds United", "location": "Leeds", "stadium": "Elland Road", "capacity": 37608},
        {"team": "Liverpool", "location": "Liverpool (Anfield)", "capacity": 61276},
        {"team": "Manchester City", "location": "Manchester (Bradford)", "stadium": "Etihad Stadium", "capacity": 52900},
        {"team": "Manchester United", "location": "Manchester (Stretford)", "stadium": "Old Trafford", "capacity": 74197},
        {"team": "Newcastle United", "location": "Newcastle upon Tyne", "stadium": "St James' Park", "capacity": 52258},
        {"team": "Nottingham Forest", "location": "West Bridgford", "stadium": "City Ground", "capacity": 30404},
        {"team": "Sunderland", "location": "Sunderland", "stadium": "Stadium of Light", "capacity": 49000},
        {"team": "Tottenham Hotspur", "location": "London (Tottenham)", "stadium": "Tottenham Hotspur Stadium", "capacity": 62850},
        {"team": "West Ham United", "location": "London (Stratford)", "stadium": "London Stadium", "capacity": 62500},
        {"team": "Wolverhampton Wanderers", "location": "Wolverhampton", "stadium": "Molineux Stadium", "capacity": 31750},
    ]
    return teams

def generate_fixtures(teams):
    """
    Generates a list of fixtures for a single round of the Premier League season.

    Args:
        teams: A list of team dictionaries.

    Returns:
        A list of tuples, where each tuple represents a single match
        (e.g., (team_dict_1, team_dict_2)).  Returns an empty list if
        the number of teams is odd.
    """
    if len(teams) % 2 != 0:
        print("Warning: Odd number of teams.  One team will not have a match each round.")
        return []  # Return an empty list for an odd number of teams

    fixtures = []
    for i in range(0, len(teams), 2):
        fixtures.append((teams[i], teams[i+1]))
    return fixtures

def check_fixture_balance(schedule, team, window=5):
    """
    Checks if the home/away balance is maintained for a team within a given window.

    Args:
        schedule: The generated schedule (list of lists of tuples).
        team: The team to check (dictionary).
        window: The number of past matches to consider.

    Returns:
        True if the balance is within the rule, False otherwise.
    """
    home_count = 0
    away_count = 0
    for round_fixtures in schedule[-window:]:
        for match in round_fixtures:
            if match[0] == "BYE" or match[1] == "BYE":
                continue
            elif match[0]['team'] == team['team']:
                home_count += 1
            elif match[1]['team'] == team['team']:
                away_count += 1
    return 2 <= home_count <= 3 and 2 <= away_count <= 3

def check_consecutive_matches(schedule, team, max_consecutive=2):
    """
    Checks if a team has more than a maximum number of consecutive home or away matches.

    Args:
        schedule: The generated schedule (list of lists of tuples).
        team: The team to check (dictionary).
        max_consecutive: The maximum number of consecutive home/away matches allowed.

    Returns:
        True if the rule is not violated, False otherwise.
    """
    consecutive_home = 0
    consecutive_away = 0
    for round_fixtures in schedule:
        for match in round_fixtures:
            if match[0] == "BYE" or match[1] == "BYE":
                continue
            elif match[0]['team'] == team['team']:
                consecutive_home += 1
                consecutive_away = 0
            elif match[1]['team'] == team['team']:
                consecutive_away += 1
                consecutive_home = 0
            else:
                continue  # Team not involved in this match
        if consecutive_home > max_consecutive or consecutive_away > max_consecutive:
            return False
    return True

def check_start_end_balance(schedule, team):
    """
    Checks if a team starts and ends the season with balanced home/away matches.

    Args:
        schedule: The generated schedule (list of lists of tuples).
        team: The team to check (dictionary).

    Returns:
        True if the rule is not violated, False otherwise.
    """
    first_round = schedule[0]
    last_round = schedule[-1]
    first_match_home = False
    last_match_home = False

    for match in first_round:
        if match[0] == "BYE" or match[1] == "BYE":
            continue
        elif match[0]['team'] == team['team']:
            first_match_home = True
            break
        elif match[1]['team'] == team['team']:
            break

    for match in last_round:
        if match[0] == "BYE" or match[1] == "BYE":
            continue
        elif match[0]['team'] == team['team']:
            last_match_home = True
            break
        elif match[1]['team'] == team['team']:
            break
    return not (first_match_home and last_match_home) and not (not first_match_home and not last_match_home)

def check_boxing_day_new_years(schedule, team_dict):
    """
    Checks that a team is not home on both Boxing Day and New Year's Day.

    Args:
        schedule: The generated schedule (list of lists of tuples).
        team_dict: The team to check.

    Returns:
        True if the rule is not violated, False otherwise.
    """
    boxing_day_round = -1
    new_years_round = -1
    # Find potential Boxing Day and New Year's Day rounds (adjust as needed)
    for i, round_fixtures in enumerate(schedule):
        # This is a simplified check.  You'd need actual date logic.
        if i == 18:  # Assume round 18 is Boxing Day (adjust as needed)
            boxing_day_round = i
        if i == 21:  # Assume round 21 is New Year's Day (adjust)
            new_years_round = i

    if boxing_day_round == -1 or new_years_round == -1:
        return True  # Can't check if rounds not found

    boxing_day_home = False
    new_years_day_home = False

    for match in schedule[boxing_day_round]:
        if match[0] == "BYE" or match[1] == "BYE":
            continue
        elif match[0]['team'] == team_dict['team']:
            boxing_day_home = True
            break
        elif match[1]['team'] == team_dict['team']:
            break

    for match in schedule[new_years_round]:
        if match[0] == "BYE" or match[1] == "BYE":
            continue
        elif match[0]['team'] == team_dict['team']:
            new_years_day_home = True
            break
        elif match[1]['team'] == team_dict['team']:
            break
    return not (boxing_day_home and new_years_day_home)

def calculate_schedule_score(schedule, teams):
    """
    Calculates a score for a given schedule based on rule adherence.
    A higher score indicates a better schedule.

    Args:
        schedule: The generated schedule (list of lists of tuples).
        teams: List of team dictionaries.

    Returns:
        An integer representing the schedule's score.
    """
    score = 0
    for team in teams:
        if check_fixture_balance(schedule, team):
            score += 1
        if check_consecutive_matches(schedule, team):
            score += 1
        if check_start_end_balance(schedule, team):
            score += 1
        if check_boxing_day_new_years(schedule, team):
            score += 1
    return score



def generate_full_schedule(teams, balanced=True):
    """
    Generates a full Premier League schedule, attempting to adhere to all rules
    and optimize the schedule quality.  This version uses a smarter approach
    to try and place games strategically.

    Args:
        teams: A list of team dictionaries.
        balanced: Boolean, if True generates home and away fixtures.
                    If False, generates only single match between teams

    Returns:
        A list of lists, where each inner list represents a round of fixtures.
        Returns an empty list if the number of teams is less than 2 or an error occurs.
    """
    if len(teams) < 2:
        return []

    all_teams = list(teams)
    num_teams = len(all_teams)
    schedule = []
    available_fixtures = []  # List of all possible matches
    for t1, t2 in itertools.combinations(all_teams, 2):
        available_fixtures.append((t1, t2))
        if balanced:
            available_fixtures.append((t2, t1)) # Add the reverse fixture

    rounds = (num_teams - 1) * 2 if balanced else (num_teams - 1)
    fixtures_per_round = num_teams // 2

    for round_num in range(rounds):
        round_fixtures = []
        round_slots = list(range(fixtures_per_round)) # Keep track of available slots in round
        random.shuffle(available_fixtures) #randomize

        for _ in range(fixtures_per_round):
            if not available_fixtures:
                break # No more fixtures

            best_fixture = None
            best_score = -1

            for i, fixture in enumerate(available_fixtures):
                #check if both teams are available
                team1_available = True
                team2_available = True
                for round_match in round_fixtures:
                    if round_match[0] != "BYE" and round_match[1] != "BYE":
                        if fixture[0]['team'] == round_match[0]['team'] or fixture[0]['team'] == round_match[1]['team']:
                            team1_available = False
                        if fixture[1]['team'] == round_match[0]['team'] or fixture[1]['team'] == round_match[1]['team']:
                            team2_available = False
                if team1_available and team2_available:

                    temp_schedule = schedule + [round_fixtures + [fixture]]
                    current_score = calculate_schedule_score(temp_schedule, teams)

                    if current_score > best_score:
                        best_score = current_score
                        best_fixture = fixture

            if best_fixture:
                round_fixtures.append(best_fixture)
                available_fixtures.remove(best_fixture)
            else:
                round_fixtures.append(("BYE","BYE")) # Add Bye



        schedule.append(round_fixtures)

    return schedule

def print_schedule(schedule, teams, balanced=True):
    """
    Prints the schedule in a user-friendly format, including team details.

    Args:
        schedule: A list of lists, where each inner list represents a round
                  of fixtures.
        teams: List of team dictionaries.
        balanced: Boolean, if True prints home and away fixtures.
                    If False, prints only single match between teams
    """
    if not schedule:
        if len(teams) % 2 != 0:
            print("Schedule cannot be generated.  Odd number of teams.")
        else:
            print("No schedule to print (likely due to less than 2 teams or failure to generate a valid schedule).")
        return

    if balanced:
        num_rounds = len(schedule) // 2
        print(f"\n--- Premier League Schedule (Balanced) ---")
        for round_num, round_fixtures in enumerate(schedule[:num_rounds], 1):
            print(f"\nRound {round_num}:")
            if not round_fixtures:
                print("  No matches")
            else:
                for match in round_fixtures:
                    if match[0] == "BYE" or match[1] == "BYE":
                        print(f"  {match[0]} vs {match[1]}")
                    else:
                        home_team = match[0]
                        away_team = match[1]
                        print(f"  {home_team['team']} ({home_team['location']}) vs {away_team['team']} ({away_team['location']})")

        print(f"\n--- Reverse Fixtures ---")
        for round_num, round_fixtures in enumerate(schedule[num_rounds:], num_rounds + 1):
            print(f"\nRound {round_num}:")
            if not round_fixtures:
                print("  No matches")
            else:
                for match in round_fixtures:
                    if match[0] == "BYE" or match[1] == "BYE":
                        print(f"  {match[0]} vs {match[1]}")
                    else:
                        home_team = match[0]
                        away_team = match[1]
                        print(f"  {home_team['team']} ({home_team['location']}) vs {away_team['team']} ({away_team['location']})")
    else:
        print(f"\n--- Premier League Schedule (Single Round) ---")
        for round_num, round_fixtures in enumerate(schedule, 1):
            print(f"\nRound {round_num}:")
            if not round_fixtures:
                print("  No matches")
            else:
                for match in round_fixtures:
                    if match[0] == "BYE" or match[1] == "BYE":
                        print(f"  {match[0]} vs {match[1]}")
                    else:
                        home_team = match[0]
                        away_team = match[1]
                        print(f"  {home_team['team']} ({home_team['location']}) vs {away_team['team']} ({away_team['location']})")



def main():
    """
    Main function to generate and print the Premier League schedule.
    """
    teams = get_premier_league_teams()
    # Generate a balanced schedule (home and away games)
    balanced_schedule = generate_full_schedule(teams, balanced=True)
    print_schedule(balanced_schedule, teams, balanced=True)

    # Generate a single round robin schedule
    single_schedule = generate_full_schedule(teams, balanced=False)
    print_schedule(single_schedule, teams, balanced=False)

if __name__ == "__main__":
    main()
