import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
pd.set_option('chained_assignment', None)

HOOP_1_X = 88.65
HOOP_2_X = 5.35
HOOP_Y = 25
HOOP_Z = 10


def add_sv_distance(sv):
    # add a column that notes the distance from the hoop
    sv['dist_hoop_1_2d'] = 0
    sv['dist_hoop_2_2d'] = 0
    sv['dist_hoop_1_3d'] = 0
    sv['dist_hoop_2_3d'] = 0
    sv['shot_distance'] = 0
    for i in range(len(sv)):
        xa = sv.iloc[i, 2]
        ya = sv.iloc[i, 3]
        za = sv.iloc[i, 4]
        sv.iloc[i, 23] = np.sqrt((xa - HOOP_1_X) ** 2 + (ya - HOOP_Y) ** 2)  # 2D from hoop 1
        sv.iloc[i, 24] = np.sqrt((xa - HOOP_2_X) ** 2 + (ya - HOOP_Y) ** 2)  # 2D from hoop 2
        if sv.iloc[i, 0] == -1:
            sv.iloc[i, 25] = np.sqrt((xa - HOOP_1_X) ** 2 + (ya - HOOP_Y) ** 2 + (za - HOOP_Z) ** 2)  # 3D from hoop 1
            sv.iloc[i, 26] = np.sqrt((xa - HOOP_2_X) ** 2 + (ya - HOOP_Y) ** 2 + (za - HOOP_Z) ** 2)  # 3D from hoop 2
        sv.iloc[i, 27] = min([sv.iloc[i, 23], sv.iloc[i, 24]])  # select the min distance as the shot distance

    return sv


def find_long_shots(pbp):
    # remove any long shots and save the events of those shots
    no_long_shots_pbp = pbp[pbp['distance'] < 40]
    long_shots = list(pbp[pbp['distance'] >= 40]['EVENTNUM'])

    return no_long_shots_pbp, long_shots


def remove_sv_events_based_on_list(sv, list_of_events):
    # get rid of any events that are mentioned in the list
    clean_sv = sv[~sv['event_id'].isin(list_of_events)]

    return clean_sv


def remove_pbp_events_based_on_list(pbp, list_of_events):
    # get rid of any events that describe long shots
    clean_pbp = pbp[~pbp['EVENTNUM'].isin(list_of_events)]

    return clean_pbp


def compare_shot_distance(sv, pbp):
    distance_differences = []
    events_to_remove = []
    events = pbp['EVENTNUM']
    for event in events:
        pbp_d = list(pbp[pbp['EVENTNUM'] == event]['distance'])[0]
        sv_d = list(sv[(sv['event_id'] == event) & (sv['shot_taken'] != 0)]['shot_distance'])[0]
        d = abs(sv_d - pbp_d)
        distance_differences.append(sv_d - pbp_d)
        if d > 5:
            events_to_remove.append(event)

    return distance_differences, events_to_remove


def plot_histogram(list_to_plot, title='', x_label='', y_label='', save_fig='', bins=50,
                   range_arg=(-10, +10), density=True):
    plt.hist(list_to_plot, bins, range_arg, density)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.savefig(save_fig)
    plt.show()

    return


