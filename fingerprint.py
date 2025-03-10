import uasyncio as asyncio
from pyfingerprint import PyFingerprint
from machine import UART, Pin
from data import (
    register_id,
    delete_id,
    log_attendance,
    clear_all_id,
)
from oled import interact_txt, menu, cycle_images, cross, check, fingerScan
from time import sleep
from audio import beep, thanks, bye, wificonn, wificross, again, needinput, touch, notvalid, btconn, cancelopt

# Inisialisasi UART dan Fingerprint Sensor
try:
    uart = UART(1, baudrate=57600, tx=Pin(8), rx=Pin(9))  # UART1 di Raspberry Pi Pico W
    finger = PyFingerprint(uart)
except Exception as e:
    print(f"Error initializing UART or fingerprint sensor: {e}")
    finger = None

# Fungsi untuk verifikasi koneksi sensor
async def initialize_sensor():
    try:
        if finger and finger.verifyPassword():
            print("Fingerprint sensor initialized successfully.")
            return True
        else:
            print("Wrong password for fingerprint sensor.")
            return False
    except Exception as e:
        print(f"Failed to initialize sensor: {e}")
        return False
    
# Fungsi asinkronus untuk enroll fingerprint
async def enroll_fingerprint(ID):
    try:
        ID = int(ID)  # Pastikan ID adalah integer

        # 🔍 Cek apakah ID sudah ada (gunakan try-except untuk menangani error sistem fingerprint)
        try:
            if finger.loadTemplate(ID):  
                print(f"ID {ID} sudah digunakan di sensor!")
                cross()
                cancelopt()
                await asyncio.sleep(2)
                interact_txt("ID sudah\ndigunakan!")
                await asyncio.sleep(2)
                menu()
                return  # Keluar jika ID sudah digunakan
        except Exception:
            print(f"ID {ID} belum ditemukan, lanjut proses pendaftaran...")

        # ✅ Proses pendaftaran fingerprint
        print("Step 1: Place your finger on the sensor...")
        fingerScan()
        touch()
        while not finger.readImage():
            await asyncio.sleep(1.5)
        print("Fingerprint image captured.")
        
        beep()  # Suara indikator
        cycle_images() # animasi
        
        if not finger.convertImage(0x01):
            print("Gagal mengonversi sidik jari pada langkah 1!")
            cross()
            cancelopt()
            interact_txt("Gagal membaca jari!")
            await asyncio.sleep(1)
            menu()
            return

        print("Step 1 complete. Remove your finger.")
        interact_txt("Angkat jari\nsebentar")
        again()
        await asyncio.sleep(2)

        print("Step 2: Place the same finger again...")
        fingerScan()
        touch()
        while not finger.readImage():
            await asyncio.sleep(1.5)
        print("Fingerprint image captured again.")
        
        beep()  # Suara indikator
        cycle_images() # animasi
        
        if not finger.convertImage(0x02):
            print("Gagal mengonversi sidik jari pada langkah 2!")
            cross()
            cancelopt()
            interact_txt("terjadi kesalahan!")
            await asyncio.sleep(2)
            menu()
            return

        if not finger.createTemplate():
            print("Gagal membuat template sidik jari!")
            cross()
            cancelopt()
            interact_txt("terjadi kesalahan!")
            await asyncio.sleep(2)
            menu()
            return

        # ✅ Simpan template ke ID yang diinginkan
        if not finger.storeTemplate(ID):
            print("Gagal menyimpan fingerprint.")
            cross()
            cancelopt()
            interact_txt("terjadi kesalahan!")
            await asyncio.sleep(2)
            menu()
            return

        print(f"Fingerprint stored at ID {ID}.")
        register_id(ID)
        log_attendance(ID)
        check()
        thanks()
        interact_txt(f"Terdaftar dengan\nID {ID}!")
        await asyncio.sleep(2)

    except Exception as e:
        print(f"Error during enrollment: {e}")
        cross()
        cancelopt()
        interact_txt("Terjadi kesalahan!")
        await asyncio.sleep(2)
    menu()

