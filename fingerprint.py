import uasyncio as asyncio
from pyfingerprint import PyFingerprint
from machine import UART, Pin
from data import create_data
from oled import interact_txt

# Inisialisasi UART dan Fingerprint Sensor
uart = UART(1, baudrate=57600, tx=Pin(8), rx=Pin(9))  # UART1 di Raspberry Pi Pico W
finger = PyFingerprint(uart)

# Fungsi untuk verifikasi koneksi sensor
async def initialize_sensor():
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

# Fungsi asinkronus untuk enroll fingerprint
async def enroll_fingerprint(ID, NIK, NAME):
    print("Step 1: Place your finger on the sensor...")
    interact_txt("tempelkan jari")
    while not finger.readImage():
        await asyncio.sleep(0.1)  # Hindari loop blocking
    print("Fingerprint image captured.")

    if finger.convertImage(0x01):
        print("Step 1 complete. Remove your finger.")
        interact_txt("angkat jari")
    
    await asyncio.sleep(2)  # Tunggu sebelum scan ulang
    
    print("Step 2: Place the same finger again...")
    interact_txt("tempelkan kembali")
    while not finger.readImage():
        await asyncio.sleep(0.1)
    print("Fingerprint image captured again.")

    if finger.convertImage(0x02):
        print("Step 2 complete.")

    if finger.createTemplate():
        print("Fingerprint template created successfully.")
        create_data({'id': ID, 'nik': NIK, 'nama': NAME})
        interact_txt(f"terima kasih! {NAME}")
    else:
        print("Failed to create fingerprint template.")
        return

    # Simpan template ke lokasi tertentu
    position = finger.storeTemplate(ID)
    print(f"Fingerprint stored at position: {position}")

# Fungsi asinkronus untuk mencocokkan sidik jari
async def match_fingerprint():
    print("Step 1: Place your finger on the sensor...")
    while not finger.readImage():
        await asyncio.sleep(0.1)
    print("Fingerprint image captured.")

    finger.convertImage(0x01)

    position, accuracy = finger.searchTemplate()
    if position >= 0:
        print(f"Fingerprint matched at position {position} with accuracy {accuracy}")
    else:
        print("No matching fingerprint found.")

# Fungsi asinkronus untuk menghapus sidik jari
async def remove_fingerprint(ID):
    try:
        if finger.deleteTemplate(ID):
            print(f"Fingerprint at position {ID} removed successfully.")
        else:
            print("Failed to delete fingerprint.")
    except Exception as e:
        print(f"Error: {e}")

# Fungsi asinkronus untuk menghapus semua sidik jari
async def clear_all_fingerprints():
    try:
        if finger.clearDatabase():
            print("All fingerprints cleared successfully.")
        else:
            print("Failed to clear fingerprints.")
    except Exception as e:
        print(f"Error: {e}")

'''

# Menu utama asinkronus
async def main():
    if not await initialize_sensor():
        print("Exiting program...")
        return

    while True:
        print("\nChoose an option:")
        print("1 - Enroll Fingerprint")
        print("2 - Match Fingerprint")
        print("3 - Delete Fingerprint")
        print("4 - Clear All Fingerprints")
        print("5 - Exit")

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            ID = int(input("Enter storage ID (0-127): "))
            NIK = input("Enter NIK: ")
            NAME = input("Enter Name: ")
            await enroll_fingerprint(ID, NIK, NAME)
        elif choice == "2":
            await match_fingerprint()
        elif choice == "3":
            ID = int(input("Enter position to delete (0-127): "))
            await remove_fingerprint(ID)
        elif choice == "4":
            await clear_all_fingerprints()
        elif choice == "5":
            print("Exiting program...")
            break
        else:
            print("Invalid choice. Please try again.")
            
'''

# Jalankan program
#asyncio.run(main())