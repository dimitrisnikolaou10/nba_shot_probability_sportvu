from Constant import Constant


def get_players(moments):
    player_ids, player_names, player_jerseys = [], [], []
    for i in range(len(moments)):
        p_id = moments.iloc[i, 1]
        if p_id != -1 and p_id not in player_ids:
            player_ids.append(p_id)

            player_name = Constant.PLAYER_LIST[Constant.PLAYER_LIST['player_id'] == p_id].iloc[0, 3]  # Place of name
            player_names.append(player_name)

            player_jersey = Constant.PLAYER_LIST[Constant.PLAYER_LIST['player_id'] == p_id].iloc[0, 12]  # Jersey
            player_jerseys.append(str(int(player_jersey)))

    return player_ids, player_names, player_jerseys
