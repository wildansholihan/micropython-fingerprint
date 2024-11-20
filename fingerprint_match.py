from oled import OLEDDisplay
from machine import UART, Pin
import time

oled_display = OLEDDisplay()

# Initialize UART for the fingerprint sensor
uart = UART(0, baudrate=57600, tx=Pin(0), rx=Pin(1))  # Adjust TX and RX pins as needed

# Function to send a packet to the sensor
def send_packet(data):
    uart.write(bytearray(data))

# Function to read response from the sensor
def read_response(timeout=2):
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < timeout * 1000:
        if uart.any():
            response = uart.read()
            if response:
                return response
    print("No response received.")
    oled_display.clear()
    oled_display.display_text("No response", 0, 7)
    time.sleep(2)
    return None

# Function to match a fingerprint
def match_fingerprint():
    print("Place your finger on the sensor for matching.")
    oled_display.clear()
    oled_display.display_text("place your", 0, 7)
    oled_display.display_text("finger", 0, 20)
    time.sleep(3)

    # Step 1: Capture fingerprint image
    capture_image_cmd = [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x01, 0x00, 0x05]
    send_packet(capture_image_cmd)
    response = read_response()
    if not response or (len(response) > 9 and response[9] != 0x00):
        print("Failed to capture fingerprint. Please try again.")
        oled_display.clear()
        oled_display.display_text("Capture failed", 0, 7)
        oled_display.display_text("Try again", 0, 20)
        time.sleep(3)  # Berikan waktu untuk pengguna sebelum percobaan ulang

    # Kirim ulang perintah untuk menangkap sidik jari
    send_packet(capture_image_cmd)
    response = read_response()

    # Validasi ulang tanggapan setelah percobaan ulang
    if not response or (len(response) > 9 and response[9] != 0x00):
        print("Failed to capture fingerprint on second attempt. Exiting.")
        oled_display.clear()
        oled_display.display_text("failed again", 0, 7)
        oled_display.display_text("Exiting...", 0, 20)
        time.sleep(3)
        return None  # Akhiri proses jika tetap gagal
    
    print("Fingerprint image captured successfully.")
    oled_display.clear()
    oled_display.display_text("Image captured", 0, 7)
    oled_display.display_text("successfully", 0, 20)
    time.sleep(2)

    # Step 2: Generate character file from image (Buffer 1)
    generate_char_cmd = [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x04, 0x02, 0x01, 0x00, 0x08]
    send_packet(generate_char_cmd)
    response = read_response()
    if not response or response[9] != 0x00:
        print("Failed to generate fingerprint template. Please try again.")
        oled_display.clear()
        oled_display.display_text("failed generate", 0, 7)
        oled_display.display_text("template", 0, 20)
        oled_display.display_text("try again...", 0, 33)
        time.sleep(3)
        
        send_packet(generate_char_cmd)
        response = read_response()
        
    if not response or response[9] != 0x00:
        print("Failed to generate fingerprint template. Please try again.")
        oled_display.clear()
        oled_display.display_text("failed generate", 0, 7)
        oled_display.display_text("again", 0, 20)
        oled_display.display_text("exiting...", 0, 33)
        time.sleep(2)
        return None
    print("Fingerprint template generated successfully.")
    oled_display.clear()
    oled_display.display_text("template generated", 0, 7)
    oled_display.display_text("successfully", 0, 20)
    time.sleep(2)

    # Step 3: Search the template in the database
    search_cmd = [
        0xEF, 0x01,  # Start code
        0xFF, 0xFF, 0xFF, 0xFF,  # Address
        0x01,  # Packet identifier (Command packet)
        0x00, 0x08,  # Packet length
        0x04,  # Instruction code (Search template)
        0x01,  # Buffer ID (Buffer 1)
        0x00, 0x00,  # Start page ID (high and low byte)
        0x00, 0xFF,  # Number of pages to search (high and low byte)
    ]

    # Calculate checksum
    checksum = sum(search_cmd[6:]) & 0xFFFF
    search_cmd.append(checksum >> 8)  # High byte of checksum
    search_cmd.append(checksum & 0xFF)  # Low byte of checksum

    # Send the search command
    send_packet(search_cmd)
    response = read_response()

    # Handle the response
    if response and len(response) >= 16:
        if response[9] == 0x00:  # Success
            page_id = (response[10] << 8) | response[11]
            match_score = (response[12] << 8) | response[13]
            print(f"Match found! ID: {page_id}, Score: {match_score}")
            oled_display.clear()
            oled_display.display_text(f"Match found! ID: {page_id}", 0, 7)
            oled_display.display_text(f"Score: {match_score}", 0, 20)
            time.sleep(2)
            return page_id
        elif response[9] == 0x09:  # No match
            print("No match found.")
            oled_display.clear()
            oled_display.display_text("No match found.", 0, 7)
            time.sleep(2)
            return None
        else:  # Error
            print(f"Error: {response[9]:02X}")
            oled_display.clear()
            oled_display.display_text(f"Error: {response[9]:02X}", 0, 7)
            time.sleep(2)
            return None
    else:
        print("Invalid or no response received.")
        oled_display.clear()
        oled_display.display_text("Invalid/no response", 0, 7)
        time.sleep(2)
        return None
