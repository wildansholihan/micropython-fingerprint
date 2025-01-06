import time
from machine import Pin, I2C
#import terminalio
import ssd1306
import framebuf
import os
import ustruct

# Initialize the display
def init_display(width=128, height=64, sda_pin=16, scl_pin=17):
    i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin))  # Initialize I2C bus
    display = ssd1306.SSD1306_I2C(width, height, i2c)  # Initialize the display
    return display

display = init_display()

# Function to invert all colors in the sprite palette
def invert_image(data):
    return bytearray(~b & 0xFF for b in data)

def flip_vertical(data, width, height):
    """Flip the image data vertically."""
    row_size = width // 8  # Bytes per row
    flipped = bytearray(len(data))
    for y in range(height):
        for x in range(row_size):
            flipped[y * row_size + x] = data[(height - 1 - y) * row_size + x]
    return flipped

# Function to display the sprite animation on the display
def display_image(display, bmp_path, x=0, y=0, scale_factor=1):
    clear_display(display)
    try:
        with open(bmp_path, "rb") as f:
            f.seek(62)  # Skip BMP header
            bmp_data = bytearray(f.read(512))  # Read 64x64 pixel data
            
            # Optional: Flip the image vertically
            bmp_data = flip_vertical(bmp_data, 64, 64)
            
            # Invert the image if necessary
            bmp_data = invert_image(bmp_data)
            
            # Resize image if scale_factor is different from 1
            if scale_factor != 1:
                bmp_data = resize_image(bmp_data, 64, 64, scale_factor)
                width = int(64 * scale_factor)
                height = int(64 * scale_factor)
            else:
                width, height = 64, 64
            
            # Load into framebuffer
            fb = framebuf.FrameBuffer(bmp_data, width, height, framebuf.MONO_HLSB)
            display.fill(0)
            display.blit(fb, x, y)
            display.show()
    except Exception as e:
        print("Error:", e)


# Function to display the sprite animation on the display
def resize_image(data, original_width, original_height, scale_factor):
    """Resize the image by a scale factor."""
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)
    
    # Pastikan lebar dan tinggi adalah kelipatan 8
    new_width = (new_width + 7) // 8 * 8
    new_height = (new_height + 7) // 8 * 8
    
    resized_data = bytearray((new_width * new_height) // 8)  # Ukuran data baru berdasarkan lebar dan tinggi baru
    
    # Resize logic: iterate through each pixel of the new image
    for y in range(new_height):
        for x in range(new_width):
            original_x = int(x / scale_factor)
            original_y = int(y / scale_factor)
            original_index = (original_y * (original_width // 8)) + (original_x // 8)
            resized_index = (y * (new_width // 8)) + (x // 8)
            bit_offset = 7 - (x % 8)
            
            # Pastikan kita mengakses indeks yang valid
            if original_index < len(data):  # Cek agar indeks tidak melebihi panjang data
                if (data[original_index] & (1 << (7 - original_x % 8))):
                    resized_data[resized_index] |= (1 << bit_offset)
    
    return resized_data


# Clear display content
def clear_display(display):
    """Clear all content on the display."""
    display.fill(0)  # Fill the screen with black
    display.show()

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

# Display text on the display screen
def display_text(display, text="", wrap_at=20):
    """
    Display word-wrapped text on the display.
    :param display: Display object
    :param text: Text to display
    :param wrap_at: Number of characters per line before wrapping
    """
    clear_display(display)

    lines = word_wrap(text, wrap_at)
    line_height = 10  # Approximate line height
    y_offset = 0

    for line in lines:
        if y_offset + line_height > display.height:
            break
        display.text(line, 0, y_offset)
        y_offset += line_height

# Display text centered on the display screen
def display_centered_text(display, color=0xFFFFFF, text="", wrap_at=20):
    """
    Display word-wrapped text centered on the display.
    :param display: Display object
    :param text: Text to display
    :param wrap_at: Number of characters per line before wrapping
    """
    #clear_display(display)
    clear_display(display)
    # Wrap the text based on the provided wrap_at
    lines = word_wrap(text, wrap_at)
    
    # Estimate font height and width per character for proper text positioning
    line_height = 10  # Assumed line height for default font
    total_height = len(lines) * line_height
    y_offset = max(0, (display.height - total_height) // 2)  # Center vertically

    for line in lines:
        # Center the text horizontally
        text_width = len(line) * 6  # Approximate width for each character
        x_offset = (display.width - text_width) // 2
        
        # Display the text
        display.text(line, x_offset, y_offset)
        y_offset += line_height
    display.show()
        
# Test the function
display_image(display, "scanCheck.bmp", 0, 0, scale_factor=0.4)  # Adjust scale_factor for resizing
display_centered_text(display, text="test.")