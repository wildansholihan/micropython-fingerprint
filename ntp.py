import time
import board
import wifi
import socketpool
import adafruit_ntp
import adafruit_requests

# Koneksi Wi-Fi
wifi.radio.connect("GoThru Master (2.4G)", "mediaindonesia123")  # Ganti dengan SSID dan password Wi-Fi Anda
print("Connected to Wi-Fi")

# Membuat pool socket
pool = socketpool.SocketPool(wifi.radio)

# Menghubungkan ke server NTP
ntp = adafruit_ntp.NTP(pool, tz_offset=0)  # Ganti tz_offset sesuai zona waktu Anda
print("Connected to NTP server")

# Menyinkronkan waktu
current_time = ntp.datetime
print("Current time (from NTP):", current_time)

# Menunggu dan menampilkan waktu terus-menerus
while True:
    current_time = ntp.datetime
    print(f"Current Time: {current_time}")
    time.sleep(2)