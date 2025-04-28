import pygame
from pygame.sprite import Sprite

class Bullet(Sprite):
    #This class will manage the bullets fired from the ship

    def __init__(self, ai_game):
        #creating a bullet object at the ships current position
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color
        self.bullet_id = None  # Will be set when bullet is fired

        # Create a bullet surface
        self.image = pygame.Surface((self.settings.bullet_width, self.settings.bullet_height))
        self.image.fill(self.color)
        
        self.rect = self.image.get_rect()
        self.rect.midtop = ai_game.ship.rect.midtop

        #store the bullets position as a float.
        self.y = float(self.rect.y)

    def update(self):
        #This will move the bullet up the screen
        self.y -= self.settings.bullet_speed #update the bullets exact position
        self.rect.y = self.y # update the rect position

    def draw_bullet(self):
        #this will draw the bullet on the screen
        self.screen.blit(self.image, self.rect)
