import sys
from time import sleep
import pygame

from settings import Settings #Creating an instance of settings in this class
from game_stats import GameStats #Creating and instance of gamestats in this class
from ship import Ship #Creating an instance of ship in this class
from bullet import Bullet # Creating an instance of bullet in this class
from alien import Alien # Creating an instance of alien in this class
from button import Button # Creating an instance of button in this class

class AlienInvasion:
    #This class will manage game assets and behavior.

    def __init__(self):
        pygame.init() #This will initialize the game, and create game resources.
        self.clock = pygame.time.Clock() #This controls the frame rate
        self.settings = Settings()

        self.screen = pygame.display.set_mode((self.settings.screen_width,self.settings.screen_height))

        #If you want to play in full screen:
        """
        self.screen = pygame.display.set_mode((0,0)), pygame.FULLSCREEN()
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height"""

        pygame.display.set_caption("Alien Invasion")

        self.stats = GameStats(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.create_fleet()

        self.bg_color = (0, 0, 0) #Setting the background color
        self.game_active = False

        # Make the Play Button
        self.play_button = Button(self, "Play")
    
    def run_game(self):
        while True:  #This will be the loop of the game.
            self.check_events()
            if self.game_active:
                self.ship.update()
                self.update_bullets()
                self.update_aliens()
            self.update_screen()
            self.clock.tick(60)  #Creating an instance of the clock

    def check_events(self):
        #This will check keypresses and mouse events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self.check_keydown_events(event)
            
            elif event.type == pygame.KEYUP:
                self.check_keyup_events(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self.fire_bullet()
    
    def check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_play_button(self, mouse_pos):
        # Start a new game when the player clicks play
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self.stats.reset_stats()
            self.game_active = True

            # Remove any remaining bullets and aliens
            self.bullets.empty()
            self.aliens.empty()

            # Create a new fleet and center the ship
            self.create_fleet()
            self.ship.center_ship()

    def fire_bullet(self):
        #this will create a new bullet and add it to the bullets group
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def create_fleet(self):
        #create the fleet of aliens
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size


        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):    
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self.create_alien(current_x,current_y)
                current_x += 2 * alien_width

            current_x = alien_width
            current_y += 2 * alien_height

    def create_alien(self, x_position, y_position):
        #create an alien and place it in a row
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def check_fleet_edges(self):
        #this will take care of the alien if it touches an edge
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self.change_fleet_direction()
                break

    def change_fleet_direction(self):
        #This will drop the entire fleet and change the fleet's direction
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def ship_hit(self):
        #this will respond to a ship being hit by an alien
        if self.stats.ship_left > 0:
            self.stats.ships_left -= 1 #Decrement ships_left

            #get rid of any remaining bullets and aliens
            self.bullets.empty()
            self.aliens.empty()

            #create a new fleet and center the ship
            self.create_fleet()
            self.ship.center_ship()

            #pause
            sleep(0.5)

        else:
            self.game_active = False

    def check_aliens_bottom(self):
        #check if any aliens have reached the bottom of the screen
        for alien in self.aliens.sprites():
            if alien.rect.bottom >=self.settings.screen_height:
                #Treat it as if the ship got hit, meaning restart the game
                self.ship_hit()
                break

    def update_aliens(self):
        #update the positions of all aliens in the fleet
        self.check_fleet_edges()
        self.aliens.update()
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self.ship_hit()
        self.check_aliens_bottom() #check if any of the aliens hit the bottom of the screen

    def update_bullets(self):
        """Update the position of bullets and get rid of old bullets."""
        self.bullets.update()
        for bullet in self.bullets.copy(): # This will get rid of bullets that have disappeared.
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        print(len(self.bullets))
        self.check_bullet_alien_collisions()

        if not self.aliens:
            self.bullets.empty()
            self.create_fleet()

    def check_bullet_alien_collisions(self):
        #this will check if any bullets have hit an alien
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)

        
    def update_screen(self):
        #This will update the events on the screen and flip them to the new screen
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)

        #Draw the play button if the game is inactive
        if not self.game_active:
            self.play_button.draw_button()


        pygame.display.flip()

if __name__ == '__main__':
    #This will make a game instance & run
    ai = AlienInvasion()
    ai.run_game()