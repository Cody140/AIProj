from typing import Callable
import pygame as pg


class Restart(pg.sprite.Sprite):
    def __init__(self, image: pg.Surface, coords: tuple[int, int], on_click: Callable):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect(topleft=coords)
        self.on_click = on_click
        self.active = True


    def detect_click(self, click: pg.event.Event):
        """Determine if a mouse click was inside the button and, if it was,
        fire the button's on_click function.

        :param click: a pygame.MOUSEBUTTONDOWN event
        :type click: pygame.event.Evenet
        """

        if self.rect.collidepoint(click.pos):
            self.on_click()


class BoardButton(pg.sprite.Sprite):
    def __init__(self, coords: tuple[int, int], on_click: Callable, color=(0,255,0)):
        pg.sprite.Sprite.__init__(self)
        self.radius = 20  # Радиус круга
        self.coords = coords
        self.center_coords = (coords[0] + self.radius, coords[1] + self.radius)
        
        self.color = color  # Текущий цвет кнопки
        self.image = pg.Surface((self.radius * 2, self.radius * 2), pg.SRCALPHA)
        self.rect = self.image.get_rect(topleft=coords)
        
        self.on_click = on_click
        self.active = True

        self.draw_button()  # Рисуем кнопку

    def draw_button(self):
        """Перерисовывает кнопку с текущим цветом"""
        self.image.fill((0, 0, 0, 0))  # Очистка изображения (прозрачность)
        pg.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)

    def set_color(self, new_color):
        """Меняет цвет и перерисовывает кнопку"""
        self.color = new_color
        self.draw_button()

    def detect_click(self, click: pg.event.Event):
        """Determine if a mouse click was inside the button and, if it was,
        fire the button's on_click function.

        :param click: a pygame.MOUSEBUTTONDOWN event
        :type click: pygame.event.Evenet
        """

        if self.rect.collidepoint(click.pos):
            self.on_click()


# class Start(pg.sprite.Sprite):
#     def __init__(self, image: pg.Surface, coords: tuple[int, int], on_click: Callable):
#         pg.sprite.Sprite.__init__(self)
#         self.image = image
#         self.rect = image.get_rect(topleft=coords)
#         self.on_click = on_click

#     def detect_click(self, click: pg.event.Event):
#         """Determine if a mouse click was inside the button and, if it was,
#         fire the button's on_click function.

#         :param click: a pygame.MOUSEBUTTONDOWN event
#         :type click: pygame.event.Evenet
#         """

#         if self.rect.collidepoint(click.pos):
#             self.on_click()