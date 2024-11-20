from machine import Pin, I2C
import ssd1306
import time

class OLEDDisplay:
    def __init__(self, i2c_id=0, scl_pin=17, sda_pin=16, freq=200000, max_retries=3):
        """
        Initialize the OLED display with the specified I2C configuration.
        """
        retry_count = 0
        while retry_count < max_retries:
            try:
                # Initialize I2C
                self.i2c = I2C(i2c_id, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=freq)
                devices = self.i2c.scan()
                if not devices:
                    raise RuntimeError("No I2C devices found. Check wiring!")
                print("I2C devices found:", [hex(addr) for addr in devices])
                
                # Set OLED address
                self.oled_address = devices[0]  # Assuming the first detected device is the OLED
                
                # Initialize the OLED
                self.oled = ssd1306.SSD1306_I2C(128, 64, self.i2c, addr=self.oled_address)
                self.clear()  # Clear the display
                print("OLED initialized successfully.")
                return  # Exit the retry loop upon successful initialization
            except Exception as e:
                print(f"Error initializing OLED (attempt {retry_count + 1}): {e}")
                retry_count += 1
                time.sleep(1)  # Wait 1 second before retrying
                if retry_count == max_retries:
                    print("Failed to initialize OLED after maximum retries.")
                    self.oled = None  # Set to None to indicate initialization failure

    def clear(self):
        """Clear the OLED display."""
        if self.oled:
            self.oled.fill(0)
            self.oled.show()

    def display_text(self, text, x=0, y=0):
        """
        Display text on the OLED at the specified coordinates.
        :param text: Text to display.
        :param x: X-coordinate (default: 0).
        :param y: Y-coordinate (default: 0).
        """
        if self.oled:
            self.oled.text(text, x, y)
            self.oled.show()
        else:
            print("OLED not initialized.")
    
    def display_text_centered(self, text):
        """
        Display text centered on the OLED screen.
        :param text: Text to display centered.
        """
        if self.oled:
            # Assuming each character is 6 pixels wide and 8 pixels high
            text_width = len(text) * 6
            text_height = 8  # Default font height is 8 pixels
            
            # Calculate position to center the text
            x = (128 - text_width) // 2
            y = (64 - text_height) // 2
            
            self.display_text(text, x, y)
        else:
            print("OLED not initialized.")

# Example usage when running oled.py directly
if __name__ == "__main__":
    oled_display = OLEDDisplay()
    if oled_display.oled:
        oled_display.display_text("Hello World!", 0, 0)
        oled_display.display_text("kumaha damang!", 0, 15)
        oled_display.display_text_centered("Centered Text!")
