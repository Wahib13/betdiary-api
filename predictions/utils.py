import pandas as pd

import numpy as np
from scipy.stats import poisson


def display_head_to_head(df, team_a, team_b):
    return df[((df.HomeTeam == team_a) & (df.AwayTeam == team_b)) | ((df.AwayTeam == team_a) & (df.HomeTeam == team_b))]


def display_team(df, team_a):
    return df[(df.HomeTeam == team_a) | (df.AwayTeam == team_a)]


def get_goals(row, team):
    if row['HomeTeam'] == team:
        return row.FTHG
    if row['AwayTeam'] == team:
        return row.FTAG


def get_match_location(row, team):
    if row.HomeTeam == team:
        return 'H'
    if row.AwayTeam == team:
        return 'A'


def get_goals_conceded(row, team):
    if row['HomeTeam'] == team:
        return row.FTAG
    if row['AwayTeam'] == team:
        return row.FTHG


def get_team(row, team):
    if row['HomeTeam'] == team:
        return row.HomeTeam
    if row['AwayTeam'] == team:
        return row.AwayTeam


def get_opponent(row, team):
    if row['HomeTeam'] == team:
        return row.AwayTeam
    if row['AwayTeam'] == team:
        return row.HomeTeam


def get_result(row, team):
    if row.FTR == 'D':
        return 'D'
    if row.HomeTeam == team and row.FTR == 'H':
        return 'W'
    if row.AwayTeam == team and row.FTR == 'A':
        return 'W'
    return 'L'


def get_shots(row, team):
    if row.HomeTeam == team:
        return row.HS
    if row.AwayTeam == team:
        return row.AS


def get_shots_conceded(row, team):
    if row.HomeTeam == team:
        return row.AS
    if row.AwayTeam == team:
        return row.HS


def get_goal_difference(team):
    return get_shots(team) - get_shots_conceded(team)


def get_gg(row, team):
    if row.FTHG > 0 and row.FTAG > 0:
        return True
    return False


def summarize_team_season(df, team_name):
    columns_of_interest = ['Date', 'Time', 'HomeTeam', 'AwayTeam', 'FTR', 'FTHG', 'FTAG']

    df_team = display_team(df, team_name)
    df_team = df_team[columns_of_interest]
    df_team['team'] = df_team.apply(lambda row: get_team(row, team_name), axis=1)
    df_team['opponent'] = df_team.apply(lambda row: get_opponent(row, team_name), axis=1)
    df_team['location'] = df_team.apply(lambda row: get_match_location(row, team_name), axis=1)
    df_team['result'] = df_team.apply(lambda row: get_result(row, team_name), axis=1)
    df_team['goals_scored'] = df_team.apply(lambda row: get_goals(row, team_name), axis=1)
    df_team['goals_conceded'] = df_team.apply(lambda row: get_goals_conceded(row, team_name), axis=1)
    # df_team['shots'] = df_team.apply(lambda row: get_shots(row, team_name), axis=1)
    # df_team['shots_conceded'] = df_team.apply(lambda row: get_shots_conceded(row, team_name), axis=1)
    df_team['goal_goal'] = df_team.apply(lambda row: get_gg(row, team_name), axis=1)

    df_team = df_team.reset_index()
    df_team.drop(columns=['FTR', 'HomeTeam', 'AwayTeam', 'FTR', 'FTHG', 'FTAG'], inplace=True)
    return df_team


def get_total_wins(df_team):
    return len(df_team[df_team.result == 'W'])


def get_total_losses(df_team):
    return len(df_team[df_team.result == 'L'])


def get_total_draws(df_team):
    return len(df_team[df_team.result == 'D'])


def get_total_goals(df_team):
    return df_team.goals_scored.sum()


def get_total_goals_conceded(df_team):
    return df_team.goals_conceded.sum()


def get_home_goals(df_team):
    return df_team[df_team.location == 'H'].goals_scored.sum()


def get_away_goals(df_team):
    return df_team[df_team.location == 'A'].goals_scored.sum()


def get_total_clean_sheets(df_team):
    return len(df_team[df_team.goals_conceded == 0])


def get_goal_goal_count(df_team):
    return df_team.goal_goal.sum()


