import pygame

class ButtonWithText:
    def __init__(self, x, y, width, height, text, 
                 font_size=24, 
                 text_color=(255, 255, 255),
                 normal_color=(70, 70, 70),
                 hover_color=(100, 100, 100),
                 pressed_color=(50, 50, 50),
                 border_radius=5,
                 on_click=None,
                 font_name=None):
     
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.text_color = text_color
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self.border_radius = border_radius
        self.on_click = on_click
        self.current_color = normal_color
        self.is_hovered = False
        self.is_pressed = False
        
        # Font setup
        try:
            if font_name:
                self.font = pygame.font.Font(font_name, font_size)
            else:
                self.font = pygame.font.SysFont(None, font_size)
        except:
            self.font = pygame.font.SysFont(None, font_size)  # Fallback
            
        # Create text surface
        self.text_surface = self.font.render(text, True, text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
    
    def handle_event(self, event):
        """Handle pygame events for the button"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            self.current_color = self.hover_color if self.is_hovered else self.normal_color
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.is_pressed = True
                self.current_color = self.pressed_color
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.is_hovered and self.on_click:
                self.on_click()
            self.is_pressed = False
            self.current_color = self.hover_color if self.is_hovered else self.normal_color
    
    def draw(self, surface):
        """Draw the button on the given surface"""
        # Draw button background
        pygame.draw.rect(
            surface, 
            self.current_color, 
            self.rect, 
            border_radius=self.border_radius
        )
        
        # Draw button text
        surface.blit(self.text_surface, self.text_rect)
        
        # Optional: Draw border when hovered
        if self.is_hovered:
            pygame.draw.rect(
                surface, 
                (150, 150, 150), 
                self.rect, 
                width=2, 
                border_radius=self.border_radius
            )
    
    def set_text(self, new_text):
        """Update the button text"""
        self.text = new_text
        self.text_surface = self.font.render(new_text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
    
    def set_position(self, x, y):
        """Update the button position"""
        self.rect.x = x
        self.rect.y = y
        self.text_rect.center = self.rect.center
    
    def set_colors(self, normal=None, hover=None, pressed=None):
        """Update button colors"""
        if normal: self.normal_color = normal
        if hover: self.hover_color = hover
        if pressed: self.pressed_color = pressed
        self.current_color = self.hover_color if self.is_hovered else self.normal_color