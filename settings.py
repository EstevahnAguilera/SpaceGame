class Settings:
    #This class will store all of the settings for Alien Invasion

    def __init__(self):
        #Initializing the games settings

        #Screen Settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)
        
        #Ship settings
        self.ship_speed = 1.5 #This is the ships speed
        self.ship_limit = 3

        #Bullet settings
        self.bullet_speed = 2.5
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60,60,60)

        #If you want to set a limit to the amount of bullets allowed
        self.bullets_allowed = 3

        #this is the aliens speed/ directions
        self.alien_speed = 1.0
        self.fleet_drop_speed = 10
        self.fleet_direction = 1 # 1 represents right & -1 represents left.