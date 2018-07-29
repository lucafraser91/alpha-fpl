import urllib.request
import json
import pickle


def save_data(id):
    fp = urllib.request.urlopen("https://fantasy.premierleague.com/drf/element-summary/" + str(id))
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    fp.close()

    with open(r"C:\Users\lucaf\PycharmProjects\FPL\DataFiles" + "\\" + "Raw" + str(id) + ".txt", "w") as myfile:
        myfile.write(mystr)
        myfile.close()


def get_weekly_player_data():
    print("Getting raw player data")
    for id in range(1, 700):
        try:
            fp = urllib.request.urlopen("https://fantasy.premierleague.com/drf/element-summary/" + str(id))
            mybytes = fp.read()
            mystr = mybytes.decode("utf8")
            fp.close()

            with open(r"C:\Users\lucaf\PycharmProjects\FPL\DataFiles" + "\\" + "RawPlayerData_" + str(id) + ".txt",
                      "w") as myfile:
                myfile.write(mystr)
                myfile.close()

            print(str(id))

        except:
            print("error on " + str(id))
    print("done - Got all raw player data")
    return True


def get_current_data():
    "https://fantasy.premierleague.com/drf/bootstrap-static"

    fp = urllib.request.urlopen("https://fantasy.premierleague.com/drf/bootstrap-static")
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    fp.close()

    with open(r"C:\Users\lucaf\PycharmProjects\FPL\DataFiles" + "\\" + "AllData" + ".txt", "w") as myfile:
        myfile.write(mystr)
        myfile.close()

    return True

def unpack_raw_data():
    with open(r"C:\Users\lucaf\PycharmProjects\FPL\DataFiles" + "\\" + "AllData" + ".txt", "r") as f:
        all_data = json.load(f)
        f.close()

    player_data = all_data['elements']
    team_data = all_data['teams']

    # add the weekly history to each player under "history"
    for p in player_data:
        with open(r"C:\Users\lucaf\PycharmProjects\FPL\DataFiles\RawPlayerData_" + str(p['id']) + '.txt') as f:
            history = json.load(f)
            f.close()

        p['history'] = history['history']



    return player_data, team_data

if __name__ == "__main__":
    #get_current_data()
    player_data, team_data = unpack_raw_data()

    for t in team_data:
        print(t['name'])

    with open(r"C:\Users\lucaf\PycharmProjects\FPL\DataFiles" + "\\" + "History" + ".txt", "w") as myfile:

        for player in player_data:
            for game in player['history']:
                mystr = player['web_name'] + "\t"
                mystr += str(player['team']) + "\t"
                mystr += str(game['was_home']) + "\t"
                mystr += str(game['opponent_team']) + "\t"
                mystr += str(game['minutes']) + "\t"
                mystr += str(game['total_points']) + "\n"
                myfile.write(mystr)


        myfile.close()

    pass
    #get_weekly_player_data()