def print_stats_of_interest(df_team):
    print(f'total matches: {len(df_team)}')
    print(f'total wins: {get_total_wins(df_team)}')
    print(f'total draws: {get_total_draws(df_team)}')
    print(f'total losses: {get_total_losses(df_team)}')
    print(f'total goals: {get_total_goals(df_team)}')
    print(f'total home goals: {get_home_goals(df_team)}')
    print(f'total away goals: {get_away_goals(df_team)}')
    print(f'total goals conceded: {get_total_goals_conceded(df_team)}')
    print(f'total clean sheets: {get_total_clean_sheets(df_team)}')
    print(f'{round(get_total_clean_sheets(df_team) / len(df_team), 2) * 100}% clean sheets')
    print(f'GG matches: {get_goal_goal_count(df_team)}')
    print(f'{round(get_goal_goal_count(df_team) / len(df_team), 2) * 100}% GG')


def get_last_match_performance(df, team_name, n_matches_in_past=-1):
    df_team = summarize_team_season(df, team_name)

    # print(df_team)

    teamA_last_match_row = df_team.iloc[n_matches_in_past]
    teamA_matches_up_to_last_match = df_team.iloc[:n_matches_in_past]

    total_goals = teamA_matches_up_to_last_match.goals_scored.sum()
    if total_goals == 0:
        weighted_goals = total_goals
    else:
        weighted_goals = teamA_last_match_row.goals_scored / total_goals

    total_conceded = teamA_matches_up_to_last_match.goals_conceded.sum()

    if total_conceded == 0:
        weighted_conceded = 0
    else:
        weighted_conceded = teamA_last_match_row.goals_conceded / total_conceded

    teamA_performance = weighted_goals - weighted_conceded

    opponent_team = teamA_last_match_row.opponent
    df_opponent = summarize_team_season(df, opponent_team)

    # print(df_opponent)

    last_matchup = df_opponent[df_opponent.opponent == team_name].iloc[-1]
    teamB_matches_up_to_last_match = df_opponent.iloc[:int(last_matchup.name)]

    total_goals = teamB_matches_up_to_last_match.goals_scored.sum()
    if total_goals == 0:
        weighted_goals = 0
    else:
        weighted_goals = last_matchup.goals_scored / total_goals

    total_conceded = teamB_matches_up_to_last_match.goals_conceded.sum()
    if total_conceded == 0:
        weighted_conceded = 0
    else:
        weighted_conceded = last_matchup.goals_conceded / total_conceded

    teamB_performance = weighted_goals - weighted_conceded

    # print(teamA_performance)
    # print(teamB_performance)

    return teamA_performance - teamB_performance


def get_goal_difference_before_match(df_team, row):
    """
    an estimate of the team's current 'strength
    """
    df_matches_before_row = df_team.iloc[:int(row.name)]
    sum_goal_difference = df_matches_before_row.goals_scored.sum() - df_matches_before_row.goals_conceded.sum()
    return sum_goal_difference


def get_average_goals_scored_before_match(df_country, df_team, row=None):
    """
    estimate of team's attacking strength at that match day - chance of scoring (higher is better)
    """
    if row is not None:
        df_team_matches_before_row = df_team.iloc[:int(row.name)]
        df_league_matches_before_row = df_country[
            pd.to_datetime(df_country.Date, format='%d/%m/%Y') < pd.to_datetime(row.Date, format='%d/%m/%Y')]
    else:
        df_team_matches_before_row = df_team
        df_league_matches_before_row = df_country

    sum_team_goals = df_team_matches_before_row.goals_scored.sum()
    average_team_goals = sum_team_goals / len(df_team)

    sum_league_goals = df_league_matches_before_row.FTHG.sum() + df_league_matches_before_row.FTAG.sum()
    average_league_goals = sum_league_goals / len(df_league_matches_before_row)

    return average_team_goals / average_league_goals


def get_average_goals_conceded_before_match(df_country, df_team, row=None):
    """
    estimate of team's defensive strength at that match day - chance of conceding (lower is better)
    """
    if row is not None:
        df_team_matches_before_row = df_team.iloc[:int(row.name)]
        df_league_matches_before_row = df_country[
            pd.to_datetime(df_country.Date, format='%d/%m/%Y') < pd.to_datetime(row.Date, format='%d/%m/%Y')]
    else:
        df_team_matches_before_row = df_team
        df_league_matches_before_row = df_country

    sum_team_conceded = df_team_matches_before_row.goals_conceded.sum()
    average_team_conceded = sum_team_conceded / len(df_team)

    sum_league_goals = df_league_matches_before_row.FTHG.sum() + df_league_matches_before_row.FTAG.sum()
    average_league_goals = sum_league_goals / len(df_league_matches_before_row)

    return average_team_conceded / average_league_goals


