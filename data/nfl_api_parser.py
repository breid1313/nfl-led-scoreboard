import requests
import datetime
from utils import convert_time

URL = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"

def get_game(team_name):
    try:
        res = requests.get(URL)
        res = res.json()
        for g in res['events']:
            if team_name in g['shortName']:
                info = g['competitions'][0]
                game = {'name': g['shortName'], 'date': g['date'],
                        'hometeam': info['competitors'][0]['team']['abbreviation'], 'homeid': info['competitors'][0]['id'], 'homescore': int(info['competitors'][0]['score']),
                        'awayteam': info['competitors'][1]['team']['abbreviation'], 'awayid': info['competitors'][1]['id'], 'awayscore': int(info['competitors'][1]['score']),
                        'down': info.get('situation', {}).get('shortDownDistanceText'), 'spot': info.get('situation', {}).get('possessionText'),
                        'time': info['status']['displayClock'], 'quarter': info['status']['period'], 'over': info['status']['type']['completed'],
                        'redzone': info.get('situation', {}).get('isRedZone'), 'possession': info.get('situation', {}).get('possession'), 'state': info['status']['type']['state']}
                return game
    except requests.exceptions.RequestException:
        print("Error encountered getting game info, can't hit ESPN api")
    except Exception as e:
        print("something bad?", e)

def get_all_games():
    try:
        res = requests.get(URL)
        res = res.json()
        games = {}
        i = 0
        for g in res['events']:
            info = g['competitions'][0]
            game = {'name': g['shortName'], 'date': g['date'],
                    'hometeam': info['competitors'][0]['team']['abbreviation'], 'homeid': info['competitors'][0]['id'], 'homescore': int(info['competitors'][0]['score']),
                    'awayteam': info['competitors'][1]['team']['abbreviation'], 'awayid': info['competitors'][1]['id'], 'awayscore': int(info['competitors'][1]['score']),
                    'down': info.get('situation', {}).get('shortDownDistanceText'), 'spot': info.get('situation', {}).get('possessionText'),
                    'time': info['status']['displayClock'], 'quarter': info['status']['period'], 'over': info['status']['type']['completed'],
                    'redzone': info.get('situation', {}).get('isRedZone'), 'possession': info.get('situation', {}).get('possession'), 'state': info['status']['type']['state']}
            games[i] = game
            i += 1
        return games
    except requests.exceptions.RequestException:
        print("Error encountered getting game info, can't hit ESPN api")
    except Exception as e:
        print("something bad?", e)

def which_playoff_game(games, game):
    # games should be sorted by date, earliest to latest
    for game in games:
        # testing purposes
        # if games[game]['state'] == 'post':
        #     return games[game]
        if games[game]['state'] == 'in':
            return games[game]
        if games[game]['state'] == 'pre':
            return games[game]
    return game

def is_playoffs():
    try:
        res = requests.get(URL)
        res = res.json()
        return res['season']['type'] == 3
    except requests.exceptions.RequestException:
        print("Error encountered getting game info, can't hit ESPN api")
    except Exception as e:
        print("something bad?", e)