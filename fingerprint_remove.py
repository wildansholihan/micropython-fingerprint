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

def remove_fingerprint(finger_id):
    """
    Removes a fingerprint with the specified ID from the sensor's database.
    """
    print(f"Attempting to remove fingerprint ID {finger_id}...")

    # Convert finger_id to high byte and low byte
    finger_id_high = (finger_id >> 8) & 0xFF
    finger_id_low = finger_id & 0xFF

    # Command: Delete template
    delete_cmd = [
        0xEF, 0x01,  # Start code
        0xFF, 0xFF, 0xFF, 0xFF,  # Device address
        0x01,  # Packet identifier (Command packet)
        0x00, 0x07,  # Packet length
        0x0C,  # Instruction code (Delete template)
        finger_id_high, finger_id_low,  # Start ID (High and Low bytes of ID)
        0x00, 0x01  # Number of templates to delete (1 template)
    ]

    # Calculate checksum
    checksum = sum(delete_cmd[6:]) & 0xFFFF
    delete_cmd.append(checksum >> 8)  # High byte of checksum
    delete_cmd.append(checksum & 0xFF)  # Low byte of checksum

    # Send the delete command
    send_packet(delete_cmd)
    response = read_response()

    # Debugging: Print the raw response from the sensor
    print(f"Raw response: {response}")

    # Parse the response
    if response and len(response) >= 12:
        if response[9] == 0x00:  # Response indicates success
            print(f"Fingerprint ID {finger_id} removed successfully.")
            return True
        elif response[9] == 0x01:  # Error: No such ID
            print(f"Error: Fingerprint ID {finger_id} does not exist.")
        else:
            print(f"Error: Response code {hex(response[9])}.")
    else:
        print("Invalid response received or communication error.")

    # If we reach here, removal was unsuccessful
    print(f"Failed to remove fingerprint ID {finger_id}.")
    return False

def delete_all_fingerprints_iteratively(start_id=0, end_id=100):
    """
    Deletes fingerprints by ID from start_id to end_id, with a progress indicator.
    """
    total_ids = end_id - start_id + 1  # Total number of IDs to process
    for finger_id in range(start_id, end_id + 1):
        print(f"Attempting to delete fingerprint ID {finger_id}...")

        # Command: Delete template (for a specific ID)
        finger_id_high = (finger_id >> 8) & 0xFF
        finger_id_low = finger_id & 0xFF

        delete_cmd = [
            0xEF, 0x01,  # Start code
            0xFF, 0xFF, 0xFF, 0xFF,  # Device address
            0x01,  # Packet identifier (Command packet)
            0x00, 0x07,  # Packet length
            0x0C,  # Instruction code (Delete template)
            finger_id_high, finger_id_low,  # Start ID (High and Low bytes of ID)
            0x00, 0x01  # Number of templates to delete (1 template)
        ]

        # Calculate checksum
        checksum = sum(delete_cmd[6:]) & 0xFFFF
        delete_cmd.append(checksum >> 8)  # High byte of checksum
        delete_cmd.append(checksum & 0xFF)  # Low byte of checksum

        # Send the delete command
        send_packet(delete_cmd)
        response = read_response()

        # Debugging: Print the raw response from the sensor
        print(f"Raw response: {response}")

        if response and len(response) >= 12:
            if response[9] == 0x00:  # Response indicates success
                print(f"Fingerprint ID {finger_id} removed successfully.")
            else:
                print(f"Error deleting fingerprint ID {finger_id}.")
        else:
            print(f"Failed to delete fingerprint ID {finger_id}.")

        # Calculate progress
        progress = (finger_id - start_id + 1) / total_ids * 100  # Percentage of progress
        print(f"Progress: {progress:.2f}%")

    print("Fingerprint deletion completed.")
    return True



