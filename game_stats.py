class GameStats:
    #this class will track the stats of the alien invasion

    def __init__(self, ai_game):
        self.settings = ai_game.settings
        self.reset_stats()

        # Start game in an inactive state.
        self.game_active = False
        self.game_over = False

    def reset_stats(self):
        #This will hold all of the stats in game
        self.ships_left = self.settings.ship_limit
        self.score = 0  # Initialize score to 0
        self.wave = 1  # Start at wave 1
        self.difficulty_multiplier = 1.0  # Base difficulty multiplier