import time
import board
import busio
from oled import init_display, display_text, display_centered_text, clear_display, display_image, display, group
from adafruit_fingerprint import Adafruit_Fingerprint
from bluetooth_CL import check_bluetooth_status
from wifi_pi import send_attendance_data, get_attendance_data

# Initialize UART for communication with the fingerprint sensor
uart2 = busio.UART(board.GP0, board.GP1, baudrate=57600)

# Create a fingerprint sensor instance
finger = Adafruit_Fingerprint(uart2)


# Function to enroll a fingerprint with ID and finger validation
def enroll_fingerprint(location):
    # Check if the ID already exists
    message = f"Checking if ID {location} is in use..."
    print(message)
    clear_display(group)
    display_centered_text(display, group, text=message, wrap_at=20)
    
    if finger.load_model(location) == 0:  # 0 indicates success, meaning ID exists
        message = f"Error: ID {location} is already in use."
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        return
    
    # Check if the fingerprint is already registered
    message = "Place finger to check if registered..."
    print(message)
    clear_display(group)
    display_centered_text(display, group, text=message, wrap_at=20)
    
    while finger.get_image() != 0:  # Wait until a valid image is captured
        pass
    if finger.image_2_tz(1) != 0:
        message = "Error converting image!"
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        return
    
    if finger.finger_search() == 0:  # 0 indicates a match was found
        message = f"Error: Fingerprint exists with ID {finger.finger_id}."
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        return
    
    # Proceed with enrollment
    message = "Place finger for enrollment..."
    print(message)
    clear_display(group)
    display_centered_text(display, group, text=message, wrap_at=20)
    
    while finger.get_image() != 0:  # Wait for a valid image
        pass
    if finger.image_2_tz(1) != 0:
        message = "Error converting image!"
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        return
    
    message = "Remove your finger..."
    print(message)
    clear_display(group)
    display_centered_text(display, group, text=message, wrap_at=20)
    time.sleep(1)
    
    message = "Place the same finger again..."
    print(message)
    clear_display(group)
    display_centered_text(display, group, text=message, wrap_at=20)
    while finger.get_image() != 0:
        pass
    if finger.image_2_tz(2) != 0:
        message = "Error converting image!"
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        return
    
    if finger.create_model() != 0:
        message = "Error creating model!"
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        return
    if finger.store_model(location) != 0:
        message = "Error storing model!"
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        return
    
    send_attendance_data(location)
    message = f"Fingerprint enrolled successfully at ID {location}!"
    print(message)
    clear_display(group)
    display_centered_text(display, group, text=message, wrap_at=20)

# Function to search for a fingerprint
def search_fingerprint():
    message = "Place your finger on the sensor..."
    print(message)
    clear_display(group)
    display_centered_text(display, group, text=message, wrap_at=20)
    
    while finger.get_image() != 0:  # Wait for a valid image
        pass
    if finger.image_2_tz(1) != 0:
        message = "Error converting image!"
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        return
    
    if finger.finger_search() == 0:  # 0 indicates success
        message = f"Found fingerprint at ID {finger.finger_id} with confidence {finger.confidence}."
        print(message)
        clear_display(group)
        display_text(display, group, text=message, wrap_at=25)
    else:
        message = "Fingerprint not found."
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)


def search_fingerprint_noBT():
    """
    Cari sidik jari tanpa Bluetooth, menampilkan gambar statis pada OLED saat pencarian berlangsung.
    """
    # Tampilkan gambar tunggal (statis) selama pencarian sidik jari
    display_image(display, group, "scan.bmp")

    # Loop untuk mencari sidik jari
    while finger.get_image() != 0 and not check_bluetooth_status():
        pass
    if finger.image_2_tz(1) != 0:
        message = "Error converting image!"
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        time.sleep(2)
        return

    if finger.finger_search() == 0:  # 0 indicates success
        message = f"Found fingerprint at ID {finger.finger_id} with confidence {finger.confidence}."
        print(message)
        clear_display(group)
        display_text(display, group, text=message, wrap_at=25)
        get_attendance_data(finger.finger_id)
        time.sleep(2)
    else:
        message = "Fingerprint not found."
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        time.sleep(2)

# Function to remove a fingerprint by ID
def remove_fingerprint(location):
    message = f"Removing fingerprint at ID {location}..."
    print(message)
    clear_display(group)
    display_centered_text(display, group, text=message, wrap_at=20)
    
    if finger.delete_model(location) == 0:  # 0 indicates success
        message = f"Fingerprint at ID {location} removed successfully!"
    else:
        message = f"Failed to remove fingerprint at ID {location}."
    
    print(message)
    clear_display(group)
    display_centered_text(display, group, text=message, wrap_at=20)

# Function to remove all fingerprints
def remove_all_fingerprints():
    message = "Removing all fingerprints..."
    print(message)
    clear_display(group)
    display_centered_text(display, group, text=message, wrap_at=20)
    
    if finger.empty_library() == 0:  # 0 indicates success
        message = "All fingerprints removed successfully!"
    else:
        message = "Failed to remove fingerprints."
    
    print(message)
    clear_display(group)
    display_centered_text(display, group, text=message, wrap_at=20)