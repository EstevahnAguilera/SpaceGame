import pygame
from pygame.sprite import Sprite
import random
import time
import math

class Alien(Sprite):
    """This class will represent a single alien in the fleet."""

    def __init__(self, ai_game):
        #Initialize the alien and set its starting position.
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.stats = ai_game.stats
        
        # Load the alien image and set its starting position
        try:
            original_image = pygame.image.load('images/alien2.png')
            self.image = pygame.transform.scale(original_image, (75, 50))
        except:
            # Fallback to a colored rectangle if image loading fails
            self.image = pygame.Surface((75, 50))
            self.image.fill(self.settings.alien_color)
        
        self.rect = self.image.get_rect()

        #This will start a new alien near the top left of the screen.
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        #Store the alien's exact position
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        #Random movement direction
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        
        #Random movement speed (adjusted for more vertical movement)
        base_speed_x = random.uniform(0.4, 0.7) * self.settings.alien_speed
        base_speed_y = random.uniform(0.3, 0.5) * self.settings.alien_speed
        
        # Calculate speed based on level
        self._calculate_speed()

        #Shooting behavior
        self.last_shot = 0
        # Reduce shoot delay as level increases
        base_delay = random.randint(800, 2000)
        self.shoot_delay = int(base_delay / (1.0 + (self.stats.level - 1) * 0.1))

        # Movement pattern variables
        self.movement_timer = 0
        self.movement_change_interval = random.randint(1000, 3000)  # Change direction every 1-3 seconds
        self.target_direction = None
        self.last_direction_change = pygame.time.get_ticks()

    def _calculate_speed(self):
        """Calculate alien speed based on current level."""
        base_speed = self.settings.alien_speed
        level_multiplier = 1.0 + (self.stats.level - 1) * 0.1  # 10% increase per level
        self.speed_x = base_speed * level_multiplier
        self.speed_y = base_speed * level_multiplier

    def check_edges(self):
        #This will make aliens bounce off the edges of the screen and stay in upper portion
        screen_rect = self.screen.get_rect()
        
        # Check horizontal edges
        if self.rect.right >= screen_rect.right:
            self.rect.right = screen_rect.right
            self.direction_x *= -1
        elif self.rect.left <= 0:
            self.rect.left = 0
            self.direction_x *= -1
            
        # Check vertical edges - keep aliens in upper 2/3 of screen
        max_height = screen_rect.height * 2/3
        if self.rect.bottom >= max_height:
            self.rect.bottom = max_height
            self.direction_y *= -1
        elif self.rect.top <= 0:
            self.rect.top = 0
            self.direction_y *= -1

    def update(self):
        #Update the alien's position with random movement
        self.check_edges()
        
        # Change direction periodically
        current_time = pygame.time.get_ticks()
        if current_time - self.last_direction_change > self.movement_change_interval:
            self.last_direction_change = current_time
            self.movement_change_interval = random.randint(1000, 3000)
            
            # Random chance to change direction
            if random.random() < 0.3:  # 30% chance to change direction
                self.direction_x *= -1
            if random.random() < 0.3:  # 30% chance to change direction
                self.direction_y *= -1
            
            # Random chance to adjust speed
            if random.random() < 0.2:  # 20% chance to adjust speed
                self._calculate_speed()
        
        #Update horizontal position
        self.x += self.speed_x * self.direction_x
        self.rect.x = self.x
        
        #Update vertical position
        self.y += self.speed_y * self.direction_y
        self.rect.y = self.y

    def can_shoot(self):
        """Check if the alien can shoot based on time delay."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            self.last_shot = current_time
            # Update shoot delay based on current level
            base_delay = random.randint(800, 2000)
            level_multiplier = 1.0 + (self.stats.level - 1) * 0.1
            self.shoot_delay = int(base_delay / level_multiplier)
            return True
        return False