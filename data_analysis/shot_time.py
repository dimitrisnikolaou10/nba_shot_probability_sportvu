import pandas as pd
import matplotlib.pyplot as plt
import os


def mark_shots(sv, jump_shots, mark):
    # place mark at shot_taken column (mark = 1 for jump shots, mark = 2 for dribble jump shots)

    # for a jump shot to be valid there must be at least one point where the ball was within 3 feet of the shooter
    valid_jump_shots = []
    for j in jump_shots:
        a = list(sv[(sv['dist_ball_2d'] < 3.5) & (sv['team_id'] != -1) & (sv['event_id'] == j)].index)
        if not a:
            continue
        else:
            valid_jump_shots.append(j)

    # create a list with indices when the jump shot was taken
    shots_at_index = []
    remaining_valid_shots = []
    for v in valid_jump_shots:
        # store in list a all times when the ball was close to the shooter
        a = list(sv[(sv['dist_ball_2d'] < 3.5) & (sv['team_id'] != -1) & (sv['event_id'] == v)].index)

        # store in list b all times when ball was higher than 9 feet
        b = list(sv[(sv['radius'] > 9) & (sv['team_id'] == -1) & (sv['event_id'] == v)].index)

        # match the index level of the ball to player indices so intersection possible
        c = [x + 1 for x in b]

        # if there is intersection, mark the first index as shot time
        possible_shot = list(set(a).intersection(c))
        possible_shot.sort()
        if possible_shot:
            shots_at_index.append(possible_shot[0])
            remaining_valid_shots.append(v)

    # mark 1 everywhere indicated by the shots
    for row in shots_at_index:
        sv.iloc[row, 22] = mark

    return sv, remaining_valid_shots


def add_features_to_pbp(pbp):
    #  mark the the 3PT shots, note the distance, add shooting attempts

    # 3 pointers
    three_pointers = list(pbp[pbp['HOMEDESCRIPTION'].str.contains('3PT ')].index)
    pbp['3PT'] = 0
    for three in three_pointers:
        pbp.iloc[three, 14] = 1

    # distance
    pbp['distance'] = 0
    for i in range(len(pbp)):
        if len(pbp.iloc[i, 5].split("' ")) > 1:
            pbp.iloc[i, 15] = int(pbp.iloc[i, 5].split("' ")[0].split(" ")[-1])

    # shooting attempts
    pbp['2PA'] = 0
    pbp['2PM'] = 0
    pbp['3PA'] = 0
    pbp['3PM'] = 0
    player_ids = list(set(pbp['PLAYER1_ID']))
    for player_id in player_ids:
        shots_of_player = pbp[pbp['PLAYER1_ID'] == player_id].index
        twoa = 0
        twom = 0
        tha = 0
        thm = 0
        for shot in shots_of_player:
            if not pbp.iloc[shot, 14]:  # if two pointer
                twoa = twoa + 1
                if pbp.iloc[shot, 2] == 1:  # if made
                    twom = twom + 1
            else:  # if three pointer
                tha = tha + 1
                if pbp.iloc[shot, 2] == 1:  # if made
                    thm = thm + 1
            pbp.iloc[shot, 16] = twoa
            pbp.iloc[shot, 17] = twom
            pbp.iloc[shot, 18] = tha
            pbp.iloc[shot, 19] = thm

    return pbp


def match_sv(pbp, events):
    # only match the events that are in sv
    new_pbp = pbp[pbp['EVENTNUM'].isin(events)]
    return new_pbp


def compare_shot_times(sv, pbp):
    # compare the shot times between the two data sources
    time_comp = sv[sv['shot_taken'] != 0]
    time_comp = time_comp[['game_clock', 'shot_clock', 'event_id']].reset_index(drop=True)
    time_comp['pbp_time'] = pbp['SECONDS_REMAINING']
    time_comp.columns = ['sv_time', 'sv_24', 'event_id', 'pbp_time']
    time_comp['time_diff'] = time_comp['sv_time'] - time_comp['pbp_time']

    events_to_remove = list(time_comp[(time_comp['time_diff'] > 6) | (time_comp['time_diff'] < -2.5)]['event_id'])

    return list(time_comp['time_diff']), events_to_remove


