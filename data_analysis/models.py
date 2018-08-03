from __future__ import division
import pandas as pd
import numpy as np
from time import time

from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib
import statsmodels.api as sm
pd.options.mode.chained_assignment = None

df = pd.read_csv('../data/merge/all/final_version.csv')
df.drop(['game_id'], axis=1, inplace=True)
df.drop(['event_id'], axis=1, inplace=True)
labels = pd.read_csv('../data/merge/all/labels.csv')


def feature_scaling(features):
    # Feature scaling (range between 0 and 1)
    min_max_scaler = preprocessing.MinMaxScaler()
    for col in features.columns:
        features[col] = pd.DataFrame(min_max_scaler.fit_transform(pd.DataFrame(features[col])))

    return features


def split_data(features, target):
    # Split train and test (80%/20%)
    x_tr, x_te, y_tr, y_te = train_test_split(
        features, target, test_size=0.2, shuffle=True, random_state=4)

    return x_tr, x_te, y_tr, y_te


def extra_metrics(base_pred, test):
    # Find confusion matrix of benchmark model
    true_positives = 0
    false_negatives = 0
    false_positives = 0
    for actual, predicted in zip(list(test['make']), base_pred):
        if (actual == predicted) and (actual == 1):
            true_positives += 1
        elif actual > predicted:
            false_negatives += 1
        elif actual < predicted:
            false_positives += 1
    true_negatives = len(base_pred) - (true_positives + false_negatives + false_positives)
    precision = true_positives / (true_positives + false_positives)
    recall = true_positives / (true_positives + false_negatives)
    f1 = 2 * ((precision * recall) / (precision + recall))
    metrics = (precision, recall, f1)
    return metrics


def baseline_model(x_tr, x_te, y_te):
    # Develop a baseline model
    # It creates a prediction based on whether the player was a good shooter last season
    # Good shooter is determined by the TS%
    # If a player has a TS% over average then the player will make the shot otherwise he will miss
    # Baseline accuracy is 52%
    ts_avg = x_tr['ts%'].mean()
    base_pred = pd.DataFrame(x_te['ts%'])
    for i in range(len(base_pred)):
        if base_pred.iloc[i, 0] > ts_avg:
            base_pred.iloc[i, 0] = 1
        else:
            base_pred.iloc[i, 0] = 0
    accuracy = accuracy_score(y_te, base_pred)
    metrics = extra_metrics(base_pred['ts%'], y_te)

    return accuracy, metrics


def logistic_regression():
    # Logit model for benchmark
    # Only use type of shot and distance (besides those, linearity is lost)
    # Dependent variable is make
    # Independent variables are layup, dunk, dribble and distance
    # have excluded jump shot as if it is not layup and dunk it is jump shot
    # effectively these numbers are the difference compared to jump shot
    # based on summary all have low p value so all are significant
    df_cut = df[['layup', 'dunk', 'dribble', 'distance']]

    df_sc = feature_scaling(df_cut)

    x_tr, x_te, y_tr, y_te = split_data(df_sc, labels)

    lm = sm.Logit(y_tr, x_tr)
    result = lm.fit()
    predicted = result.predict(x_te)
    # check to see accuracy of model with 0.5 as the cutoff
    for i in list(predicted.index):
        if predicted[i] > 0.5:
            predicted[i] = 1
        else:
            predicted[i] = 0
    accuracy = accuracy_score(y_te, predicted)
    metrics = extra_metrics(predicted, y_te)

    return accuracy, result.summary(), metrics


def report(results, n_top=3):
    # Utility function to report best scores of Grid Search
    for i in range(1, n_top + 1):
        candidates = np.flatnonzero(results['rank_test_score'] == i)
        for candidate in candidates:
            print("Model with rank: {0}".format(i))
            print("Mean validation score: {0:.3f} (std: {1:.3f})".format(
                  results['mean_test_score'][candidate],
                  results['std_test_score'][candidate]))
            print("Parameters: {0}".format(results['params'][candidate]))
            print("")


