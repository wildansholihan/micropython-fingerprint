from wifi_pi import wifi_setup, connect_wifi, load_wifi_config
import digitalio
import board
from buzzer import beep
from bluetooth_CL import configure_bluetooth, send_at_command, uart  # Pastikan uart ada di sini
from oled_text import init_display, display_text, display_centered_text, clear_display
from fingerprint import enroll_fingerprint, search_fingerprint, remove_fingerprint, remove_all_fingerprints, display, group
import time

# Setup GPIO untuk LED
LED_GREEN = digitalio.DigitalInOut(board.GP18)  # Pin GPIO 18 untuk LED hijau
LED_GREEN.direction = digitalio.Direction.OUTPUT

LED_RED = digitalio.DigitalInOut(board.GP19)  # Pin GPIO 19 untuk LED merah
LED_RED.direction = digitalio.Direction.OUTPUT

# Fungsi untuk mengatur status LED
def set_led_status(connected):
    if connected:
        LED_GREEN.value = True  # Nyalakan LED hijau
        LED_RED.value = False   # Matikan LED merah
    else:
        LED_GREEN.value = False  # Matikan LED hijau
        LED_RED.value = True     # Nyalakan LED merah

# Memuat konfigurasi Wi-Fi
ssid, password = load_wifi_config()

if ssid and password:  # Jika SSID dan password ada
    display_centered_text(display, group, text="Connecting Wifi...")
    try:
        # Mencoba untuk menghubungkan ke Wi-Fi
        connect_wifi(ssid, password)
        display_centered_text(display, group, text="Connected!")
        set_led_status(True)  # Indikasikan berhasil dengan LED hijau
        beep(1, 0.1)  # Bunyi sukses
        time.sleep(2)  # Tunggu sebentar
    except Exception as e:
        # Jika gagal terhubung ke Wi-Fi
        print(f"Failed to connect: {e}")
        display_centered_text(display, group, text="Disconnected!")
        set_led_status(False)  # Indikasikan gagal dengan LED merah
        beep(2, 0.1)  # Bunyi gagal
        time.sleep(2)
else:
    display_centered_text(display, group, text="No Wi-Fi Config Found!")
    set_led_status(False)  # Indikasikan gagal dengan LED merah
clear_display(group)
beep(2, 0.1)
display_centered_text(display, group, text="setup bluetooth...", wrap_at=16)
configure_bluetooth()  # Fungsi konfigurasi bluetooth dari bluetooth_CL
time.sleep(1)

while True:
    clear_display(group)
    display_text(display, group, text=("1. Enroll Fingerprint\n2. Search Fingerprint\n3. Remove Fingerprint\n4. Remove All\n5. Wifi Setup"), wrap_at=25)
    print("1. Enroll Fingerprint")
    print("2. Search Fingerprint")
    print("3. Remove Fingerprint")
    print("4. Remove All Fingerprints")
    print("5. Wifi Setup")

    # Tunggu sampai ada data yang diterima di UART
    choice = ""
    while not uart.in_waiting:
        time.sleep(0.1)  # Menunggu input dari UART

    choice = uart.read().decode('utf-8').strip()

    if choice == "1":
        beep(1, 0.1)
        print("Masukkan location ID...")
        clear_display(group)
        display_centered_text(display, group, text="Masukkan location ID...", wrap_at=20)
        while not uart.in_waiting:
            time.sleep(0.1)
        location = uart.read().decode('utf-8').strip()
        if location.isdigit():
            location = int(location)
            enroll_fingerprint(location)
        else:
            print("Invalid location ID!")
    elif choice == "2":
        beep(2, 0.1)
        search_fingerprint()
    elif choice == "3":
        beep(2, 0.1)
        print("Masukkan location ID...")
        while not uart.in_waiting:
            time.sleep(0.1)
        location = uart.read().decode('utf-8').strip()
        if location.isdigit():
            location = int(location)
            remove_fingerprint(location)
        else:
            print("Invalid location ID!")
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
