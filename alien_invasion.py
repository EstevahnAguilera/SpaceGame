import sys
from time import sleep
import pygame
import os
import threading
import multiprocessing
import signal
from os_game_utils import GameOSUtils

from settings import Settings #Creating an instance of settings in this class
from game_stats import GameStats #Creating and instance of gamestats in this class
from ship import Ship #Creating an instance of ship in this class
from bullet import Bullet # Creating an instance of bullet in this class
from alien import Alien # Creating an instance of alien in this class
from button import Button # Creating an instance of button in this class
from alien_bullet import AlienBullet
from star_field import StarField

class AlienInvasion:
    #This class will manage game assets and behavior.

    def __init__(self):
        # Initialize pygame only if it hasn't been initialized
        if not pygame.get_init():
            pygame.init()
            pygame.mixer.init()
        
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        self.os_utils = GameOSUtils()

        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))

        #If you want to play in full screen:
        """
        self.screen = pygame.display.set_mode((0,0)), pygame.FULLSCREEN()
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height"""

        pygame.display.set_caption("Alien Invasion")

        # Load and scale the background image
        self.background = pygame.image.load('images/background.jpg')
        self.background = pygame.transform.scale(self.background, 
                                              (self.settings.screen_width, 
                                               self.settings.screen_height))

        self.stats = GameStats(self)

        # Create the ship first
        self.ship = Ship(self)
        
        # Then create other game elements
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        
        self.star_field = StarField(self.screen, self.settings)
        
        self.create_fleet()
        
        self.bg_color = (0, 0, 0) #Keeping this for reference
        self.showing_high_scores = False

        # Make the Play Button
        self.play_button = Button(self, "Play")
        # Make the Play Again Button
        self.play_again_button = Button(self, "Play Again")
        # Make the View High Scores Button
        self.high_scores_button = Button(self, "High Scores")
        # Make the Back Button
        self.back_button = Button(self, "Back")
        # Make the Exit Button
        self.exit_button = Button(self, "Exit")
        
        # Load high scores
        self.high_scores = self.os_utils.load_high_scores()
        print("Current high scores:", self.high_scores)
        
        # Start background music in a separate thread
        self.os_utils.start_music_thread("sounds/background_music.mp3")
    
    def run_game(self):
        """Main game loop"""
        running = True
        while running:
            # Handle events in the main thread
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                        break
                    self.check_keydown_events(event)
                elif event.type == pygame.KEYUP:
                    self.check_keyup_events(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.showing_high_scores:
                        self._check_back_button(mouse_pos)
                    elif self.stats.game_over:
                        self._check_play_again_button(mouse_pos)
                        self._check_high_scores_button(mouse_pos)
                        self._check_exit_button(mouse_pos)
                    elif not self.stats.game_active:
                        self._check_play_button(mouse_pos)
                        self._check_high_scores_button(mouse_pos)

            # Update the screen
            self.screen.blit(self.background, (0, 0))
            
            # Update and draw the star field only if game is active
            if self.stats.game_active:
                self.star_field.update()
                self.star_field.draw()
            
            if self.showing_high_scores:
                # Create a semi-transparent overlay
                overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))  # Semi-transparent black
                self.screen.blit(overlay, (0, 0))
                
                # Draw high scores
                self._draw_high_scores()
            elif self.stats.game_over:
                # Draw game over elements
                self._draw_game_over_elements(self.screen)
            else:
                if self.stats.game_active:
                    # Update game elements
                    self.ship.update()
                    self.update_bullets()
                    self.update_aliens()
                    
                    # Draw game elements
                    self.ship.blitme()
                    for bullet in self.bullets.sprites():
                        bullet.draw_bullet()
                    for bullet in self.alien_bullets.sprites():
                        bullet.draw_bullet()
                    self.aliens.draw(self.screen)
                    self._draw_score()
                else:
                    # Draw start screen
                    self._draw_start_screen()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        # Clean up when game loop ends
        pygame.quit()
        sys.exit()

    def _collision_handler(self):
        """Handle collisions in a separate thread"""
        while True:
            if self.stats.game_active:
                # Check bullet-alien collisions
                self.check_bullet_alien_collisions()
                
                # Check aliens reaching bottom
                self.check_aliens_bottom()
            sleep(0.016)  # ~60 FPS

    def check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self.check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self.check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.stats.game_over:
                    self._check_play_again_button(mouse_pos)
                    self._check_high_scores_button(mouse_pos)
                elif not self.stats.game_active:
                    self._check_play_button(mouse_pos)
                    self._check_high_scores_button(mouse_pos)

    def check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_UP:
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self.fire_bullet()
    
    def check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_UP:
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = False

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            print("Play button clicked")
            self._start_game()

    def _check_play_again_button(self, mouse_pos):
        """Start a new game when the player clicks Play Again."""
        button_clicked = self.play_again_button.rect.collidepoint(mouse_pos)
        if button_clicked and self.stats.game_over:
            # Reset game stats
            self.stats.reset_stats()
            self.stats.game_active = True
            self.stats.game_over = False
            
            # Clear any remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()
            self.alien_bullets.empty()
            
            # Create a new fleet and center the ship
            self.create_fleet()
            self.ship.center_ship()

    def _check_high_scores_button(self, mouse_pos):
        """Show high scores when the player clicks High Scores."""
        button_clicked = self.high_scores_button.rect.collidepoint(mouse_pos)
        if button_clicked and (self.stats.game_over or not self.stats.game_active):
            self.showing_high_scores = True

    def _check_back_button(self, mouse_pos):
        """Return to previous screen when the player clicks Back."""
        button_clicked = self.back_button.rect.collidepoint(mouse_pos)
        if button_clicked and self.showing_high_scores:
            self.showing_high_scores = False

    def _check_exit_button(self, mouse_pos):
        """Exit the game when the player clicks Exit."""
        button_clicked = self.exit_button.rect.collidepoint(mouse_pos)
        if button_clicked:
            pygame.quit()
            sys.exit()

    def _start_game(self):
        """Start a new game."""
        print("Starting new game")
        # Reset game state
        self.stats.reset_stats()
        self.stats.game_active = True
        self.stats.game_over = False
        
        # Clear existing game elements
        self.aliens.empty()
        self.bullets.empty()
        self.alien_bullets.empty()
        
        # Create new fleet and center ship
        self.create_fleet()
        self.ship.center_ship()
        
        # Ensure screen is updated
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
        
        print("Game started")

    def _draw_high_scores(self):
        """Draw the high scores screen."""
        # Draw title
        font = pygame.font.SysFont(self.settings.ui_font, 64)
        title = font.render("High Scores", True, self.settings.ui_highlight_color)
        title_rect = title.get_rect()
        title_rect.centerx = self.screen.get_rect().centerx
        title_rect.top = 100
        self.screen.blit(title, title_rect)
        
        # Draw high scores
        font = pygame.font.SysFont(self.settings.ui_font, 48)
        for i, score in enumerate(self.high_scores[:10]):  # Show top 10 scores
            score_text = font.render(f"{i+1}. {score}", True, self.settings.ui_color)
            score_rect = score_text.get_rect()
            score_rect.centerx = self.screen.get_rect().centerx
            score_rect.top = 200 + i * 50
            self.screen.blit(score_text, score_rect)
        
        # Draw back button
        self.back_button.rect.centerx = self.screen.get_rect().centerx
        self.back_button.rect.top = 700
        self.back_button._prep_msg()
        self.back_button.draw_button()

    def fire_bullet(self):
        """Fire a bullet if we haven't reached the limit."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def create_fleet(self):
        """Create the fleet of aliens"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        # Reduced number of rows and spacing
        number_rows = 2  # Reduced from 3
        number_aliens_x = 4  # Reduced from 6
        
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                x_position = alien_width + 3 * alien_width * alien_number
                y_position = alien_height + 2 * alien_height * row_number
                self.create_alien(x_position, y_position)

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
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left > 0:
            # Decrement ships_left.
            self.stats.ships_left -= 1
            print(f"Ships left: {self.stats.ships_left}")
            
            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()
            self.alien_bullets.empty()
            
            # Create a new fleet and center the ship.
            self.create_fleet()
            self.ship.center_ship()
            
            # Pause.
            sleep(0.5)
        else:
            self.stats.game_active = False
            self.stats.game_over = True
            print("Game Over! No ships left.")
            
            # Save the score if it's a high score
            if self.stats.score > 0:
                print(f"Game over! Final score: {self.stats.score}")
                self.os_utils.save_high_score(self.stats.score)
                self.high_scores = self.os_utils.load_high_scores()
                print("Updated high scores:", self.high_scores)

    def check_aliens_bottom(self):
        #This method is no longer needed as aliens will bounce off the bottom
        pass

    def update_aliens(self):
        """Update the positions of all aliens in the fleet."""
        self.aliens.update()
        
        # Check for ship-alien collisions
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            # Set game state
            self.stats.game_active = False
            self.stats.game_over = True
            self.stats.ships_left = 0
            
            # Save high score
            if self.stats.score > 0:
                self.os_utils.save_high_score(self.stats.score)
                self.high_scores = self.os_utils.load_high_scores()
            
            # Clear everything
            self.aliens.empty()
            self.bullets.empty()
            self.alien_bullets.empty()
            
            # Clear the screen
            self.screen.fill(self.settings.bg_color)
            
            # Draw background
            self.screen.blit(self.background, (0, 0))
            
            # Create a semi-transparent overlay
            overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))  # Semi-transparent black
            self.screen.blit(overlay, (0, 0))
            
            # Draw game over message
            font = pygame.font.SysFont(self.settings.ui_font, 64)
            game_over_text = font.render("Game Over", True, self.settings.ui_highlight_color)
            game_over_rect = game_over_text.get_rect()
            game_over_rect.centerx = self.screen.get_rect().centerx
            game_over_rect.top = 100
            self.screen.blit(game_over_text, game_over_rect)
            
            # Draw final score
            score_text = font.render(f"Final Score: {self.stats.score}", True, self.settings.ui_color)
            score_rect = score_text.get_rect()
            score_rect.centerx = self.screen.get_rect().centerx
            score_rect.top = 200
            self.screen.blit(score_text, score_rect)
            
            # Position and draw buttons
            self.play_again_button.rect.centerx = self.screen.get_rect().centerx
            self.play_again_button.rect.top = 300
            self.play_again_button._prep_msg()
            self.play_again_button.draw_button()
            
            self.high_scores_button.rect.centerx = self.screen.get_rect().centerx
            self.high_scores_button.rect.top = 400
            self.high_scores_button._prep_msg()
            self.high_scores_button.draw_button()
            
            self.exit_button.rect.centerx = self.screen.get_rect().centerx
            self.exit_button.rect.top = 500
            self.exit_button._prep_msg()
            self.exit_button.draw_button()
            
            # Force screen update
            pygame.display.flip()
            return

        # Handle alien shooting
        for alien in self.aliens.sprites():
            if alien.can_shoot() and len(self.alien_bullets) < self.settings.alien_bullets_allowed:
                new_bullet = AlienBullet(self, alien)
                self.alien_bullets.add(new_bullet)

    def update_bullets(self):
        """Update bullet positions and handle bullet cleanup"""
        # Update player bullets
        self.bullets.update()
        
        # Remove bullets that have left the screen
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        
        # Update alien bullets
        self.alien_bullets.update()
        
        # Remove alien bullets that have left the screen
        for bullet in self.alien_bullets.copy():
            if bullet.rect.top >= self.settings.screen_height:
                self.alien_bullets.remove(bullet)
        
        # Check for bullet-alien collisions
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)
        
        # Handle collisions
        if collisions:
            for aliens in collisions.values():
                self.stats.score += len(aliens) * 10

        # Check for alien bullet-ship collisions
        if pygame.sprite.spritecollideany(self.ship, self.alien_bullets):
            print("GAME OVER - Ship hit by alien bullet!")
            self.stats.game_active = False
            self.stats.game_over = True
            self.stats.ships_left = 0
            
            # Save high score
            if self.stats.score > 0:
                print(f"Final score: {self.stats.score}")
                self.os_utils.save_high_score(self.stats.score)
                self.high_scores = self.os_utils.load_high_scores()
            
            # Clear everything
            self.aliens.empty()
            self.bullets.empty()
            self.alien_bullets.empty()
            
            # Force game over screen
            self.screen.blit(self.background, (0, 0))
            self._draw_game_over_elements(self.screen)
            pygame.display.flip()
            pygame.time.wait(1000)  # Pause for a second to show game over

        # Create new fleet if all aliens are destroyed
        if not self.aliens:
            self.bullets.empty()
            self.alien_bullets.empty()
            self.stats.wave += 1
            self.stats.difficulty_multiplier = 1.0 + (self.stats.wave * 0.1)  # Increase difficulty by 10% each wave
            print(f"Starting wave {self.stats.wave} with difficulty multiplier {self.stats.difficulty_multiplier}")
            self.create_fleet()

    def check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)
            
        if collisions:
            for aliens in collisions.values():
                self.stats.score += len(aliens) * 10  # Add 10 points per alien hit
                print(f"Score: {self.stats.score}")  # Debug print

    def update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.screen.blit(self.background, (0, 0))
        self.star_field.update()
        self.star_field.draw()
        
        if self.stats.game_active:
            self.ship.blitme()
            for bullet in self.bullets.sprites():
                bullet.draw_bullet()
            for bullet in self.alien_bullets.sprites():
                bullet.draw_bullet()
            self.aliens.draw(self.screen)
            self._draw_score()
        elif self.stats.game_over:
            self._draw_game_over_elements(self.screen)
        else:
            self._draw_start_screen()
        
        pygame.display.flip()

    def _draw_score(self):
        """Draw the score and high score to the screen."""
        # Don't draw score if game is over
        if self.stats.game_over:
            return
            
        # Create a semi-transparent background for the score
        score_rect = pygame.Rect(0, 0, 200, 100)
        score_rect.right = self.screen.get_rect().right - 20
        score_rect.top = 20
        score_surface = pygame.Surface((score_rect.width, score_rect.height), pygame.SRCALPHA)
        score_surface.fill(self.settings.ui_background_color)
        self.screen.blit(score_surface, score_rect)
        
        # Set up the font
        font = pygame.font.SysFont(self.settings.ui_font, self.settings.ui_font_size)
        
        # Draw current score
        score_str = f"Score: {self.stats.score}"
        score_image = font.render(score_str, True, self.settings.ui_color)
        score_rect = score_image.get_rect()
        score_rect.right = self.screen.get_rect().right - 20
        score_rect.top = 20
        self.screen.blit(score_image, score_rect)
        
        # Draw wave number
        wave_str = f"Wave: {self.stats.wave}"
        wave_image = font.render(wave_str, True, self.settings.ui_color)
        wave_rect = wave_image.get_rect()
        wave_rect.right = self.screen.get_rect().right - 20
        wave_rect.top = 60
        self.screen.blit(wave_image, wave_rect)

    def _draw_game_over_elements(self, surface):
        """Draw game over elements on the given surface."""
        # Create a new surface for the game over screen
        game_over_surface = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
        
        # Draw background
        game_over_surface.blit(self.background, (0, 0))
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Semi-transparent black
        game_over_surface.blit(overlay, (0, 0))
        
        # Draw game over message
        font = pygame.font.SysFont(self.settings.ui_font, 64)
        game_over_text = font.render("Game Over", True, self.settings.ui_highlight_color)
        game_over_rect = game_over_text.get_rect()
        game_over_rect.centerx = game_over_surface.get_rect().centerx
        game_over_rect.top = 100
        game_over_surface.blit(game_over_text, game_over_rect)
        
        # Draw final score
        score_text = font.render(f"Final Score: {self.stats.score}", True, self.settings.ui_color)
        score_rect = score_text.get_rect()
        score_rect.centerx = game_over_surface.get_rect().centerx
        score_rect.top = 200
        game_over_surface.blit(score_text, score_rect)
        
        # Position buttons
        self.play_again_button.rect.centerx = game_over_surface.get_rect().centerx
        self.play_again_button.rect.top = 300
        self.play_again_button._prep_msg()
        
        self.high_scores_button.rect.centerx = game_over_surface.get_rect().centerx
        self.high_scores_button.rect.top = 400
        self.high_scores_button._prep_msg()
        
        self.exit_button.rect.centerx = game_over_surface.get_rect().centerx
        self.exit_button.rect.top = 500
        self.exit_button._prep_msg()
        
        # Blit the complete game over surface to the screen
        surface.blit(game_over_surface, (0, 0))
        
        # Draw buttons directly on the screen
        self.play_again_button.draw_button()
        self.high_scores_button.draw_button()
        self.exit_button.draw_button()

    def _draw_start_screen(self):
        """Draw the start screen."""
        # Draw title
        font = pygame.font.SysFont(None, 64)
        title_text = font.render("Alien Invasion", True, (255, 255, 255))
        title_rect = title_text.get_rect()
        title_rect.centerx = self.screen.get_rect().centerx
        title_rect.top = 100
        self.screen.blit(title_text, title_rect)
        
        # Position and draw play button
        self.play_button.rect.centerx = self.screen.get_rect().centerx
        self.play_button.rect.centery = self.screen.get_rect().centery - 50
        self.play_button._prep_msg()  # Re-prep the message after moving the button
        self.play_button.draw_button()
        
        # Position and draw high scores button
        self.high_scores_button.rect.centerx = self.screen.get_rect().centerx
        self.high_scores_button.rect.top = self.play_button.rect.bottom + 20
        self.high_scores_button._prep_msg()  # Re-prep the message after moving the button
        self.high_scores_button.draw_button()

    def _handle_game_over(self):
        """Handle the game over state and transition."""
        # Set game state
        self.stats.game_active = False
        self.stats.game_over = True
        self.stats.ships_left = 0
        
        # Save high score if needed
        if self.stats.score > 0:
            self.os_utils.save_high_score(self.stats.score)
            self.high_scores = self.os_utils.load_high_scores()
        
        # Clear all game elements
        self.aliens.empty()
        self.bullets.empty()
        self.alien_bullets.empty()
        
        # Clear the screen
        self.screen.fill(self.settings.bg_color)
        
        # Draw background and star field
        self.screen.blit(self.background, (0, 0))
        self.star_field.update()
        self.star_field.draw()
        
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over elements
        self._draw_game_over_elements(self.screen)
        
        # Force screen update
        pygame.display.flip()

def main():
    """Main function to run the game."""
    # Initialize pygame only once
    pygame.init()
    pygame.mixer.init()
    
    try:
        # Create game instance
        ai = AlienInvasion()
        
        # Run the game
        ai.run_game()
        
    except Exception as e:
        print(f"Error running game: {e}")
    finally:
        pygame.quit()

if __name__ == '__main__':
    main()