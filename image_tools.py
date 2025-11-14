from PIL import Image

def resize_img(image: Image.Image, width, height):
    """
    Resizes an image to the specified width and height while maintaining its aspect ratio, 
    then returns both the resized image and its grayscale version.
    Args:
        image (PIL.Image.Image): The image to be resized.
        width (int): The desired width of the output image.
        height (int): The desired height of the output image.
    Returns:
        tuple: A tuple containing:
            - img (PIL.Image.Image): The resized image.
            - img_gry (PIL.Image.Image): The grayscale version of the resized image.
    """
    
    img = image.resize((width, height), Image.Resampling.LANCZOS)

    img_gry = img.convert('L')
    
    return img, img_gry

def get_normalized_brightness_matrix(image: Image.Image) -> list[list[float]]:
    """
    Converts a grayscale image to a 2D matrix of normalized brightness values (0-1).
    
    Args:
        image (PIL.Image.Image): The grayscale image to be converted.
    
    Returns:
        list[list[float]]: A 2D list representing the normalized brightness values of the image.
    """
    width, height = image.size
    pixels = image.load()
    
    brightness_matrix = []
    for y in range(height):
        row = []
        for x in range(width):
            brightness = pixels[x, y] / 255.0  # Normalize to 0-1
            row.append(brightness)
        brightness_matrix.append(row)
    
    return brightness_matrix

def get_rgb_matrix(image: Image.Image) -> list[list[tuple[int, int, int]]]:
    """
    Converts an RGB image to a 2D matrix of RGB tuples.
    
    Args:
        image (PIL.Image.Image): The RGB image to be converted.
    
    Returns:
        list[list[tuple[int, int, int]]]: A 2D list representing the RGB values of the image.
    """
    width, height = image.size
    pixels = image.load()
    
    rgb_matrix = []
    for y in range(height):
        row = []
        for x in range(width):
            rgb = pixels[x, y]  # This will be a tuple (R, G, B)
            row.append(rgb)
        rgb_matrix.append(row)
    
    return rgb_matrix

def load_image(image_path):
    """
    Loads an image from the specified file path.
    Args:
        image_path (str): The file path to the image to be loaded.
    Returns:
        PIL.Image.Image: The loaded image.
    """
    img = Image.open(image_path)
    return img