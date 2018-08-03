import pandas as pd
import numpy as np
import os


def shooter():
    # add new column that signifies who is shooter in tracking data
    files = os.listdir('../data/shots/csv/')
    path = '../data/shots/csv/shooter/'
    count = 1
    for file in files:
        if '.csv' not in file:
            continue
        game_events = pd.read_csv('../data/shots/events/' + file)
        game_tracking = pd.read_csv('../data/shots/csv/' + file)
        game_tracking['shooter'] = 0
        i = 0
        while i < len(game_tracking):
            player_id = list(game_events[game_events['EVENTNUM'] == game_tracking.loc[i, 'event_id']]['PLAYER1_ID'])[0]
            if game_tracking.loc[i, 'player_id'] == player_id:
                game_tracking.loc[i, 'shooter'] = 1
                i = i + 6  # if found skip all visitors - for better performance
            i = i + 1
            if i % 1000 == 0:
                print(i)
        game_tracking.to_csv(path + file, index=False)
        print(count, '/110')
        count = count + 1


def add_distances(game_id):
    # add ten new columns that contain the distance of the shooter from the other 10 elements
    path = '../data/shots/csv/shooter/eliminate_non_ball/eliminate_shooter_subbed/'
    df = pd.read_csv(path + game_id + '.csv')
    shooters = df.index[df['shooter'] == 1].tolist()
    balls = df.index[df['team_id'] == -1].tolist()

    df['dist_ball_2d'] = 0
    df['dist_ball_3d'] = 0
    df['dist_team_1'] = 0
    df['dist_team_2'] = 0
    df['dist_team_3'] = 0
    df['dist_team_4'] = 0
    df['dist_opp_1'] = 0
    df['dist_opp_2'] = 0
    df['dist_opp_3'] = 0
    df['dist_opp_4'] = 0
    df['dist_opp_5'] = 0

    for ball in balls:
        shooter_index = shooters.pop(0)
        col = 1
        for i in range(ball, ball + 11):
            if i == shooter_index:
                continue
            else:
                xa = df.loc[shooter_index, 'x_loc']
                ya = df.loc[shooter_index, 'y_loc']
                za = df.loc[shooter_index, 'radius']
                xb = df.loc[i, 'x_loc']
                yb = df.loc[i, 'y_loc']
                zb = df.loc[i, 'radius']
                if col == 1:
                    dist = np.sqrt((xa-xb)**2 + (ya-yb)**2)
                    df.iloc[shooter_index, 10 + col] = dist
                    col = col + 1
                dist = np.sqrt((xa-xb)**2 + (ya-yb)**2 + (za-zb)**2)
                df.iloc[shooter_index, 10 + col] = dist
                col = col + 1
    return df


def keep_only_balls(game_id):
    # some tracking data moments are missing the ball, this script removes them
    # (splitting in two for memory purposes)
    path = '../data/shots/csv/shooter/'
    df = pd.read_csv(path + game_id + '.csv')

    balls = df.index[df['team_id'] == -1].tolist()
    split_index = int(len(df) / 2)
    while split_index not in balls:
        split_index = split_index + 1

    df1 = df[0:split_index]
    df2 = df[split_index:]
    df2.reset_index(drop=True)

    i = 0
    criteria = len(df1)
    while i < criteria:
        while df1.iloc[i, 0] != -1:
            df1.drop(df1.index[i: i + 10], inplace=True)
            criteria = criteria - 10
            if i >= criteria:
                break
        i = i + 11
    df1.reset_index(drop=True)

    i = 0
    criteria = len(df2)
    while i < criteria:
        while df2.iloc[i, 0] != -1:
            df2.drop(df2.index[i: i + 10], inplace=True)
            criteria = criteria - 10
            if i >= criteria:
                break
        i = i + 11
    df2.reset_index(drop=True)

    res_df = pd.concat([df1, df2])

    return res_df


def remove_when_shooter_subbed(game_id):
    # In an event, a shooter may get subbed but there might still be moments left
    # This script eliminates that part of the data as it is not useful (obviously the shot has taken place)
    path = '../data/shots/csv/shooter/eliminate_non_ball/'
    df = pd.read_csv(path + game_id + '.csv')

    balls = df.index[df['team_id'] == -1].tolist()
    split_index = int(len(df) / 2)
    while split_index not in balls:
        split_index = split_index + 1

    df1 = df[0:split_index]
    df2 = df[split_index:]
    df2.reset_index(drop=True)

    i = 0
    criteria = len(df1)
    while i < criteria:
        s = sum(df1.iloc[i:i + 11, 10])
        while s == 0:
            df1.drop(df1.index[i: i + 11], inplace=True)
            criteria = criteria - 11
            if i >= criteria:
                break
            s = sum(df1.iloc[i:i + 11, 10])
        i = i + 11
    df1.reset_index(drop=True)

    i = 0
    criteria = len(df2)
    while i < criteria:
        s = sum(df2.iloc[i:i + 11, 10])
        while s == 0:
            df2.drop(df2.index[i: i + 11], inplace=True)
            criteria = criteria - 11
            if i >= criteria:
                break
            s = sum(df2.iloc[i:i + 11, 10])
        i = i + 11
    df2.reset_index(drop=True)

    res_df = pd.concat([df1, df2])

    return res_df


