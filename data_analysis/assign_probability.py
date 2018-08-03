import pandas as pd
from sklearn.externals import joblib
import numpy as np


def add_prob():
    # add probability to all shots
    path = '../data/merge/all/'
    final = pd.read_csv(path + 'final_version.csv')
    all_games = pd.read_csv(path + 'all_games.csv')

    probabilities = []

    rf = joblib.load('../pickle/rf_model.pkl')

    for index, row in final.iterrows():
        row.drop(['game_id'], inplace=True)
        row.drop(['event_id'], inplace=True)
        probability_to_make = rf.predict_proba(np.asarray(row).reshape(1, -1))[0][1]
        probabilities.append(probability_to_make)

    final['probability'] = probabilities

    final['expected_value'] = final['probability']*2

    final['team_id'] = 0

    for i in range(len(final)):

        game_id = final.iloc[i, 0]  # game ID location
        event_id = final.iloc[i, 1]  # event ID location

        three = all_games[(all_games['game_id'] == game_id) & (all_games['event_id'] == event_id)].iloc[0, 11]
        if three == 1:
            final.iloc[i, 22] += final.iloc[i, 21]  # If three pointer, add a probability value

        team_id = all_games[(all_games['game_id'] == game_id) & (all_games['event_id'] == event_id)].iloc[0, 2]

        final.iloc[i, 23] = team_id

    final.to_csv('../data/with_prob.csv', index=False)

    return


def expected_shot_value_generate():
    # get expected value score for teams (based on previous shots)
    probs = pd.read_csv('../data/with_prob.csv')
    game_map = pd.read_csv('../data/game_map.csv')

    game_map['home_team'] = game_map['Game'].apply(lambda x: x.split(' ')[2])
    game_map['away_team'] = game_map['Game'].apply(lambda x: x.split(' ')[0])

    team_ids = set(probs['team_id'])
    teams_dict = {key: [0, 0] for key in team_ids}

    probs['team_expected_value'] = 0

    for i in range(len(probs)):
        team_id = probs.iloc[i, 23]
        teams_dict[team_id][0] += 1  # increase the total number of games played
        teams_dict[team_id][1] += probs.iloc[i, 22]  # increase the total number of games played

        probs.iloc[i, 24] = teams_dict[team_id][1] / teams_dict[team_id][0]  # average expected value (sum of / # shots)

    game_ids = game_map['ID']
    game_map['expected_shot_value'] = 0

    for i, game_id in enumerate(game_ids):
        if list(probs[probs['game_id'] == game_id].tail(1)['team_expected_value']):
            game_map.iloc[i, 5] = list(probs[probs['game_id'] == game_id].tail(1)['team_expected_value'])[0]
        else:
            game_map.iloc[i, 5] = 0

    game_map['expected_shot_value_shifted'] = game_map.groupby(['home_team'])['expected_shot_value'].shift(1)

    game_map.dropna(inplace=True)
    # game_map.drop(game_map[game_map['expected_shot_value_shifted']==0].index, inplace = True)
    game_map.reset_index(drop=True, inplace=True)

    for i in game_map[game_map['expected_shot_value_shifted'] == 0].index:
        team = game_map.iloc[i, 3]
        previous_i = i - 1
        while game_map.iloc[previous_i, 3] != team:
            previous_i -= 1
        expected = game_map.iloc[previous_i, 6]
        game_map.iloc[i, 6] = expected

    game_map.to_csv('../data/expected_prob.csv', index=False)

    return


def expected_shot_value_model():
    # develop model based on the expected shot value
    # accuracy of 45% really bad!
    # did not have all shots after clean up so cannot trust results
    games = pd.read_csv('../data/expected_prob.csv')

    average_expected = games['expected_shot_value'].mean()

    games['prediction_based_on_expected'] = 0

    for i in range(len(games)):
        if games.iloc[i, 5] > average_expected:
            games.iloc[i, 6] = 1

    correct = 0
    for i in range(len(games)):
        if games.iloc[i, 6] == games.iloc[i, 2]:
            correct += 1

    accuracy = correct / len(games)

    print(accuracy)

    return


# execute functions (uncomment if you want to run)
# add_prob()
# expected_shot_value_generate()
# expected_shot_value_model()
