from blessed import Terminal
import queue
import threading

from data import Size, FrameBuffer, DiffBuffer
from video_processing import get_aspect_ratio, stream_video_from_disk
from pixel_matrix import img_to_pixel_matrix, img_to_pixel_matrix_batched
from constants import WIDTH_COMPENSATION
from diff_to_ansi import diff_buffer_to_ANSI

class VideoProcessor:
    def __init__(self):
        self.terminal = Terminal()
        self.term_width, self.term_height = self.terminal.width, self.terminal.height
        self._frame_queue = queue.Queue()
        self._finished = False

    def diff_buffer_to_ANSI(self, diff_buffer: DiffBuffer, terminal: Terminal) -> str:
        return diff_buffer_to_ANSI(diff_buffer, terminal)
    
    def frame_producer_thread(self, file_path: str):
        def produce_frames():
            for frame in stream_video_from_disk(file_path):
                self._frame_queue.put(frame)
            self._finished = True

        thread = threading.Thread(target=produce_frames)
        thread.start()

    def process_video(self, file_path: str, as_ascii: bool = False, size: int = 32, batch_size: int = 1) -> iter:
        aspect_ratio = get_aspect_ratio(file_path)
        last_buffer = FrameBuffer()

        self.frame_producer_thread(file_path)

        all_matrices = []

        while not self._finished or not self._frame_queue.empty():
            frame_batch = []
            for _ in range(min(batch_size, self._frame_queue.qsize())):
                try:
                    frame = self._frame_queue.get_nowait()
                    frame_batch.append(frame)
                except queue.Empty:
                    break
            
            if not frame_batch:
                continue

            matrices = img_to_pixel_matrix_batched(
                frame_batch,
                size=Size(
                    height=size,
                    width=int(size * WIDTH_COMPENSATION)
                ),
                render_as_ascii=as_ascii,
                aspect_ratio=aspect_ratio
            )

            all_matrices.extend(matrices)

            yield len(all_matrices)

        for matrix in all_matrices:
            buffer = FrameBuffer()
            
            buffer.write(matrix)

            output = buffer.get_difference(last_buffer, self.terminal) if self.terminal.width == self.term_width and self.terminal.height == self.term_height else buffer.get_difference(FrameBuffer(), self.terminal)

            size_changed = self.terminal.width != self.term_width or self.terminal.height != self.term_height

            self.term_width, self.term_height = self.terminal.width, self.terminal.height

            last_buffer = buffer

            yield (output, size_changed)
