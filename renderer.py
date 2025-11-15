from copy import copy

from blessed import Terminal

import terminal_api
import data
import compositor

current_frame_buffer: data.FrameBuffer = data.FrameBuffer()
frame_buffer = data.FrameBuffer()

def render(elements: list[data.Element], terminal: Terminal):
    global frame_buffer, current_frame_buffer

    frame_buffer = compositor.construct_frame_buffer(elements)

    output_string = frame_buffer.get_difference(current_frame_buffer, terminal)

    bytes_sent = len(output_string.encode('utf-8'))
    kb_sent = bytes_sent / 1024
    # logging.info(f"Data sent to terminal: {kb_sent:.2f} kb")

    if output_string:
        terminal_api.print_at(terminal, (0, 0), output_string)

    current_frame_buffer = copy(frame_buffer)

def on_terminal_size_change(terminal: Terminal, refresh: bool) -> None:
    global current_frame_buffer
    if refresh:
        terminal_api.clear_screen(terminal)
    current_frame_buffer = data.FrameBuffer()