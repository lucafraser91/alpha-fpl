import json
import pickle
from GetRawData import *

def get_pos(element_type):
    return ['GK', 'DF', 'MF', 'FW'][element_type - 1]



class DataPoint(object):
    def __init__(self, pid, web_name, team_no, pos, opponent, washome, gw, selected_lw, points_5, points_4, points_3,
                 points_2, points_1, consecutive, start_lw, net_transfers_lw, target):
        self.pid = pid
        self.web_name = web_name
        self.team = team_no
        self.pos = pos
        self.opponent = opponent
        self.washome = washome
        self.gw = gw
        self.selected_lw = selected_lw
        self.net_transfers_lw = net_transfers_lw
        self.points_5 = points_5
        self.points_4 = points_4
        self.points_3 = points_3
        self.points_2 = points_2
        self.points_1 = points_1
        self.consecutive = consecutive
        self.start_lw = start_lw
        self.target = target


player_data, team_data = unpack_raw_data()

all_data_points = []
for p in player_data:
    print(str(p['id']) + "\t" + p['web_name'])

    for w, weeks_data in enumerate(p['history']):
        if w > 4:

            consecutive = 0
            for i in range(w - 1, w - 5, -1):
                if p['history'][i]['minutes'] > 0:
                    consecutive += 1
                else:
                    break

            all_data_points.append(DataPoint(pid=p['id'],
                                             web_name=p['web_name'],
                                             team_no=str(p['team']),
                                             pos=get_pos(p['element_type']),
                                             opponent=team_data[weeks_data['opponent_team']-1]['name'],
                                             washome=weeks_data['was_home'],
                                             selected_lw=p['history'][w - 1]['selected'],
                                             gw=weeks_data['round'],
                                             points_5=(p['history'][w - 5]['total_points'] + p['history'][w - 4][
                                                 'total_points'] + p['history'][w - 3]['total_points'] + p['history'][w - 2][
                                                           'total_points'] + p['history'][w - 1]['total_points']) / 5,
                                             points_4=(p['history'][w - 4]['total_points'] + p['history'][w - 3][
                                                 'total_points'] + p['history'][w - 2][
                                                           'total_points'] + p['history'][w - 1]['total_points']) / 4,
                                             points_3=(p['history'][w - 3]['total_points'] + p['history'][w - 2][
                                                 'total_points'] + p['history'][w - 1]['total_points']) / 3,
                                             points_2=(p['history'][w - 2]['total_points'] + p['history'][w - 1][
                                                 'total_points']) / 2,
                                             points_1=p['history'][w - 1]['total_points'],
                                             consecutive=consecutive,
                                             start_lw=min(p['history'][w - 1]['minutes'], 1),
                                             net_transfers_lw=p['history'][w - 1]['transfers_balance'],
                                             target=weeks_data['total_points']))




clean_data = []
for data_point in all_data_points:
    if data_point.start_lw == 1 and data_point.selected_lw > 25000:
        clean_data.append(data_point)

clean_data




from sklearn import datasets, linear_model
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from numpy import array



lm = linear_model.LinearRegression()
df = pd.DataFrame([[feture[1] for feture in datapoint.__dict__.items()] for datapoint in clean_data],
                  columns=[feture[0] for feture in clean_data[0].__dict__.items()])


X = pd.concat([df[['points_3','points_5','washome']],pd.get_dummies(df['pos']),pd.get_dummies(df['opponent'])], axis=1)
Y = df['target']
lm.fit(X,Y)
pred = lm.predict(X)

print("LM score" + str(lm.score(X,Y)))


plt.rcParams.update({'font.size': 8})
plt.figure(1)
plt.subplot(111)
plt.scatter(pred.tolist(), Y.tolist(),s=170, alpha=0.01)
ax = plt.gca()
ax.set_title('pred')


plt.figure(2)
plt.subplot(111)

plt.scatter(X['points_5'].tolist(), pred.tolist(),s=370, alpha=0.01,marker="s")
plt.scatter(X['points_5'].tolist(), Y.tolist(),s=370, alpha=0.01,marker="s")
ax = plt.gca()
ax.set_title('pred')


plt.show()
