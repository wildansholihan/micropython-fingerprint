import storage
import wifi
import socketpool
import time
from buzzer import beep
from oled_text import display_centered_text, clear_display, display_text
from fingerprint import group, display
from bluetooth_CL import uart

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

# Fungsi untuk menghubungkan ke Wi-Fi
def connect_wifi(ssid, password):
    wifi.radio.connect(ssid, password)
    print(f"Connected to {ssid}")

def wifi_setup():
    clear_display(group)
    display_centered_text(display, group, text="Cek Wi-Fi Config...")

    # Cek apakah sudah ada SSID yang tersimpan
    ssid, password = load_wifi_config()

    if ssid and password:
        display_centered_text(display, group, text="Mencoba menghubungkan...")
        try:
            connect_wifi(ssid, password)
            display_centered_text(display, group, text="Connected!")
            beep(1, 0.1)
            time.sleep(2)  # Tunggu sejenak
        except Exception as e:
            print(f"Failed to connect: {e}")
            display_centered_text(display, group, text="Gagal Terhubung!")
            beep(2, 0.1)
            time.sleep(2)
            # Jika gagal, beri kesempatan untuk memasukkan SSID dan password baru
            while True:
                display_centered_text(display, group, text="Masukkan SSID baru...")
                ssid = safe_uart_read()  # Gunakan fungsi aman untuk membaca SSID
                if ssid:  # Cek jika SSID tidak kosong
                    break  # Keluar dari loop jika SSID valid

            while True:
                display_centered_text(display, group, text="Masukkan Password...")
                password = safe_uart_read()  # Gunakan fungsi aman untuk membaca Password
                if password:  # Cek jika password tidak kosong
                    break  # Keluar dari loop jika password valid

            # Pastikan SSID dan password tidak kosong sebelum menyimpannya
            save_wifi_config(ssid, password)
            try:
                connect_wifi(ssid, password)
                display_centered_text(display, group, text="Connected!")
                beep(1, 0.1)
                time.sleep(2)
            except Exception as e:
                print(f"Failed to reconnect: {e}")
                display_centered_text(display, group, text="Gagal Terhubung Lagi!")
                beep(2, 0.1)
                time.sleep(2)

    else:
        # Jika tidak ada konfigurasi, minta SSID dan password
        while True:
            display_centered_text(display, group, text="Masukkan SSID...")
            ssid = safe_uart_read()  # Gunakan fungsi aman untuk membaca SSID
            if ssid:  # Pastikan SSID tidak kosong
                break  # Keluar dari loop jika SSID valid

        while True:
            display_centered_text(display, group, text="Masukkan Password...")
            password = safe_uart_read()  # Gunakan fungsi aman untuk membaca Password
            if password:  # Pastikan password tidak kosong
                break  # Keluar dari loop jika password valid

        # Pastikan SSID dan password tidak kosong sebelum menyimpannya
        save_wifi_config(ssid, password)
        try:
            connect_wifi(ssid, password)
            display_centered_text(display, group, text="Connected!")
            beep(1, 0.1)
            time.sleep(2)
        except Exception as e:
            print(f"Failed to connect: {e}")
            display_centered_text(display, group, text="Gagal Terhubung!")
            beep(2, 0.1)
            time.sleep(2)
            # Minta pengguna untuk memasukkan SSID dan password lagi jika gagal
            while True:
                display_centered_text(display, group, text="Masukkan SSID baru...")
                ssid = safe_uart_read()  # Gunakan fungsi aman untuk membaca SSID
                if ssid:  # Pastikan SSID tidak kosong
                    break  # Keluar dari loop jika SSID valid

            while True:
                display_centered_text(display, group, text="Masukkan Password...")
                password = safe_uart_read()  # Gunakan fungsi aman untuk membaca Password
                if password:  # Pastikan password tidak kosong
                    break  # Keluar dari loop jika password valid

            # Pastikan SSID dan password tidak kosong sebelum menyimpannya
            save_wifi_config(ssid, password)
            try:
                connect_wifi(ssid, password)
                display_centered_text(display, group, text="Connected!")
                beep(1, 0.0)
                time.sleep(2)
            except Exception as e:
                print(f"Failed to reconnect: {e}")
                display_centered_text(display, group, text="Gagal Terhubung Lagi!")
                beep(2, 0.1)
                time.sleep(2)