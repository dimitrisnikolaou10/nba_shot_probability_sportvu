import user_interface
import players_of_event
import obtain_probability
from Game import Game


def runner():
    # Obtain the name of the game, the moments of the event, the id selected
    game_id, event_moments, event_id, event_description, shot_time = user_interface.get_event_sv()

    if not game_id:  # if game_id is None
        print('The user chose to exit')
        return

    player_ids, player_names, player_jerseys = players_of_event.get_players(event_moments)

    player_info = (player_ids, player_names, player_jerseys)

    probability_to_make = obtain_probability.get_prob(game_id, event_id)

    feature_info = obtain_probability.get_feature_info(game_id, event_id)

    game = Game(event_moments, player_info, event_description, probability_to_make, shot_time, feature_info)

    game.start()


runner()
