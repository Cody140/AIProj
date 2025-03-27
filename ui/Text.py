import pygame

class Text:
    def __init__(self, x, y, content, font_name='Arial', font_size=32, color=(0, 0, 0),bold=False, antialias=True):
        self.x = x
        self.y = y
        self.content = content
        self.font_name = font_name
        self.font_size = font_size
        self.color = color
        self.antialias = antialias
        
        # Try to load as system font first, then as file if that fails
        try:
            self.font = pygame.font.SysFont(font_name, font_size,bold)
        except:
            try:
                self.font = pygame.font.Font(font_name, font_size,bold)
            except:
                # Fallback to default font if specified font fails
                self.font = pygame.font.SysFont(None, font_size,bold)
        
        # Create the text surface
        self.surface = self.font.render(self.content, self.antialias, self.color)
        self.rect = self.surface.get_rect(topleft=(self.x, self.y))
    
    def update(self, new_content=None, new_color=None):
        """Update the text content and/or color"""
        if new_content is not None:
            self.content = new_content
        if new_color is not None:
            self.color = new_color
        
        self.surface = self.font.render(self.content, self.antialias, self.color)
        self.rect = self.surface.get_rect(topleft=(self.x, self.y))
    
    def draw(self, screen):
        """Draw the text on the given screen surface"""
        screen.blit(self.surface, self.rect)
    
    def set_position(self, x, y):
        """Set new position coordinates"""
        self.x = x
        self.y = y
        self.rect.topleft = (self.x, self.y)