def mark_shot_time():
    # create new column and mark it with the type of shot when a shot is taken
    files = os.listdir('../data/build_feat/sv/')
    for file in files:
        if '.csv' not in file:
            continue
        game_id = file.replace('.csv', '')

        pbp_path = '../data/build_feat/pbp/'
        pbp = pd.read_csv(pbp_path + game_id + '.csv')

        # create a list of each type of an event as they will be treated differently
        jump_shots = list(pbp[pbp['TYPE'] == 1]['EVENTNUM'])
        dribble_jump_shots = list(pbp[pbp['TYPE'] == 2]['EVENTNUM'])
        hooks = list(pbp[pbp['TYPE'] == 3]['EVENTNUM'])
        layups = list(pbp[pbp['TYPE'] == 4]['EVENTNUM'])
        dunks = list(pbp[pbp['TYPE'] == 5]['EVENTNUM'])

        sv_path = '../data/build_feat/sv/'
        sv = pd.read_csv(sv_path + game_id + '.csv')

        # create new column and mark with appropriate mark in functions below
        sv['shot_taken'] = 0

        sv1, js = mark_shots(sv, jump_shots, 1)
        sv2, djs = mark_shots(sv1, dribble_jump_shots, 2)  # same function used as criteria the same
        sv3, hs = mark_shots(sv2, hooks, 3)  # same function used as criteria the same
        sv4, ls = mark_shots(sv3, layups, 4)  # same function used as criteria the same
        sv5, ds = mark_shots(sv4, dunks, 5)  # same function used as criteria the same

        shots = js + djs + hs + ls + ds

        final_sv = sv5[sv5['event_id'].isin(shots)]

        write_path = '../data/build_feat/sv/shots_marked/'
        final_sv.to_csv(write_path + game_id + '.csv', index=False)

    # add features to pbp data (best added before we clear data later in the code)
    files = os.listdir('../data/build_feat/pbp/')
    for file in files:
        if '.csv' not in file:
            continue
        game_id = file.replace('.csv', '')

        pbp_path = '../data/build_feat/pbp/'
        pbp = pd.read_csv(pbp_path + game_id + '.csv')

        adjusted_pbp = add_features_to_pbp(pbp)
        write_path = '../data/build_feat/pbp/features_added/'
        adjusted_pbp.to_csv(write_path + game_id + '.csv', index=False)

    # match the pbp data to the adjusted sv
    files = os.listdir('../data/build_feat/sv/shots_marked/')
    for file in files:
        if '.csv' not in file:
            continue
        game_id = file.replace('.csv', '')

        sv_path = '../data/build_feat/sv/shots_marked/'
        sv = pd.read_csv(sv_path + game_id + '.csv')
        events = list(set(sv['event_id']))

        pbp_path = '../data/build_feat/pbp/features_added/'
        pbp = pd.read_csv(pbp_path + game_id + '.csv')

        pbp_adjusted = match_sv(pbp, events)

        pbp_adjusted.to_csv(pbp_path + 'shots_marked/' + game_id + '.csv', index=False)

    # compare times between pbp and sv
    shot_times = []
    files = os.listdir('../data/build_feat/sv/shots_marked/')
    for file in files:
        if '.csv' not in file:
            continue
        game_id = file.replace('.csv', '')

        sv_path = '../data/build_feat/sv/shots_marked/'
        sv = pd.read_csv(sv_path + game_id + '.csv')

        pbp_path = '../data/build_feat/pbp/features_added/shots_marked/'
        pbp = pd.read_csv(pbp_path + game_id + '.csv')

        new_shot_times, new_events_to_remove = compare_shot_times(sv, pbp)

        shot_times = shot_times + new_shot_times

        events_to_remove = []

        events_to_remove = events_to_remove + new_events_to_remove

        new_pbp = pbp[~pbp['EVENTNUM'].isin(events_to_remove)]
        new_pbp.to_csv(pbp_path + 'clean_time/' + game_id + '.csv', index=False)

        new_sv = sv[~sv['event_id'].isin(events_to_remove)]
        new_sv.to_csv(sv_path + 'clean_time/' + game_id + '.csv', index=False)

    # plt.hist(shot_times, 50, range=(-10, +10), density=True)
    # plt.title('Shot time difference between PBP and SV data')
    # plt.xlabel('Time difference (seconds)')
    # plt.ylabel('Density')
    # plt.savefig('shot_time_diff_clean')
    # plt.show()


# execute function (uncomment if you want to run)
# mark_shot_time()