# Fungsi asinkronus untuk mencocokkan sidik jari
async def match_fingerprint():
    try:
        print("Step 1: Place your finger on the sensor...")
        fingerScan()
        touch()
        while not finger.readImage():
            await asyncio.sleep(1.5)
        print("Fingerprint image captured.")

        finger.convertImage(0x01)

        position, accuracy = finger.searchTemplate()
        beep()  # Suara indikator
        cycle_images() # animasi
        if position >= 0:
            print(f"Fingerprint matched at position {position} with accuracy {accuracy}")
            log_attendance(position)
            check()
            thanks()
            interact_txt("terima kasih!")
            await asyncio.sleep(2)
        else:
            print("No matching fingerprint found.")
            cross()
            bye()
            interact_txt("Sidik jari\ntidak dikenali!")
            await asyncio.sleep(2)
    except Exception as e:
        print(f"Error during fingerprint matching: {e}")
        beep()  # Suara indikator
        cycle_images() # animasi
        cross()
        bye()
        interact_txt("Sidik jari\ntidak dikenali!")
        await asyncio.sleep(2)
    menu()


async def remove_fingerprint(ID):
    try:
        ID = int(ID)  # Pastikan ID adalah integer

        # 🔍 Cek apakah ID valid dengan try-except untuk menghindari error fingerprint
        try:
            if not finger.loadTemplate(ID):  
                print(f"ID {ID} tidak ditemukan dalam database.")
                cross()
                cancelopt()
                interact_txt("ID tidak\nditemukan!")
                await asyncio.sleep(2)
                menu()
                return  # Keluar dari fungsi jika ID tidak ada
        except Exception:
            print(f"ID {ID} tidak ditemukan atau error saat membaca.")
            cross()
            cancelopt()
            interact_txt("ID tidak\nditemukan!")
            await asyncio.sleep(2)
            menu()
            return

        # ✅ Jika ID ditemukan, hapus fingerprint
        if not finger.deleteTemplate(ID):
            print("Gagal menghapus ID!")
            cross()
            cancelopt()
            interact_txt("Gagal menghapus ID!")
            await asyncio.sleep(2)
            menu()
            return

        # ✅ Hapus dari database jika berhasil
        print(f"Fingerprint at position {ID} removed successfully.")
        delete_id(ID)
        check()
        thanks()
        interact_txt("Data ID tersebut\ndihapus!")
        await asyncio.sleep(2)

    except Exception as e:
        print(f"Error during fingerprint removal: {e}")
        interact_txt("operasi dibatalkan")
        cancelopt()

    menu()

# Fungsi asinkronus untuk menghapus semua sidik jari
async def clear_all_fingerprints(confirm: bool):
    try:
        if confirm:
            if finger.clearDatabase():
                clear_all_id()
                check()
                thanks()
                interact_txt("berhasil membersihkan ID!")
                await asyncio.sleep(2)
            else:
                print("Failed to clear all fingerprints.")
                
                cross()
                cancelopt()
                interact_txt("gagal menghapus!")
                
                await asyncio.sleep(2)
        else:
            print("Operasi dibatalkan.")
            cross()
            cancelopt()
            interact_txt("operasi dibatalkan")
    except Exception as e:
        print(f"Error: {e}")
        cross()
        cancelopt()
        interact_txt("ada kesalahan!")
    menu()


'''
# Menu utama asinkronus
async def main():
    if not await initialize_sensor():
        print("Exiting program...")
        return

    while True:
        try:
            print("\nChoose an option:")
            print("1 - Enroll Fingerprint")
            print("2 - Match Fingerprint")
            print("3 - Delete Fingerprint")
            print("4 - Clear All Fingerprints")
            print("5 - Exit")

            choice = input("Enter your choice: ").strip()
            if choice == "1":
                ID = int(input("Enter storage ID (0-127): "))
                await enroll_fingerprint(ID)
            elif choice == "2":
                await match_fingerprint()
            elif choice == "3":
                ID = int(input("Enter position to delete (0-127): "))
                await remove_fingerprint(ID)
            elif choice == "4":
                confirm = input("Apakah Anda yakin ingin menghapus semua sidik jari? (y/n): ").strip().lower()
                await clear_all_fingerprints(confirm == "1")
            elif choice == "5":
                print("Exiting program...")
                break
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"Error in main menu: {e}")
'''

# Jalankan program
#asyncio.run(main())