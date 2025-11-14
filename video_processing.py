import cv2
from PIL import Image
from typing import Any, Generator

def get_aspect_ratio(file_path: str) -> float:
    """
    Calculates the aspect ratio of a video.

    Args:
        file_path (str): The path to the video file.

    Returns:
        float: The aspect ratio of the video.
    """
    cap = cv2.VideoCapture(file_path)

    if not cap.isOpened():
        raise ValueError(f"Error: Could not open video file at {file_path}")

    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    cap.release()

    if height > 0:
        return width / height
    return 0.0

def get_framerate(file_path: str) -> int:
    """
    Gets the framerate of a video.

    Args:
        file_path (str): The path to the video file.

    Returns:
        int: The framerate of the video.
    """
    cap = cv2.VideoCapture(file_path)

    if not cap.isOpened():
        raise ValueError(f"Error: Could not open video file at {file_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    return int(fps)

def process_video(file_path: str):
    generator = stream_video_from_disk(file_path)
    for frame in generator:
        yield frame

def stream_video_from_disk(video_path: str) -> Generator[Image.Image, Any, None]:
    """
    Streams a video from the specified path and yields its frames.

    Args:
        video_path (str): The path to the video file.
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Error: Could not open video file at {video_path}")

    while cap.isOpened():
        ret, frame = cap.read()

        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            yield pil_image
        else:
            break

    cap.release()
    cv2.destroyAllWindows()