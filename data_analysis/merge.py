import os
import pandas as pd


def merge():
    files = os.listdir('../data/build_feat/sv/shots_marked/clean_time/clean_distance/extra_features/')

    for file in files:
        if '.csv' not in file:
            continue
        game_id = file.replace('.csv', '')

        pbp_path = '../data/build_feat/pbp/features_added/shots_marked/clean_time/clean_distance/'
        pbp = pd.read_csv(pbp_path + game_id + '.csv')

        sv_path = '../data/build_feat/sv/shots_marked/clean_time/clean_distance/extra_features/'
        sv = pd.read_csv(sv_path + game_id + '.csv')

        sosv = sv[sv['shot_taken'] != 0].reset_index(drop=True)  # only keep the shots from sv data

        df = pd.DataFrame(pbp['GAME_ID'])  # create the new dataframe
        df.columns = ['game_id']  # change the name to lower case
        df['event_id'] = pbp['EVENTNUM']
        df['team_id'] = pbp['PLAYER1_TEAM_ID']
        df['player_id'] = pbp['PLAYER1_ID']
        df['player_name'] = pbp['PLAYER1_NAME']

        df['shot_made'] = pbp['EVENTMSGTYPE']  # this column will serve as label later on

        df['quarter'] = pbp['PERIOD']
        df['seconds_left'] = pbp['SECONDS_REMAINING']

        df['desc'] = pbp['HOMEDESCRIPTION']
        df['type_of_shot'] = pbp['TYPE']

        df['distance'] = pbp['distance']
        df['3PT'] = pbp['3PT']

        df['2PM'] = pbp['2PM']
        df['2PA'] = pbp['2PA']
        df['3PM'] = pbp['3PM']
        df['3PA'] = pbp['3PA']

        df['desperation_shot'] = sosv['last_second_shot']
        df['quick_shot'] = sosv['first_6_seconds_shot']

        df['opp_1_dist'] = sosv['opponent_1_distance']
        df['opp_2_dist'] = sosv['opponent_2_distance']
        df['opp_3_dist'] = sosv['opponent_3_distance']

        df.to_csv('../data/merge/' + game_id + '.csv', index=False)

    return


def obtain_player_list():
    files = os.listdir('../data/merge/')
    player_names = []
    player_ids = []
    team_ids = []
    for f in files:
        df = pd.read_csv('../data/merge/' + f)
        for player_name, player_id, team_id in zip(df['player_name'], df['player_id'], df['team_id']):
            if player_name not in player_names:
                player_names.append(player_name)
                player_ids.append(player_id)
                team_ids.append(team_id)

    df = pd.DataFrame(team_ids)  # create the new dataframe
    df.columns = ['team_id']  # change the name to lower case
    df['player_id'] = player_ids
    df['player_name'] = player_names

    df.to_csv('../data/player_list.csv', index=False)

    return


# execute function (uncomment if you want to run)
# merge()
# obtain_player_list()
