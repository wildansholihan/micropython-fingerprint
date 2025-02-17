import tm1637
import uasyncio as asyncio
from machine import Pin, I2C
from ds1302 import DS1302
from ssd1306 import SSD1306_I2C
import time
from font import Font
import os
import re
import framebuf

# Inisialisasi TM1637 (7-segment)
tm = tm1637.TM1637(clk=Pin(21), dio=Pin(20))

# Inisialisasi DS1302 (RTC)
clk_pin = Pin(5)
dio_pin = Pin(4)
rst_pin = Pin(3)
rtc = DS1302(clk=clk_pin, dio=dio_pin, cs=rst_pin)

# Inisialisasi I2C dan OLED
i2c = I2C(1, scl=Pin(11), sda=Pin(10), freq=400000)
display = SSD1306_I2C(128, 64, i2c)

f = Font(display)

# Variabel global untuk menyimpan animasi
def cycle_images(animationName='fingerScan'):
    """Memuat dan menampilkan gambar animasi secara bergiliran."""
    images = []
    folder = '/animation'  # Folder default

    # Ambil file yang sesuai dengan pola dan urutkan berdasarkan angka
    files = sorted(
        [f for f in os.listdir(folder) if re.match(rf"^{animationName}\d+\.pbm$", f)],
        key=lambda x: int(re.search(r'(\d+)', x).group(1))  # Urutkan berdasarkan angka di nama file
    )

    # Muat semua gambar ke dalam list
    for file in files:
        try:
            with open(f'{folder}/{file}', 'rb') as g:
                g.readline()  # Magic number
                g.readline()  # Creator comment
                g.readline()  # Dimensions
                data = bytearray(g.read())
            fbuf = framebuf.FrameBuffer(data, 64, 64, framebuf.MONO_HLSB)  # Sesuaikan ukuran
            images.append(fbuf)
        except Exception as e:
            print(f"Gagal memuat {file}: {e}")

    # Tampilkan gambar secara bergiliran
    display.fill(0)
    for img in images:
        display.blit(img, 32, 0)
        display.show()

