from Event import Event
from Team import Team
from Constant import Constant


class Game:
    """A class for keeping info about the games"""
    def __init__(self, event_moments, player_info, event_description, probability_to_make, shot_time, feat_info):
        home_team_player_id = player_info[0][0]
        away_team_player_id = player_info[0][5]
        home_team_id = Constant.PLAYER_LIST[Constant.PLAYER_LIST['player_id'] == home_team_player_id].iloc[0, 0]
        away_team_id = Constant.PLAYER_LIST[Constant.PLAYER_LIST['player_id'] == away_team_player_id].iloc[0, 0]
        self.home_team = Team(home_team_id)
        self.guest_team = Team(away_team_id)

        self.event = Event(event_moments, player_info, event_description, probability_to_make, shot_time, feat_info)

    def start(self):
        self.event.show()
