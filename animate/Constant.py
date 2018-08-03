import pandas as pd


class Constant:
    """A class for handling constants"""
    NORMALIZATION_COEF = 7
    PLAYER_CIRCLE_SIZE = 12 / NORMALIZATION_COEF
    INTERVAL = 10
    DIFF = 6
    X_MIN = 0
    X_MAX = 100
    Y_MIN = 0
    Y_MAX = 50
    COL_WIDTH = 0.3
    SCALE = 1.65
    FONTSIZE = 6
    X_CENTER = X_MAX / 2 - DIFF / 1.5 + 0.10
    Y_CENTER = Y_MAX - DIFF / 1.5 - 0.35
    GAME_MAP = pd.read_csv('../data/game_map.csv')
    PLAYER_LIST = pd.read_csv('../data/full_player_list.csv')
    SHOTS = pd.read_csv('../data/merge/all/final_version.csv')
