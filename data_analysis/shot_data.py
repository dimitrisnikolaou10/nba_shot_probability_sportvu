import pandas as pd
import os


def only_shots(name, path='../data/events/'):
    # made shots have the msgtype 1, missed have the msgtype 2
    df = pd.read_csv(path + name + '.csv')

    df1 = df[df['EVENTMSGTYPE'].isin([1, 2])].reset_index(drop=True)
    df2 = df1[df1['HOMEDESCRIPTION'].notnull()].reset_index(drop=True)
    df3 = df2[~df2['HOMEDESCRIPTION'].str.contains("BLK")].reset_index(drop=True)

    return df3


def match_events(name, path='../data/csv/'):
    # from all tracking data only keep events that shots were taken
    event_path = '../data/events/adjusted/'
    df_ev = pd.read_csv(event_path + name + '.csv')
    event_list = list(df_ev['EVENTNUM'])

    df_tr = pd.read_csv(path + name + '.csv')
    df_tr1 = df_tr[df_tr['event_id'].isin(event_list)].reset_index(drop=True)

    return df_tr1


def match_tracking(name, path='../data/events/adjusted/'):
    # tracking data don't have all events from event data - need to match
    track_path = '../data/csv/adjusted/'
    df_tr = pd.read_csv(track_path + name + '.csv')
    track_list = list(set(df_tr['event_id']))

    df_ev = pd.read_csv(path + name + '.csv')
    df_ev1 = df_ev[df_ev['EVENTNUM'].isin(track_list)].reset_index(drop=True)

    return df_ev1


def write_adjusted_csv(df, name, path='../data/events/adjusted/'):
    df.to_csv(path + name + '.csv', index=False)


def adjust_data():
    # adjust event data to only reflect made shots and misses
    files = os.listdir('../data/events/')
    for file in files:
        if '.csv' not in file:
            continue
        else:
            game_id = file.replace('.csv', '')
            df = only_shots(game_id)
            write_adjusted_csv(df, game_id)

    # match the tracking data to the event data
    files = os.listdir('../data/csv/')
    for file in files:
        if '.csv' not in file:
            continue
        else:
            game_id = file.replace('.csv', '')
            df = match_events(game_id)
            write_adjusted_csv(df, game_id, '../data/csv/adjusted/')

    # match the event data to the tracking data (make sure they have same events)
    files = os.listdir('../data/csv/adjusted/')
    for file in files:
        if '.csv' not in file:
            continue
        else:
            game_id = file.replace('.csv', '')
            df = match_tracking(game_id)
            write_adjusted_csv(df, game_id, '../data/events/readjusted/')

    # move files to final destination
    files = os.listdir('../data/csv/adjusted/')
    for file in files:
        if '.csv' not in file:
            continue
        os.rename("../data/csv/adjusted/" + file, "../data/shots/csv/" + file)

    files = os.listdir('../data/events/readjusted/')
    for file in files:
        if '.csv' not in file:
            continue
        os.rename("../data/events/readjusted/" + file, "../data/shots/events/" + file)


# Run the program (uncomment if you want to run)
# adjust_data()
