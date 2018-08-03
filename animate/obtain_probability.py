from sklearn.externals import joblib
from Constant import Constant
import pandas as pd
pd.options.mode.chained_assignment = None


def get_prob(game_id, event_id):
    df = Constant.SHOTS
    row = df[(df['game_id'] == int(game_id[2:])) & (df['event_id'] == event_id)]
    row.drop(['game_id'], axis=1, inplace=True)
    row.drop(['event_id'], axis=1, inplace=True)

    rf = joblib.load('../pickle/rf_model.pkl')
    probability_to_make = rf.predict_proba(row)[0][1]
    
    return round(probability_to_make * 100, 1)


def get_feature_info(game_id, event_id):
    df = Constant.SHOTS
    row = df[(df['game_id'] == int(game_id[2:])) & (df['event_id'] == event_id)]
    opp_1_dist = row.iloc[0, 5]
    opp_2_dist = row.iloc[0, 6]
    opp_3_dist = row.iloc[0, 7]
    ts = row['ts%']
    feature_info = (opp_1_dist, opp_2_dist, opp_3_dist, ts)

    return feature_info
