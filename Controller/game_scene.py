from Controller.state import State

class Game_Scene(State):
    def __init__(self, game):
        State.__init__(self, game)

    def update(self, actions):
        if actions["restart"]:
            self.game.STARTED = False
            self.game.exit_state()
        self.game.reset_keys()

    def render(self, display):
        display.fill((255,255,255))
        self.game.draw_text(display, "Game States Demo", (0,0,0), 400, 450 )