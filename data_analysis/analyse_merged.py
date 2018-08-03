import os
import pandas as pd


def concatenate_all_games():

    games = []
    files = os.listdir('../data/merge/')
    for file in files:
        if '.csv' not in file:
            continue
        df = pd.read_csv('../data/merge/' + file)
        games.append(df)

    all_games = pd.concat(games)
    all_games.to_csv('../data/merge/all/all_games.csv', index=False)

    return


def adjust_all_game_data():

    df = pd.read_csv('../data/merge/all/all_games.csv')

    df['cumm_2PM'] = 1
    df['cumm_2PA'] = 2
    df['cumm_3PM'] = 2
    df['cumm_3PA'] = 5
    games = list(set(df['game_id']))
    games.sort()
    for game in games:
        players = list(set(df[df['game_id'] == game]['player_id']))
        for player in players:
            last_two_made = list(df[(df['game_id'] == game) & (df['player_id'] == player)]['2PM'])[-1]
            last_two_attempted = list(df[(df['game_id'] == game) & (df['player_id'] == player)]['2PA'])[-1]
            last_three_made = list(df[(df['game_id'] == game) & (df['player_id'] == player)]['3PM'])[-1]
            last_three_attempted = list(df[(df['game_id'] == game) & (df['player_id'] == player)]['3PA'])[-1]
            index_of_this_player = df[df['player_id'] == player].index
            for index in index_of_this_player:
                if df.iloc[index, 0] > game:  # for future games only, update the shooting based on this game
                    df.iloc[index, 21] = df.iloc[index, 21] + last_two_made  # cumm 2PM
                    df.iloc[index, 22] = df.iloc[index, 22] + last_two_attempted  # cumm 2PA
                    df.iloc[index, 23] = df.iloc[index, 23] + last_three_made  # cumm 3PM
                    df.iloc[index, 24] = df.iloc[index, 24] + last_three_attempted  # cumm 3PA

    player_list = pd.read_csv('../data/player_list.csv')

    # create cummulative percentages
    df['cumm_2P%'] = df['cumm_2PM'] / df['cumm_2PA']
    df['cumm_3P%'] = df['cumm_3PM'] / df['cumm_3PA']

    # get information from the player_list db (height, rookie, ts%)
    df['height'] = 0
    df['rookie'] = 0
    df['ts%'] = 0
    for i, player_id in enumerate(df['player_id']):
        height = list(player_list[player_list['player_id'] == player_id]['height'])[0]
        rookie = list(player_list[player_list['player_id'] == player_id]['rookie'])[0]
        ts = list(player_list[player_list['player_id'] == player_id]['TS'])[0]
        df.iloc[i, 27] = height
        df.iloc[i, 28] = rookie
        df.iloc[i, 29] = ts

    # drop all hook shots
    df.drop(df[df['type_of_shot'] == 3].index, inplace=True)

    # create seperate column for all type of shots (for modelling purposes - categoric variable)
    df['jump_shot'] = 0
    df['dribble'] = 0
    df['layup'] = 0
    df['dunk'] = 0
    for i in range(len(df)):
        if df.iloc[i, 9] == 1:  # if jump shot
            df.iloc[i, 30] = 1  # mark the jump shot column
        if df.iloc[i, 9] == 2:  # if it is a dribble jump shot
            df.iloc[i, 30] = 1  # mark the jump shot column
            df.iloc[i, 31] = 1  # mark the dribble column
        if df.iloc[i, 9] == 4:  # if layup
            df.iloc[i, 32] = 1  # mark the layup column
        if df.iloc[i, 9] == 5:  # if dunk
            df.iloc[i, 33] = 1  # mark the dunk column

    # same practice but for quarters
    df['quarter_1'] = 0
    df['quarter_2'] = 0
    df['quarter_3'] = 0
    df['quarter_4'] = 0
    for i in range(len(df)):
        if df.iloc[i, 6] == 1:  # if quarter 1
            df.iloc[i, 34] = 1
        if df.iloc[i, 6] == 2:  # if quarter 2
            df.iloc[i, 35] = 1
        if df.iloc[i, 6] == 3:  # if quarter 3
            df.iloc[i, 36] = 1
        if df.iloc[i, 6] == 4:  # if quarter 4
            df.iloc[i, 37] = 1

    # change label from 1,2 to 1,0
    for i in range(len(df)):
        if df.iloc[i, 5] == 2:
            df.iloc[i, 5] = 0

    # remove columns that will not be used
    df.drop(['player_name'], axis=1, inplace=True)  # remove player_name
    df.drop(['player_id'], axis=1, inplace=True)  # remove player_id
    df.drop(['team_id'], axis=1, inplace=True)  # remove player_id
    df.drop(['quarter'], axis=1, inplace=True)  # remove quarter
    df.drop(['seconds_left'], axis=1, inplace=True)  # remove seconds_left
    df.drop(['desc'], axis=1, inplace=True)  # remove desc
    df.drop(['type_of_shot'], axis=1, inplace=True)  # remove type_of_shot
    df.drop(['3PT'], axis=1, inplace=True)  # remove 3PT
    df.drop(['2PM'], axis=1, inplace=True)  # remove 2PM
    df.drop(['2PA'], axis=1, inplace=True)  # remove 2PA
    df.drop(['3PM'], axis=1, inplace=True)  # remove 3PM
    df.drop(['3PA'], axis=1, inplace=True)  # remove 3PA
    df.drop(['cumm_2PM'], axis=1, inplace=True)  # remove cumm_2PM
    df.drop(['cumm_2PA'], axis=1, inplace=True)  # remove cumm_2PA
    df.drop(['cumm_3PM'], axis=1, inplace=True)  # remove cumm_3PM
    df.drop(['cumm_3PA'], axis=1, inplace=True)  # remove cumm_3PA

    labels = pd.DataFrame(df['shot_made'])  # create the new labels dataframe
    labels.columns = ['make']  # change the name
    df.drop(['shot_made'], axis=1, inplace=True)  # remove cumm_3PA

    df.to_csv('../data/merge/all/final_version.csv', index=False)
    labels.to_csv('../data/merge/all/labels.csv', index=False)


# execute function (uncomment if you want to run)
# concatenate_all_games()
# adjust_all_game_data()
