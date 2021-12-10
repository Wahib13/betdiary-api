import asyncio
import os
from uuid import uuid4

import pandas as pd

from dependencies import data
from dependencies.data import delete_other_bet_info
from models import League, BetInfo
from predictions.scrape import save_new_data_files, leagues, english_teams, get_upcoming_matches
from predictions.utils import give_all_info


def get_dataframe_team_name(upcoming_match_name):
    teams = list(filter(lambda team: team.upcoming_match_name == upcoming_match_name, english_teams))
    if len(teams) == 0:
        return ''
    team = teams[0]
    return team.dataframe_name


async def load():
    # identify the job that loaded this info
    processing_job_id = uuid4()
    save_new_data_files()
    # process england
    english_league: League = leagues.get('english')
    df_england = pd.read_csv(f'{os.environ.get("DATA_STORAGE_ROOT")}/{english_league.current_data_filename}')
    upcoming_matches = get_upcoming_matches(english_league.url_upcoming_matches)
    for match in upcoming_matches:
        print(f'Processing {match[0]} vs {match[1]}')
        stats = give_all_info(df_england, get_dataframe_team_name(match[0]), get_dataframe_team_name(match[1]))
        print(f'\n')
        bet_info = BetInfo(league=english_league.common_name, home_team_name=match[0],
                           away_team_name=match[1], home_team_form=stats.get('team_form'),
                           away_team_form=stats.get('opponent_form'), form_difference=stats.get('form_difference'),
                           scoring_probabilities=stats.get('upcoming_match_scoring_probabilities'),
                           conceding_probabilities=stats.get('upcoming_match_conceding_probabilities'),
                           job_id=str(processing_job_id))
        await data.create_bet_info(bet_info)

    # delete other records
    await delete_other_bet_info(str(processing_job_id))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(load())
