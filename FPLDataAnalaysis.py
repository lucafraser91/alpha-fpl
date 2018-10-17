from FPLDataFunctions import *
import numpy as np
import pandas as pd
from colorama import Fore, Style
import matplotlib
from scipy.stats import rankdata
import seaborn as sns
import matplotlib.pyplot as plt



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
        fpl_expected_next = 1*float(player.fpl_expected_points)  # TODO change back to 'float(player.fpl_expected_points)'
        # (1 * min([1, float(player.mins_1)])) + 0.25*float(player.fpl_expected_points)

        next_opponent = player.opponent_schedule[0][0]
        next_ishome = player.ishome_schedule[0][0]

        fpl_normalised_expected = float(fpl_expected_next) / static_team_weight[next_opponent] / static_home_weight[
            next_ishome]

        for (opponet, ishome) in zip(player.opponent_schedule, player.ishome_schedule):
            player.fpl_expected_points_schedule.append(0)
            for (opponet_fixture, ishome_fixture) in zip(opponet, ishome):
                player.fpl_expected_points_schedule[-1] += \
                    fpl_normalised_expected * static_team_weight[opponet_fixture] * static_home_weight[ishome_fixture]


def update_point_forecasts(all_players):
    for player in all_players:
        norm_pts = []
        for (opponet, ishome, points, time_on) in zip(player.opponent_past_schedule,
                                                      player.ishome_past_schedule,
                                                      player.points_past_schedule,
                                                      player.mins_played_past):




            if float(time_on) > 1:
                norm_pts.append(points / static_team_weight[opponet] / static_home_weight[ishome])


        # Normalised expected based on regresion of last 5 GW vs achual, for 16/17 season. ep = 1 + 0.5*average(5)
        normalised_ev = 1 + 0.5*np.mean(norm_pts[-5:])

        for (opponet, ishome) in zip(player.opponent_schedule, player.ishome_schedule):
            player.expected_points_schedule.append(0)
            for (opponet_fixture, ishome_fixture) in zip(opponet, ishome):
                player.expected_points_schedule[-1] += \
                    normalised_ev * static_team_weight[opponet_fixture] * static_home_weight[ishome_fixture]






def make_output_file(all_players, prediction_model="fpl", selection_filter=0):
    io = []
    io.append(["Name", "Team", "GK", "DF", "MF", "FW", "Cost", "GW1", "GW2", "GW3", "GW4", "GW5", "Next_Opponent1",
               "Next_Opponent2", "Next_Opponent3", "Next_Opponent4", "Next_Opponent5", "News", "Selected"])

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
                           str([team_name_lookup[pl] for pl in player.opponent_schedule[0][:]])[2:-2],
                           str([team_name_lookup[pl] for pl in player.opponent_schedule[1][:]])[2:-2],
                           str([team_name_lookup[pl] for pl in player.opponent_schedule[2][:]])[2:-2],
                           str([team_name_lookup[pl] for pl in player.opponent_schedule[3][:]])[2:-2],
                           str([team_name_lookup[pl] for pl in player.opponent_schedule[4][:]])[2:-2],
                           player.news,
                           player.selected_by
                           ])

            elif prediction_model == "custom":
                io.append([player.name,
                           player.team_name,
                           int(player.position is "GK"),
                           int(player.position is "DF"),
                           int(player.position is "MF"),
                           int(player.position is "FW"),
                           player.cost / 10,
                           player.expected_points_schedule[0],
                           player.expected_points_schedule[1],
                           player.expected_points_schedule[2],
                           player.expected_points_schedule[3],
                           player.expected_points_schedule[4],
                           str([team_name_lookup[pl] for pl in player.opponent_schedule[0][:]])[2:-2],
                           str([team_name_lookup[pl] for pl in player.opponent_schedule[1][:]])[2:-2],
                           str([team_name_lookup[pl] for pl in player.opponent_schedule[2][:]])[2:-2],
                           str([team_name_lookup[pl] for pl in player.opponent_schedule[3][:]])[2:-2],
                           str([team_name_lookup[pl] for pl in player.opponent_schedule[4][:]])[2:-2],
                           player.news,
                           player.selected_by
                           ])

    with open("FLP_Data_" + prediction_model + ".txt", "w") as myfile:
        for d in io:
            string = "\t".join([str(x) for x in d]) + "\n"
            myfile.write(string)
        myfile.close()


def make_friends_file(friends):
    matrix = np.zeros([len(friends), len(friends)])

    for x, f1 in enumerate(friends):
        for y, f2 in enumerate(friends):
            n1, n2 = 0, 0
            for n in range(15):
                n1 += f1['picks'][-1][n]['ep_next']
                n2 += f2['picks'][-1][n]['ep_next']

            n = max([n1, n2])
            for p1 in range(15):
                for p2 in range(15):
                    if f1['picks'][-1][p1]['element'] == f2['picks'][-1][p2]['element']:
                        if f1['picks'][-1][p1]['ep_next'] == f2['picks'][-1][p2]['ep_next']:
                            matrix[x, y] = matrix[x, y] + f1['picks'][-1][p1]['ep_next'] / n

    return matrix


