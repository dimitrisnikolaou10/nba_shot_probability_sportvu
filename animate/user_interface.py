import pandas as pd
import time


def get_event_sv():
    # Ask the user what game they want to select, then ask which event of that list
    # Need to add checks of when there is no event in game or when user does not select valid event !!!
    game_map = pd.read_csv('../data/game_map.csv')  # Obtain the map between game and game_id
    game_map = game_map[['Game', 'ID']]

    print('Return a game_id from the following list')
    time.sleep(0)
    print(game_map.to_string())  # to_string used so that whole df can be printed
    game_ids = list(game_map['ID'])
    print(' ')
    while True:
        game_id = input()  # ask the user to choose the input
        if int(game_id) in game_ids:
            break
        else:
            print("Please choose an ID from the list above or enter '0' to exit")
            if game_id == '0':
                return None, None, None, None, None
    game_id = '00' + str(game_id)  # add 00s in the beginning
    # game_id = 21500492  # Remove later
    # game_id = '00' + str(game_id)  # add 00s in the beginning

    pbp_path = '../data/build_feat/pbp/features_added/shots_marked/clean_time/clean_distance/'
    pbp = pd.read_csv(pbp_path + game_id + '.csv')

    events = pbp[['EVENTNUM', 'HOMEDESCRIPTION']]
    events.columns = ['Event_ID', 'Event_Description']
    events = events[['Event_Description', 'Event_ID']]
    event_ids = list(events['Event_ID'])

    for i in range(10):
        print(" ")

    print('Return an event_id from the following list')
    time.sleep(0)

    print(events.to_string())
    print(' ')

    while True:
        event_id = int(input())  # ask the user to choose the input
        if event_id in event_ids:
            break
        else:
            print("Please choose an ID from the list above or enter 0 to exit")
            if str(event_id) == '0':
                return None, None, None, None, None
    # event_id = 6  # Remove later

    event_description = pbp[pbp['EVENTNUM'] == event_id].iloc[0, 5]

    shot_time = pbp[pbp['EVENTNUM'] == event_id].iloc[0, 13]

    sv_path = '../data/shots/csv/shooter/eliminate_non_ball/eliminate_shooter_subbed/distances/'
    sv = pd.read_csv(sv_path + game_id + '.csv')

    sv_event = sv[sv['event_id'] == event_id]

    return game_id, sv_event, event_id, event_description, shot_time




