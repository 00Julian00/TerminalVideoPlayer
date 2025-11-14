from dataclasses import dataclass, field
import time

from data import Pixel, Element, Transform, Size, Position, Color
from ascii_tools import img_to_pixel_matrix
import video_processing
from constants import WIDTH_COMPENSATION

@dataclass
class element_VIDEO(Element):
    """
    An element that displays a video feed.
    """
    video_path: str = ''
    render_as_ascii: bool = False
    size: int = 32

    def __post_init__(self):
        self._transform: Transform = Transform(Position(0, 0), Size(self.size, self.size))

        self.stream = video_processing.process_video(self.video_path)
        self.aspect_ratio = video_processing.get_aspect_ratio(self.video_path)

    def on_new_frame(self):
        next_frame = next(self.stream, [])

        if not next_frame:
            return

        self.data = img_to_pixel_matrix(
            next_frame,
            size=Size(
                height=self.transform.size.height,
                width=int(self.transform.size.width * WIDTH_COMPENSATION)
            ),
            render_as_ascii=self.render_as_ascii,
            aspect_ratio=self.aspect_ratio
        )

    def on_terminal_size_change(self, _):
        pass

    @property
    def transform(self) -> Transform:
        return self._transform
    
    @transform.setter
    def transform(self, value: Transform):
        self._transform = value

@dataclass
class element_COORDINATES(Element):
    """
    An element that displays the coordinates of each pixel in the terminal.
    """
    color: Color = field(default_factory=lambda: Color(1.0, 1.0, 1.0))
    marker_step_size: int = 16

    def __post_init__(self):
        self._transform: Transform = Transform(Position(0, 0), Size(1, 1))

    @property
    def transform(self) -> Transform:
        return self._transform
    
    @transform.setter
    def transform(self, value: Transform):
        self._transform = value

    def on_terminal_size_change(self, new_size):
        self.data.clear()
        y = 0
        while y < new_size.height:
            x = 0
            while x < new_size.width:
                char = f"{x},{y}"

                if char:
                    if x + len(char) > new_size.width:
                        break

                self.data.extend(Pixel.string_to_pixels(char, self.color, position=Position(x, y)))

                # Step by marker_step_size or at least 1 to avoid infinite loop
                x += max(self.marker_step_size, 1)
            y += self.marker_step_size

    def on_new_frame(self):
        pass

@dataclass
class element_FPS(Element):
    """
    An element that displays the rate at which the terminal is beeing updated.
    """
    color: Color = field(default_factory=lambda: Color(1.0, 1.0, 1.0))

    def __post_init__(self):
        self._transform: Transform = Transform(Position(0, 0), Size(0, 0))
        self._timestamps: list[float] = []
        self.current_fps: float = 0.0

    def on_new_frame(self):
        now = time.time()
        self._timestamps.append(now)

        one_second_ago = now - 1
        self._timestamps = [t for t in self._timestamps if t > one_second_ago]

        self.current_fps = len(self._timestamps)

        self.data = Pixel.string_to_pixels(f"FPS: {self.current_fps}", color=self.color, position=Position(0, 0))

    def on_terminal_size_change(self, _):
        pass

    @property
    def transform(self) -> Transform:
        return self._transform

    @transform.setter
    def transform(self, value: Transform):
        self._transform = value
