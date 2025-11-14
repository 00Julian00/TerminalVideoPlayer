import asyncio
import time
import atexit
import argparse
import logging

from blessed import Terminal

import logger
import data
import terminal_api
import renderer
import elements
import video_processing

terminal = Terminal()

active_elements: list[elements.Element] = []

async def watch_terminal_dimensions():
    delay = 1.0 / 30
    prev_width, prev_height = terminal.width, terminal.height

    while True:
        await asyncio.sleep(delay)

        width, height = terminal.width, terminal.height
        
        if width != prev_width or height != prev_height:
            prev_width, prev_height = width, height
            renderer.on_terminal_size_change(terminal)

            for element in active_elements:
                element.on_terminal_size_change(data.Size(width, height))

async def _play_video(file_path: str, ascii_mode: bool = False, size: int = 32, debug_mode: bool = False):
    global terminal

    atexit.register(terminal_api.show_cursor, terminal)
    # atexit.register(terminal_api.clear_screen, terminal)
    atexit.register(terminal_api.reset_text_color, terminal)

    asyncio.create_task(watch_terminal_dimensions())

    terminal_api.hide_cursor(terminal)
    terminal_api.clear_screen(terminal)

    framerate = video_processing.get_framerate(file_path)
    
    try:
        if debug_mode:
            logger.start_external_log()
        else:
            logging.getLogger().setLevel(logging.ERROR)

        coords = elements.element_COORDINATES(
            color=data.Color(1.0, 1.0, 1.0)
        )

        vid = elements.element_VIDEO(
            video_path=file_path,
            render_as_ascii=ascii_mode,
            size=size
        )

        fps = elements.element_FPS(
            color=data.Color(0.0, 1.0, 0.0)
        )

        active_elements.extend([vid])

        if debug_mode:
            active_elements.extend([coords, fps])

        # Generate initial data
        for element in active_elements:
            element.on_terminal_size_change(data.Size(terminal.width, terminal.height))

        # Main render loop
        while True:
            renderer.render(active_elements, terminal)
            await asyncio.sleep(1.0 / framerate)

    finally:
        if logger.log_manager:
            logger.log_manager.cleanup()
        time.sleep(0.5)  # Brief pause to ensure cleanup completes

def play_video(file_path: str, ascii_mode: bool = False, size: int = 32, debug_mode: bool = False):
    asyncio.run(_play_video(file_path, ascii_mode, size, debug_mode))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play a video in the terminal.")
    parser.add_argument("file_path", help="The path to the video file.")
    parser.add_argument("--size", type=int, default=32, help="The size of the video element.")
    parser.add_argument("--ascii", action="store_true", help="Render video as ASCII.")
    parser.add_argument("--debug", action="store_true", help="Show debug overlay.")
    args = parser.parse_args()

    play_video(args.file_path, args.ascii, args.size, args.debug)
