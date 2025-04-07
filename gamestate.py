import copy

class GameState:
    def __init__(self, board, lines, current_player, score1, score2):
        self.board = board            # list of all dot positions (x,y)
        self.lines = lines.copy()     # list of existing lines [(p1, p2), ...]
        self.current_player = current_player
        self.score1 = score1
        self.score2 = score2

    @staticmethod
    def line_intersects(line1, line2):
        (x1, y1), (x2, y2) = line1
        (x3, y3), (x4, y4) = line2

        def ccw(a, b, c):
            return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

        return (ccw((x1, y1), (x3, y3), (x4, y4)) != ccw((x2, y2), (x3, y3), (x4, y4)) and
                ccw((x1, y1), (x2, y2), (x3, y3)) != ccw((x1, y1), (x2, y2), (x4, y4)))

    @staticmethod
    def point_on_segment(p1, p2, p):
        """
        Checks if point p = (px, py) lies exactly on the line segment p1 -> p2.
        """
        (x1, y1), (x2, y2) = p1, p2
        (px, py) = p

        # 1) Check for collinearity via cross product = 0
        cross = (py - y1) * (x2 - x1) - (px - x1) * (y2 - y1)
        if abs(cross) > 1e-6:
            return False  # Not collinear

        # 2) Check that p is within bounding box of p1 -> p2
        if min(x1, x2) <= px <= max(x1, x2) and min(y1, y2) <= py <= max(y1, y2):
            return True
        return False

    def line_passes_through_dot(self, line):
        """
        Returns True if 'line' (p1->p2) passes through the center of
        any OTHER dot on the board (i.e. not counting endpoints).
        """
        (p1, p2) = line
        for dot in self.board:
            # skip the endpoints
            if dot == p1 or dot == p2:
                continue

            # if dot is exactly on the segment, it's illegal
            if self.point_on_segment(p1, p2, dot):
                return True
        return False

    def get_possible_moves(self):
        used_dots = set()
        for move in self.lines:
            used_dots.add(move[0])
            used_dots.add(move[1])

        # Only consider dots not already used as endpoints
        free_dots = [dot for dot in self.board if dot not in used_dots]

        moves = []
        for i in range(len(free_dots)):
            for j in range(i + 1, len(free_dots)):
                candidate_move = (free_dots[i], free_dots[j])
                
                # 1) Make sure it doesn’t intersect any existing line
                illegal = False
                for existing_move in self.lines:
                    if self.line_intersects(existing_move, candidate_move):
                        illegal = True
                        break

                # 2) Make sure it doesn’t pass through any other dot
                if not illegal and self.line_passes_through_dot(candidate_move):
                    illegal = True

                if not illegal:
                    moves.append(candidate_move)

        return moves

    def apply_move(self, move):
        """
        Returns a new GameState with the move applied.
        This updates the move list, scores, and switches the turn.
        """
        new_state = copy.deepcopy(self)
        new_state.lines.append(move)
        # Update score: here we simply add one point to the current player.
        if new_state.current_player:
            new_state.score1 += 1
        else:
            new_state.score2 += 1
        new_state.current_player = not new_state.current_player
        return new_state

    def is_terminal(self):
        """Returns True if no more moves are available."""
        return len(self.get_possible_moves()) == 0

    def evaluate(self):
        """
        Evaluates the state from player 1's perspective.
        A simple evaluation is the score difference.
        """
        return self.score1 - self.score2


def minimax(state, depth, maximizingPlayer):
    """
    Standard minimax algorithm (without alpha-beta pruning).
    Returns the evaluated value for the given state.
    """
    if depth == 0 or state.is_terminal():
        return state.evaluate()
    if maximizingPlayer:
        maxEval = float("-inf")
        for move in state.get_possible_moves():
            child_state = state.apply_move(move)
            eval = minimax(child_state, depth - 1, False)
            maxEval = max(maxEval, eval)
        return maxEval
    else:
        minEval = float("inf")
        for move in state.get_possible_moves():
            child_state = state.apply_move(move)
            eval = minimax(child_state, depth - 1, True)
            minEval = min(minEval, eval)
        return minEval


def minimax_decision(state, depth, maximizingPlayer):
    """
    Chooses the best move using the minimax algorithm.
    Returns a tuple (best_move, best_value).
    """
    best_move = None
    if maximizingPlayer:
        best_value = float("-inf")
        for move in state.get_possible_moves():
            child_state = state.apply_move(move)
            eval = minimax(child_state, depth - 1, False)
            if eval > best_value:
                best_value = eval
                best_move = move
    else:
        best_value = float("inf")
        for move in state.get_possible_moves():
            child_state = state.apply_move(move)
            eval = minimax(child_state, depth - 1, True)
            if eval < best_value:
                best_value = eval
                best_move = move
    return best_move, best_value


