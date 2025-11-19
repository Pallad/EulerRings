import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from matplotlib.widgets import TextBox, Button
from typing import Dict, Optional, Tuple


class SetVisualizer:
    """Interactive visualizer for set operations with drag-and-drop functionality."""
    
    # Constants
    GRID_SIZE: int = 100  # Reduced from 200x200 for better performance
    GRID_RANGE: Tuple[float, float] = (-4.8, 4.8)
    CANVAS_RANGE: Tuple[float, float] = (-5, 5)
    
    # Set configurations
    SET_CONFIG = {
        'A': {'pos': (-2, 0), 'radius': 1.5, 'color': 'darkred'},
        'B': {'pos': (2, 0), 'radius': 1.5, 'color': 'darkblue'},
        'C': {'pos': (0, 2), 'radius': 1.5, 'color': 'darkgreen'}
    }
    
    DEFAULT_EXPRESSION: str = 'A U B'
    
    def __init__(self):
        self.points: Optional[np.ndarray] = None
        self.text_box: Optional[TextBox] = None
        self.reset_button: Optional[Button] = None
        self.result_scatter = None
        self.current_expression: str = ''
        
        # Initialize plot
        self.fig, self.ax = plt.subplots(figsize=(12, 9))
        plt.subplots_adjust(bottom=0.25)
        
        # Set custom window title
        self.fig.canvas.manager.set_window_title('Визуализатор множеств - Set Operations Visualizer')

        self.ax.set_xlim(*self.CANVAS_RANGE)
        self.ax.set_ylim(*self.CANVAS_RANGE)
        self.ax.set_aspect('equal')
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.set_title('Визуализатор операций над множествами\n(Перетаскивайте круги мышью!)')

        # Universal set background
        canvas_size = self.CANVAS_RANGE[1] - self.CANVAS_RANGE[0]
        self.universal_set = Rectangle(
            (self.CANVAS_RANGE[0], self.CANVAS_RANGE[0]), 
            canvas_size, canvas_size,
            facecolor='lightgray', alpha=0.3, edgecolor='black', linewidth=1
        )
        self.ax.add_patch(self.universal_set)

        # Initialize sets with stored text references
        self.sets: Dict[str, Dict] = {}
        for key, config in self.SET_CONFIG.items():
            circle = Circle(
                config['pos'], config['radius'],
                facecolor='white', alpha=0.7,
                edgecolor=config['color'], linewidth=2, label=key
            )
            self.sets[key] = {
                'circle': circle,
                'dragging': False,
                'offset': (0, 0),
                'text': None  # Will be set below
            }

        # Add circles and labels
        for key in self.sets:
            self.ax.add_patch(self.sets[key]['circle'])
            center = self.sets[key]['circle'].center
            text = self.ax.text(
                center[0], center[1], key,
                ha='center', va='center', fontsize=16, fontweight='bold', color='black'
            )
            self.sets[key]['text'] = text

        self.create_point_grid()
        self.setup_ui()
        self.connect_events()
        self.update_plot(self.DEFAULT_EXPRESSION)

    def create_point_grid(self) -> None:
        """Create optimized point grid for visualization."""
        x = np.linspace(*self.GRID_RANGE, self.GRID_SIZE)
        y = np.linspace(*self.GRID_RANGE, self.GRID_SIZE)
        lx, ly = np.meshgrid(x, y)
        self.points = np.vstack([lx.ravel(), ly.ravel()]).T

    def setup_ui(self) -> None:
        """Setup user interface components."""
        axbox = plt.axes([0.2, 0.12, 0.6, 0.05])
        self.text_box = TextBox(axbox, 'Формула: ', initial=self.DEFAULT_EXPRESSION)
        self.text_box.on_submit(self.on_formula_submit)

        reset_ax = plt.axes([0.82, 0.12, 0.1, 0.05])
        self.reset_button = Button(reset_ax, 'Сброс')
        self.reset_button.on_clicked(self.reset_event)

        instructions = '''
Операции:
  A U B   - Объединение (OR) 
  A & B   - Пересечение (AND)  
  A ^ B   - Симметрическая разность (XOR)
  A - B   - Разность
  A.      - Инверсия (NOT)

Примеры:
  A U B   - Объединение A и B
 (A U B). - Инверсия объединения
  A - B   - Элементы A, не входящие в B
'''
        self.ax.text(
            self.GRID_RANGE[0], self.GRID_RANGE[0], instructions,
            font='Courier New', fontsize=9, verticalalignment='bottom',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8)
        )

    def connect_events(self) -> None:
        """Connect mouse event handlers."""
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)

    def points_in_circle(self, circle: Circle) -> np.ndarray:
        """Return boolean mask of points inside the circle."""
        center = circle.center
        radius = circle.get_radius()
        distances = np.sum((self.points - center) ** 2, axis=1)
        return distances <= radius ** 2

    def evaluate_expression(self, expression: str) -> np.ndarray:
        """Safely evaluate set expression without using eval()."""
        try:
            # Validate input
            if not expression or not expression.strip():
                return np.zeros(len(self.points), dtype=bool)
            
            # Get masks for each set
            masks = {
                'A': self.points_in_circle(self.sets['A']['circle']),
                'B': self.points_in_circle(self.sets['B']['circle']),
                'C': self.points_in_circle(self.sets['C']['circle'])
            }
            
            # Parse and evaluate expression safely
            return self._safe_evaluate(expression, masks)

        except Exception as e:
            print(f'Ошибка в выражении: {e}')
            return np.zeros(len(self.points), dtype=bool)
    
    def _safe_evaluate(self, expr: str, masks: Dict[str, np.ndarray]) -> np.ndarray:
        """Safely parse and evaluate boolean expression using recursive descent."""
        expr = expr.strip()
        universal_mask = np.ones(len(self.points), dtype=bool)
        
        # Tokenize expression
        tokens = self._tokenize(expr)
        result, _ = self._parse_expression(tokens, 0, masks, universal_mask)
        return result
    
    def _tokenize(self, expr: str) -> list:
        """Convert expression string into tokens."""
        tokens = []
        i = 0
        while i < len(expr):
            if expr[i].isspace():
                i += 1
            elif expr[i] in 'ABC':
                tokens.append(expr[i])
                i += 1
            elif expr[i] == '.':
                tokens.append('NOT')
                i += 1
            elif expr[i] == 'U':
                tokens.append('OR')
                i += 1
            elif expr[i] == '&':
                tokens.append('AND')
                i += 1
            elif expr[i] == '^':
                tokens.append('XOR')
                i += 1
            elif expr[i] == '-':
                tokens.append('DIFF')
                i += 1
            elif expr[i] == '(':
                tokens.append('(')
                i += 1
            elif expr[i] == ')':
                tokens.append(')')
                i += 1
            else:
                raise ValueError(f"Unknown character: {expr[i]}")
        return tokens
    
    def _parse_expression(self, tokens: list, pos: int, masks: Dict, universal: np.ndarray) -> Tuple[np.ndarray, int]:
        """Parse expression with operator precedence: NOT > AND > XOR > OR > DIFF."""
        left, pos = self._parse_or(tokens, pos, masks, universal)
        return left, pos
    
    def _parse_or(self, tokens: list, pos: int, masks: Dict, universal: np.ndarray) -> Tuple[np.ndarray, int]:
        """Parse OR operations (lowest precedence)."""
        left, pos = self._parse_diff(tokens, pos, masks, universal)
        
        while pos < len(tokens) and tokens[pos] == 'OR':
            pos += 1
            right, pos = self._parse_diff(tokens, pos, masks, universal)
            left = left | right
        
        return left, pos
    
    def _parse_diff(self, tokens: list, pos: int, masks: Dict, universal: np.ndarray) -> Tuple[np.ndarray, int]:
        """Parse DIFF operations."""
        left, pos = self._parse_xor(tokens, pos, masks, universal)
        
        while pos < len(tokens) and tokens[pos] == 'DIFF':
            pos += 1
            right, pos = self._parse_xor(tokens, pos, masks, universal)
            left = left & ~right
        
        return left, pos
    
    def _parse_xor(self, tokens: list, pos: int, masks: Dict, universal: np.ndarray) -> Tuple[np.ndarray, int]:
        """Parse XOR operations."""
        left, pos = self._parse_and(tokens, pos, masks, universal)
        
        while pos < len(tokens) and tokens[pos] == 'XOR':
            pos += 1
            right, pos = self._parse_and(tokens, pos, masks, universal)
            left = left ^ right
        
        return left, pos
    
    def _parse_and(self, tokens: list, pos: int, masks: Dict, universal: np.ndarray) -> Tuple[np.ndarray, int]:
        """Parse AND operations."""
        left, pos = self._parse_not(tokens, pos, masks, universal)
        
        while pos < len(tokens) and tokens[pos] == 'AND':
            pos += 1
            right, pos = self._parse_not(tokens, pos, masks, universal)
            left = left & right
        
        return left, pos
    
    def _parse_not(self, tokens: list, pos: int, masks: Dict, universal: np.ndarray) -> Tuple[np.ndarray, int]:
        """Parse NOT operations (highest precedence after atoms)."""
        operand, pos = self._parse_atom(tokens, pos, masks, universal)
        
        if pos < len(tokens) and tokens[pos] == 'NOT':
            pos += 1
            return universal & ~operand, pos
        
        return operand, pos
    
    def _parse_atom(self, tokens: list, pos: int, masks: Dict, universal: np.ndarray) -> Tuple[np.ndarray, int]:
        """Parse atomic expressions (sets or parenthesized expressions)."""
        if pos >= len(tokens):
            raise ValueError("Unexpected end of expression")
        
        token = tokens[pos]
        
        if token == '(':
            pos += 1
            result, pos = self._parse_expression(tokens, pos, masks, universal)
            if pos >= len(tokens) or tokens[pos] != ')':
                raise ValueError("Missing closing parenthesis")
            pos += 1
            return result, pos
        elif token in masks:
            return masks[token], pos + 1
        else:
            raise ValueError(f"Unexpected token: {token}")

    def _get_used_sets(self, expression: str) -> set:
        """Detect which sets (A, B, C) are used in the expression."""
        used = set()
        for char in expression:
            if char in 'ABC':
                used.add(char)
        return used
    
    def _update_circle_visibility(self, expression: str) -> None:
        """Show only circles that are used in the formula."""
        used_sets = self._get_used_sets(expression)
        
        for key in self.sets:
            is_used = key in used_sets
            # Update circle visibility
            self.sets[key]['circle'].set_visible(is_used)
            # Update text label visibility
            self.sets[key]['text'].set_visible(is_used)

    def update_plot(self, expression: Optional[str] = None) -> None:
        """Update visualization with new expression result."""
        if expression is None:
            expression = self.current_expression
        else:
            self.current_expression = expression

        # Remove previous result
        if self.result_scatter:
            self.result_scatter.remove()
            self.result_scatter = None

        if expression and expression.strip():
            # Update circle visibility based on formula
            self._update_circle_visibility(expression)
            
            result_mask = self.evaluate_expression(expression)
            result_points = self.points[result_mask]
            point_count = len(result_points)

            if point_count > 0:
                self.result_scatter = self.ax.scatter(
                    result_points[:, 0], result_points[:, 1],
                    color='purple', alpha=0.7, s=1.5, label='Результат'
                )

            # Show formula and point count
            title = f'Визуализатор операций над множествами\nФормула: {expression}'
            if point_count > 0:
                title += f' | Точек: {point_count}'
            self.ax.set_title(title)
        else:
            # Show all circles if expression is empty
            for key in self.sets:
                self.sets[key]['circle'].set_visible(True)
                self.sets[key]['text'].set_visible(True)

        self.fig.canvas.draw_idle()

    def on_formula_submit(self, text: str) -> None:
        """Handle formula text box submission."""
        self.update_plot(text)

    def on_press(self, event) -> None:
        """Handle mouse press event for dragging."""
        if event.inaxes != self.ax:
            return

        for key in self.sets:
            circle = self.sets[key]['circle']
            contains, _ = circle.contains(event)
            if contains:
                self.sets[key]['dragging'] = True
                self.sets[key]['offset'] = (
                    circle.center[0] - event.xdata,
                    circle.center[1] - event.ydata
                )
                break

    def on_motion(self, event) -> None:
        """Handle mouse motion event for dragging."""
        if event.inaxes != self.ax:
            return

        for key in self.sets:
            if self.sets[key]['dragging']:
                circle = self.sets[key]['circle']
                circle.center = (
                    event.xdata + self.sets[key]['offset'][0],
                    event.ydata + self.sets[key]['offset'][1]
                )

                # Update text position using stored reference (optimized)
                self.sets[key]['text'].set_position(circle.center)
                self.update_plot()
                break

    def on_release(self, event) -> None:
        """Handle mouse release event."""
        for key in self.sets:
            self.sets[key]['dragging'] = False

    def reset_event(self, event) -> None:
        """Reset sets to initial positions."""
        for key, config in self.SET_CONFIG.items():
            self.sets[key]['circle'].center = config['pos']
            self.sets[key]['text'].set_position(config['pos'])

        self.text_box.set_val(self.DEFAULT_EXPRESSION)
        self.update_plot(self.DEFAULT_EXPRESSION)

    def show(self) -> None:
        """Display the visualizer window."""
        plt.show()


if __name__ == '__main__':
    visualizer = SetVisualizer()
    visualizer.show()
