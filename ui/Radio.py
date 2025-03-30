from typing import Callable
from typing import Callable
import pygame as pg

class RadioButton:
    def __init__(self, x, y, group,value, text="", font_size=24,on_click=Callable, checked=False, 
                 color=(255, 255, 255), active_color=(0, 100, 200)):
  
        self.x = x
        self.y = y
        self.group = group
        self.value = value
        self.text = text
        self.checked = checked
        self.color = color
        self.active_color = active_color
        self.radius = 10  # Outer circle radius
        self.inner_radius = 5  # Inner circle radius
        self.spacing = 5  # Space between circle and text
        self.on_click = on_click
        # Text rendering
        self.font = pg.font.SysFont(None, font_size)
        self.text_surface = self.font.render(text, True, color)
        self.text_rect = self.text_surface.get_rect()
        
        # Calculate total width and height
        self.width = self.radius * 2 + self.spacing + self.text_rect.width
        self.height = max(self.radius * 2, self.text_rect.height)
        
        # Position elements
        self.circle_pos = (x + self.radius, y + self.height // 2)
        self.text_pos = (x + self.radius * 2 + self.spacing, y + (self.height - self.text_rect.height) // 2)
        
        # Create hitbox rectangle
        self.hitbox = pg.Rect(x, y, self.width, self.height)
    
    def draw(self, screen):
        """Draw the radio button on the given surface"""
        # Draw outer circle
        pg.draw.circle(
            screen, 
            self.active_color if self.checked else self.color, 
            self.circle_pos, 
            self.radius, 
            2  # Line thickness
        )
        
        # Draw inner circle if checked
        if self.checked:
            pg.draw.circle(
                screen, 
                self.active_color, 
                self.circle_pos, 
                self.inner_radius
            )
        
        # Draw text
        screen.blit(self.text_surface, self.text_pos)
    
    def handle_event(self, event):
        """Handle pygame events (returns True if state changed)"""
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.hitbox.collidepoint(event.pos):
                if not self.checked:
                    self.checked = True
                    return True
        return False
    
    def is_checked(self):
        """Return the current checked state"""
        return self.checked
    
    def get_value(self):
        return self.value

    def set_checked(self, checked):
        """Manually set the checked state"""
        self.checked = checked
        self.on_click()
    
    def get_group(self):
        """Get the radio button group name"""
        return self.group

class RadioButtonGroup:
    def __init__(self):
        """Manage a group of radio buttons for mutual exclusion"""
        self.buttons = []
    
    def add(self, button):
        """Add a radio button to the group"""
        self.buttons.append(button)
    
    def handle_event(self, event):
        """Handle events for all buttons in the group"""
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.buttons:
                if button.hitbox.collidepoint(event.pos):
                    # Uncheck all buttons in the same group
                    for b in self.buttons:
                        if b.get_group() == button.get_group():
                            b.set_checked(False)
                    # Check the clicked button
                    button.set_checked(True)
                    return True
        return False
    
    def get_checked(self, group):
        """Get the currently checked button in a group"""
        for button in self.buttons:
            if button.get_group() == group and button.is_checked():
                return button
        return None
    
    def draw(self, screen):
        """Draw all buttons in the group"""
        for button in self.buttons:
            button.draw(screen)