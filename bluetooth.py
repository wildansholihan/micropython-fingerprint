import board
import busio
import time

# Initialize UART globally for reuse
uart = busio.UART(board.GP0, board.GP1, baudrate=38400)  # Default baud rate for AT commands


def send_at_command(command):
    """Send AT command to HC-05 and return response."""
    uart.write((command + "\r\n").encode('utf-8'))
    time.sleep(0.5)
    response = uart.read(64)  # Read up to 64 bytes
    if response:
        return response.decode('utf-8').strip()
    return "No response"


def rename_bluetooth(new_name):
    """Rename the HC-05 Bluetooth module."""
    print(f"Renaming Bluetooth to {new_name}...")
    response = send_at_command(f"AT+NAME={new_name}")
    print(f"Rename Response: {response}")


def make_bluetooth_pairable():
    """Make the Bluetooth module pairable and discoverable."""
    print("Starting Bluetooth configuration...")
    
    # Renaming Bluetooth device
    response = send_at_command("AT+NAME=MyNewBluetoothName")  # Set name
    print(f"Rename Response: {response}")
    
    # Set HC-05 to slave mode
    response = send_at_command("AT+ROLE=0")  # Set to Slave mode
    if "OK" in response:
        print("Already in slave mode.")
    else:
        print(f"Role Response: {response}")
    
    # Allow pairing with any device
    response = send_at_command("AT+CMODE=1")  # Allow connections from any device
    print(f"CMODE Response: {response}")
    
    # Set pairing password
    response = send_at_command('AT+PSWD="1234"')  # Set pairing password
    print(f"Password Response: {response}")
    
    # Check Bluetooth state
    state = send_at_command("AT+STATE?")
    print(f"Bluetooth State: {state}")
    
    # Try resetting the module to clear any existing state
    #print("Resetting HC-05 module...")
    #reset_response = send_at_command("AT+RESET")
    #print(f"Reset Response: {reset_response}")
    
    # Try to start Bluetooth inquiry mode (discoverable mode)
    print("Attempting to start Bluetooth inquiry (discoverable mode)...")
    inquiry_response = send_at_command("AT+INQ")
    print(f"Bluetooth Inquiry: {inquiry_response}")
    
    # Check Bluetooth name again
    name_response = send_at_command("AT+NAME?")
    print(f"Bluetooth name response: {name_response}")
    
    # Check Bluetooth inquiry status again
    inquiry_status = send_at_command("AT+INQ")
    print(f"Bluetooth inquiry response: {inquiry_status}")


def check_bluetooth_name():
    """Check the Bluetooth name set on the module."""
    print("Checking current Bluetooth name...")
    response = send_at_command("AT+NAME?")
    print(f"Bluetooth name response: {response}")


def check_bluetooth_status():
    """Check Bluetooth module status."""
    print("Checking Bluetooth module status...")
    response = send_at_command("AT+INQ")
    print(f"Bluetooth inquiry response: {response}")


# Main function to initialize and configure HC-05
def configure_bluetooth():
    print("Starting Bluetooth configuration...")
    
    # Rename the Bluetooth module
    rename_bluetooth("MyNewBluetoothName")
    
    # Make Bluetooth pairable and set it to slave mode
    make_bluetooth_pairable()
    
    # Check Bluetooth name
    check_bluetooth_name()
    
    # Check Bluetooth status
    check_bluetooth_status()


# Run the main configuration function
configure_bluetooth()