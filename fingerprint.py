import time
import board
import busio
from adafruit_fingerprint import Adafruit_Fingerprint

# Initialize UART for communication with the fingerprint sensor
uart = busio.UART(board.GP0, board.GP1, baudrate=57600)

# Create a fingerprint sensor instance
finger = Adafruit_Fingerprint(uart)

# Function to enroll a fingerprint with ID and finger validation
def enroll_fingerprint(location):
    # Check if the ID already exists
    print(f"Checking if ID {location} is already in use...")
    if finger.load_model(location) == 0:  # 0 indicates success, meaning ID exists
        print(f"Error: ID {location} is already in use. Choose a different ID.")
        return
    
    # Check if the fingerprint is already registered
    print("Place your finger on the sensor to check if it is already registered...")
    while finger.get_image() != 0:  # Wait until a valid image is captured
        pass
    if finger.image_2_tz(1) != 0:
        print("Error converting image!")
        return
    if finger.finger_search() == 0:  # 0 indicates a match was found
        print(f"Error: This fingerprint is already registered with ID {finger.finger_id}.")
        return
    
    # Proceed with enrollment
    print("Place your finger on the sensor for enrollment...")
    while finger.get_image() != 0:  # Wait for a valid image
        pass
    if finger.image_2_tz(1) != 0:
        print("Error converting image!")
        return
    print("Remove your finger...")
    time.sleep(1)
    
    print("Place the same finger again...")
    while finger.get_image() != 0:
        pass
    if finger.image_2_tz(2) != 0:
        print("Error converting image!")
        return
    
    if finger.create_model() != 0:
        print("Error creating model!")
        return
    if finger.store_model(location) != 0:
        print("Error storing model!")
        return
    
    print(f"Fingerprint enrolled successfully at location {location}")

# Function to search for a fingerprint
def search_fingerprint():
    print("Place your finger on the sensor...")
    while finger.get_image() != 0:  # 0 indicates OK
        pass
    if finger.image_2_tz(1) != 0:
        print("Error converting image!")
        return
    
    # Call finger_search and capture the response
    result = finger.finger_search()
    if result == 0:  # 0 indicates success
        print(f"Found fingerprint at ID {finger.finger_id} with confidence {finger.confidence}")
    else:
        print("Fingerprint not found")
        
# Function to remove a fingerprint by ID
def remove_fingerprint(location):
    print(f"Attempting to remove fingerprint at ID {location}...")
    if finger.delete_model(location) == 0:  # 0 indicates success
        print(f"Fingerprint at ID {location} removed successfully!")
    else:
        print(f"Failed to remove fingerprint at ID {location}.")
        
# Function to remove all fingerprints
def remove_all_fingerprints():
    print("Attempting to remove all fingerprints...")
    if finger.empty_library() == 0:  # 0 indicates success
        print("All fingerprints have been removed successfully!")
    else:
        print("Failed to remove fingerprints.")

