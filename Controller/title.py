from Controller.state import State
from Controller.game_scene import Game_Scene

class Title(State):
    def __init__(self, game):
        State.__init__(self, game)
        

    def update(self, actions, ext_data):
        if ext_data["dot_count"] is not None:
            self.game.STARTED = True
            new_state = Game_Scene(self.game)
            new_state.enter_state()
        self.game.reset_keys()

    def render(self, display):
        display.fill((255,255,255))
        #self.game.draw_text(display, "Game States Demo", (0,0,0), 400, 450 )