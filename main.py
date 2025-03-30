import pygame as pg
from ui.Buttons import Restart, BoardButton
from ui.ButtonWithText import ButtonWithText
from ui.Input import InputBox
import numpy as np
from ui.Text import Text
from ui.Radio import RadioButton,RadioButtonGroup


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
            if button.rect.collidepoint(pos) and button.active == True:
                print("button_active ")
                
                if self.selected is None:
                    self.selected = button
                    button.set_color((0,0,255))
                    button.active = False
                else:
                    new_line = (self.selected.center_coords, button.center_coords)
                    if new_line not in self.lines and new_line[::-1] not in self.lines:  # Проверка дубликатов
                        for existing_line in self.lines:
                            if self.line_intersects(existing_line, new_line):
                                # self.selected.set_color((0,255,0))
                                # self.selected.active = True
                                # self.selected = None
                                print(f"Пересечение! Очки: ")
                                self.player_1 -= 1 if self.turn else 0
                                self.player_2 -= 1 if not self.turn else 0
                                
                                #return
                        
                        if self.line_crosses_button(new_line):
                            print("Линия проходит через кнопку! Запрещено.")
                            
                            # Отменяем выбор
                            self.selected.set_color((0, 255, 0))
                            self.selected.active = True
                            self.selected = None
                            return  # Выход из метода
                        
                        button.active = False
                        self.lines.append(new_line)  # Добавляем линию только если не пересеклось
                        if self.turn:
                            button.set_color((255,0,0))
                            self.selected.set_color((255,0,0))
                        else:
                            button.set_color((157,0,255))
                            self.selected.set_color((157,0,255))
                       
                        
                        
                        
                        self.player_1 += 1 if self.turn else 0
                        self.player_2 += 1 if not self.turn else 0
                        self.turn = not self.turn
                        print(f"Очки: p1 {self.player_1} - p2 {self.player_2}")
                        
                        if not self.check_available_moves():
                            if self.player_1 > self.player_2:
                                print("Spele pabeigta Игра окончена! uzvareja 1 Победил игрок 1!")
                            elif self.player_1 < self.player_2:
                                print("Spele pabeigta Игра окончена! uzvareja 2 Победил игрок 2!")
                            else:
                                print("Spele pabeigta Игра окончена! izskirts Ничья!")
                    self.selected = None

    def update(self):
        if self.game_started is False:
            self.input_box.update()
    
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
            for line in self.lines:
                pg.draw.line(self.screen, (0, 255, 0), line[0], line[1], 2)
            pass
        
        
        pg.display.flip()

if __name__ == '__main__':
    game = Game()
    while game.running:
        game.game_loop()
    
