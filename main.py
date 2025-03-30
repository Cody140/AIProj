import pygame as pg
from ui.Buttons import Restart, BoardButton
from ui.ButtonWithText import ButtonWithText
from ui.Input import InputBox
import numpy as np
from ui.Text import Text
from ui.Radio import RadioButton, RadioButtonGroup


class Game:
    def __init__(self):
        pg.init()
        self.clock = pg.time.Clock()
        self.running = True
        self.screen = pg.display.set_mode((840, 680))
        self.input_box = InputBox(100, 508, 140, 32)

        self.tittle = Text(250, 50, "1.Praktiskais darbs", "Arial", 48, (255, 255, 255))
        self.radioButtons = RadioButtonGroup()

        self.firstPlayer = "human"
        self.algorithm = "minimax"
        self.init_radio_buttons()

        self.startButton = ButtonWithText(
            320, 500, 200, 50,
            "Sākt spēli!",
            on_click=self.start_game,
            normal_color=(50, 150, 250),
            hover_color=(80, 180, 255),
            pressed_color=(30, 120, 220)
        )

        button_image = pg.Surface((200, 50))
        button_image.fill((50, 150, 250))

        self.buttons = pg.sprite.Group()
        self.board_buttons = pg.sprite.Group()
        self.restart_button = Restart(button_image, (100, 100), self.restart)
        self.buttons.add(self.restart_button)

        self.board = []
        self.lines = []
        self.selected = None
        self.player_1 = 0
        self.player_2 = 0
        self.turn = True
        self.game_started = False
        self.game_ended = False
        self.dots_count = None

    def init_radio_buttons(self):
        self.human = RadioButton(100, 170, "firstPlayer", "human", "Cilvēks", 24, on_click=self.set_first_player, checked=True)
        self.ai = RadioButton(200, 170, "firstPlayer", "ai", "Mākslīgais intelekts", 24, on_click=self.set_first_player)
        self.minimax = RadioButton(100, 245, "algorithm", "minimax", "Minimaks", 24, on_click=self.set_algorithm, checked=True)
        self.alpha_beta = RadioButton(215, 245, "algorithm", "alpha_beta", "Alfa-beta", 24, on_click=self.set_algorithm)

        for rb in [self.human, self.ai, self.minimax, self.alpha_beta]:
            self.radioButtons.add(rb)

    def set_first_player(self):
        checked = self.radioButtons.get_checked("firstPlayer")
        if checked:
            self.firstPlayer = checked.get_value()

    def set_algorithm(self):
        checked = self.radioButtons.get_checked("algorithm")
        if checked:
            self.algorithm = checked.get_value()

    def start_game(self):
        try:
            result = int(self.input_box.text)
        except ValueError:
            return

        if 15 <= result <= 25:
            self.input_box.is_valid = True
            self.game_started = True
            self.game_ended = False
            self.dots_count = result
            self.load_board(self.dots_count)

    def restart(self):
        self.game_started = False
        self.dots_count = None
        self.input_box.is_valid = False
        self.input_box.result = None
        self.input_box.text = ""
        self.input_box.txt_surface = self.input_box.FONT.render("", True, self.input_box.color)
        self.board_buttons.empty()
        self.lines = []
        self.selected = None
        self.player_1 = 0
        self.player_2 = 0
        self.turn = True

    def game_loop(self):
        while self.running:
            self.get_events()
            self.update()
            self.draw()

    def get_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            if not self.game_started:
                self.input_box.handle_event(event)
                self.radioButtons.handle_event(event)
                self.startButton.handle_event(event)
            else:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    for button in self.buttons:
                        button.detect_click(event)
                    if not self.game_ended:
                        for board_but in self.board_buttons:
                            board_but.detect_click(event)

    def load_board(self, count):
        print("Speli uzsāk:", self.firstPlayer)
        print("Izvēlētais algoritms:", self.algorithm)

        n = int(count ** 0.5)
        m = (count + n - 1) // n
        self.board = np.full((n, m), -1, dtype=int)

        for i in range(count):
            x, y = divmod(i, m)
            self.board[x, y] = 0

        for i in range(n):
            for j in range(m):
                if self.board[i, j] == -1:
                    continue
                button = BoardButton((100 + i * 100, 200 + j * 100), on_click=self.update_buttons)
                self.board_buttons.add(button)

    def update_buttons(self):
        pos = pg.mouse.get_pos()
        for button in self.board_buttons:
            if button.rect.collidepoint(pos) and button.active:
                if self.selected is None:
                    self.selected = button
                    button.set_color((0, 0, 255))
                    button.active = False
                else:
                    new_line = (self.selected.center_coords, button.center_coords)
                    if new_line in self.lines or new_line[::-1] in self.lines:
                        self.selected = None
                        return

                    if self.line_crosses_button(new_line):
                        print("Līnija nedrīkst šķērsot citu pogu.")
                        self.selected.set_color((0, 255, 0))
                        self.selected.active = True
                        self.selected = None
                        return

                    button.active = False
                    self.lines.append(new_line)

                    color = (255, 0, 0) if self.turn else (157, 0, 255)
                    button.set_color(color)
                    self.selected.set_color(color)

                    if self.turn:
                        self.player_1 += 1
                    else:
                        self.player_2 += 1

                    self.turn = not self.turn
                    self.selected = None
                    print(f"Rezultāts: p1 = {self.player_1}, p2 = {self.player_2}")

                    if not self.check_available_moves():
                        self.game_ended = True
                        if self.player_1 > self.player_2:
                            print("Uzvarētājs: Spēlētājs 1!")
                        elif self.player_2 > self.player_1:
                            print("Uzvarētājs: Spēlētājs 2!")
                        else:
                            print("Neizšķirts!")

    def check_available_moves(self):
        active_buttons = [btn for btn in self.board_buttons if btn.active]
        for i, btn1 in enumerate(active_buttons):
            for btn2 in active_buttons[i + 1:]:
                new_line = (btn1.center_coords, btn2.center_coords)
                if new_line in self.lines or new_line[::-1] in self.lines:
                    continue
                if self.line_crosses_button(new_line):
                    continue
                return True
        return False

    def line_crosses_button(self, line):
        (x1, y1), (x2, y2) = line
        for button in self.board_buttons:
            if button.center_coords in line:
                continue
            bx, by = button.center_coords
            if self.point_on_segment((x1, y1), (x2, y2), (bx, by)):
                return True
        return False

    def point_on_segment(self, p1, p2, p):
        (x1, y1), (x2, y2) = p1, p2
        (px, py) = p
        cross = (py - y1) * (x2 - x1) - (px - x1) * (y2 - y1)
        if abs(cross) > 1e-6:
            return False
        return min(x1, x2) <= px <= max(x1, x2) and min(y1, y2) <= py <= max(y1, y2)

    def update(self):
        if not self.game_started:
            self.input_box.update()

    def draw(self):
        self.screen.fill((30, 30, 30))
        if not self.game_started:
            self.tittle.draw(self.screen)
            Text(100, 120, "Kurš uzsāk spēli?", "Arial", 24, (255, 255, 255)).draw(self.screen)
            self.radioButtons.draw(self.screen)
            Text(100, 205, "Kurš algoritms tiks pielietots?", "Arial", 24, (255, 255, 255)).draw(self.screen)
            self.input_box.draw(self.screen)
            self.startButton.draw(self.screen)
            Text(120, 550, "Sākot no 15 līdz 25", "Arial", 13, (255, 255, 255)).draw(self.screen)
        else:
            self.buttons.draw(self.screen)
            self.board_buttons.draw(self.screen)
            Text(145, 113, "Sākt no jauna", "Arial", 20, (255, 255, 255), True).draw(self.screen)
            pg.draw.rect(self.screen, (255, 0, 0), pg.Rect(370, 50, 40, 40))
            pg.draw.rect(self.screen, (157, 0, 255), pg.Rect(370, 100, 40, 40))
            Text(420, 60, "1. Spēlētājs:", "Arial", 20, (255, 255, 255)).draw(self.screen)
            Text(540, 60, str(self.player_1), "Arial", 20, (255, 255, 255)).draw(self.screen)
            Text(420, 110, "2. Spēlētājs:", "Arial", 20, (255, 255, 255)).draw(self.screen)
            Text(540, 110, str(self.player_2), "Arial", 20, (255, 255, 255)).draw(self.screen)
            for line in self.lines:
                pg.draw.line(self.screen, (0, 255, 0), line[0], line[1], 2)

        pg.display.flip()


if __name__ == '__main__':
    game = Game()
    game.game_loop()
