import pygame.font

class Button:
    """A class to create buttons in the game."""
    
    def __init__(self, ai_game, msg):
        """Initialize button attributes."""
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings
        
        # Set the dimensions and properties of the button
        self.width, self.height = 300, 60  # Increased size for better visibility
        self.button_color = (0, 0, 0, 180)  # More opaque black
        self.text_color = ai_game.settings.ui_color
        self.highlight_color = ai_game.settings.ui_highlight_color
        self.font = pygame.font.SysFont(ai_game.settings.ui_font, 48)
        
        # Build the button's rect object and center it
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center
        
        # Store the message
        self.msg = msg
        
        # The button message needs to be prepped only once
        self._prep_msg()
        
    def _prep_msg(self):
        """Turn msg into a rendered image and center text on the button."""
        self.msg_image = self.font.render(self.msg, True, self.text_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center
        
    def draw_button(self):
        """Draw blank button and then draw message."""
        # Create a semi-transparent surface for the button
        button_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        button_surface.fill(self.button_color)
        
        # Draw the button surface
        self.screen.blit(button_surface, self.rect)
        
        # Draw a gradient-like effect around the border
        border_width = 3
        for i in range(border_width):
            alpha = int(255 * (1 - i/border_width))
            color = (*self.highlight_color[:3], alpha)
            pygame.draw.rect(self.screen, color, 
                           (self.rect.x - i, self.rect.y - i, 
                            self.rect.width + 2*i, self.rect.height + 2*i), 
                           1)
        
        # Draw the text
        self.screen.blit(self.msg_image, self.msg_image_rect)
