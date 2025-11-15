"""
Takes in a list of elements and outputs the final frame buffer.
"""
import data

def construct_frame_buffer(elements: list[data.Element]) -> data.FrameBuffer:
    all_elements = sorted(elements, key=lambda e: e.priority)

    buffer = data.FrameBuffer()
    
    for element in all_elements:
        element.on_new_frame()
        buffer.write(element.data)

    return buffer
