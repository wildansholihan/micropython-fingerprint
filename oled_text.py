import board
import busio
import displayio
from adafruit_display_text import label
import terminalio
import adafruit_displayio_ssd1306

# Initialize the display
def init_display(width=128, height=64, sda_pin=board.GP16, scl_pin=board.GP17):
    displayio.release_displays()
    i2c = busio.I2C(scl_pin, sda_pin)
    display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
    display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=width, height=height)
    
    group = displayio.Group()
    display.root_group = group
    
    return display, group

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

    # Perform word-wrap
    lines = word_wrap(text, wrap_at)

    # Calculate vertical spacing
    line_height = 12  # Approximate height of each line
    y_offset = 0

    for line in lines:
        if y_offset + line_height > display.height:
            break  # Stop displaying if text exceeds the screen height

        text_area = label.Label(font, text=line, color=color)
        text_area.anchor_point = (0, 0)  # Align each line to top-left
        text_area.anchored_position = (0, y_offset)  # Position line at current offset
        group.append(text_area)

        y_offset += line_height  # Move down for the next line

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

    # Perform word-wrap
    lines = word_wrap(text, wrap_at)

    # Calculate total height of the wrapped text
    line_height = 12  # Approximate height of each line
    total_height = len(lines) * line_height

    # Calculate starting Y position to center vertically
    y_offset = max(0, (display.height - total_height) // 2)

    for line in lines:
        # Create a text area for each line and center it horizontally
        text_area = label.Label(font, text=line, color=color)
        text_area.anchor_point = (0.5, 0)  # Center horizontally
        text_area.anchored_position = (display.width // 2, y_offset)
        group.append(text_area)

        # Move down for the next line
        y_offset += line_height
