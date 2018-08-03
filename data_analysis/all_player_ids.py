import pandas as pd
import os
import json


def get_ids():
    # SV Path
    json_path = '../data/json/'
    files = os.listdir(json_path)
    player_ids, team_ids, names, jerseys = [], [], [], []
    types = ['home', 'visitor']
    for file in files:
        game_id = os.listdir('../data/json/' + file)[0]
        js = open('../data/json/' + file + '/' + game_id)  # import the data from wherever you saved it.
        data = json.load(js)  # load the data
        for i in range(len(data['events'])):
            for t in types:
                team_id = data['events'][i][t]['teamid']
                for j in range(len(data['events'][i][t]['players'])):
                    last_name = data['events'][i][t]['players'][j]['lastname']
                    first_name = data['events'][i][t]['players'][j]['firstname']
                    name = first_name + ' ' + last_name
                    jersey = data['events'][i][t]['players'][j]['jersey']
                    p_id = data['events'][i][t]['players'][j]['playerid']
                    if p_id not in player_ids:
                        player_ids.append(p_id)
                        team_ids.append(team_id)
                        names.append(name)
                        jerseys.append(jersey)

    all_players = pd.DataFrame(player_ids, columns=['player_id'])
    all_players['team_id'] = team_ids
    all_players['player_name'] = names
    all_players['Jersey'] = jerseys
    all_players.to_csv('../data/all_players.csv', index=False)

    return


def copy_to_player_list():
    all_players = pd.read_csv('../data/all_players.csv')
    player_list = pd.read_csv('../data/player_list.csv')
    existing_ids = list(player_list['player_id'])

    temp = [None] * 13
    columns = ['team_id', 'team_name', 'player_id', 'player_name', 'rookie', 'height', 'FGM', 'FGA', 'FTM', 'FTA',
               'Points', 'TS', 'Jersey']
    extra = pd.DataFrame(data=[temp], columns=columns)

    for index, player in all_players.iterrows():
        if player['player_id'] not in existing_ids:
            player_list = player_list.append(extra)
            player_list.reset_index(inplace=True, drop=True)

            last_row = len(player_list) - 1

            player_list.iloc[last_row, 0] = player['team_id']
            player_list.iloc[last_row, 2] = player['player_id']
            player_list.iloc[last_row, 3] = player['player_name']
            player_list.iloc[last_row, 12] = player['Jersey']

    player_list.to_csv('../data/full_player_list.csv', index=False)

    return

# Execute functions, uncomment if you want to run
# get_ids()
# copy_to_player_list()
