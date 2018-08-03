import pandas as pd
import os


def create_map():
    game_dict = {}
    files = os.listdir('../data/json/')
    for file_name in files:
        if '.csv' in file_name:
            continue
        game_id = os.listdir('../data/json/' + file_name)[0]
        game_id = game_id.replace('.json', '')

        file_parts = file_name.split('.')
        full_game_name = file_parts[3] + ' ' + file_parts[4] + ' ' + file_parts[5] + ' ' + \
                '(' + file_parts[1] + '/' + file_parts[0] + '/' + file_parts[2] + ')'

        game_dict[full_game_name] = game_id

    df_1 = pd.DataFrame(list(game_dict.items()), columns=['Game', 'ID'])

    return df_1


df = create_map()
df.to_csv('../data/game_map.csv', index=False)

