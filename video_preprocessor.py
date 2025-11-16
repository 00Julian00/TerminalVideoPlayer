import pickle
from blessed import Terminal
import time
import os
import argparse

import elements
import compositor
import data
import video_processing

# Progress bar state
_start_time = None
_progress_line = None

def progress_bar(current, total, terminal, bar_length=40):
    """Draw and update a progress bar with frame counter and timer"""
    global _start_time, _progress_line
    
    # Initialize on first call
    if _start_time is None:
        _start_time = time.time()
        _progress_line = terminal.get_location()[0]  # Save current line
        print()  # Create a line for the progress bar
    
    # Calculate progress
    percent = current / total
    filled_length = int(bar_length * percent)
    
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    percent_display = f"{percent * 100:.1f}%"
    
    # Calculate elapsed time
    elapsed = time.time() - _start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    time_display = f"{minutes:02d}:{seconds:02d}"
    
    # Calculate remaining time estimate
    if current > 0:
        time_per_frame = elapsed / current
        remaining_frames = total - current
        remaining_time = time_per_frame * remaining_frames
        rem_minutes = int(remaining_time // 60)
        rem_seconds = int(remaining_time % 60)
        remaining_display = f"{rem_minutes:02d}:{rem_seconds:02d}"
    else:
        remaining_display = "--:--"
    
    # Build the progress bar (with fixed width for numbers)
    display = f"Processed frames: {current:4d} / {total:4d} [{bar}] {percent_display:6s} | Time: {time_display} | Remaining Est.: {remaining_display}"
    
    # Save cursor, move to progress line, update, restore cursor
    print(terminal.save + terminal.move_x(0) + terminal.clear_eol + display + terminal.restore, end='', flush=True)

def reset_progress_bar():
    """Reset the progress bar state"""
    global _start_time, _progress_line
    _start_time = None
    _progress_line = None

def process_video(file_path: str, ascii_mode: bool = False, size: int = 32):
    terminal = Terminal()
    
    vid = elements.element_VIDEO(
        video_path=file_path,
        render_as_ascii=ascii_mode,
        size=size
    )

    last_frame_buffer = data.FrameBuffer()
    total_frames = video_processing.get_frame_amount(file_path)
    current_frame = 0

    processed_video = data.ProcessedVideo(
        framerate=video_processing.get_framerate(file_path),
        size=vid.size,
        is_in_ascii=vid.render_as_ascii,
        frames=[]
    )

    # Use hidden cursor for cleaner display
    with terminal.hidden_cursor():
        while current_frame < total_frames:
            frame_buffer = compositor.construct_frame_buffer([vid])

            if not frame_buffer:
                break

            processed_video.frames.append(frame_buffer.get_difference(last_frame_buffer, terminal, render_outside_bounds=True))

            last_frame_buffer = frame_buffer
            
            current_frame += 1
            progress_bar(current_frame, total_frames, terminal)

    # Calculate total time before resetting
    elapsed_time = time.time() - _start_time if _start_time else 0
    
    # Reset progress bar state
    reset_progress_bar()

    # Move to new line after progress bar
    print()

    target_location = os.path.dirname(file_path)
    output_path = os.path.join(target_location, "processed_video.pkl")
    with open(output_path, "wb") as f:
        pickle.dump(processed_video, f)

    print(f"Video processing completed. Total time: {elapsed_time:.2f} seconds.")
    print(f"Output saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pre-process a video file for terminal playback.")
    parser.add_argument("file_path", help="The path to the video file to process.")
    parser.add_argument("--ascii", action="store_true", help="Process the video in ASCII mode.")
    parser.add_argument("--size", type=int, default=32, help="The width of the video in characters.")

    args = parser.parse_args()

    process_video(args.file_path, args.ascii, args.size)
