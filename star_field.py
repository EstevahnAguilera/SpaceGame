import pygame
import random

class Star:
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings
        self.reset()
        
    def reset(self):
        self.x = random.randint(0, self.settings.screen_width)
        self.y = random.randint(0, self.settings.screen_height)
        self.speed = random.uniform(0.5, self.settings.star_speed)
        self.size = random.randint(1, self.settings.star_size)
        
    def update(self):
        self.y += self.speed
        if self.y > self.settings.screen_height:
            self.reset()
            self.y = 0
            
    def draw(self):
        pygame.draw.circle(self.screen, self.settings.star_color, 
                         (int(self.x), int(self.y)), self.size)

class StarField:
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings
        self.stars = [Star(screen, settings) for _ in range(settings.star_count)]
        
    def update(self):
        for star in self.stars:
            star.update()
            
    def draw(self):
        for star in self.stars:
            star.draw() 