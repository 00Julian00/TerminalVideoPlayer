import sys

from blessed import Terminal

import data

def hide_cursor(terminal: Terminal):
    """Hides the cursor in the terminal."""
    print(terminal.hide_cursor(), end='', flush=True)

def show_cursor(terminal: Terminal):
    """Shows the cursor in the terminal."""
    print(terminal.show_cursor(), end='', flush=True)

def clear_screen(terminal: Terminal):
    """Clears the terminal screen."""
    print(terminal.home + terminal.clear + '\x1b[3J', end='', flush=True)

def reset_text_color(terminal: Terminal):
    """Resets the text color to default."""
    print(terminal.normal, end='', flush=True)

def set_text_color(terminal: Terminal, color: data.Color):
    """Sets the text color using RGB values."""
    r, g, b = color.to_tuple_rgb()
    print(terminal.color_rgb(r, g, b), end='', flush=True)

def print_at(terminal: Terminal, pos: tuple[int, int], text: str):
    """
    Prints the given text at the specified (x, y) position in the terminal.

    Args:
        terminal (Terminal): The terminal object used to control cursor movement.
        pos (tuple[int, int]): A tuple (x, y) representing the position to print the text.
        text (str): The text to be printed at the specified position.
    """
    sys.stdout.write(terminal.move_xy(pos[0], pos[1]) + text)
    sys.stdout.flush()

def clear_and_print_at(terminal: Terminal, pos: tuple[int, int], text: str):
    """
    Clears the terminal screen and prints the given text at the specified (x, y) position.

    Args:
        terminal (Terminal): The terminal object used to control cursor movement.
        pos (tuple[int, int]): A tuple (x, y) representing the position to print the text.
        text (str): The text to be printed at the specified position.
    """
    print_at(terminal, pos, terminal.home + terminal.clear + '\x1b[3J' + text)