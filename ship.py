import pygame

class Ship:
    #This class will manage the ship

    def __init__(self,ai_game):
        #Initialize the shape and set its starting position
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        #Load the ship image and get its rectangle
        original_image = pygame.image.load('SpaceGame/images/ship.png')
        self.image = pygame.transform.scale(original_image, (45, 65))  

        
        # self.image = pygame.image.load('SpaceGame/images/ship.png')
        self.rect = self.image.get_rect()

        #Start each new ship at the bottom center of the screen
        self.rect.midbottom = self.screen_rect.midbottom

        #Store a float for the ship's exact horizontal position
        self.x = float(self.rect.x)

        #Start with a ship that is not moving
        self.moving_right = False
        self.moving_left = False

    def center_ship(self):
        #center the ship on the screen
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)

    def update(self):
        #Updating the ship's position based on the  movement flag
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        #updating rext object from self.x
        self.rect.x = self.x

    def blitme(self):
        #Draw the ship at is current location
        self.screen.blit(self.image, self.rect)