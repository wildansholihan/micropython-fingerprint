import board
import busio
import displayio
import adafruit_displayio_ssd1306
import time
from adafruit_display_text import label
import terminalio
import adafruit_imageload

# Path to the image file
IMAGE_FILE = "scan.bmp"
SPRITE_SIZE = (64, 64)
FRAMES = 28

# Initialize the display
def init_display(width=128, height=64, sda_pin=board.GP16, scl_pin=board.GP17):
    displayio.release_displays()
    i2c = busio.I2C(scl_pin, sda_pin)
    display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
    display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=width, height=height)
    group = displayio.Group()
    display.root_group = group
    return display, group

# Function to invert all colors in the sprite palette
def invert_colors(icon_pal):
    for i in range(len(icon_pal)):
        icon_pal[i] = (icon_pal[i] ^ 0xFFFFFF)  # Invert each color in the palette

# Function to display the sprite animation on the OLED
def display_sprite_animation(display, group, bmp_path):
    icon_bit, icon_pal = adafruit_imageload.load(bmp_path, bitmap=displayio.Bitmap, palette=displayio.Palette)
    invert_colors(icon_pal)
    
    icon_grid = displayio.TileGrid(
        icon_bit, pixel_shader=icon_pal,
        width=1, height=1,
        tile_height=SPRITE_SIZE[1], tile_width=SPRITE_SIZE[0],
        default_tile=0,
        x=32, y=0
    )
    
    group.append(icon_grid)

    timer = 0
    pointer = 0
    while True:
        if (timer + 0.1) < time.monotonic():
            icon_grid[0] = pointer
            pointer += 1
            timer = time.monotonic()
            if pointer >= FRAMES:
                pointer = 0

# Clear display content
def clear_display(group):
    """Clear all content on the display."""
    while len(group) > 0:
        group.pop()

# Word wrap function
def word_wrap(text, max_chars):
    """Split text into lines with a maximum number of characters per line."""
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars:
            current_line += (word + " ")
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())

    return lines

# Display text on the OLED screen
def display_text(display, group, font=terminalio.FONT, color=0xFFFFFF, text="", wrap_at=20):
    """
    Display word-wrapped text on the OLED.
    :param display: Display object
    :param group: Display group to add content
    :param font: Font to be used for text
    :param color: Color of the text
    :param text: Text to display
    :param wrap_at: Number of characters per line before wrapping
    """
    clear_display(group)

    lines = word_wrap(text, wrap_at)
    line_height = 12
    y_offset = 0

    for line in lines:
        if y_offset + line_height > display.height:
            break

        text_area = label.Label(font, text=line, color=color)
        text_area.anchor_point = (0, 0)
        text_area.anchored_position = (0, y_offset)
        group.append(text_area)

        y_offset += line_height

# Display text centered on the OLED screen
def display_centered_text(display, group, font=terminalio.FONT, color=0xFFFFFF, text="", wrap_at=20):
    """
    Display word-wrapped text centered on the OLED.
    :param display: Display object
    :param group: Display group to add content
    :param font: Font to be used for text
    :param color: Color of the text
    :param text: Text to display
    :param wrap_at: Number of characters per line before wrapping
    """
    clear_display(group)

    lines = word_wrap(text, wrap_at)
    line_height = 12
    total_height = len(lines) * line_height
    y_offset = max(0, (display.height - total_height) // 2)

    for line in lines:
        text_area = label.Label(font, text=line, color=color)
        text_area.anchor_point = (0.5, 0)
        text_area.anchored_position = (display.width // 2, y_offset)
        group.append(text_area)

        y_offset += line_height