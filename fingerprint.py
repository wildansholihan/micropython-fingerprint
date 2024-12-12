import time
from buzzer import beep
import board
import busio
from oled import init_display, display_text, display_centered_text, clear_display, display_image, display, group
from adafruit_fingerprint import Adafruit_Fingerprint
from bluetooth_CL import check_bluetooth_status
from wifi_pi import send_attendance_data, is_wifi_connected

# Initialize UART for communication with the fingerprint sensor
uart2 = busio.UART(board.GP0, board.GP1, baudrate=57600)

# Create a fingerprint sensor instance
finger = Adafruit_Fingerprint(uart2)

# Enroll a fingerprint with ID
def enroll_fingerprint(location):
    message = f"Checking if ID {location} is in use..."
    print(message)
    clear_display(group)
    display_centered_text(display, group, text=message, wrap_at=20)
    
    if finger.load_model(location) == 0:
        beep(2, 0.1)
        message = f"Error: ID {location} is already in use."
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        time.sleep(2)
        return

    display_image(display, group, "scan.bmp")
    while finger.get_image() != 0:  # Wait for finger placement
        pass
    
    display_image(display, group, "scanCheck.bmp")
    beep(1, 0.1)
    if finger.image_2_tz(1) != 0:
        beep(2, 0.1)
        message = "Error converting image!"
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        time.sleep(2)
        return

    message = "Place the finger again..."
    print(message)
    clear_display(group)
    display_centered_text(display, group, text=message, wrap_at=20)
    time.sleep(1)

    display_image(display, group, "scan.bmp")
    while finger.get_image() != 0:
        pass
    
    display_image(display, group, "scanCheck.bmp")
    beep(1, 0.1)
    if finger.image_2_tz(2) != 0:
        beep(2, 0.1)
        message = "Error converting image!"
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        time.sleep(2)
        return

    if finger.create_model() != 0:
        beep(2, 0.1)
        message = "Error creating model!"
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        time.sleep(2)
        return

    if finger.store_model(location) != 0:
        beep(2, 0.1)
        message = "Error storing model!"
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        time.sleep(2)
        return

    if is_wifi_connected:
        send_attendance_data(location)
        time.sleep(2)
    beep(2, 0.1)
    message = f"Fingerprint enrolled at ID {location}!"
    print(message)
    clear_display(group)
    display_centered_text(display, group, text=message, wrap_at=20)
    time.sleep(2)

# Search for a fingerprint
def search_fingerprint():
    display_image(display, group, "scan.bmp")
    
    while finger.get_image() != 0:
        pass
    
    display_image(display, group, "scanCheck.bmp")
    if finger.image_2_tz(1) != 0:
        beep(2, 0.1)
        message = "Error converting image!"
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        time.sleep(2)
        return

    if finger.finger_search() == 0:
        beep(1, 0.1)
        message = f"ID {finger.finger_id} found!"
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        send_attendance_data(finger.finger_id)
        time.sleep(2)
    else:
        beep(2, 0.1)
        message = "Fingerprint not found."
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        time.sleep(2)
        
def search_fingerprint_noBT():
    """
    Cari sidik jari tanpa Bluetooth, menampilkan gambar statis pada OLED saat pencarian berlangsung.
    """
    # Tampilkan gambar tunggal (statis) selama pencarian sidik jari
    display_image(display, group, "scan.bmp")

    # Loop untuk mencari sidik jari
    while finger.get_image() != 0:
        #is_wifi_connected()
        if check_bluetooth_status():
            return
        pass

    # Tampilkan gambar memproses
    display_image(display, group, "scanCheck.bmp")
    beep(1, 0.1)
    time.sleep(1)

    # Konversi gambar ke template
    if finger.image_2_tz(1) != 0:
        message = "Error converting image!"
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        # Beep untuk kesalahan
        beep(2, 0.1)  # Dua kali beep singkat
        time.sleep(2)
        return

    # Cari sidik jari di database
    if finger.finger_search() == 0:  # 0 indicates success
        message = f"ID {finger.finger_id} found!"
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        # Beep untuk keberhasilan
        beep(2, 0.1)  # Tiga kali beep singkat
        send_attendance_data(finger.finger_id)  # kirim id
        time.sleep(2)
    else:
        message = "Fingerprint not found."
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        # Beep untuk kesalahan
        beep(2, 0.1)  # Dua kali beep singkat
        time.sleep(2)

# Delete a fingerprint by ID
def remove_fingerprint(location):
    if finger.delete_model(location) == 0:
        beep(1, 0.1)
        message = f"ID {location} has been removed"
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        send_attendance_data(location)
        time.sleep(2)
    else:
        beep(2, 0.1)
        message = f"Error deleting ID {location}."
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        time.sleep(2)

# Delete all fingerprints
def remove_all_fingerprints():
    if finger.empty_library() == 0:
        beep(1, 0.1)
        message = "Fingerprint data cleared"
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        time.sleep(2)
    else:
        beep(2, 0.1)
        message = "Failed to clear all fingerprints."
        print(message)
        clear_display(group)
        display_centered_text(display, group, text=message, wrap_at=20)
        time.sleep(2)