def add_and_clean_distances():
    # find the long shots from the pbp data and remove them from the pbp data
    # match these events with the sv data
    # add the distances to the SV data
    # compare distances between the two databases and remove the ones that have a difference > 5 feet

    all_clean_distance_differences = []
    all_dirty_distance_differences = []

    files = os.listdir('../data/build_feat/sv/shots_marked/clean_time/')

    for file in files:
        if '.csv' not in file:
            continue
        game_id = file.replace('.csv', '')

        pbp_path = '../data/build_feat/pbp/features_added/shots_marked/clean_time/'
        pbp = pd.read_csv(pbp_path + game_id + '.csv')
        pbp_no_long_shots, long_shots = find_long_shots(pbp)  # find the long shots from the pbp

        sv_path = '../data/build_feat/sv/shots_marked/clean_time/'
        sv = pd.read_csv(sv_path + game_id + '.csv')

        sv_no_long_shots = remove_sv_events_based_on_list(sv, long_shots)  # eliminate long shots from sv

        sv_with_distance = add_sv_distance(sv_no_long_shots)  # add distance from hoop to sv data

        # compare shot distance - return the differences and the events that should get removes (over 5 feet diff)
        distance_differences_dirty, events_to_remove = compare_shot_distance(sv_with_distance, pbp_no_long_shots)

        all_dirty_distance_differences = all_dirty_distance_differences + distance_differences_dirty

        # remove from the two databases the events that do not match in distance
        clean_sv = remove_sv_events_based_on_list(sv_with_distance, events_to_remove)
        clean_pbp = remove_pbp_events_based_on_list(pbp_no_long_shots, events_to_remove)

        # compare shot distance - mainly so I can get clean distance differences
        distance_differences_clean, events_to_remove_should_be_empty = compare_shot_distance(clean_sv, clean_pbp)

        all_clean_distance_differences = all_clean_distance_differences + distance_differences_clean

        clean_sv.to_csv(sv_path + 'clean_distance/' + game_id + '.csv', index=False)
        clean_pbp.to_csv(pbp_path + 'clean_distance/' + game_id + '.csv', index=False)

    return all_clean_distance_differences, all_dirty_distance_differences


# execute function, (uncomment if you want to run)
# clean_distance_differences, dirty_distance_differences = add_and_clean_distances()

# plot the histograms
# plot_histogram(dirty_distance_differences, title="Shot distance differences between SV & PBP",
#                x_label='Shot distance difference (in feet)', y_label='Density', save_fig='shot_dist_diff_dirty')
#
# plot_histogram(clean_distance_differences, title="Shot distance differences between SV & PBP (after cleanup)",
#                x_label='Shot distance difference (in feet)', y_label='Density', save_fig='shot_dist_diff_clean')


def add_defender_proximity(sv):
    sv['opponent_1_distance'] = 0
    sv['opponent_2_distance'] = 0
    sv['opponent_3_distance'] = 0
    shots = list(sv[sv['shot_taken'] != 0].index)
    for shot in shots:
        distances = []
        col = 17  # position of first opponent distance
        while col < 22:
            distances.append(sv.iloc[shot, col])
            col = col + 1
        distances.sort()
        sv.iloc[shot, 28] = distances[0]
        sv.iloc[shot, 29] = distances[1]
        sv.iloc[shot, 30] = distances[2]

    return sv


def mark_last_second_shot(sv):
    sv['last_second_shot'] = 0
    shots = list(sv[sv['shot_taken'] != 0].index)
    for shot in shots:
        if sv.iloc[shot, 6] < 2:  # if shot clock less than two
            sv.iloc[shot, 31] = 1  # mark it as last second shot

    return sv


def mark_first_6_seconds_shot(sv):
    sv['first_6_seconds_shot'] = 0
    shots = list(sv[sv['shot_taken'] != 0].index)
    for shot in shots:
        if sv.iloc[shot, 6] > 18:  # if shot clock less than two
            sv.iloc[shot, 32] = 1  # mark it as last second shot

    return sv


def extra_features():
    # mark the proximity of the two closest defenders

    files = os.listdir('../data/build_feat/sv/shots_marked/clean_time/clean_distance/')

    for file in files:
        if '.csv' not in file:
            continue
        game_id = file.replace('.csv', '')

        sv_path = '../data/build_feat/sv/shots_marked/clean_time/clean_distance/'
        sv = pd.read_csv(sv_path + game_id + '.csv')

        sv_with_def_dist = add_defender_proximity(sv)

        sv_with_last_second_shot = mark_last_second_shot(sv_with_def_dist)

        sv_with_first_seconds = mark_first_6_seconds_shot(sv_with_last_second_shot)

        sv_with_first_seconds.to_csv(sv_path + 'extra_features/' + game_id + '.csv', index=False)


# execute function (uncomment if you want to run)
extra_features()
