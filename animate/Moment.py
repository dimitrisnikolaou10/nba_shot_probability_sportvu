from Ball import Ball
from Player import Player


class Moment:
    """A class for keeping info about the moments"""
    def __init__(self, moment):
        self.quarter = moment.iloc[0, 7]  # Hardcoded position for quarter in df
        self.game_clock = moment.iloc[0, 5]  # Hardcoded position for game_clock in df
        self.shot_clock = moment.iloc[0, 6]  # Hardcoded position for shot_clock in df
        ball = moment.iloc[0, :]  # Hardcoded position for ball in df
        self.ball = Ball(ball)
        players = moment.iloc[1:, :]  # Hardcoded position for players in df
        self.players = [Player(list(player)) for index, player in players.iterrows()]
