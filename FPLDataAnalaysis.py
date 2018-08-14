from FPLDataFunctions import *
from colorama import Fore, Style

static_team_weight = {1: 0.876906824541861,
                      2: 1.07534128246658,
                      3: 1.15445879184266,
                      4: 1.01355853220228,
                      5: 1.22620515599513,
                      6: 0.835027566258126,
                      7: 1.0524476659609,
                      8: 1.07352682656674,
                      9: 1.13575483855879,
                      10: 1.22379462349427,
                      11: 0.979705499536258,
                      12: 0.794125678826656,
                      13: 0.584223364294703,
                      14: 0.779838042936587,
                      15: 1.049736223093,
                      16: 1.11057725003866,
                      17: 0.75385008890512,
                      18: 1.11085987094855,
                      19: 1.07608139214212,
                      20: 1.05256203135394
                      }

static_home_weight = {True: 1.087651551,
                      False: 0.912348449}


def update_fpl_point_forecasts(all_players):
    for player in all_players:
        fpl_expected_next = float(player.fpl_expected_points)
        next_opponent = player.opponent_schedule[0][0]
        next_ishome = player.ishome_schedule[0][0]

        fpl_normalised_expected = float(fpl_expected_next) / static_team_weight[next_opponent] / static_home_weight[
            next_ishome]

        for (opponet, ishome) in zip(player.opponent_schedule, player.ishome_schedule):
            player.fpl_expected_points_schedule.append(0)
            for (opponet_fixture, ishome_fixture) in zip(opponet, ishome):
                player.fpl_expected_points_schedule[-1] += \
                    fpl_normalised_expected * static_team_weight[opponet_fixture] * static_home_weight[ishome_fixture]


def make_output_file(all_players, prediction_model="fpl", selection_filter=0):
    io = []
    io.append(["Name", "Team", "GK", "DF", "MF", "FW", "Cost", "GW1", "GW2", "GW3", "GW4", "GW5","Next_Opponent", "News", "Selected"])

    for player in all_players:
        if float(player.selected_by) >= float(selection_filter) and player.name != "Sánchez":
            if prediction_model == "fpl":
                io.append([player.name,
                           player.team_name,
                           int(player.position is "GK"),
                           int(player.position is "DF"),
                           int(player.position is "MF"),
                           int(player.position is "FW"),
                           player.cost / 10,
                           player.fpl_expected_points_schedule[0],
                           player.fpl_expected_points_schedule[1],
                           player.fpl_expected_points_schedule[2],
                           player.fpl_expected_points_schedule[3],
                           player.fpl_expected_points_schedule[4],
                           team_name_lookup[player.opponent_schedule[0][0]],
                           player.news,
                           player.selected_by
                           ])

            else:
                io.append([player.name,
                           player.team_name,
                           int(player.position is "GK"),
                           int(player.position is "DF"),
                           int(player.position is "MF"),
                           int(player.position is "FW"),
                           player.cost / 10,
                           "select prediction model",
                           "select prediction model",
                           "select prediction model",
                           "select prediction model",
                           "select prediction model"
                           ])

    with open("FLP_Data_" + prediction_model + ".txt", "w") as myfile:
        for d in io:
            string = "\t".join([str(x) for x in d]) + "\n"
            myfile.write(string)
        myfile.close()


def make_friends_file(frends):
    pass




if __name__ == "__main__":
    fixture_info = get_fixtures()
    team_info = get_teams()
    player_info = get_players()
    gameweek_info, next_gw = get_gameweeks()
    fixture_list, ishome_list = get_schedule_lists(team_info, fixture_info, gameweek_info)
    player_info_mod = get_player_schedules(player_info, fixture_list, ishome_list, gameweek_info)
    all_players = make_player_objects(player_info_mod, next_gw)
    update_fpl_point_forecasts(all_players)

    for p in all_players:
        p.print_info_basic()

    make_output_file(all_players, "fpl", selection_filter=3)

    friends = get_friends()
    friends = friend_history(friends, next_gw, all_players)







