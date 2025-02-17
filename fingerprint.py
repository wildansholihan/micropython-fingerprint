import uasyncio as asyncio
from pyfingerprint import PyFingerprint
from machine import UART, Pin
from data import (
    create_data,
    delete_id,
    create_log,
    clear_all_id,
    
)
from oled import interact_txt, menu, cycle_images, cross, check
from time import sleep
from audio import beep, bye, thanks

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
    interact_txt("Tempelkan jari!")
    while not finger.readImage():
        await asyncio.sleep(0.1)  # Hindari loop blocking
    print("Fingerprint image captured.")

    if finger.convertImage(0x01):
        print("Step 1 complete. Remove your finger.")
        interact_txt("Angkat jari sebentar")
    
    await asyncio.sleep(2)  # Tunggu sebelum scan ulang
    
    print("Step 2: Place the same finger again...")
    interact_txt("Tempelkan\nkembali!")
    while not finger.readImage():
        await asyncio.sleep(0.1)
    print("Fingerprint image captured again.")

    if finger.convertImage(0x02):
        print("Step 2 complete.")

    if finger.createTemplate():
        print("Fingerprint template created successfully.")
        create_data({'id': ID, 'nik': NIK, 'nama': NAME})
        create_log(ID)
        await asyncio.sleep(2)
        interact_txt(f"Terima kasih!\n{NAME}!")
        await asyncio.sleep(2)
    else:
        print("Failed to create fingerprint template.")
        cross()
        await asyncio.sleep(2)
        interact_txt("Gagal membuat ID!")
        await asyncio.sleep(2)
        menu()
        return

    # Simpan template ke lokasi tertentu
    position = finger.storeTemplate(ID)
    print(f"Fingerprint stored at position: {position}")
    menu()

# Fungsi asinkronus untuk mencocokkan sidik jari
async def match_fingerprint():
    print("Step 1: Place your finger on the sensor...")
    interact_txt("Tempelkan jari!")
    while not finger.readImage():
        await asyncio.sleep(0.1)
    print("Fingerprint image captured.")

    finger.convertImage(0x01)

    position, accuracy = finger.searchTemplate()
    cycle_images()
    if position >= 0:
        print(f"Fingerprint matched at position {position} with accuracy {accuracy}")
        create_log(position)
        check()
        thanks()
        interact_txt("terima kasih!")
        await asyncio.sleep(2)
    else:
        print("No matching fingerprint found.")
        cross()
        bye()
        interact_txt("Sidik jari\n tidak dikenali!")
        await asyncio.sleep(2)
    menu()

# Fungsi asinkronus untuk menghapus sidik jari
async def remove_fingerprint(ID):
    try:
        if finger.deleteTemplate(ID):
            print(f"Fingerprint at position {ID} removed successfully.")
            delete_id(ID)
            check()
            await asyncio.sleep(2)
            interact_txt("Data ID tersebut dihapus!")
            await asyncio.sleep(2)
        else:
            print("tidak ada yang dihapus!")
            cross()
            await asyncio.sleep(2)
            interact_txt("tidak ada yang dihapus!")
            await asyncio.sleep(2)
    except Exception as e:
        print(f"Error: {e}")
    menu()

# Fungsi asinkronus untuk menghapus semua sidik jari dengan konfirmasi sebagai argumen
async def clear_all_fingerprints(confirm: bool):
    try:
        if confirm:
            if finger.clearDatabase():
                clear_all_id()
                check()
                await asyncio.sleep(2)
                interact_txt("berhasil membersihkan ID!")
                await asyncio.sleep(2)
            else:
                print("Failed to clear all fingerprints.")
                await asyncio.sleep(2)
                interact_txt("gagal menghapus!")
                await asyncio.sleep(2)
        else:
            print("Operasi dibatalkan.")
    except Exception as e:
        print(f"Error: {e}")
    menu()


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
            while True:  # Loop hingga input valid
                confirm = input("Apakah Anda yakin ingin menghapus semua sidik jari? (y/n): ").strip().lower()
                if confirm == "y":
                    await clear_all_fingerprints(True)
                    break
                elif confirm == "n":
                    print("Operasi dibatalkan.")
                    break
                else:
                    print("Input tidak valid. Masukkan 'y' untuk ya atau 'n' untuk tidak.")   
        elif choice == "5":
            print("Exiting program...")
            break
        else:
            print("Invalid choice. Please try again.")

# Jalankan program
#asyncio.run(main())