# Fungsi untuk menampilkan gambar .pbm pada layar OLED
def display_image(file_name, x_pos=0, y_pos=0, scale_percent=100):
    """Menampilkan gambar .pbm pada layar OLED dengan skala persentase"""
    try:
        with open(f"img/{file_name}.pbm", "rb") as g:
            g.readline()  # Skip magic number (P4)
            g.readline()  # Skip creator line
            dimensions = g.readline()  # Read dimensions line
            img_width, img_height = map(int, dimensions.split())

            # Hitung faktor skala
            scale_factor = scale_percent / 100.0
            target_width = int(img_width * scale_factor)
            target_height = int(img_height * scale_factor)
            
            # Pastikan ukuran gambar tidak lebih besar dari ukuran layar OLED
            target_width = min(target_width, display.width - x_pos)
            target_height = min(target_height, display.height - y_pos)

            # Baca data gambar
            data = bytearray(g.read())

            # Proses gambar per baris
            for y in range(target_height):
                src_y = int(y / scale_factor)  # Sesuaikan baris gambar dengan skala
                row_start = src_y * (img_width // 8)  # Hitung offset baris
                row_end = row_start + (img_width // 8)
                row = data[row_start:row_end]  # Ambil baris gambar
                
                for x in range(target_width):
                    src_x = int(x / scale_factor)  # Sesuaikan kolom gambar dengan skala
                    byte_idx = src_x // 8
                    bit_idx = 7 - (src_x % 8)

                    # Ambil nilai bit dari gambar monokrom
                    if row[byte_idx] & (1 << bit_idx):
                        display.pixel(x_pos + x, y_pos + y, 1)  # Set piksel ke 1 (hitam)
                    else:
                        display.pixel(x_pos + x, y_pos + y, 0)  # Set piksel ke 0 (putih)

            display.show()
    except Exception as e:
        print(f"Gagal menampilkan gambar {file_name}: {e}")

def interact_txt(text, screen_width=128, screen_height=64, font_size=16, max_length=15, total_max=48, truncate_at=44, line_spacing=16):
    """Menampilkan teks di tengah layar OLED dengan dukungan enter ('\\n'), dan truncation jika mencapai baris ke-4."""

    text = text.strip()  # Hapus spasi berlebih di awal & akhir

    # Jika teks lebih dari total_max, potong dengan '..'
    if len(text) > total_max:
        text = text[:truncate_at] + "..."

    lines = []
    current_line = ""

    for char in text:
        if char == "\n":  # Jika ada enter, pindahkan ke baris berikutnya
            lines.append(current_line.strip())
            current_line = ""
        elif len(current_line) < max_length:
            current_line += char
        else:
            lines.append(current_line.strip())  # Tambahkan baris ke daftar
            current_line = char  # Mulai baris baru dengan karakter yang tersisa

    if current_line:
        lines.append(current_line.strip())  # Tambahkan sisa teks ke baris baru

    # Jika ada lebih dari 3 baris (artinya ada baris ke-4), potong baris terakhir dengan max_length
    if len(lines) > 3:
        lines[2] = lines[2][:max_length-3] + "..."

    # Pastikan maksimal hanya ada 3 baris
    lines = lines[:3]

    # Hitung posisi Y agar tetap di tengah
    total_text_height = len(lines) * line_spacing
    start_y = (screen_height - total_text_height) // 2

    display.fill(0)  # Bersihkan layar sebelum menampilkan teks
    for i, line in enumerate(lines):
        text_width = len(line) * 8  # Asumsi 8px per karakter
        x = (screen_width - text_width) // 2  # Posisi X agar rata tengah
        f.text(line, x, start_y + (i * line_spacing), font_size)
    
    display.show()

# Fungsi untuk menampilkan teks dengan pembungkusan huruf demi huruf
def display_text(text, x, y):
    """Menampilkan teks dengan pembungkusan huruf demi huruf berdasarkan lebar aktual karakter."""
    max_width = 128 - x  # Sesuaikan lebar berdasarkan posisi x
    current_line = ""
    current_width = 0
    lines = []

    for char in text:
        # Hitung lebar aktual karakter termasuk spasi
        char_width = 7  # Lebar font default untuk SSD1306 (bisa disesuaikan jika berbeda)
        char_spacing = 1  # Spasi antar karakter
        total_char_width = char_width + char_spacing

        # Periksa apakah karakter berikutnya masih muat di baris ini
        if current_width + total_char_width <= max_width:
            current_line += char
            current_width += total_char_width
        else:
            # Simpan baris saat ini dan mulai baris baru
            lines.append(current_line)
            current_line = char
            current_width = total_char_width

    if current_line:
        lines.append(current_line)  # Simpan baris terakhir

    # Tampilkan setiap baris pada layar
    for i, line in enumerate(lines):
        display.text(line, x, y + i * 10)  # Jarak antar baris 10 piksel
    display.show()

def check():
    display_image("check", 30, 0, 100)

# Fungsi untuk menampilkan gambar dengan tanda silang
def cross():
    display_image("cross", 30, 0, 100)

# Fungsi untuk menampilkan menu
def menu():
    display_image("menu", 0, 0, 100)

prev_time_clock = None
prev_time_oled = None

# Fungsi untuk menampilkan halaman utama (OLED)
def home():
    global prev_time_oled

    current_time = rtc.date_time()  # Ambil waktu dari RTC
    tahun, bulan, tanggal, hari, jam = current_time[0], current_time[1], current_time[2], current_time[3], current_time[4]

    # Konversi angka hari ke nama hari
    hari_list = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    nama_hari = hari_list[hari % 7]  # Karena RTC DS1302 biasanya memiliki indeks 6 untuk hari

    # Konversi angka bulan ke nama bulan
    bulan_list = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
    nama_bulan = bulan_list[bulan - 1]  # Karena bulan dimulai dari 1, kita kurangi 1 untuk indeks

    # Tentukan status berdasarkan jam
    if jam < 15:
        status = "Masuk"
    elif jam < 18:
        status = "Pulang"
    else:
        status = "Lembur"

    # Cek apakah ada perubahan dari prev_time_oled (Tanggal)
    if prev_time_oled is None or prev_time_oled != (tahun, bulan, tanggal):
        display.fill(0)
        f.text(nama_hari, 0, 0, 16)  # Menampilkan nama hari
        f.text("{:02}".format(tanggal), 0, 19, 24)  # Tanggal (2 digit)
        f.text(nama_bulan, 32, 19, 24)  # Bulan (singkatan 3 huruf)
        f.text("{:04}".format(tahun), 76, 19, 24)  # Tahun (4 digit)
        f.text(status, 0, 49, 16)  # Tampilkan status (Masuk/Pulang/Lembur)

        display.show()  # Tampilkan hasil di layar
        prev_time_oled = (tahun, bulan, tanggal)  # Simpan waktu terbaru ke prev_time_oled
    else:
        display.fill(0)
        f.text(nama_hari, 0, 0, 16)  # Menampilkan nama hari
        f.text("{:02}".format(tanggal), 0, 19, 24)  # Tanggal (2 digit)
        f.text(nama_bulan, 32, 19, 24)  # Bulan (singkatan 3 huruf)
        f.text("{:04}".format(tahun), 76, 19, 24)  # Tahun (4 digit)
        f.text(status, 0, 49, 16)  # Tampilkan status (Masuk/Pulang/Lembur)

        display.show()

# Fungsi untuk memperbarui display TM1637
async def clock():
    global prev_time_clock

    while True:  # Loop agar terus berjalan
        # Ambil waktu dari RTC
        current_time = rtc.date_time()
        jam, menit, detik = current_time[4], current_time[5], current_time[6]

        # Perbarui TM1637 hanya jika waktu jam, menit, detik berubah
        if prev_time_clock is None or (jam, menit, detik) != prev_time_clock:
            tm.numbers(jam, menit)  # Perbarui tampilan TM1637
            print("Waktu sekarang: {:02}:{:02}:{:02}".format(jam, menit, detik))  # Tampilkan ke serial monitor
            prev_time_clock = (jam, menit, detik)  # Simpan waktu terbaru ke prev_time_clock

        await asyncio.sleep(1)  # Tunggu 1 detik sebelum loop selanjutnya

async def main():
    while True:
        # Jalankan clock display dan oled sebagai task terpisah
        task1 = asyncio.create_task(clock())  
        task2 = asyncio.create_task(home())  

        # Tunggu kedua task selesai
        await task1  
        await task2  
        await asyncio.sleep(0.5)  # Menunggu sejenak agar proses bisa berjalan dengan lancar

# Jalankan event loop utama
#asyncio.run(main())
#home()
#check()
#cycle_images()