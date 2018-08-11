import requests
import json
from colorama import Fore, Style
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

verify = True


def get_fixtures():
    url_fixtures = "https://fantasy.premierleague.com/drf/fixtures/"
    with requests.Session() as s:
        r = s.get(url_fixtures, verify=verify)
        fixtures = json.loads(r.text)
        return fixtures


# /leagues-h2h-standings/{leagueId}
# /leagues-classic-standings/{leagueId}
# /leagues-classic/{leagueId} (must be a member)
# /my-team/{teamId} (requires auth)
# /entry/{entryId}
# https://fantasy.premierleague.com/drf//transfers

def get_friends():
    url_fixtures = "https://fantasy.premierleague.com/drf//leagues-classic-standings/99025"
    with requests.Session() as s:
        r = s.get(url_fixtures, verify=verify)
        fixtures = json.loads(r.text)

    res = []
    for p in fixtures['standings']['results']:
        res.append(get_player(str(p['entry'])))

    return res


def friend_history(friends, next_gw, all_players):
    for friend in friends:
        friend['picks'] = []
        friend['history'] = []
        for gw in range(1, next_gw):
            with requests.Session() as s:
                r = json.loads(
                    s.get("https://fantasy.premierleague.com/drf/entry/%s/event/%s/picks" % (
                        friend['entry']['id'], str(gw)), verify=verify).text)

            friend['picks'].append(r['picks'])
            friend['history'].append(r['entry_history'])

            for pick in friend['picks'][-1]:
                for p in all_players:
                    if pick['element'] == p.pid:
                        pick['element'] = p.name
                        pick['ep_next'] = p.fpl_expected_points




    for f in friends:
        print("\n",Fore.GREEN, f['entry']['player_first_name'], f['entry']['player_last_name'],Style.RESET_ALL)

        line = "\n"
        for n, week in enumerate(f['picks']):
            line += '{:<22}'.format("GW " + str(n+1))
        print(line)

        line = Style.RESET_ALL
        for n, week in enumerate(f['picks']):
            ep = 0
            for pick in range(15):
                ep += round(float(week[pick]['ep_next']),1)
            line += '{:<22}'.format("pts (): " + Fore.RED + str(f['history'][n]['points']) + Fore.LIGHTRED_EX + " (" +str(ep) + ")")

        print(line)

        line = Style.RESET_ALL
        for n, week in enumerate(f['picks']):
            line += '{:<22}'.format("total pts: " + Fore.GREEN + str(f['history'][n]['points']))
        print(line)

        line = Style.RESET_ALL
        for n, week in enumerate(f['picks']):
            line += '{:<22}'.format("TV (bank): " + Fore.BLUE + str(f['history'][n]['value']/10) +
                                    Fore.LIGHTBLUE_EX + " (" + str(f['history'][n]['bank']/10) + ")")
        print(line+"\n")

        for pick in range(15):
            line = Fore.CYAN
            for week in f['picks']:
                line += '{:<22}'.format(week[pick]['element'])
            print(line, Style.RESET_ALL)

    return friends

def get_players():
    url_fixtures = "https://fantasy.premierleague.com/drf/elements/"
    with requests.Session() as s:
        r = s.get(url_fixtures, verify=verify)
        fixtures = json.loads(r.text)
        return fixtures


def get_teams():
    url_teams = "https://fantasy.premierleague.com/drf/teams/"
    with requests.Session() as s:
        r = s.get(url_teams, verify=verify)
        teams = json.loads(r.text)
        return teams


def get_player(entry_id):
    url_players = "https://fantasy.premierleague.com/drf//entry/" + entry_id
    with requests.Session() as s:
        r = s.get(url_players, verify=verify)
        players = json.loads(r.text)
        return players


def get_gameweeks():
    url_gameweeks = "https://fantasy.premierleague.com/drf/events/"
    with requests.Session() as s:
        r = s.get(url_gameweeks, verify=verify)
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