def rank_chance(friends):
    weekly_average_pts = []
    for n, w in enumerate(friends[-1]['history']):
        weekly_average_pts.append(0)
        for f in friends:
            weekly_average_pts[-1] += float(f['history'][n]['points']) / len(friends)

    point_samples = []
    for n, w in enumerate(friends[-1]['history']):
        for f in friends:
            point_samples.append(float(f['history'][n]['points']) - weekly_average_pts[n])

    sigma = np.std(point_samples)
    num_bins = 20
    fig, ax = plt.subplots()
    n, bins, patches = ax.hist(point_samples, num_bins, density=1)
    y = ((1 / (np.sqrt(2 * np.pi) * sigma)) *
         np.exp(-0.5 * (1 / sigma * (bins - 0)) ** 2))
    ax.plot(bins, y, '--')
    ax.set_xlabel('weekly pts')
    ax.set_ylabel('Probability density')
    ax.set_title(r'Histogram of weekly pts: $\mu=0$, $\sigma=%ss$' % int(sigma))
    fig.tight_layout()
    plt.show()

    n_sim = 50000
    start = [p['history'][-1]['total_points'] for p in friends]
    weeks_to_ny = 21 - len(friends[-1]['history'])
    weeks_to_end = 38 - len(friends[-1]['history'])

    ny_sims = np.array(
        [[st + np.random.normal(0, sigma) * (weeks_to_ny ** 0.5) for sim in range(n_sim)] for st in start])
    ye_sims = np.array(
        [[st + np.random.normal(0, sigma) * (weeks_to_end ** 0.5) for sim in range(n_sim)] for st in start])

    ny_sims = np.array([(rankdata(ny_sims[:, sim], 'ordinal')).astype(int) for sim in range(n_sim)])
    ye_sims = np.array([(rankdata(ye_sims[:, sim], 'ordinal')).astype(int) for sim in range(n_sim)])

    ny_prob = pd.DataFrame([[np.count_nonzero(ny_sims[:, n] == rank) / n_sim for n, f in enumerate(friends)] for rank in
                            [1, 2, 3, 4, 5, 6, 7]],
                           index=[f['entry']['player_last_name'] for f in friends],
                           columns=["7th", "6th", "5th", "4th", "3rd", "2nd", "1st"]).iloc[:, ::-1]
    ye_prob = pd.DataFrame([[np.count_nonzero(ye_sims[:, n] == rank) / n_sim for n, f in enumerate(friends)] for rank in
                            [1, 2, 3, 4, 5, 6, 7]],
                           index=[f['entry']['player_last_name'] for f in friends],
                           columns=["7th", "6th", "5th", "4th", "3rd", "2nd", "1st"]).iloc[:, ::-1]

    plt.pcolor(ny_prob, vmin=0, vmax=1, cmap='nipy_spectral')
    plt.title("NY rank")
    plt.yticks(np.arange(0.5, len(ny_prob.index), 1), ny_prob.index)
    plt.xticks(np.arange(0.5, len(ny_prob.columns), 1), ny_prob.columns)
    plt.colorbar()
    plt.tight_layout()
    plt.show()
    plt.clf()

    plt.pcolor(ye_prob, vmin=0, vmax=1, cmap='nipy_spectral')
    plt.title("YE rank")
    plt.yticks(np.arange(0.5, len(ye_prob.index), 1), ye_prob.index)
    plt.xticks(np.arange(0.5, len(ye_prob.columns), 1), ye_prob.columns)
    plt.colorbar()
    plt.tight_layout()
    plt.show()



    return ny_prob, ye_prob




if __name__ == "__main__":
    fixture_info = get_fixtures()
    team_info = get_teams()
    player_info = get_players()
    gameweek_info, next_gw = get_gameweeks()
    fixture_list, ishome_list = get_schedule_lists(team_info, fixture_info, gameweek_info)
    player_info_mod = get_player_schedules(player_info, fixture_list, ishome_list, gameweek_info)

    all_players = make_player_objects(player_info_mod, next_gw)
    update_fpl_point_forecasts(all_players)
    update_point_forecasts(all_players)


    for p in all_players:
        p.print_info_basic2()

    make_output_file(all_players, "custom", selection_filter=3)
    make_output_file(all_players, "fpl", selection_filter=3)

    friends = get_friends()
    friends = friend_history(friends, next_gw, all_players)
    make_friends_file(friends)
    ny, ye = rank_chance(friends)
    print(ny)
    print(ye)
