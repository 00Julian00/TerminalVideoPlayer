import string
import bisect

from PIL import Image, ImageDraw, ImageFont

import image_tools
import data
from ascii_tools import _get_max_bbox, _count_character_pixels

chars, percentages = [], []

def analyze_all_ascii(font_path: str = None):
   """
   Analyze pixel coverage of all printable ASCII characters.
   
   Renders each ASCII character at the specified font size in a fixed-size
   bounding box and calculates the weighted pixel coverage percentage,
   accounting for anti-aliasing effects.
   
   Args:
       font_path (str, optional): Path to a TrueType font file. If None,
                                 uses the default PIL font.
   
   Returns:
       tuple: A tuple containing:
           - list of str: ASCII characters sorted by weighted coverage (low to high)
           - list of float: Normalized weighted percentages (0-1 scale), sorted low to high
   """
   # Get all printable ASCII characters including space
   printable_chars = list(string.printable.strip())
   
   # Remove special whitespace except space
   chars_to_analyze = [char for char in printable_chars 
                       if char not in ['\n', '\r', '\t', '\v', '\f']]
   
   # Make sure space is included
   if ' ' not in chars_to_analyze:
       chars_to_analyze.append(' ')
   
   # Get maximum bounding box
   max_width, max_height, font = _get_max_bbox(chars_to_analyze, 200, font_path)
   
   # Calculate weighted coverage for each character
   results = []
   for char in chars_to_analyze:
       char, weighted_percent = _count_character_pixels(char, font, max_width, max_height)
       results.append((char, weighted_percent))
   
   # Sort by weighted percentage (low to high)
   results.sort(key=lambda x: x[1])
   
   # Separate into chars and percentages
   sorted_chars = [r[0] for r in results]
   sorted_percentages = [r[1] for r in results]
   
   # Normalize percentages to 0-1 scale
   normalized_percentages = [p / 100.0 for p in sorted_percentages]
   
   return sorted_chars, normalized_percentages

def get_closest_char(value: float, normalized_percentages: list, chars: list) -> str:
    """
    Map a float value to the closest weight in the normalized percentages list.
    
    Args:
        value (float): Value to map (should be between 0 and 1)
        normalized_percentages (list): Sorted list of normalized weights (0-1)
    
    Returns:
        string: The closest character corresponding to the closest weight
    """
    # Scale the value to the range of the character percentages
    max_percentage = normalized_percentages[-1]
    scaled_value = value * max_percentage

    # Find insertion point
    pos = bisect.bisect_left(normalized_percentages, scaled_value)
    
    # Handle edge cases
    if pos == 0:
        return chars[0]
    if pos == len(normalized_percentages):
        return chars[-1]

    # Check which is closer: pos or pos-1
    before = normalized_percentages[pos - 1]
    after = normalized_percentages[pos]
    if after - scaled_value < scaled_value - before:
        return chars[pos]
    else:
        return chars[pos - 1]

def img_to_pixel_matrix(img: Image.Image, size: data.Size, render_as_ascii: bool = False, aspect_ratio: float = 1.0) -> list[data.Pixel]:
    global chars, percentages

    # Generate the character coverage map
    if not chars or not percentages:
        change_font()

    img, img_gry = image_tools.resize_img(img, int(size.width * aspect_ratio), size.height)

    matrix = image_tools.get_normalized_brightness_matrix(img_gry)

    color_matrix = image_tools.get_rgb_matrix(img)

    buffer = []

    for y, row in enumerate(matrix):
        for x, val in enumerate(row):
            char = get_closest_char(val, percentages, chars) if render_as_ascii else ''
            r, g, b = color_matrix[y][x]
            
            # Normalize RGB values to 0-1
            norm_r, norm_g, norm_b = r / 255.0, g / 255.0, b / 255.0

            if not render_as_ascii:
                pixel = data.Pixel(char='█', color=data.Color(norm_r, norm_g, norm_b), position=data.Position(x, y))
            else:
                pixel = data.Pixel(char=char, color=data.Color(norm_r, norm_g, norm_b), position=data.Position(x, y))
            
            buffer.append(pixel)

    return buffer

def img_to_pixel_matrix_batched(imgs: list[Image.Image], size: data.Size, render_as_ascii: bool = False, aspect_ratio: float = 1.0):
    buffers = []
    for img in imgs:
        buffer = img_to_pixel_matrix(img, size, render_as_ascii, aspect_ratio)
        buffers.append(buffer)
    return buffers

def change_font(font_path: str=None):
    global chars, percentages
    chars, percentages = analyze_all_ascii(font_path)
