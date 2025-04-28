import pygame
from pygame.sprite import Sprite

class AlienBullet(Sprite):
    """A class to manage bullets fired from aliens."""
    
    def __init__(self, ai_game, alien):
        """Create a bullet object at the alien's current position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        
        # Load the bullet image and set its rect
        try:
            original_image = pygame.image.load('images/alien_bullet.png')
            self.image = pygame.transform.scale(original_image, (3, 15))
        except:
            # Fallback to a colored rectangle if image loading fails
            self.image = pygame.Surface((3, 15))
            self.image.fill((255, 0, 0))  # Red color for alien bullets
        
        self.rect = self.image.get_rect()
        self.rect.midbottom = alien.rect.midbottom
        
        # Store the bullet's position as a decimal value
        self.y = float(self.rect.y)
        
    def update(self):
        """Move the bullet down the screen."""
        # Update the decimal position of the bullet
        self.y += self.settings.alien_bullet_speed
        # Update the rect position
        self.rect.y = self.y
        
    def draw_bullet(self):
        """Draw the bullet to the screen."""
        self.screen.blit(self.image, self.rect) 