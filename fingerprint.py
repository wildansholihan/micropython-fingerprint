from pyfingerprint import PyFingerprint
import uasyncio as asyncio
from machine import UART, Pin
import time

# Inisialisasi UART dan Fingerprint Sensor
uart = UART(1, baudrate=57600, tx=Pin(8), rx=Pin(9))  # UART2 di ESP32
finger = PyFingerprint(uart)

# Fungsi untuk memverifikasi koneksi ke sensor
def initialize_sensor():
    try:
        if finger.verifyPassword():
            print("Fingerprint sensor initialized successfully.")
        else:
            print("Wrong password for fingerprint sensor.")
            return False
    except Exception as e:
        print(f"Failed to initialize sensor: {e}")
        return False
    return True

# Fungsi untuk mendaftarkan sidik jari
def enroll_fingerprint(location):
    print("Step 1: Place your finger on the sensor...")
    while not finger.readImage(location):
        pass
    print("Fingerprint image captured.")

    # Konversi gambar menjadi karakteristik di buffer 1
    finger.convertImage(0x01)
    print("Fingerprint image converted to characteristics.")

    # Coba membuat model/template
    if finger.createTemplate(location):
        print("Fingerprint template created successfully.")
    else:
        print("Failed to create fingerprint template.")
        return

    # Menyimpan template ke database di posisi kosong
    position = finger.storeTemplate(location)
    print(f"Fingerprint stored at position: {position}")

# Fungsi untuk mencocokkan sidik jari
def match_fingerprint():
    print("Step 1: Place your finger on the sensor...")
    while not finger.readImage():
        pass
    print("Fingerprint image captured.")

    # Konversi gambar ke buffer 1
    finger.convertImage(0x01)

    # Mencari template di database
    position, accuracy = finger.searchTemplate()
    if position >= 0:
        print(f"Fingerprint matched at position {position} with accuracy {accuracy}")
    else:
        print("No matching fingerprint found.")

# Fungsi untuk menghapus template sidik jari
def remove_fingerprint(location):
    try:
        if finger.deleteTemplate(location):
            print(f"Fingerprint at position {position} removed successfully.")
        else:
            print("Failed to delete fingerprint.")
    except Exception as e:
        print(f"Error: {e}")

# Fungsi untuk menghapus seluruh database sidik jari
def clear_all_fingerprints():
    try:
        if finger.clearDatabase():
            print("All fingerprints cleared successfully.")
        else:
            print("Failed to clear fingerprints.")
    except Exception as e:
        print(f"Error: {e}")


# Menu utama
'''if __name__ == "__main__":
    if not initialize_sensor():
        print("Exiting program...")
    else:
        while True:
            print("\nChoose an option:")
            print("1 - Enroll Fingerprint")
            print("2 - Match Fingerprint")
            print("3 - Delete Fingerprint")
            print("4 - Clear All Fingerprints")
            print("5 - Exit")

            choice = input("Enter your choice: ").strip()
            if choice == "1":
                enroll_fingerprint()
            elif choice == "2":
                match_fingerprint()
            elif choice == "3":
                position = int(input("Enter position to delete (0-127): "))
                remove_fingerprint(position)
            elif choice == "4":
                clear_all_fingerprints()
            elif choice == "5":
                print("Exiting program...")
                break
            else:
                print("Invalid choice. Please try again.")'''