import network
import time
import socket
import json
from machine import Pin, UART
from ble import recv_char  # Import fungsi untuk membaca data dari BLE

# Setup GPIO untuk LED
LED_GREEN = Pin(15, Pin.OUT)  # Pin GPIO 18 untuk LED hijau

# Fungsi untuk memeriksa koneksi Wi-Fi dan mengatur status LED
def is_wifi_connected():
    if wlan.ifconfig()[0]:  # Jika ada alamat IP, Wi-Fi terhubung
        LED_GREEN.value(1)  # Nyalakan LED hijau
        return True
    else:
        LED_GREEN.value(0)  # Matikan LED hijau
        return False

# Fungsi untuk membaca konfigurasi Wi-Fi dari file
def load_wifi_config():
    try:
        with open('wifi_config.txt', 'r') as f:
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
    data = recv_char.written()
    if data is None or data == b"NONE":  # Pastikan data bukan None atau 'NONE'
        return ""  # Mengembalikan string kosong jika data tidak valid
    return data.decode('utf-8').strip()  # Mendecode data yang valid

# Fungsi untuk menyimpan konfigurasi Wi-Fi ke file
def save_wifi_config(ssid, password):
    with open('wifi_config.txt', 'w') as f:
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
            try:
                wlan.connect(ssid_stored, password_stored)
                while not wlan.isconnected():
                    time.sleep(1)
                print(f"Berhasil terhubung ke {ssid_stored}")
                is_wifi_connected()  # Memeriksa koneksi dan mengatur status LED
                return True
            except Exception as e:
                print(f"Gagal terhubung: {e}")
                is_wifi_connected()  # Memeriksa koneksi dan mengatur status LED
                return False
        else:
            print("SSID atau password tidak cocok!")
            is_wifi_connected()  # Memeriksa koneksi dan mengatur status LED
            return False
    else:
        print("Konfigurasi Wi-Fi tidak ditemukan.")
        is_wifi_connected()  # Memeriksa koneksi dan mengatur status LED
        return False

# Fungsi untuk mengirim data
def send_attendance_data(id):
    url = "http://107.155.65.135:3010/attendance"
    headers = {'Content-Type': 'application/json'}
    data = {
        "id": id,
        "name": "test"
    }
    
    # Setup socket pool for HTTP requests
    pool = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Membuat socket pool
    
    # Inisialisasi objek requests
    try:
        pool.connect((url, 80))
        pool.sendall(json.dumps(data).encode('utf-8'))
        print(f"Data terkirim ke {url}")
        pool.close()
    except Exception as e:
        print(f"Error sending data: {e}")

# Fungsi untuk setup Wi-Fi
def wifi_setup():
    wlan = network.WLAN(network.STA_IF)  # Mode client untuk WiFi
    wlan.active(True)  # Aktifkan WiFi
    # Coba koneksi menggunakan konfigurasi tersimpan
    if connect_wifi():
        print("Wi-Fi terkoneksi.")
        return  # Jika berhasil, keluar dari fungsi
    
    # Jika koneksi gagal, minta SSID dan Password baru
    while True:
        ssid = safe_uart_read()
        if ssid:
            break  # Keluar jika SSID sudah diisi

    while True:
        clear_display(display)
        display_centered_text(display, text="Masukkan Password baru...")
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

    # Fungsi untuk membaca data dari BLE
    try:
        print("Membaca data dari BLE...")
        ble_data = read_ble_data()
        if ble_data:
            print(f"Data BLE diterima: {ble_data.decode('utf-8')}")
            send_attendance_data(ble_data.decode('utf-8'))  # Kirim data yang diterima dari BLE
        else:
            print("Tidak ada data BLE yang diterima.")
    except Exception as e:
        print(f"Error membaca data BLE: {e}")
        
# wifi_setup()