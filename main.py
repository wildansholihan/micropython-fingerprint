from buzzer import beep
from bluetooth_CL import configure_bluetooth, send_at_command, uart  # Pastikan uart ada di sini
from oled_text import init_display, display_text, display_centered_text, clear_display
from fingerprint import enroll_fingerprint, search_fingerprint, remove_fingerprint, remove_all_fingerprints, display, group
import time

display_centered_text(display, group, text="setup bluetooth...", wrap_at=16)
beep(2, 0.1)
configure_bluetooth()  # Fungsi konfigurasi bluetooth dari bluetooth_CL
time.sleep(1)

while True:
    clear_display(group)
    display_text(display, group, text=(f"1. Enroll Fingerprint\n 2. Search Fingerprint\n 3. Remove Fingerprint\n 4. Remove All Fingerprint"), wrap_at=25)

    print("1. Enroll Fingerprint")
    print("2. Search Fingerprint")
    print("3. Remove Fingerprint")
    print("4. Remove All Fingerprints")
    
    # Tunggu sampai ada data yang diterima di UART
    choice = ""
    while not uart.in_waiting:  # Menunggu sampai ada data yang tersedia di UART
        time.sleep(0.1)  # Cegah penggunaan CPU berlebihan dengan sedikit delay
    
    # Setelah ada data, baca dan dekode
    choice = uart.read().decode('utf-8').strip()
    
    # Pilihan berdasarkan input dari UART
    if choice == "1":
        beep(1, 0.1)
        print("Masukkan location ID...")
        clear_display(group)
        display_centered_text(display, group, text="Masukkan location ID...", wrap_at=20)
        while not uart.in_waiting:  # Menunggu sampai ada data yang tersedia di UART
            time.sleep(0.1)  # Cegah penggunaan CPU berlebihan dengan sedikit delay
        location = uart.read().decode('utf-8').strip()
        if location.isdigit():  # Pastikan data yang diterima adalah angka (ID yang valid)
            location = int(location)  # Ubah menjadi integer
            enroll_fingerprint(location)
        else:
            print("Invalid location ID!")  # Menangani kasus jika data tidak valid
    elif choice == "2":
        beep(2, 0.1)
        search_fingerprint()
    elif choice == "3":
        beep(2, 0.1)
        print("Masukkan location ID...")
        while not uart.in_waiting:  # Menunggu sampai ada data yang tersedia di UART
            time.sleep(0.1)  # Cegah penggunaan CPU berlebihan dengan sedikit delay
        location = uart.read().decode('utf-8').strip()
        if location.isdigit():  # Pastikan data yang diterima adalah angka (ID yang valid)
            location = int(location)  # Ubah menjadi integer
            remove_fingerprint(location)
        else:
            print("Invalid location ID!")  # Menangani kasus jika data tidak valid
    elif choice == "4":
        beep(2, 0.1)
        remove_all_fingerprints()