# Terminal Renderer

## What is it?

Terminal Renderer is a Python-based application that allows you to play videos directly in your terminal. Includes an optional ASCII mode. The application will try to play the video at its original framerate, but
don't be surprised if the video plays at a slower speed. The terminal is not designed to play videos after all. This project is an experiment and is under active development.

## How to use it

To play a video, run the `main.py` script from your terminal and provide the path to your video file.

### Basic Usage
```bash
python main.py /path/to/your/video.mp4
```

### Options

- **ASCII Mode**: Render the video using ASCII characters instead of colored blocks.
  ```bash
  python main.py /path/to/your/video.mp4 --ascii
  ```

- **Size**: Adjust the size of the video element. The default is 32.
  ```bash
  python main.py /path/to/your/video.mp4 --size 64
  ```

- **Debug Overlay**: Show a debug overlay with coordinates and FPS. Also opens a second terminal that shows additional debug information.
  ```bash
  python main.py /path/to/your/video.mp4 --debug
  ```

You can also combine these options:
```bash
python main.py /path/to/your/video.mp4 --ascii --size 64 --debug
```
