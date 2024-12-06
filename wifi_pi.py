import storage
import wifi
import board
import digitalio
import socketpool
import time
from buzzer import beep
from oled import display_centered_text, clear_display, display_text, group, display
from bluetooth_CL import uart
import adafruit_requests

# Setup GPIO untuk LED
LED_GREEN = digitalio.DigitalInOut(board.GP18)  # Pin GPIO 18 untuk LED hijau
LED_GREEN.direction = digitalio.Direction.OUTPUT

# Fungsi untuk memeriksa koneksi Wi-Fi dan mengatur status LED
def is_wifi_connected():
    if wifi.radio.ipv4_address:  # Jika ada alamat IP, Wi-Fi terhubung
        LED_GREEN.value = True  # Nyalakan LED hijau
        return True
    else:
        LED_GREEN.value = False  # Matikan LED hijau
        return False

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
                beep(1, 0.1)
                is_wifi_connected()  # Memeriksa koneksi dan mengatur status LED
                return True
            except Exception as e:
                print(f"Gagal terhubung: {e}")
                display_centered_text(display, group, text="Gagal Terhubung!")
                is_wifi_connected()  # Memeriksa koneksi dan mengatur status LED
                beep(2, 0.1)
                return False
        else:
            print("SSID atau password tidak cocok!")
            display_centered_text(display, group, text="SSID/PASS Tidak Cocok!")
            is_wifi_connected()  # Memeriksa koneksi dan mengatur status LED
            beep(3, 0.1)
            return False
    else:
        print("Konfigurasi Wi-Fi tidak ditemukan.")
        display_centered_text(display, group, text="Config Kosong!")
        is_wifi_connected()  # Memeriksa koneksi dan mengatur status LED
        beep(3, 0.1)
        return False

# Fungsi untuk mengambil data
def get_attendance_data(id):
    url = f"http://107.155.65.135:3010/attendance/{id}"
    headers = {'Content-Type': 'application/json'}
    
    # Setup socket pool for HTTP requests
    pool = socketpool.SocketPool(wifi.radio)
    
    # Inisialisasi objek requests
    requests_session = adafruit_requests.Session(pool, None)
    
    try:
        # Send GET request to fetch data
        response = requests_session.get(url, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        response.close()
    except Exception as e:
        print(f"Error retrieving data: {e}")

# Fungsi untuk mengirim data
def send_attendance_data(id):
    url = "http://107.155.65.135:3010/attendance"
    headers = {'Content-Type': 'application/json'}
    data = {
        "id": id,
        "name": "fingerprint"
    }
    
    # Setup socket pool for HTTP requests
    pool = socketpool.SocketPool(wifi.radio)  # Membuat pool koneksi
    
    # Inisialisasi objek requests
    requests_session = adafruit_requests.Session(pool, None)
    
    try:
        # Send POST request directly using requests_session.post
        response = requests_session.post(url, json=data, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        response.close()
    except Exception as e:
        print(f"Error sending data: {e}")
      
# Fungsi untuk menghapus data
def delete_attendance_data(id):
    url = f"http://107.155.65.135:3010/attendance/{id}"
    headers = {'Content-Type': 'application/json'}
    
    # Setup socket pool for HTTP requests
    pool = socketpool.SocketPool(wifi.radio)
    
    # Inisialisasi objek requests
    requests_session = adafruit_requests.Session(pool, None)
    
    try:
        # Send DELETE request to delete data
        response = requests_session.delete(url, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        response.close()
    except Exception as e:
        print(f"Error deleting data: {e}")

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

connect_wifi()
send_attendance_data(1)