# NBA Shot Probability with SportVU and Play by Play data
NBA SportVU data is a spatiotemporal database that tracks the 10 players and the ball 25 times a second.
Play by Play data is an event based database that describes the event that occured in the game (shot, rebound, turnover etc.)

These two databases were combined and a probability model was developed that predicts if a shot will go in.

Best performing model was a Random Forest and it achieved a classification rate of 67%.

The data was obtained from this source: https://github.com/sealneaward/nba-movement-data/tree/master/data
NBA stopped the circulation of this data in the middle of the 15-16 season.

With the help of code from this source: https://github.com/linouk23/NBA-Player-Movements , a software that generates the play animation together with its likelihood to go in was generated. 
