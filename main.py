import asyncio
import time
import atexit
import argparse
import logging
import cProfile
import pickle

from blessed import Terminal

import logger
import data
import terminal_api
import renderer
import elements
import video_processing

terminal = Terminal()

active_elements: list[elements.Element] = []

async def watch_terminal_dimensions(should_refresh: bool = True):
    delay = 1.0 / 30
    prev_width, prev_height = terminal.width, terminal.height

    while True:
        await asyncio.sleep(delay)

        width, height = terminal.width, terminal.height
        
        if width != prev_width or height != prev_height:
            prev_width, prev_height = width, height
            renderer.on_terminal_size_change(terminal, should_refresh)

            for element in active_elements:
                element.on_terminal_size_change(data.Size(width, height))

async def _play_video(file_path: str, ascii_mode: bool = False, size: int = 32, debug_mode: bool = False):
    global terminal

    is_preprocessed = file_path.lower().endswith((".pickle", ".pkl"))

    if is_preprocessed:
        processed_video: data.ProcessedVideo
        with open(file_path, "rb") as f:
            processed_video = pickle.load(f)

        frame_generator = processed_video.consume_frames()

    atexit.register(terminal_api.show_cursor, terminal)
    atexit.register(terminal_api.reset_text_color, terminal)

    asyncio.create_task(watch_terminal_dimensions(not is_preprocessed))

    terminal_api.hide_cursor(terminal)
    terminal_api.clear_screen(terminal)

    framerate = video_processing.get_framerate(file_path) if not is_preprocessed else processed_video.framerate
    
    try:
        if debug_mode:
            logger.start_external_log()
        else:
            logging.getLogger().setLevel(logging.ERROR)

        coords = elements.element_COORDINATES(
            color=data.Color(1.0, 1.0, 1.0)
        )

        fps = elements.element_FPS(
            color=data.Color(0.0, 1.0, 0.0)
        )

        if not is_preprocessed:
            vid = elements.element_VIDEO(
                video_path=file_path,
                render_as_ascii=ascii_mode,
                size=size
            )

            active_elements.extend([vid])

        if debug_mode and not is_preprocessed:
            active_elements.extend([coords, fps])

        # Generate initial data
        for element in active_elements:
            element.on_terminal_size_change(data.Size(terminal.width, terminal.height))

        # Main render loop
        frame_time = 1.0 / framerate  # Target: 33.33ms per frame

        # Main render loop
        while True:
            frame_start = time.time()
            
            if not is_preprocessed:
                renderer.render(active_elements, terminal)
            else:
                next_frame = next(frame_generator, None)
                if next_frame is None:  # Video finished
                    break
                terminal_api.print_at(terminal, (0, 0), next_frame)
            
            # Calculate how long to sleep
            elapsed = time.time() - frame_start
            sleep_time = max(0, frame_time - elapsed)

            logging.info(f"Frame time: {elapsed:.4f}s, sleeping for {sleep_time:.4f}s")
            
            await asyncio.sleep(sleep_time)

    except Exception as e:
        terminal_api.show_cursor(terminal)
        terminal_api.reset_text_color(terminal)
        terminal_api.clear_screen(terminal)
        raise e

    finally:
        terminal_api.show_cursor(terminal)
        terminal_api.reset_text_color(terminal)
        terminal_api.clear_screen(terminal)
        if logger.log_manager:
            logger.log_manager.cleanup()
        time.sleep(0.5)  # Brief pause to ensure cleanup completes

def play_video(file_path: str, ascii_mode: bool = False, size: int = 32, debug_mode: bool = False):
    try:    
        asyncio.run(_play_video(file_path, ascii_mode, size, debug_mode))
    except KeyboardInterrupt:
        terminal_api.show_cursor(terminal)
        terminal_api.reset_text_color(terminal)
        terminal_api.clear_screen(terminal)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Play a video in the terminal.")
    parser.add_argument("file_path", help="The path to the video file.")
    parser.add_argument("--size", type=int, default=32, help="The size of the video element.")
    parser.add_argument("--ascii", action="store_true", help="Render video as ASCII.")
    parser.add_argument("--debug", action="store_true", help="Show debug overlay.")
    args = parser.parse_args()

    if args.debug:
        cProfile.run('play_video(args.file_path, args.ascii, args.size, args.debug)')
    else:
        play_video(args.file_path, args.ascii, args.size, args.debug)
