import storage
import wifi
import board
import digitalio
import socketpool
import time
from buzzer import beep
from oled_text import display_centered_text, clear_display, display_text
from fingerprint import group, display
from bluetooth_CL import uart

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

# Ini sangat penting! Jangan dihapus!
storage.remount('/', readonly=False)

# Fungsi untuk membaca konfigurasi Wi-Fi dari file
def load_wifi_config():
    try:
        with open('/wifi_config.txt', 'r') as f:
            content = f.read().strip()
            if ':' not in content:
                raise ValueError("Format konfigurasi salah, harus SSID:Password")
            ssid, password = content.split(':')
            print(f"Loaded SSID: {ssid}, Password: {password}")  # Debug print
            return ssid, password
    except OSError:
        print("Tidak ada konfigurasi Wi-Fi ditemukan.")
        return None, None  # No config file or invalid format
    except ValueError as e:
        print(f"Kesalahan format: {e}")
        return None, None  # Invalid format

# Fungsi untuk membaca input dari UART, menghindari nilai 'NONE'
def safe_uart_read():
    data = uart.read()
    if data is None or data == b"NONE":  # Pastikan data bukan None atau 'NONE'
        return ""  # Mengembalikan string kosong jika data tidak valid
    return data.decode('utf-8').strip()  # Mendecode data yang valid

# Fungsi untuk menyimpan konfigurasi Wi-Fi ke file
def save_wifi_config(ssid, password):
    with open('/wifi_config.txt', 'w') as f:
        f.write(f"{ssid}:{password}")
    print("Wi-Fi configuration saved.")

# Fungsi untuk mencoba koneksi Wi-Fi dengan logika lengkap
def connect_wifi(ssid_input=None, password_input=None):
    ssid_stored, password_stored = load_wifi_config()

    # Gunakan konfigurasi tersimpan jika input kosong
    if not ssid_input:
        ssid_input = ssid_stored
    if not password_input:
        password_input = password_stored

    if ssid_input and password_input:
        if ssid_input == ssid_stored and password_input == password_stored:
            print("Mencoba menghubungkan...")
            display_centered_text(display, group, text="Connecting...")
            try:
                wifi.radio.connect(ssid_stored, password_stored)
                print(f"Berhasil terhubung ke {ssid_stored}")
                display_centered_text(display, group, text="Connected!")
                set_led_status(True)
                beep(1, 0.1)
                return True
            except Exception as e:
                print(f"Gagal terhubung: {e}")
                display_centered_text(display, group, text="Gagal Terhubung!")
                set_led_status(False)
                beep(2, 0.1)
                return False
        else:
            print("SSID atau password tidak cocok!")
            display_centered_text(display, group, text="SSID/PASS Tidak Cocok!")
            set_led_status(False)
            beep(3, 0.1)
            return False
    else:
        print("Konfigurasi Wi-Fi tidak ditemukan.")
        display_centered_text(display, group, text="Config Kosong!")
        set_led_status(False)
        beep(3, 0.1)
        return False

# Fungsi untuk setup Wi-Fi
def wifi_setup():
    clear_display(group)
    display_centered_text(display, group, text="Cek Wi-Fi Config...")
    
    # Coba koneksi menggunakan konfigurasi tersimpan
    if connect_wifi():
        print("Wi-Fi terkoneksi.")
        return  # Jika berhasil, keluar dari fungsi
    
    # Jika koneksi gagal, minta SSID dan Password baru
    while True:
        clear_display(group)
        display_centered_text(display, group, text="Masukkan SSID baru...")
        ssid = safe_uart_read()
        if ssid:
            break  # Keluar jika SSID sudah diisi

    while True:
        clear_display(group)
        display_centered_text(display, group, text="Masukkan Password baru...")
        password = safe_uart_read()
        if password:
            break  # Keluar jika password sudah diisi

    # Simpan konfigurasi baru
    save_wifi_config(ssid, password)

    # Coba koneksi ulang dengan SSID dan Password baru
    print(f"Mencoba menghubungkan ke {ssid}...")
    if not connect_wifi(ssid, password):
        print("Koneksi masih gagal")
        time.sleep(2)
    else:
        print("Koneksi berhasil dengan konfigurasi baru!")
        time.sleep(2)