def get_teams_scoring_probability(df_country, df_team, row):
    scoring_probability = get_average_goals_scored_before_match(df_country, df_team, row=row)
    df_opponent = add_form(df_country, row.opponent)
    # corresponding row in opponent dataframe
    row_opponent = df_opponent[df_opponent['index'] == row['index']].iloc[0]
    opponents_conceding_probability = get_average_goals_conceded_before_match(df_country, df_opponent, row=row_opponent)

    full_scoring_probability = scoring_probability * opponents_conceding_probability
    return full_scoring_probability


def upcoming_scoring_probability(df_country, df_team, opponent_name):
    df_opponent = add_form(df_country, opponent_name)

    scoring_probability = get_average_goals_scored_before_match(df_country, df_team)
    opponents_conceding_probability = get_average_goals_conceded_before_match(df_country, df_opponent)

    full_scoring_probability = scoring_probability * opponents_conceding_probability
    return full_scoring_probability


def get_teams_conceding_probability(df_country, df_team, row):
    """
    same logic as scoring probability but reversed
    """
    conceding_probability = get_average_goals_conceded_before_match(df_country, df_team, row=row)
    df_opponent = add_form(df_country, row.opponent)
    # corresponding row in opponent dataframe
    row_opponent = df_opponent[df_opponent['index'] == row['index']].iloc[0]

    opponents_scoring_probability = get_average_goals_scored_before_match(df_country, df_opponent, row=row_opponent)

    full_conceding_probability = conceding_probability * opponents_scoring_probability
    return full_conceding_probability


def get_form_difference_last_match_week(df_team, df_country, row):
    match_week = int(row.name)
    if match_week == 0:
        return 0
    last_match_week = match_week - 1
    form_difference = df_team.iloc[last_match_week].form - add_form(df_country, row.opponent).iloc[last_match_week].form
    return form_difference


def add_form(df_country, team_name):
    form_array = []
    for i in range(11):
        form_array.append(get_last_match_performance(df_country, team_name, -(i + 1)))
    form_array.reverse()
    form_array = np.array(form_array)

    df_team = summarize_team_season(df_country, team_name)
    # pad to make up for the gaps in the early matches
    for i in range(len(df_team) - len(form_array)):
        form_array = np.insert(form_array, 0, 0)
    df_team['form'] = form_array
    df_team['goal_difference'] = df_team.apply(lambda row: row.goals_scored - row.goals_conceded, axis=1)
    df_team['goal_difference_before_match'] = df_team.apply(lambda row: get_goal_difference_before_match(df_team, row),
                                                            axis=1)
    return df_team


def add_form_before_match(df_team, df_country):
    df_team['form_difference_before_match'] = df_team.apply(
        lambda row: get_form_difference_last_match_week(df_team, df_country, row), axis=1)
    return df_team


def add_scoring_and_conceding_probabilities(df_team, df_country):
    df_team['scoring_probability'] = df_team.apply(lambda row: get_teams_scoring_probability(df_country, df_team, row),
                                                   axis=1)
    df_team['conceding_probability'] = df_team.apply(
        lambda row: get_teams_conceding_probability(df_country, df_team, row), axis=1)
    return df_team


def get_team_features(df_country, team_name):
    df_team = add_form(df_country, team_name)
    df_team = add_form_before_match(df_team, df_country)
    return df_team


def get_poisson_probabilities(scoring_probability):
    scores = []
    mu = scoring_probability
    scores_of_interest = [0, 1, 2, 3, 4, 5]
    for score in scores_of_interest:
        scores.append(round(poisson.pmf(k=score, mu=mu), 8))
    return scores


def give_all_info(df_country, team_name, opponent_name):
    result = {}
    df_team = add_form(df_country, team_name)
    df_opponent = add_form(df_country, opponent_name)
    df_team = add_form_before_match(df_team, df_country)
    df_team = add_scoring_and_conceding_probabilities(df_team, df_country)

    upcoming_match_scoring_probability = upcoming_scoring_probability(df_country, df_team, opponent_name)
    upcoming_match_conceding_probability = upcoming_scoring_probability(df_country, df_opponent, team_name)

    result['upcoming_match_scoring_probabilities'] = get_poisson_probabilities(upcoming_match_scoring_probability)
    result['upcoming_match_conceding_probabilities'] = get_poisson_probabilities(upcoming_match_conceding_probability)

    result['team_form'] = df_team.iloc[-1].form
    result['opponent_form'] = df_opponent.iloc[-1].form
    result['form_difference'] = result['team_form'] - result['opponent_form']

    return result
