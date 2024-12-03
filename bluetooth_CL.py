import board
import digitalio
import busio
import time

# Initialize UART globally for Bluetooth communication
uart = busio.UART(board.GP4, board.GP5, baudrate=38400)  # Default baud rate for HC-05 (Data Mode)

# Initialize pin STATE from HC-05 to monitor connection status
state_pin = digitalio.DigitalInOut(board.GP11)  # Ganti dengan GPIO yang Anda pilih
state_pin.direction = digitalio.Direction.INPUT

# Initialize pin EN (Enable) for mode control
en_pin = digitalio.DigitalInOut(board.GP22)  # Pin GPIO untuk EN
en_pin.direction = digitalio.Direction.OUTPUT
en_pin.value = True  # Default HIGH, HC-05 dalam mode Data

def send_at_command(command):
    """Send AT command to HC-05 and return response."""
    uart.write((command + "\r\n").encode('utf-8'))
    time.sleep(0.5)
    response = uart.read(128)  # Read up to 128 bytes for larger responses
    if response:
        return response.decode('utf-8').strip()
    return "No response"

def enter_at_mode():
    """Set the HC-05 module to AT mode by setting EN LOW."""
    print("Entering AT Mode...")
    en_pin.value = False  # Set EN pin to LOW to enter AT mode
    time.sleep(2)  # Delay to ensure mode change
    print("HC-05 should now be in AT mode. You can manually call AT commands.")

def ensure_at_mode():
    """Ensure the HC-05 module is in AT mode."""
    print("Checking AT mode...")
    response = send_at_command("AT")
    if "OK" in response:
        print("AT mode active.")
        # If in AT mode, send AT+RESET to restart and exit AT mode.
        send_at_command("AT+RESET")
        print("AT+RESET sent, exiting AT mode.")
    else:
        print("Error: Module not in AT mode. Proceeding to check Bluetooth connection.")

def check_bluetooth_status():
    """Check Bluetooth connection status via STATE pin."""
    print("Checking Bluetooth connection via STATE pin...")
    state = state_pin.value  # Read the value of STATE pin (High if connected, Low if not)
    
    if state:
        print("Bluetooth is connected to a device.")
        return True
    else:
        print("No Bluetooth connection detected.")
        return False

# Main function to initialize and configure HC-05
def configure_bluetooth():
    print("Starting Bluetooth configuration...")

    # Check Bluetooth connection status via STATE pin
    check_bluetooth_status()

    # Module is ready for communication in Data mode
    print("Bluetooth module is ready for communication.")

# NOTE: Manual function calls for entering/exiting AT mode
# Uncomment and use when needed:
# enter_at_mode()

# Run the main configuration function