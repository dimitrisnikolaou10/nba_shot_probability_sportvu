from Team import Team
from Constant import Constant


class Player:
    """A class for keeping info about the players"""
    def __init__(self, player):
        self.team = Team(player[0])
        self.id = player[1]
        self.x = player[2]
        self.y = Constant.Y_MAX - player[3]
        self.shooter = player[10]
        self.color = self.team.color
