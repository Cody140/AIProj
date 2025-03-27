import pygame as pg
from collections import deque

# Tree Structure Classes
class GameNode:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.value = None
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

class GameTree:
    def __init__(self):
        self.root = None
        self.nodes = {}

    def create_node(self, state, parent=None):
        new_node = GameNode(state, parent)
        if not self.root:
            self.root = new_node
        self.nodes[state] = new_node
        return new_node

    def add_edge(self, parent_state, child_state):
        parent_node = self.nodes[parent_state]
        child_node = self.create_node(child_state, parent_node)
        parent_node.children.append(child_node)

# Pygame Visualization
class TreeVisualizer:
    def __init__(self, tree, width=1200, height=800):
        pg.init()
        self.screen = pg.display.set_mode((width, height))
        self.tree = tree
        self.node_radius = 25
        self.vertical_spacing = 100
        self.horizontal_spacing = 200
        self.colors = {
            'bg': (240, 240, 240),
            'node': (50, 120, 200),
            'line': (80, 80, 80),
            'text': (255, 255, 255)
        }
        
    def calculate_positions(self):
        positions = {}
        queue = deque([(self.tree.root, self.screen.get_width()//2, 50)])
        
        while queue:
            node, x, y = queue.popleft()
            positions[node] = (x, y)
            
            # Calculate child positions
            num_children = len(node.children)
            if num_children > 0:
                start_x = x - (num_children-1)*self.horizontal_spacing//2
                for i, child in enumerate(node.children):
                    child_x = start_x + i*self.horizontal_spacing
                    child_y = y + self.vertical_spacing
                    queue.append((child, child_x, child_y))
                    
        return positions
    
    def draw_tree(self, positions):
        # Draw connections first
        for node, (x, y) in positions.items():
            for child in node.children:
                if child in positions:
                    cx, cy = positions[child]
                    pg.draw.line(self.screen, self.colors['line'], (x, y), (cx, cy), 2)

        # Then draw nodes
        for node, (x, y) in positions.items():
            # Node circle
            pg.draw.circle(self.screen, self.colors['node'], (x, y), self.node_radius)
            
            # Node text
            font = pg.font.Font(None, 24)
            text = font.render(f"{node.state}\n{node.value or ''}", True, self.colors['text'])
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
    
    def run(self):
        running = True
        positions = self.calculate_positions()
        
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            
            self.screen.fill(self.colors['bg'])
            self.draw_tree(positions)
            pg.display.flip()
        
        pg.quit()

# Example Usage
if __name__ == "__main__":
    # Create sample tree
    tree = GameTree()
    root = tree.create_node("A")
    tree.add_edge("A", "B")
    tree.add_edge("A", "C")
    tree.add_edge("B", "D")
    tree.add_edge("B", "E")
    tree.add_edge("C", "F")

    # Assign values
    tree.nodes["B"].value = 3
    tree.nodes["C"].value = 2
    tree.nodes["D"].value = 5
    tree.nodes["E"].value = 1
    tree.nodes["F"].value = 4

    # Visualize
    visualizer = TreeVisualizer(tree)
    visualizer.run()