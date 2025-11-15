import pickle
from blessed import Terminal
import time
import os
import argparse

import elements
import compositor
import data
import video_processing

def process_video(file_path: str, ascii_mode: bool = False, size: int = 32):
    start_time = time.time()
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

    while current_frame < total_frames:
        frame_buffer = compositor.construct_frame_buffer([vid])

        if not frame_buffer:
            break

        current_frame += 1
        print(f"processed {current_frame} out of {total_frames} frames")

        processed_video.frames.append(frame_buffer.get_difference(last_frame_buffer, terminal, render_outside_bounds=True))

        last_frame_buffer = frame_buffer

    target_location = os.path.dirname(file_path)
    output_path = os.path.join(target_location, "processed_video.pkl")
    with open(output_path, "wb") as f:
        pickle.dump(processed_video, f)

    end_time = time.time()
    print(f"Video processing completed. Took: {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pre-process a video file for terminal playback.")
    parser.add_argument("file_path", help="The path to the video file to process.")
    parser.add_argument("--ascii", action="store_true", help="Process the video in ASCII mode.")
    parser.add_argument("--size", type=int, default=32, help="The width of the video in characters.")

    args = parser.parse_args()

    process_video(args.file_path, args.ascii, args.size)