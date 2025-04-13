class GameStats:
    #this class will track the stats of the alien invasion

    def __init__(self, ai_game):
        self.settings = ai_game.settings
        self.reset_stats()

    def reset_stats(self):
        #This will hold all of the stats in game
        self.ships_left = self.settings.ship_limit