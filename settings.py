class Settings:
    #This class will store all of the settings for Alien Invasion

    def __init__(self):
        #Initializing the games settings

        #Screen Settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (0, 0, 0)
        
        #Ship settings
        self.ship_speed = 1.5 #This is the ships speed
        self.ship_vertical_speed = 1.2  # Vertical movement speed
        self.ship_limit = 3

        #Bullet settings
        self.bullet_speed = 2.5
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (255, 255, 0)  # Changed to yellow for better visibility

        #If you want to set a limit to the amount of bullets allowed
        self.bullets_allowed = 3

        #Alien bullet settings
        self.alien_bullet_speed = 2.0  # Increased from 1.5
        self.alien_bullets_allowed = 5  # Increased from 3
        self.alien_fire_frequency = 800  # Decreased from 1000 (shoot more often)
        self.alien_bullet_color = (255, 0, 0)  # Red color for alien bullets

        #this is the aliens speed/ directions
        self.alien_speed = 2.5  # Increased from 2.0
        self.fleet_drop_speed = 10
        self.fleet_direction = 1 # 1 represents right & -1 represents left.

        # UI Settings
        self.ui_font = 'Arial'
        self.ui_font_size = 36
        self.ui_color = (255, 255, 255)
        self.ui_highlight_color = (255, 255, 0)  # Yellow for highlighted text
        self.ui_background_color = (0, 0, 0, 128)  # Semi-transparent black

        # Star field settings
        self.star_count = 100
        self.star_speed = 1.0
        self.star_color = (255, 255, 255)
        self.star_size = 2