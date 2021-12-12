import os
import shutil
from bs4 import BeautifulSoup
import requests
from models import *

premier_league_url_upcoming_matches = 'https://www.oddsportal.com/soccer/england/premier-league/'
bundesliga_url_upcoming_matches = 'https://www.oddsportal.com/soccer/germany/bundesliga/'
serie_a_url_upcoming_matches = 'https://www.oddsportal.com/soccer/italy/serie-a/'
la_liga_url_upcoming_matches = 'https://www.oddsportal.com/soccer/spain/laliga/'

premier_league_url_current_data = 'https://www.football-data.co.uk/mmz4281/2122/E0.csv'
bundesliga_url_current_data = 'https://www.football-data.co.uk/mmz4281/2122/D1.csv'
serie_a_url_current_data = 'https://www.football-data.co.uk/mmz4281/2122/SP1.csv'
la_liga_url_current_data = 'https://www.football-data.co.uk/mmz4281/2122/I1.csv'

english_league: League = League(common_name='premier_league', url_upcoming_matches=premier_league_url_upcoming_matches,
                                url_current_data=premier_league_url_current_data, current_data_filename='E0.csv')

german_league: League = League(common_name='bundesliga', url_upcoming_matches=bundesliga_url_upcoming_matches,
                               url_current_data=bundesliga_url_current_data, current_data_filename='D1.csv')

spanish_league: League = League(common_name='la_liga', url_upcoming_matches=la_liga_url_upcoming_matches,
                                url_current_data=la_liga_url_current_data, current_data_filename='SP1.csv')

italian_league: League = League(common_name='serie_a', url_upcoming_matches=serie_a_url_upcoming_matches,
                                url_current_data=la_liga_url_current_data, current_data_filename='I1.csv')

leagues = {
    'english': english_league,
    'german': german_league,
    'spanish': spanish_league,
    'italian': italian_league
}


def save_new_data_files():
    for league in leagues.values():
        r = requests.get(league.url_current_data, stream=True)
        # todo make directory if does not exist
        filename = f'{os.environ.get("DATA_STORAGE_ROOT")}/{league.current_data_filename}'
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)


def get_upcoming_league_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    html_text = requests.get(url, headers=headers).text
    return html_text


def is_link_to_upcoming_match(table_link):
    if table_link.get('href') != 'javascript:void(0);':
        if ' - ' in table_link.text:
            return True
    return False


def not_postponed_due_to_covid(column):
    spans = column.find_all('span')
    if len(spans) == 0:
        return True
    span = spans[0]
    if span.get('onmouseover',
                '') == "toolTip('Postponed due to Covid-19.', this, event, '4');" \
                       "allowHideTootip(false);delayHideTip(200);return false;":
        return False
    return True


def extract_upcoming_matches(table_row):
    columns = table_row.find_all('td')
    columns = list(filter(lambda column: column.get('class') == ['name', 'table-participant'], columns))
    # filter out matches that have a span (eg: match postponed)
    columns = list(filter(not_postponed_due_to_covid, columns))
    if len(columns) > 0:
        column = columns[0]
        links = column.find_all('a')
        upcoming_match = list(filter(is_link_to_upcoming_match, links))[0]
        return [upcoming_match.text.split(' - ')[0], upcoming_match.text.split(' - ')[1]]


def get_upcoming_matches(url):
    html_text = get_upcoming_league_html(url)
    soup = BeautifulSoup(html_text, 'html.parser')
    table_body = soup.find('table').find('tbody')

    table_rows = table_body.find_all('tr')
    # table_rows = filter(lambda table_row: table_row.get('class') or table_row.get('xeid'), table_rows)
    table_rows = filter(lambda table_row: ('odd' in table_row.get('class', []) and 'deactivate' not in table_row.get(
        'class', [])) or table_row.get('xeid'), table_rows)

    upcoming_matches = list(map(extract_upcoming_matches, table_rows))

    # limit to only upcoming week
    unique_teams = []
    true_upcoming_matches = []
    for upcoming_match in upcoming_matches:
        if not upcoming_match:
            continue
        home_team = upcoming_match[0]
        away_team = upcoming_match[1]
        if home_team in unique_teams or away_team in unique_teams:
            break
        unique_teams.append(home_team)
        unique_teams.append(away_team)
        true_upcoming_matches.append(upcoming_match)

    return true_upcoming_matches


arsenal: Team = Team(league=english_league, dataframe_name='Arsenal', upcoming_match_name='Arsenal')
aston_villa: Team = Team(league=english_league, dataframe_name='Aston Villa', upcoming_match_name='Aston Villa')
brentford: Team = Team(league=english_league, dataframe_name='Brighton', upcoming_match_name='Brighton')
brighton: Team = Team(league=english_league, dataframe_name='Brentford', upcoming_match_name='Brentford')
burnley: Team = Team(league=english_league, dataframe_name='Burnley', upcoming_match_name='Burnley')

chelsea: Team = Team(league=english_league, dataframe_name='Chelsea', upcoming_match_name='Chelsea')
crystal_palace: Team = Team(league=english_league, dataframe_name='Crystal Palace',
                            upcoming_match_name='Crystal Palace')
everton: Team = Team(league=english_league, dataframe_name='Everton', upcoming_match_name='Everton')
leeds: Team = Team(league=english_league, dataframe_name='Leeds', upcoming_match_name='Leeds')
leicester: Team = Team(league=english_league, dataframe_name='Leicester', upcoming_match_name='Leicester')

liverpool: Team = Team(league=english_league, dataframe_name='Liverpool', upcoming_match_name='Liverpool')
man_city: Team = Team(league=english_league, dataframe_name='Man City', upcoming_match_name='Manchester City')
man_united: Team = Team(league=english_league, dataframe_name='Man United', upcoming_match_name='Manchester Utd')
newcastle: Team = Team(league=english_league, dataframe_name='Newcastle', upcoming_match_name='Newcastle')
norwich: Team = Team(league=english_league, dataframe_name='Norwich', upcoming_match_name='Norwich')

southampton: Team = Team(league=english_league, dataframe_name='Southampton', upcoming_match_name='Southampton')
tottenham: Team = Team(league=english_league, dataframe_name='Tottenham', upcoming_match_name='Tottenham')
watford: Team = Team(league=english_league, dataframe_name='Watford', upcoming_match_name='Watford')
west_ham: Team = Team(league=english_league, dataframe_name='West Ham', upcoming_match_name='West Ham')
wolves: Team = Team(league=english_league, dataframe_name='Wolves', upcoming_match_name='Wolves')

english_teams = [
    arsenal,
    aston_villa,
    brentford,
    brighton,
    burnley,
    chelsea,
    crystal_palace,
    everton,
    leeds,
    leicester,
    liverpool,
    man_city,
    man_united,
    newcastle,
    norwich,
    southampton,
    tottenham,
    watford,
    west_ham,
    wolves
]
