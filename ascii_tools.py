from PIL import Image, ImageDraw, ImageFont

chars, percentages = [], []

def _get_max_bbox(chars, font_size, font_path=None):
   """Find the maximum bounding box size among all characters."""
   if font_path:
       font = ImageFont.truetype(font_path, font_size)
   else:
       font = ImageFont.load_default()
   
   max_width = 0
   max_height = 0
   
   for char in chars:
       bbox = font.getbbox(char)
       width = bbox[2] - bbox[0]
       height = bbox[3] - bbox[1]
       max_width = max(max_width, width)
       max_height = max(max_height, height)
   
   return max_width, max_height, font

def _count_character_pixels(char, font, fixed_width, fixed_height):
   """Count weighted pixels for a character rendered in a fixed-size box."""
   # Get the actual bounding box of the character for centering
   bbox = font.getbbox(char)
   char_width = bbox[2] - bbox[0]
   char_height = bbox[3] - bbox[1]
   
   # Create an image with fixed size and transparent background
   img = Image.new('RGBA', (fixed_width, fixed_height), (0, 0, 0, 0))
   draw = ImageDraw.Draw(img)
   
   # Center the character in the fixed box
   x_offset = (fixed_width - char_width) // 2 - bbox[0]
   y_offset = (fixed_height - char_height) // 2 - bbox[1]
   
   # Draw the character in white
   draw.text((x_offset, y_offset), char, font=font, fill=(255, 255, 255, 255))
   
   # Calculate weighted sum (anti-aliasing aware)
   pixels = img.getdata()
   weighted_sum = sum(pixel[3] / 255.0 for pixel in pixels)
   weighted_coverage_percent = (weighted_sum / (fixed_width * fixed_height)) * 100
   
   return char, weighted_coverage_percent