def keep_shooters_and_ball(game_id):
    # remove all data of players that are not shooters (also maintain the ball)
    path = '../data/shots/csv/shooter/eliminate_non_ball/eliminate_shooter_subbed/distances/'
    df = pd.read_csv(path + game_id + '.csv')
    df2 = df[(df.team_id == -1) | (df.shooter == 1)].reset_index(drop=True)

    return df2


def adjust_pbp_events(game_id):
    # Place shots in to type buckets, remove extra columns, turn the string of quarter time left to int
    path = '../data/shots/events/'
    df = pd.read_csv(path + game_id + '.csv')

    # Remove all non shots
    df2 = df[(df.EVENTMSGACTIONTYPE != 0)].reset_index(drop=True)

    # Remove unnessecary columns
    cols = [8, 9, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]  # Neutral & Visitor desc, Players 2 & 3 info
    df2.drop(df2.columns[cols], axis=1, inplace=True)

    # Placing each shot into one of five buckets
    jump_shot = [45, 66, 1]  # 1
    dribble_jump_shot = [2, 77, 78, 79, 80, 101, 102, 103, 104, 46, 47, 63, 81, 82, 83, 84, 85, 86, 105]  # 2
    hook_shot = [3, 55, 57, 58, 67, 93, 96]  # 3
    layup = [5, 40, 41, 42, 43, 44, 71, 72, 73, 74, 75, 76, 97, 98, 99, 100]  # 4
    dunk = [7, 48, 49, 50, 51, 52, 87, 106, 107, 108, 109, 110]  # 5
    df2['TYPE'] = 0
    for i in range(len(df2)):
        if df2.iloc[i, 3] in jump_shot:
            df2.iloc[i, 17] = 1
        elif df2.iloc[i, 3] in dribble_jump_shot:
            df2.iloc[i, 17] = 2
        elif df2.iloc[i, 3] in hook_shot:
            df2.iloc[i, 17] = 3
        elif df2.iloc[i, 3] in layup:
            df2.iloc[i, 17] = 4
        elif df2.iloc[i, 3] in dunk:
            df2.iloc[i, 17] = 5
        else:
            # check to verify that all EVENTMSGACTIONTYPE belong to a bucket
            print("The game_id ", df2.iloc[i, 0], " row ", i, " has 0 type")

    # Change PCTIMESTRING to reflect seconds remaining in quarter
    df2['SECONDS_REMAINING'] = 0
    for i in range(len(df2)):
        mins, secs = int(df2.iloc[i, 6].split(':')[0]), int(df2.iloc[i, 6].split(':')[1])
        df2.iloc[i, 18] = 60 * mins + secs
    df2.drop(['PCTIMESTRING'], axis=1, inplace=True)

    # Remove some additional columns (Time, Score & Unknown PERSON1TYPE col)
    df2.drop(['WCTIMESTRING'], axis=1, inplace=True)
    df2.drop(['SCORE'], axis=1, inplace=True)
    df2.drop(['SCOREMARGIN'], axis=1, inplace=True)
    df2.drop(['PERSON1TYPE'], axis=1, inplace=True)

    return df2


def acting_main():
    shooter()

    files = os.listdir('../data/shots/csv/shooter/')
    path = '../data/shots/csv/shooter/eliminate_non_ball/'
    for file in files:
        if '.csv' not in file:
            continue
        game_id = file.replace('.csv', '')
        df = keep_only_balls(game_id)
        df.to_csv(path + game_id + '.csv', index=False)

    files = os.listdir('../data/shots/csv/shooter/eliminate_non_ball/')
    path = '../data/shots/csv/shooter/eliminate_non_ball/eliminate_shooter_subbed/'
    for file in files:
        if '.csv' not in file:
            continue
        game_id = file.replace('.csv', '')
        df = remove_when_shooter_subbed(game_id)
        df.to_csv(path + game_id + '.csv', index=False)

    files = os.listdir('../data/shots/csv/shooter/eliminate_non_ball/eliminate_shooter_subbed/')
    path = '../data/shots/csv/shooter/eliminate_non_ball/eliminate_shooter_subbed/distances/'
    for file in files:
        if '.csv' not in file:
            continue
        game_id = file.replace('.csv', '')
        df = add_distances(game_id)
        df.to_csv(path + game_id + '.csv', index=False)

    files = os.listdir('../data/shots/csv/shooter/eliminate_non_ball/eliminate_shooter_subbed/')
    path = '../data/build_feat/sv/'
    for file in files:
        if '.csv' not in file:
            continue
        game_id = file.replace('.csv', '')
        df = keep_shooters_and_ball(game_id)
        df.to_csv(path + game_id + '.csv', index=False)

    files = os.listdir('../data/shots/events/')
    path = '../data/build_feat/pbp/'
    for file in files:
        if '.csv' not in file:
            continue
        game_id = file.replace('.csv', '')
        df = adjust_pbp_events(game_id)
        df.to_csv(path + game_id + '.csv', index=False)


# execute functions (uncomment if you want to run)
# acting_main()
