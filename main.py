import pygame as pg
from ui.Buttons import Restart, BoardButton
from ui.ButtonWithText import ButtonWithText
from ui.Input import InputBox
import numpy as np
from ui.Text import Text
from ui.Radio import RadioButton,RadioButtonGroup
from gamestate import GameState, minimax_decision


class Game: 
    def __init__(self):
        pg.init()
        self.clock = pg.time.Clock()
        self.running = True
        self.screen = pg.display.set_mode((840, 680))
        
        self.input_box = InputBox(100, 508, 140, 32)
        
        self.game_table = None
        
        self.tittle = Text(250, 50, "1.Praktiskais darbs", "Arial", 48, (255, 255, 255))

        self.radioButtons= RadioButtonGroup()
        """Izvēlas kurš uzsāk spēli"""
        self.firstPlayer = "human"
        def set_firstPlayer():
            if self.radioButtons.get_checked("firstPlayer") != None:
                self.firstPlayer = self.radioButtons.get_checked("firstPlayer").get_value()

        self.human = RadioButton(100, 170, "firstPlayer","human", "Cilvēks",24,on_click=set_firstPlayer, checked=True)
        self.ai = RadioButton(200, 170, "firstPlayer","ai", "Mākslīgais intelekts",24,on_click=set_firstPlayer)
        self.radioButtons.add(self.human)
        self.radioButtons.add(self.ai)
        
        """Izvēlas algoritmu"""
        self.algorithm = "minimax"
        def set_algorithm():
            if self.radioButtons.get_checked("algorithm") != None:
                self.algorithm = self.radioButtons.get_checked("algorithm").get_value()

        self.minimax = RadioButton(100, 245, "algorithm","minimax", "Minimaks",24,on_click=set_algorithm, checked=True)
        self.alpha_beta = RadioButton(215, 245, "algorithm","alpha_beta", "Alfa-beta",24,on_click=set_algorithm)
        self.radioButtons.add(self.minimax)
        self.radioButtons.add(self.alpha_beta)

        def startGame():
            print("hi")
            result = self.input_box.result = int(self.input_box.text)
            if result >= 15 and result <= 25:
                        
                self.input_box.is_valid = True
                self.game_started = True
                self.game_ended = False
                self.dots_count = self.input_box.result
                self.load_board(self.dots_count)

        self.startButton = ButtonWithText(
        320, 500, 200, 50, 
        "Sākt spēli!", 
        on_click=startGame,
        normal_color=(50, 150, 250),
        hover_color=(80, 180, 255),
        pressed_color=(30, 120, 220)
        )
        

        button_image = pg.Surface((200, 50))
        button_image.fill((50, 150, 250))
        
        self.buttons = pg.sprite.Group()

        self.board = []
        self.board_buttons = pg.sprite.Group()

        self.restart_button = Restart(button_image, (100, 100), self.restart)
        
        self.buttons.add(self.restart_button)
        
        self.game_ended = False
       
        self.game_started = False        
        self.dots_count = None
        
        self.selected = None
        self.lines = []
        
        self.player_1 = 0
        self.player_2 = 0
        self.turn = True

        
    
    
        
    def line_intersects(self,line1, line2):
        """Проверяет пересечение двух линий."""
        (x1, y1), (x2, y2) = line1
        (x3, y3), (x4, y4) = line2

        def ccw(a, b, c):
            return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

        return ccw((x1, y1), (x3, y3), (x4, y4)) != ccw((x2, y2), (x3, y3), (x4, y4)) and \
            ccw((x1, y1), (x2, y2), (x3, y3)) != ccw((x1, y1), (x2, y2), (x4, y4))
        
    #перезапустить игру
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
        
    # игровой цикл
    def game_loop(self):
        while self.running:
            self.get_events()
            self.update()
            self.draw()

    # получаем события от пользователя (мышка и  клавиатура)
    def get_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            
            # если игра не началась, то обрабатываем события для ввода количества точек
            if self.game_started is False:
                self.input_box.handle_event(event)
                self.radioButtons.handle_event(event)
                self.startButton.handle_event(event)
                # если пользователь ввел правильное число точек, то начинаем игру    
            
            else:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    for button in self.buttons:
                        button.detect_click(event)
                    if self.game_ended is False:
                        #получение данных о нажатии на кнопку в игровом поле
                        for board_but in self.board_buttons:
                            board_but.detect_click(event)    
                        
                pass

    # загрузка игрового поля
    def load_board(self, count):
        print("Speli uzsak-"+self.firstPlayer)
        print("Speles algoritms-"+self.algorithm)
        n = int(count ** 0.5)  # Приблизительный размер стороны
        m = (count + n - 1) // n
        self.board = np.full((n, m), -1, dtype=int)  # Доска заполнена -1
        
        for i in range(count):
            x, y = divmod(i, m)
            self.board[x, y] = 0
    
        for i in range(n):
            for j in range(m):
                if self.board[i, j] == -1:
                    continue
                button = BoardButton(coords=(100 + i * 100, 200 + j *100),on_click= self.update_buttons)
                self.board_buttons.add(button)
                
    def check_available_moves(self):
        """Проверяет, можно ли провести хотя бы одну новую линию"""
        active_buttons = [btn for btn in self.board_buttons if btn.active]

        for i, btn1 in enumerate(active_buttons):
            for btn2 in active_buttons[i + 1:]:  # Перебираем пары кнопок
                new_line = (btn1.center_coords, btn2.center_coords)

                # Проверяем, нет ли такой линии уже
                if new_line in self.lines or new_line[::-1] in self.lines:
                    continue

                # Проверяем, не проходит ли новая линия через другие кнопки
                if self.line_crosses_button(new_line):
                    continue  # Запрещаем такие линии

                # Если хотя бы одна линия возможна, возвращаем True
                return True
        self.game_ended = True  # Если не нашли ни одной линии, игра окончена
        return False

    def line_crosses_button(self, line):
        """Проверяет, проходит ли линия через другие кнопки (кроме концов)"""
        (x1, y1), (x2, y2) = line

        for button in self.board_buttons:
            if button.center_coords in line:  # Пропускаем начальную и конечную кнопку
                continue

            # Проверяем, находится ли центр кнопки внутри отрезка
            bx, by = button.center_coords
            if self.point_on_segment((x1, y1), (x2, y2), (bx, by)):
                return True  # Линия проходит через кнопку

        return False

    def point_on_segment(self, p1, p2, p):
        """Проверяет, лежит ли точка p на отрезке p1-p2"""
        (x1, y1), (x2, y2) = p1, p2
        (px, py) = p

        # Проверка, лежит ли точка p на одной прямой с p1 и p2
        cross_product = (py - y1) * (x2 - x1) - (px - x1) * (y2 - y1)
        if abs(cross_product) > 1e-6:  # Числовая погрешность
            return False

        # Проверка, лежит ли точка p между p1 и p2 по координатам X и Y
        if min(x1, x2) <= px <= max(x1, x2) and min(y1, y2) <= py <= max(y1, y2):
            return True

        return False
                
    
    def update_buttons(self):
        pos = pg.mouse.get_pos()
        for button in self.board_buttons:
            if button.rect.collidepoint(pos) and button.active:
                # If no dot has been selected yet, select this dot.
                if self.selected is None:
                    self.selected = button
                    button.set_color((0, 0, 255))  # Blue indicates selection.
                    button.active = False
                    return  # Wait for the next click.
                else:
                    # Second dot is selected; create the connection.
                    new_line = (self.selected.center_coords, button.center_coords)
                    # Ensure we don't duplicate an existing connection.
                    if new_line in self.lines or new_line[::-1] in self.lines:
                        self.selected = None
                        return

                    # Check if the move is illegal.
                    illegal = False
                    # Check for crossing any existing line.
                    for existing_line in self.lines:
                        if self.line_intersects(existing_line, new_line):
                            illegal = True
                            break
                    # Check if the new line passes through any other dot.
                    if not illegal and self.line_crosses_button(new_line):
                        illegal = True

                    # If illegal, apply a penalty to the mover.
                    if illegal:
                        print("Illegal move detected: penalty applied, but connection will be drawn.")
                        if self.turn:
                            self.player_1 += 1
                        else:
                            self.player_2 += 1

                    # Draw the connection regardless of legality.
                    button.active = False
                    self.lines.append(new_line)
                    if self.firstPlayer== "human":
                        button.set_color((255, 0, 0))
                        self.selected.set_color((255, 0, 0))
                    elif self.firstPlayer== "ai":
                        button.set_color((157, 0, 255))
                        self.selected.set_color((157, 0, 255))
                    # Switch the turn.
                    self.turn = not self.turn
                    # Clear the selection.
                    self.selected = None
                    return


    def apply_ai_move(self, p1, p2):
        """
        Mark the two buttons used by the AI, set their color,
        and update self.lines.
        """
        # Find the two BoardButton objects
        button1 = None
        button2 = None
        for btn in self.board_buttons:
            if btn.center_coords == p1:
                button1 = btn
            elif btn.center_coords == p2:
                button2 = btn

        # Mark them as inactive, set AI color
        if self.firstPlayer == "ai": 
            if button1:
                button1.active = False
                button1.set_color((255, 0, 0))  # AI color
            if button2:
                button2.active = False
                button2.set_color((255, 0, 0))
        elif self.firstPlayer =="human":
            if button1:
                button1.active = False
                button1.set_color((157, 0, 255))  # AI color
            if button2:
                button2.active = False
                button2.set_color((157, 0, 255))

        # Add the line
        self.lines.append((p1, p2))

        # Reset any user selection
        self.selected = None

    def update(self):
        if not self.game_started:
            self.input_box.update()
        elif not self.game_ended:
            # ...
            if (self.firstPlayer == "ai" and self.turn) or (self.firstPlayer == "human" and not self.turn):
                # Build state and run minimax
                state = GameState(
                    board=[btn.center_coords for btn in self.board_buttons],
                    lines=self.lines,
                    current_player=self.turn,
                    score1=self.player_1,
                    score2=self.player_2
                )
                depth = 2
                best_move, best_value = minimax_decision(state, depth, True)
                if best_move is not None:
                    p1, p2 = best_move
                    new_line = (p1, p2)

                    # 1) Check crossing
                    crossing = False
                    for existing_line in self.lines:
                        if self.line_intersects(existing_line, new_line):
                            crossing = True
                            break

                    if crossing:
                        print("AI move crosses an existing line! Penalty to opponent.")
                        if self.turn:   # AI is player1
                            self.player_2 += 1
                        else:           # AI is player2
                            self.player_1 += 1
                        # No move is added, just switch turn
                        self.turn = not self.turn

                    else:
                        # 2) Check if it goes through another button
                        if self.line_crosses_button(new_line):
                            print("AI move goes through a button, illegal. Penalty to opponent.")
                            if self.turn:
                                self.player_2 += 1
                            else:
                                self.player_1 += 1
                            self.turn = not self.turn
                        else:
                            # 3) Legal move: apply AI move, but do NOT award a point
                            self.apply_ai_move(p1, p2)
                            # Just switch turn, no points for normal line
                            self.turn = not self.turn


            
    
    def draw(self):

        self.screen.fill((30, 30, 30))
        
        if self.game_started is False:
            self.screen.fill((30, 30, 30))
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
            
            Text(145, 113, "Sākt no jauna", "Arial", 20, (255, 255, 255),True).draw(self.screen)
            pg.draw.rect(self.screen, (255,0,0), pg.Rect(370, 50, 40, 40))
            pg.draw.rect(self.screen, (157,0,255), pg.Rect(370, 100, 40, 40))
            Text(420, 60, "1. Spēlētājs:", "Arial", 20, (255, 255, 255)).draw(self.screen)
            Text(540, 60, str(self.player_1), "Arial", 20, (255, 255, 255)).draw(self.screen)
            Text(420, 110, "2. Spēlētājs:", "Arial", 20, (255, 255, 255)).draw(self.screen)
            Text(540, 110, str(self.player_2), "Arial", 20, (255, 255, 255)).draw(self.screen)
            


            if not self.check_available_moves():
                            if self.player_1 > self.player_2:
                                Text(390, 160, "Spēle pabeigta! Uzvarēja 2. spēlētājs!", "Arial", 20, (255, 255, 255)).draw(self.screen)
                                
                            elif self.player_1 < self.player_2:
                                Text(390, 160, "Spēle pabeigta! Uzvarēja 1. spēlētājs!", "Arial", 20, (255, 255, 255)).draw(self.screen)
                            else:
                                Text(390, 160, "Spēle pabeigta! Izšķirts!", "Arial", 20, (255, 255, 255)).draw(self.screen)

            
            for line in self.lines:
                pg.draw.line(self.screen, (0, 255, 0), line[0], line[1], 2)
            pass
            
        
        pg.display.flip()

if __name__ == '__main__':
    game = Game()
    while game.running:
        game.game_loop()
    
