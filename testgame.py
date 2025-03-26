import pygame

pygame.init()
WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Кнопки (координаты центров)
buttons = [(x * 100 + 50, y * 100 + 50) for x in range(5) for y in range(5)]



print(buttons)
# Линии между кнопками
lines = []
player_score = 10

def line_intersects(line1, line2):
    """Проверяет пересечение двух линий."""
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2

    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

    return ccw((x1, y1), (x3, y3), (x4, y4)) != ccw((x2, y2), (x3, y3), (x4, y4)) and \
           ccw((x1, y1), (x2, y2), (x3, y3)) != ccw((x1, y1), (x2, y2), (x4, y4))

running = True
selected = None

while running:
    screen.fill((30, 30, 30))

    # Рисуем кнопки
    for button in buttons:
        pygame.draw.circle(screen, (200, 200, 200), button, 10)

    # Рисуем линии
    for line in lines:
        pygame.draw.line(screen, (0, 255, 0), line[0], line[1], 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for button in buttons:
                if (button[0] - pos[0]) ** 2 + (button[1] - pos[1]) ** 2 <= 100:  # Проверяем клик по кнопке
                    if selected is None:
                        selected = button
                    else:
                        new_line = (selected, button)
                        if new_line not in lines and new_line[::-1] not in lines:  # Проверка дубликатов
                            for existing_line in lines:
                                if line_intersects(existing_line, new_line):
                                    player_score -= 1
                                    print(f"Пересечение! Очки: {player_score}")
                                    break
                            else:
                                lines.append(new_line)  # Добавляем линию только если не пересеклось
                        selected = None  # Сбрасываем выделение

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
