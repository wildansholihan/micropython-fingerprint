import board
import busio
import time

# Initialize UART globally for reuse
uart = busio.UART(board.GP4, board.GP5, baudrate=38400)  # Default baud rate for AT commands

def send_at_command(command):
    """Send AT command to HC-05 and return response."""
    uart.write((command + "\r\n").encode('utf-8'))
    time.sleep(0.5)
    response = uart.read(128)  # Read up to 128 bytes for larger responses
    if response:
        return response.decode('utf-8').strip()
    return "No response"

def ensure_at_mode():
    """Ensure the HC-05 module is in AT mode."""
    print("Checking AT mode...")
    response = send_at_command("AT")
    if "OK" in response:
        print("AT mode active.")
    else:
        print("Error: Module not in AT mode. Check hardware setup.")
        exit()

def rename_bluetooth(new_name):
    """Rename the HC-05 Bluetooth module."""
    print(f"Renaming Bluetooth to {new_name}...")
    response = send_at_command(f"AT+NAME={new_name}")
    if "OK" in response:
        print(f"Rename successful. Current name: {new_name}")
    else:
        print(f"Rename failed. Response: {response}")

def enable_discoverable_mode():
    """Enable discoverable mode and exit AT mode."""
    print("Setting module to discoverable mode...")

    # Set to slave mode
    response = send_at_command("AT+ROLE=0")
    print(f"Set Role Response: {response}")
    
    # Allow pairing with any device
    response = send_at_command("AT+CMODE=1")
    print(f"Set Connect Mode Response: {response}")
    
    # Initialize Bluetooth to ensure discoverable mode
    response = send_at_command("AT+INIT")
    if "OK" not in response:
        print(f"Initialize failed. Response: {response}")
        return
    
    print("Discoverable mode enabled. Exit AT mode manually.")

def make_bluetooth_pairable():
    """Make the Bluetooth module pairable and discoverable."""
    print("Starting Bluetooth configuration...")

    # Rename Bluetooth device
    rename_bluetooth("MyNewBluetoothName")
    
    # Set HC-05 to slave mode
    response = send_at_command("AT+ROLE=0")
    print(f"Role Response: {response}")
    
    # Allow pairing with any device
    response = send_at_command("AT+CMODE=1")
    print(f"CMODE Response: {response}")
    
    # Set pairing password
    response = send_at_command('AT+PSWD="1234"')
    print(f"Password Response: {response}")
    
    # Enable discoverable mode
    enable_discoverable_mode()
    
    # Check Bluetooth name again
    name_response = send_at_command("AT+NAME?")
    print(f"Bluetooth name response: {name_response}")
    
    # Check Bluetooth state
    state = send_at_command("AT+STATE?")
    print(f"Bluetooth State: {state}")

def check_bluetooth_name():
    """Check the Bluetooth name set on the module."""
    print("Checking current Bluetooth name...")
    response = send_at_command("AT+NAME?")
    print(f"Bluetooth name response: {response}")

def check_bluetooth_status():
    """Check Bluetooth module status."""
    print("Checking Bluetooth module status...")
    response = send_at_command("AT+STATE?")
    print(f"Bluetooth state response: {response}")

def exit_at_mode():
    """Guide to exit AT mode manually."""
    print("Exit AT mode by releasing the button or changing EN/KEY pin to LOW.")

# Main function to initialize and configure HC-05
def configure_bluetooth():
    print("Starting Bluetooth configuration...")
    
    # Ensure the module is in AT mode
    ensure_at_mode()
    
    # Rename the Bluetooth module
    rename_bluetooth("MyNewBluetoothName")
    
    # Make Bluetooth pairable and set it to slave mode
    make_bluetooth_pairable()
    
    # Exit AT mode to make it discoverable
    exit_at_mode()

# Run the main configuration function
# configure_bluetooth()