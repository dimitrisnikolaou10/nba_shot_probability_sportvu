from Moment import Moment
from Constant import Constant
import matplotlib.pyplot as plt
from matplotlib import animation
from moviepy.editor import *


class Event:
    """ A class for handling and showing events """

    def __init__(self, moments, player_info, event_description, probability_to_make, shot_time, feat_info):
        moments_list = []  # Create list of moments (11 rows of the dataframe)
        first_index_of_moment, last_index_of_moment, last_index = 0, 11, len(moments) - 1
        while last_index_of_moment <= last_index:
            df_temp = moments.iloc[first_index_of_moment:last_index_of_moment, :]
            moments_list.append(df_temp)
            first_index_of_moment, last_index_of_moment = last_index_of_moment, last_index_of_moment + 11
        self.moments = [Moment(moment) for moment in moments_list]  # store the list in self.moments
        player_ids = player_info[0]
        player_names = player_info[1]
        player_jerseys = player_info[2]
        values = list(zip(player_names, player_jerseys))
        # Dictionary for player ids that contains Name, Jersey Number
        self.player_ids_dict = dict(zip(player_ids, values))
        self.event_description = event_description
        self.probability_to_make = probability_to_make
        self.shot_time = shot_time
        self.feat_info = feat_info  # tuple with -> [0] opp_1_dist, [1] opp_2_dist, [2] opp_3_dist, [3] ts%

    # This function runs iteratively and updates all circles and clock - it is called by the animation function
    def update_radius(self, i, player_circles, ball_circle, annotations, clock_info, shot, feature_info):
        moment = self.moments[i]  # obtain the moment
        for j, circle in enumerate(player_circles):  # repeat for all players
            circle.center = moment.players[j].x, moment.players[j].y  # center of circle is x,y coordinates
            annotations[j].set_position(circle.center)  # add the number of the jersey
            clock_test = 'Quarter {:d}\n {:02d}:{:02d}\n {:03.1f}'.format(  # format the clock
                         moment.quarter,
                         int(moment.game_clock) % 3600 // 60,
                         int(moment.game_clock) % 60,
                         moment.shot_clock)
            if self.shot_time + 2 + 2 > moment.game_clock > self.shot_time + 2 - 2:
                shot.set_color('black')
                shot.set_position([39, 5])
                feature_info.set_color('black')
                feature_info.set_position([44, 2])
            else:
                shot.set_color('white')
                shot.set_position([-5, -5])
                feature_info.set_color('white')
                feature_info.set_position([-15, -15])
            clock_info.set_text(clock_test)  # add the clock text based on above
        ball_circle.center = moment.ball.x, moment.ball.y  # center of ball circle, the x,y coordinates
        ball_circle.radius = moment.ball.radius / Constant.NORMALIZATION_COEF  # adjust the radius based on height
        return player_circles, ball_circle

    def show(self):
        # Leave some space for inbound passes
        ax = plt.axes(xlim=(Constant.X_MIN,
                            Constant.X_MAX),
                      ylim=(Constant.Y_MIN,
                            Constant.Y_MAX))
        ax.axis('off')
        fig = plt.gcf()
        ax.grid(False)  # Remove grid
        start_moment = self.moments[0]
        player_dict = self.player_ids_dict

        # mark the shot probability
        shot = ax.annotate('Shot probability: ' + str(self.probability_to_make) + '%', xy=[0, 0],
                                 color='white', horizontalalignment='center',
                                 verticalalignment='center', fontweight='bold')

        # mark the feature information (opponent distances and ts%)
        feature_info = ax.annotate('Closest Opp. distances: ' + str(round(self.feat_info[0], 1)) + ', ' +
                                   str(round(self.feat_info[1], 1)) + ', ' +
                                   str(round(self.feat_info[2], 1)),
                                   xy=[0, 0], color='white', horizontalalignment='center',
                                   verticalalignment='center', fontweight='bold')

        # mark the clock (to be precise, note the spot where the clock will be placed)
        clock_info = ax.annotate('', xy=[Constant.X_CENTER, Constant.Y_CENTER],
                                 color='black', horizontalalignment='center',
                                 verticalalignment='center')

        # mark the jersey numbers on the players
        annotations = [ax.annotate(self.player_ids_dict[player.id][1], xy=[0, 0], color='w',
                                   horizontalalignment='center',
                                   verticalalignment='center', fontweight='bold')
                       for player in start_moment.players]

        # Prepare table

        # Sort players so you know that in next step you get home team player
        sorted_players = sorted(start_moment.players, key=lambda player: player.team.id)

        # You now know where there is a home team player and where there is an away team player
        home_player = sorted_players[0]
        guest_player = sorted_players[5]

        # Name the columns based on the name of the teams, also obtain the colour
        column_labels = tuple([home_player.team.name, guest_player.team.name])
        column_colours = tuple([home_player.team.color, guest_player.team.color])
        cell_colours = [column_colours for _ in range(5)]

        # Obtain home and away players in Name, Jersey Number format and zip the two lists
        home_players = [' #'.join([player_dict[player.id][0], player_dict[player.id][1]]) for player in
                        sorted_players[:5]]
        guest_players = [' #'.join([player_dict[player.id][0], player_dict[player.id][1]]) for player in
                         sorted_players[5:]]
        players_data = list(zip(home_players, guest_players))

        # Create the table based on all the previous info (player table)
        table = plt.table(cellText=players_data,
                          colLabels=column_labels,
                          colColours=column_colours,
                          colWidths=[Constant.COL_WIDTH, Constant.COL_WIDTH],
                          loc='top',
                          cellColours=cell_colours,
                          fontsize=Constant.FONTSIZE,
                          cellLoc='center')
        table.scale(1, Constant.SCALE)
        table_cells = table.properties()['child_artists']
        for cell in table_cells:
            cell._text.set_color('white')

        # Create the second table that goes under. This table will contain description and probability.
        # If you want to add second row you have to do [[self.event_description], [xxx]]
        # If you want to add second col you have to do [['xxx','xxx']] and also change the colWid to [0.3,0.3]
        table = plt.table(cellText=[[self.event_description],
                                    ['Probability for shot to go in: ' + str(self.probability_to_make)]],
                          loc='bottom',
                          colWidths=[0.6],
                          cellColours=[['#bcd0e2'], ['#bcd0e2']],
                          cellLoc='center',
                          # rowLabels=['Description'],
                          fontsize=Constant.FONTSIZE)
        table.scale(1, Constant.SCALE)
        table_cells = table.properties()['child_artists']
        for cell in table_cells:
            cell._text.set_color('black')

        # create 10 player circles and 1 ball circle and add to ax
        player_circles = [plt.Circle((0, 0), Constant.PLAYER_CIRCLE_SIZE, color=player.color)
                          for player in start_moment.players]
        ball_circle = plt.Circle((0, 0), Constant.PLAYER_CIRCLE_SIZE,
                                 color=start_moment.ball.color)
        for circle in player_circles:
            ax.add_patch(circle)
        ax.add_patch(ball_circle)

        # This is the most important function. It call a function iteratively. The function is update_radius.
        # With fargs, I pass all arguments needed for update_radius. Update radius first argument is always the
        # frame that we are at. The arguments are the created circles for players and ball, the jersey numbers
        # that follow the circles and the clock. If you want to speed up, lower the interval.
        anim = animation.FuncAnimation(
            fig, self.update_radius,
            fargs=(player_circles, ball_circle, annotations, clock_info, shot, feature_info),
            frames=len(self.moments), interval=Constant.INTERVAL)

        # Add the basketball court in the plot
        court = plt.imread('../data/court.png')
        plt.imshow(court, zorder=0, extent=[Constant.X_MIN, Constant.X_MAX - Constant.DIFF,
                                            Constant.Y_MAX, Constant.Y_MIN])

        # anim.save('../animations/animation.mp4', writer='ffmpeg', fps=25)  # save file as mp4
        # clip = (VideoFileClip("animations/Curry 28' 3PT Pullup Jump Shot (12 PTS).mp4"))  # convert to gif
        # clip.write_gif("animations/Curry.gif")

        plt.show()
