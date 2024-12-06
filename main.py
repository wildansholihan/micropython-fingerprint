from wifi_pi import wifi_setup, connect_wifi, load_wifi_config, is_wifi_connected
from buzzer import beep
from bluetooth_CL import configure_bluetooth, send_at_command, check_bluetooth_status, uart  # Pastikan uart ada di sini
from oled import init_display, display_text, display_centered_text, clear_display, display_image, group, display
from fingerprint import enroll_fingerprint, search_fingerprint, remove_fingerprint, remove_all_fingerprints, finger, search_fingerprint_noBT
import time

# Memuat konfigurasi Wi-Fi
is_wifi_connected()
connect_wifi()

clear_display(group)
beep(2, 0.1)
display_centered_text(display, group, text="setup bluetooth...", wrap_at=16)
configure_bluetooth()  # Fungsi konfigurasi bluetooth dari bluetooth_CL
time.sleep(1)

while True:  
    is_wifi_connected()
    while not check_bluetooth_status():
        search_fingerprint_noBT()
    
    while check_bluetooth_status():
        clear_display(group)
        display_text(display, group, text=("1.Register\n 2.Matchmaking\n 3.Remove\n 4.Clear All\n 5.Connect Wifi"), wrap_at=16)
        print("1. Register")
        print("2. Matchmaking")
        print("3. Remove")
        print("4. Clear All")
        print("5. Connect Wifi")
        
        # Tunggu sampai ada data yang diterima di UART
        choice = ""
        while not uart.in_waiting and check_bluetooth_status():
            time.sleep(0.1)  # Menunggu input dari UART
        
        # Pastikan ada data yang diterima sebelum mencoba membaca
        if uart.in_waiting:
            choice = uart.read().decode('utf-8').strip()

        else:
            print("Tidak ada data yang diterima dari UART.")
            continue  # Kembali ke menu atau beri tahu pengguna
        
        
        # Cek apakah Bluetooth terputus setelah memasuki menu
        if not check_bluetooth_status():
            print("Koneksi Bluetooth terputus! Kembali ke menu awal.")
            clear_display(group)
            display_centered_text(display, group, text="Bluetooth terputus, kembali ke menu...", wrap_at=16)
            time.sleep(2)
            break  # Kembali ke loop awal untuk pengecekan Bluetooth

        if choice == "1":
            beep(1, 0.1)
            print("Masukkan ID...")
            clear_display(group)
            display_centered_text(display, group, text="Masukkan ID...", wrap_at=20)
            while not uart.in_waiting and check_bluetooth_status():
                time.sleep(0.1)
            if uart.in_waiting:
                location = uart.read().decode('utf-8').strip()
                if location.isdigit():
                    location = int(location)
                    enroll_fingerprint(location)
                else:
                    print("Invalid ID!")
            else:
                print("Tidak ada data untuk ID!")
                continue  # Kembali ke menu utama atau beri tahu pengguna

        elif choice == "2":
            beep(2, 0.1)
            search_fingerprint()
        elif choice == "3":
            beep(2, 0.1)
            print("Masukkan ID...")
            while not uart.in_waiting and check_bluetooth_status():
                time.sleep(0.1)
            if uart.in_waiting:
                location = uart.read().decode('utf-8').strip()
                if location.isdigit():
                    location = int(location)
                    remove_fingerprint(location)
                else:
                    print("Invalid ID!")
            else:
                print("Tidak ada data untuk ID!")
                continue  # Kembali ke menu utama atau beri tahu pengguna

        elif choice == "4":
            beep(2, 0.1)
            remove_all_fingerprints()
        elif choice == "5":
            beep(2, 0.1)  # Suara notifikasi
            if not wifi_setup():
                print("kembali ke menu utama...")
                clear_display(group)
                display_centered_text(display, group, text="kembali ke menu...", wrap_at=16)
                time.sleep(2)  # Tampilkan pesan selama 2 detik
                continue  # Kembali ke menu utama jika Wi-Fi gagal
        else:
            print("Pilihan tidak valid, coba lagi!")
