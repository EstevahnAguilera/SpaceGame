import sys
from time import sleep
import pygame
import os
import threading
import multiprocessing
import signal
from os_game_utils import GameOSUtils
from game_os_wrapper import GameOSWrapper
from pygame.sprite import Group

from settings import Settings #Creating an instance of settings in this class
from game_stats import GameStats #Creating and instance of gamestats in this class
from ship import Ship #Creating an instance of ship in this class
from bullet import Bullet # Creating an instance of bullet in this class
from alien import Alien # Creating an instance of alien in this class
from button import Button # Creating an instance of button in this class
from alien_bullet import AlienBullet
from star_field import StarField
from scoreboard import Scoreboard

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
        self.game_os = GameOSWrapper()  # Initialize OS wrapper

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
        self.sb = Scoreboard(self)

        # Create the ship first
        self.ship = Ship(self)
        
        # Then create other game elements
        self.bullets = Group()
        self.aliens = Group()
        self.alien_bullets = Group()
        
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
        self.high_scores = self.game_os.load_high_scores()
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
                    self._check_keydown_events(event)
                elif event.type == pygame.KEYUP:
                    self._check_keyup_events(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self._check_play_button(mouse_pos)
                    self._check_play_again_button(mouse_pos)
                    self._check_high_scores_button(mouse_pos)
                    self._check_back_button(mouse_pos)
                    self._check_exit_button(mouse_pos)

            # Get game state from C
            game_state = self.game_os.get_game_state()
            
            # Update ship position based on C state
            self.ship.rect.x = game_state['player_x']
            self.ship.rect.y = game_state['player_y']
            
            # Update game stats
            self.stats.score = game_state['score']
            self.stats.game_active = game_state['game_active']
            self.stats.game_over = game_state['game_over']
            self.stats.ships_left = game_state['player_health']
            
            # Check if all aliens are destroyed
            if self.stats.game_active:
                alien_positions = self.game_os.get_alien_positions()
                all_aliens_destroyed = True
                for x, y, active in alien_positions:
                    if active:
                        all_aliens_destroyed = False
                        break

                if all_aliens_destroyed:
                    # Advance to next level
                    self.game_os.advance_level()
                    self.stats.level = self.game_os.get_level()
                    self.sb.prep_level()
                    
                    # Clear existing bullets
                    self.bullets.empty()
                    self.alien_bullets.empty()
                    
                    # Pause briefly to show level transition
                    sleep(0.5)
            
            # Update screen
            self.update_screen()
            self.clock.tick(60)

        self.cleanup()

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.stats.game_over:
                    self._check_play_again_button(mouse_pos)
                    self._check_high_scores_button(mouse_pos)
                elif not self.stats.game_active:
                    self._check_play_button(mouse_pos)
                    self._check_high_scores_button(mouse_pos)

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.game_os.update_player_movement(0, 1, 0, 0)
        elif event.key == pygame.K_LEFT:
            self.game_os.update_player_movement(1, 0, 0, 0)
        elif event.key == pygame.K_UP:
            self.game_os.update_player_movement(0, 0, 1, 0)
        elif event.key == pygame.K_DOWN:
            self.game_os.update_player_movement(0, 0, 0, 1)
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self.game_os.fire_player_bullet()
    
    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.game_os.update_player_movement(0, 0, 0, 0)
        elif event.key == pygame.K_LEFT:
            self.game_os.update_player_movement(0, 0, 0, 0)
        elif event.key == pygame.K_UP:
            self.game_os.update_player_movement(0, 0, 0, 0)
        elif event.key == pygame.K_DOWN:
            self.game_os.update_player_movement(0, 0, 0, 0)

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            
            # Reset game state in C
            self.game_os.cleanup()
            self.game_os = GameOSWrapper()
            self.game_os.start_game()
            
            pygame.mouse.set_visible(False)

    def _check_play_again_button(self, mouse_pos):
        """Start a new game when the player clicks Play Again."""
        button_clicked = self.play_again_button.rect.collidepoint(mouse_pos)
        if button_clicked and self.stats.game_over:
            self.game_os.start_game()

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
        """Create the fleet of aliens using C game logic"""
        # The fleet is now created in C's start_game function
        pass

    def create_alien(self, x_position, y_position):
        """This method is no longer needed as aliens are managed by C"""
        pass

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
                self.game_os.save_high_score(self.stats.score)
                self.high_scores = self.game_os.load_high_scores()
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
                self.game_os.save_high_score(self.stats.score)
                self.high_scores = self.game_os.load_high_scores()
            
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
                # Notify C code about the collision
                for alien in aliens:
                    self.game_os.handle_alien_hit(alien.rect.x, alien.rect.y)

        # Check for alien bullet-ship collisions
        if pygame.sprite.spritecollideany(self.ship, self.alien_bullets):
            print("GAME OVER - Ship hit by alien bullet!")
            self.stats.game_active = False
            self.stats.game_over = True
            self.stats.ships_left = 0
            
            # Save high score
            if self.stats.score > 0:
                print(f"Final score: {self.stats.score}")
                self.game_os.save_high_score(self.stats.score)
                self.high_scores = self.game_os.load_high_scores()
            
            # Clear everything
            self.aliens.empty()
            self.bullets.empty()
            self.alien_bullets.empty()
            
            # Force game over screen
            self.screen.blit(self.background, (0, 0))
            self._draw_game_over_elements(self.screen)
            pygame.display.flip()
            pygame.time.wait(1000)  # Pause for a second to show game over

    def update_alien_bullets(self):
        """Update the positions of all alien bullets and handle collisions."""
        # Update bullet positions
        self.alien_bullets.update()
        
        # Remove bullets that have left the screen
        for bullet in self.alien_bullets.copy():
            if bullet.rect.top >= self.settings.screen_height:
                self.alien_bullets.remove(bullet)
        
        # Check for bullet-ship collisions
        if pygame.sprite.spritecollideany(self.ship, self.alien_bullets):
            self.ship_hit()

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
            # Get positions from C
            alien_positions = self.game_os.get_alien_positions()
            bullet_positions = self.game_os.get_bullet_positions()
            
            # Draw ship
            self.ship.blitme()
            
            # Draw aliens
            for x, y, active in alien_positions:
                if active:  # Only draw active aliens
                    alien = Alien(self)
                    alien.rect.x = x
                    alien.rect.y = y
                    self.screen.blit(alien.image, alien.rect)
            
            # Draw bullets
            for x, y, is_player, active in bullet_positions:
                if active:  # Only draw active bullets
                    if is_player:
                        bullet = Bullet(self)
                    else:
                        # Create a temporary alien for the bullet
                        temp_alien = Alien(self)
                        temp_alien.rect.x = x
                        temp_alien.rect.y = y
                        bullet = AlienBullet(self, temp_alien)
                    bullet.rect.x = x
                    bullet.rect.y = y
                    self.screen.blit(bullet.image, bullet.rect)
            
            # Draw score and health
            self._draw_score()
            self._draw_health_bar()
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
        score_rect.centerx = self.screen.get_rect().centerx
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
        score_rect.centerx = self.screen.get_rect().centerx
        score_rect.top = 20
        self.screen.blit(score_image, score_rect)
        
        # Draw level number
        level_str = f"Level: {self.stats.level}"
        level_image = font.render(level_str, True, self.settings.ui_color)
        level_rect = level_image.get_rect()
        level_rect.centerx = self.screen.get_rect().centerx
        level_rect.top = 60
        self.screen.blit(level_image, level_rect)

    def _draw_health_bar(self):
        """Draw the health bar at the top right of the screen."""
        if self.stats.game_over:
            return

        # Get current health from game state
        game_state = self.game_os.get_game_state()
        current_health = game_state['player_health']
        max_health = 100  # Maximum health value

        # Health bar dimensions and position
        bar_width = 150  # Made more compact
        bar_height = 15  # Made more compact
        bar_x = self.settings.screen_width - bar_width - 20  # 20 pixels from right edge
        bar_y = 20  # 20 pixels from top

        # Create a semi-transparent background for the health bar
        health_rect = pygame.Rect(bar_x - 5, bar_y - 5, bar_width + 10, bar_height + 10)
        health_surface = pygame.Surface((health_rect.width, health_rect.height), pygame.SRCALPHA)
        health_surface.fill(self.settings.ui_background_color)
        self.screen.blit(health_surface, health_rect)

        # Draw background (empty health bar)
        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # Calculate current health width
        health_width = (current_health / max_health) * bar_width
        
        # Draw health bar with color based on health percentage
        health_percentage = current_health / max_health
        if health_percentage > 0.6:
            color = (0, 255, 0)  # Green
        elif health_percentage > 0.3:
            color = (255, 255, 0)  # Yellow
        else:
            color = (255, 0, 0)  # Red
            
        pygame.draw.rect(self.screen, color, (bar_x, bar_y, health_width, bar_height))

        # Draw health text
        font = pygame.font.SysFont(self.settings.ui_font, self.settings.ui_font_size)
        health_text = f"HP: {current_health}/{max_health}"
        text_image = font.render(health_text, True, self.settings.ui_color)
        text_rect = text_image.get_rect()
        text_rect.right = bar_x + bar_width
        text_rect.top = bar_y + bar_height + 5
        self.screen.blit(text_image, text_rect)

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
            self.game_os.save_high_score(self.stats.score)
            self.high_scores = self.game_os.load_high_scores()
        
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

    def update_ship_position(self):
        """Update ship position using OS wrapper"""
        self.game_os.update_player_position(self.ship.rect.x, self.ship.rect.y)

    def update_score(self, points):
        """Update score using OS wrapper"""
        self.game_os.update_score(points)
        self.stats.score = self.game_os.get_score()

    def cleanup(self):
        """Cleanup resources"""
        self.game_os.cleanup()
        pygame.quit()

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