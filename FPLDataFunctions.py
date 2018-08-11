import requests
import json
import pandas as pd
from FPL_Player import Player


team_name_lookup = {1: 'Arsenal',
                    2: 'Bournemouth',
                    3: 'Brighton',
                    4: 'Burnley',
                    5: 'Cardiff',
                    6: 'Chelsea',
                    7: 'Crystal Palace',
                    8: 'Everton',
                    9: 'Fulham',
                    10: 'Huddersfield',
                    11: 'Leicester',
                    12: 'Liverpool',
                    13: 'Man City',
                    14: 'Man Utd',
                    15: 'Newcastle',
                    16: 'Southampton',
                    17: 'Spurs',
                    18: 'Watford',
                    19: 'West Ham',
                    20: 'Wolves'
                    }
position_lookup = {1: 'GK',
                   2: 'DF',
                   3: 'MF',
                   4: 'FW'}


def get_fixtures():
    url_fixtures = "https://fantasy.premierleague.com/drf/fixtures/"
    with requests.Session() as s:
        r = s.get(url_fixtures, verify=False)
        fixtures = json.loads(r.text)
        return fixtures


def get_teams():
    url_teams = "https://fantasy.premierleague.com/drf/teams/"
    with requests.Session() as s:
        r = s.get(url_teams, verify=False)
        teams = json.loads(r.text)
        return teams


def get_players():
    url_players = "https://fantasy.premierleague.com/drf/elements/"
    with requests.Session() as s:
        r = s.get(url_players, verify=False)
        players = json.loads(r.text)
        return players


def get_gameweeks():
    url_gameweeks = "https://fantasy.premierleague.com/drf/events/"
    with requests.Session() as s:
        r = s.get(url_gameweeks, verify=False)
        gameweeks = json.loads(r.text)

    for gameweek in gameweeks:
        if gameweek['is_next']:
            next_gw = gameweek['id']
        return gameweeks, next_gw

def clean(input):
    if input is None:
        return '0'
    else:
        return input

def get_schedule_lists(team_info, fixture_info, gameweek_info):
    fixture_list = {}
    ishome_list = {}

    for team in team_info:
        fixture_list[team["id"]] = {}
        ishome_list[team["id"]] = {}

        for gameweek in gameweek_info:
            fixture_list[team["id"]][gameweek["id"]] = []
            ishome_list[team["id"]][gameweek["id"]] = []

        for fixture in fixture_info:
            if fixture['team_h'] == team["id"]:
                fixture_list[team["id"]][fixture['event']].append(fixture['team_a'])
                ishome_list[team["id"]][fixture['event']].append(True)
            elif fixture['team_a'] == team["id"]:
                fixture_list[team["id"]][fixture['event']].append(fixture['team_h'])
                ishome_list[team["id"]][fixture['event']].append(False)
            else:
                pass

    return fixture_list, ishome_list


def get_player_schedules(player_info, fixture_list, ishome_list, gameweek_info):
    print('Updating fixture schedules')

    for n, player in enumerate(player_info[:]):
        player_info[n]['opponent_schedule'] = []
        player_info[n]['ishome_schedule'] = []

        for gameweek in gameweek_info:
            if (not gameweek['finished']) or (not gameweek['is_current']):
                player_info[n]['opponent_schedule'].append(fixture_list[player['team']][gameweek['id']])
                player_info[n]['ishome_schedule'].append(ishome_list[player['team']][gameweek['id']])

    return player_info


def make_player_objects(player_info_mod, next_gw):
    all_players = []
    for player in player_info_mod:
        new_player = Player(player['id'],
                            player['web_name'],
                            position_lookup[player['element_type']],
                            player['now_cost'],
                            player['team'],
                            team_name_lookup[player['team']],
                            next_gw,
                            player['opponent_schedule'],
                            player['ishome_schedule'],
                            clean(player['ep_next']),
                            player['selected_by_percent'],
                            player['news'])
        all_players.append(new_player)
    all_players.sort(key=lambda x: x.fpl_expected_points, reverse=True)

    return all_players





if __name__ == '__main__':

    fixture_info = get_fixtures()
    team_info = get_teams()
    player_info = get_players()
    gameweek_info, next_gw = get_gameweeks()
    fixture_list, ishome_list = get_schedule_lists(team_info, fixture_info, gameweek_info)
    player_info_mod = get_player_schedules(player_info, fixture_list, ishome_list)
    all_players = make_player_objects(player_info_mod)

    pass
