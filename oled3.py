import board
import busio
import displayio
import adafruit_displayio_ssd1306
import time
import adafruit_imageload

# Path to the image file
IMAGE_FILE = "wifi.bmp"
SPRITE_SIZE = (64, 64)
FRAMES = 28

# Function to invert all colors in the sprite palette
def invert_colors(icon_pal):
    for i in range(len(icon_pal)):
        icon_pal[i] = (icon_pal[i] ^ 0xFFFFFF)  # Invert each color in the palette

# Function to display the sprite animation on the OLED
def display_sprite_animation(bmp_path):
    # Release any previously allocated displays
    displayio.release_displays()
    
    # Set up I2C connection
    i2c = busio.I2C(board.GP17, board.GP16)  # Change pins if necessary
    display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
    
    # Create display object
    display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)
    
    # Load the sprite image and palette
    icon_bit, icon_pal = adafruit_imageload.load(bmp_path, bitmap=displayio.Bitmap, palette=displayio.Palette)
    invert_colors(icon_pal)
    
    # Set up a tile grid for displaying the sprite
    icon_grid = displayio.TileGrid(
        icon_bit, pixel_shader=icon_pal,
        width=1, height=1,
        tile_height=SPRITE_SIZE[1], tile_width=SPRITE_SIZE[0],
        default_tile=0,
        x=32, y=0
    )
    
    # Create a group and add the tile grid to it
    group = displayio.Group()
    group.append(icon_grid)
    
    # Set the display's root group
    display.root_group = group
    
    # Start the animation loop
    timer = 0
    pointer = 0
    while True:
        if (timer + 0.1) < time.monotonic():
            icon_grid[0] = pointer
            pointer += 1
            timer = time.monotonic()
            if pointer >= FRAMES:  # Reset the animation when it reaches the last frame
                pointer = 0

    # Clear the animation and return the display object for the next step
    display.root_group = None
    return display

display_sprite_animation("wifi.bmp")