from machine import UART, Pin
import time

# Configure UART for the fingerprint sensor
uart = UART(0, baudrate=57600, tx=Pin(0), rx=Pin(1))  # Adjust TX and RX pins as needed

def send_packet(data):
    uart.write(bytearray(data))

def read_response(timeout=2):
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < timeout * 1000:
        if uart.any():
            response = uart.read()
            if response:
                return response
    print("No response received.")
    return None

# Function to enroll a fingerprint
def enroll_fingerprint(finger_id):
    print("Step 1: Place your finger on the sensor.")
    
    # Command: Capture fingerprint image
    capture_image_cmd = [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x01, 0x00, 0x05]
    send_packet(capture_image_cmd)
    response = read_response()
    if response and response[9] == 0x00:
        print("Fingerprint image captured successfully.")
    else:
        print("Failed to capture fingerprint. Please try again.")
        return False

    # Command: Generate character file from image (Buffer 1)
    generate_char_cmd = [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x04, 0x02, 0x01, 0x00, 0x08]
    send_packet(generate_char_cmd)
    response = read_response()
    if response and response[9] == 0x00:
        print("Fingerprint template generated successfully.")
    else:
        print("Failed to generate fingerprint template. Please try again.")
        return False

    return store_fingerprint(finger_id)
    
def store_fingerprint(finger_id):
    print(f"Storing fingerprint template with ID {finger_id}...")
    
    # Convert finger_id to high byte and low byte
    finger_id_high = (finger_id >> 8) & 0xFF
    finger_id_low = finger_id & 0xFF

    # Command: Store template from Buffer 1 to storage
    store_cmd = [
        0xEF, 0x01,  # Start code
        0xFF, 0xFF, 0xFF, 0xFF,  # Device address
        0x01,  # Packet identifier (Command packet)
        0x00, 0x06,  # Packet length
        0x06,  # Instruction code (Store template)
        0x01,  # Buffer ID (Buffer 1)
        finger_id_high, finger_id_low  # Page ID
    ]

    # Calculate checksum
    checksum = sum(store_cmd[6:]) & 0xFFFF
    store_cmd.append(checksum >> 8)  # High byte of checksum
    store_cmd.append(checksum & 0xFF)  # Low byte of checksum

    # Send the command
    send_packet(store_cmd)
    response = read_response()

    if response and len(response) >= 12 and response[9] == 0x00:
        print("Fingerprint template stored successfully.")
        return True
    else:
        print("Failed to store fingerprint template.")
        return False
