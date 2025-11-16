from copy import copy

from blessed import Terminal

import terminal_api
import data
import compositor

current_frame_buffer: data.FrameBuffer = data.FrameBuffer()
frame_buffer = data.FrameBuffer()

def render(elements: list[data.Element], terminal: Terminal) -> str:
    """Render elements and return the output string"""
    global frame_buffer, current_frame_buffer

    frame_buffer = compositor.construct_frame_buffer(elements)

    output_string = frame_buffer.get_difference(current_frame_buffer, terminal)

    current_frame_buffer = copy(frame_buffer)
    
    return output_string

def on_terminal_size_change(terminal: Terminal, refresh: bool) -> None:
    global current_frame_buffer
    if refresh:
        terminal_api.clear_screen(terminal)
    current_frame_buffer = data.FrameBuffer()