def rf_grid_search():
    # Perform grid search to find best Random Forest (this took 12 hours to run)

    # Start with an RF with no parameters
    rf = RandomForestClassifier()

    # Specify parameters and distributions to sample from
    param_grid = {"n_estimators": [50, 100, 1000, 10000],
                  "criterion": ["gini", "entropy"],
                  "max_features": ["auto", None],
                  "max_depth": [5, 10, None],
                  "min_samples_split": [2, 3, 10],
                  "min_samples_leaf": [1, 3, 10],
                  "bootstrap": [True],
                  }

    # Run grid search
    grid_search = GridSearchCV(rf, param_grid=param_grid)
    start = time()
    grid_search.fit(df.values, labels.values.ravel())

    print("GridSearchCV took %.2f seconds for %d candidate parameter settings."
          % (time() - start, len(grid_search.cv_results_['params'])))
    report(grid_search.cv_results_, 10)

    return


def nn_grid_search():
    # Perform grid search to find best Neural Net (this took 10 hours to run)

    # Start with an RF with no parameters
    nn = MLPClassifier()

    # Specify parameters and distributions to sample from
    param_grid = {"hidden_layer_sizes": [(100, 100,), (200, 200,), (400, 400,), (100, 100, 100,), (200, 200, 200,),
                                         (400, 400, 400,)],
                  "activation": ["logistic", "relu"],
                  "solver": ["sgd", "adam"],
                  "alpha": [0.0001, 0.001],  # L2 parameter
                  "batch_size": [10, 100, "auto"],
                  "learning_rate": ["constant", "adaptive"],
                  "early_stopping": [True, False]
                  }

    # Run grid search
    grid_search = GridSearchCV(nn, param_grid=param_grid)
    start = time()
    grid_search.fit(df.values, labels.values.ravel())

    print("GridSearchCV took %.2f seconds for %d candidate parameter settings."
          % (time() - start, len(grid_search.cv_results_['params'])))
    report(grid_search.cv_results_, 10)


def random_forest(x_tr, y_tr, x_te, y_te):
    # Fit an Ensemble of Decision Trees (a random forest)
    # The RF is not sensitive to colinearity so no need to remove variables
    # The parameters were found based on Grid Search
    # Highest Accuracy is 0.654
    # Based on feature importances the opponent distances are the most important features
    rf = RandomForestClassifier(n_estimators=10000,
                                criterion='entropy',
                                max_features='auto',
                                max_depth=10,
                                min_samples_split=10,
                                min_samples_leaf=10,
                                bootstrap=True,
                                random_state=0)
    rf.fit(x_tr.values, y_tr.values.ravel())
    predicted_rf = rf.predict(x_te)
    predicted_proba_rf = rf.predict_proba(x_te)
    # in the case of an RF this simply gives a vote to every decision tree
    accuracy = accuracy_score(y_te, predicted_rf)
    feature_importances = pd.DataFrame(rf.feature_importances_,
                                       index=x_tr.columns,
                                       columns=['importance']).sort_values('importance', ascending=False)

    metrics = extra_metrics(predicted_rf, y_te)

    return rf, accuracy, feature_importances, metrics, predicted_proba_rf


def neural_net(x_tr, y_tr, x_te, y_te):
    # Fit a Neural Network
    # The NN is not sensitive to colinearity so no need to remove vriables
    # The parameters were found based on Grid Search
    # Highest Accuracy is 0.648

    nn = MLPClassifier(hidden_layer_sizes=(100, 100),
                       activation='relu',
                       solver='sgd',
                       alpha=0.0001,
                       batch_size=10,
                       learning_rate='adaptive',
                       early_stopping=False,
                       random_state=13
                       )
    nn.fit(x_tr.values, y_tr.values.ravel())
    predicted_nn = nn.predict(x_te)
    # predicted_probabilities = nn.predict_proba(x_test)
    # in the case of the NN this simply is the actual output of the last softmax classifier
    accuracy = accuracy_score(y_te, predicted_nn)

    metrics = extra_metrics(predicted_nn, y_te)

    return nn, accuracy, metrics


df_scaled = feature_scaling(df)
x_train, x_test, y_train, y_test = split_data(df_scaled, labels)


baseline_accuracy, baseline_other_metrics = baseline_model(x_train, x_test, y_test)

logit_accuracy, logit_summary, logit_other_metrics = logistic_regression()

rf_model, rf_accuracy, rf_feature_imp, rf_other_metrics, rf_prob = random_forest(x_train, y_train, x_test, y_test)
joblib.dump(rf_model, '../pickle/rf_model.pkl')

# nn_model, nn_accuracy, nn_other_metrics = neural_net(x_train, y_train, x_test, y_test)
# joblib.dump(nn_model, '../pickle/nn_model.pkl')
