from ST7735 import TFT, TFTColor
from machine import SPI, Pin
from sysfont import sysfont
from terminalfont import terminalfont
import ntptime
import time

# Inisialisasi SPI dan TFT
spi = SPI(1, baudrate=40000000, polarity=0, phase=0, sck=Pin(10), mosi=Pin(11), miso=None)
tft = TFT(spi, 6, 7, 13)  # Pin konfigurasi: DC=19, Reset=17, CS=18
tft.initr()
tft.rgb(True)
tft.rotation(3)

# Jika ukuran layar diketahui, bisa langsung dimasukkan
SCREEN_WIDTH = 160  # Gantilah dengan lebar layar TFT
SCREEN_HEIGHT = 128  # Gantilah dengan tinggi layar TFT

def invert_image(data):
    """ Fungsi untuk menginversi gambar dalam data bytearray """
    return bytearray(~b & 0xFF for b in data)

def display_image(file_name, x_pos=0, y_pos=0, scale_percentage=100, invert=False):
    with open(file_name, "rb") as f:
        f.seek(10)
        offset = int.from_bytes(f.read(4), "little")
        f.seek(18)
        img_width = int.from_bytes(f.read(4), "little")
        img_height = int.from_bytes(f.read(4), "little")
        f.seek(28)
        bit_depth = int.from_bytes(f.read(2), "little")

        if bit_depth != 1:
            raise ValueError("File bukan format BMP 1-bit")

        # Hitung ukuran target berdasarkan scale_percentage
        scale_factor = scale_percentage / 100.0
        target_width = int(img_width * scale_factor)
        target_height = int(img_height * scale_factor)

        # Pastikan gambar tidak melampaui layar
        target_width = min(target_width, SCREEN_WIDTH - x_pos)  # Gantilah tft.width() dengan SCREEN_WIDTH
        target_height = min(target_height, SCREEN_HEIGHT - y_pos)  # Gantilah tft.height() dengan SCREEN_HEIGHT

        # Set window lokasi untuk area gambar
        tft._setwindowloc((x_pos, y_pos), (x_pos + target_width - 1, y_pos + target_height - 1))

        row_size = (img_width + 7) // 8  # Byte per baris asli
        row_padded = (row_size + 3) & ~3  # Padding hingga kelipatan 4 byte
        buffer = bytearray(target_width * 2)  # Buffer warna untuk satu baris target

        for y in range(target_height):
            # Hitung posisi sumber (crop vertikal sesuai skala)
            src_y = int(y / scale_factor)
            f.seek(offset + (img_height - 1 - src_y) * row_padded)
            row = f.read(row_size)

            # Konversi baris ke format target
            color_index = 0
            for x in range(target_width):
                src_x = int(x / scale_factor)
                byte = row[src_x // 8]
                bit = (byte >> (7 - (src_x % 8))) & 1
                color = 0xFFFF if bit else 0x0000
                if invert:
                    # Inversi warna jika 'invert' True
                    color = ~color & 0xFFFF
                buffer[color_index * 2] = color >> 8
                buffer[color_index * 2 + 1] = color & 0xFF
                color_index += 1

            # Kirim buffer satu baris ke layar
            tft._writedata(buffer)
            
def get_current_time():
    # Mendapatkan waktu saat ini dalam format jam, menit, detik
    current_time = time.localtime()  # Mengambil waktu lokal
    return {
        "hour": f"{current_time[3]:02}",  # Jam
        "minute": f"{current_time[4]:02}",  # Menit
        "seconds": f"{current_time[5]:02}"  # Detik
    }

def get_current_date():
    # Mendapatkan tanggal saat ini dalam format hari, bulan, tahun, nama hari
    current_time = time.localtime()  # Mengambil waktu lokal
    days_of_week = ["SEN", "SEL", "RAB", "KAM", "JUM", "SAB", "MIN"]
    return {
        "day": f"{current_time[2]:02}",  # Tanggal
        "month": f"{current_time[1]:02}",  # Bulan
        "year": f"{current_time[0]}"[-2:],  # Tahun
        "weekday": days_of_week[current_time[6]]  # Nama hari
    }

def phone_menu():
    tft.fill(0x0000)
    display_image("btIdle.bmp", x_pos=88, y_pos=22, scale_percentage=54, invert=True)
    display_image("phone.bmp", x_pos=4, y_pos=20, scale_percentage=54, invert=True)
    display_image("arrow.bmp", x_pos=68, y_pos=38, scale_percentage=26, invert=True)
    tft.text((23, 102), "BLUETOOTH CONNECTED!", tft.WHITE, sysfont, 1)

def display_clear():
    tft.fill(0x0000)

def home():
    # Bersihkan layar
    #tft.fill(0x0000)

    # Elemen tetap
    tft.text((110, 110), "masuk", tft.WHITE, terminalfont, 1)
    display_image("fingerPrint.bmp", x_pos=100, y_pos=36, scale_percentage=40, invert=True)
    display_image("wifiSlash.bmp", x_pos=14, y_pos=98, scale_percentage=18, invert=True)

    # Elemen yang sering diperbarui
    refresh_time_and_date()

def refresh_time_and_date():
    current_time = get_current_time()  # Fungsi untuk mendapatkan waktu
    current_date = get_current_date()  # Fungsi untuk mendapatkan tanggal

    # Perbarui detik
    tft.text((50, 76), ("/" + current_time["seconds"]), tft.WHITE, sysfont, 1)
    # Perbarui jam dan menit
    tft.text((14, 52), f"{current_time['hour']}:{current_time['minute']}", tft.WHITE, sysfont, 2)
    # Perbarui tanggal
    tft.text((16, 10), f"{current_date['day']}:{current_date['month']}:{current_date['year']} {current_date['weekday']}", 
             tft.WHITE, sysfont, 1)

def display_image_rgb(file_name, x_pos=0, y_pos=0, scale_percentage=100):
    """Menampilkan gambar penuh warna (RGB) pada layar TFT"""
    with open(file_name, "rb") as f:
        f.seek(10)
        offset = int.from_bytes(f.read(4), "little")
        f.seek(18)
        img_width = int.from_bytes(f.read(4), "little")
        img_height = int.from_bytes(f.read(4), "little")
        f.seek(28)
        bit_depth = int.from_bytes(f.read(2), "little")

        if bit_depth not in (16, 24):
            raise ValueError("File bukan format BMP 16-bit atau 24-bit")

        scale_factor = scale_percentage / 100.0
        target_width = int(img_width * scale_factor)
        target_height = int(img_height * scale_factor)
        target_width = min(target_width, SCREEN_WIDTH - x_pos)
        target_height = min(target_height, SCREEN_HEIGHT - y_pos)

        tft._setwindowloc((x_pos, y_pos), (x_pos + target_width - 1, y_pos + target_height - 1))
        row_padded = ((img_width * (bit_depth // 8)) + 3) & ~3

        buffer = bytearray(target_width * 2)
        for y in range(target_height):
            src_y = int(y / scale_factor)
            f.seek(offset + (img_height - 1 - src_y) * row_padded)
            row = f.read(row_padded)

            color_index = 0
            for x in range(target_width):
                src_x = int(x / scale_factor)
                if bit_depth == 24:
                    r = row[src_x * 3 + 2] >> 3
                    g = row[src_x * 3 + 1] >> 2
                    b = row[src_x * 3] >> 3
                elif bit_depth == 16:
                    pixel = int.from_bytes(row[src_x * 2:src_x * 2 + 2], "little")
                    r = (pixel >> 11) & 0x1F
                    g = (pixel >> 5) & 0x3F
                    b = pixel & 0x1F
                color = (r << 11) | (g << 5) | b
                buffer[color_index * 2] = color >> 8
                buffer[color_index * 2 + 1] = color & 0xFF
                color_index += 1
            tft._writedata(buffer)

def display_image_on_mask(file_name, x_pos, y_pos, width, height, scale_percentage=100):
    """
    Fungsi untuk menampilkan gambar pada area tertentu sebagai masker.
    x_pos, y_pos: Koordinat atas kiri area masking.
    width, height: Ukuran area masker.
    scale_percentage: Persentase skala gambar.
    """
    with open(file_name, "rb") as f:
        f.seek(10)
        offset = int.from_bytes(f.read(4), "little")
        f.seek(18)
        img_width = int.from_bytes(f.read(4), "little")
        img_height = int.from_bytes(f.read(4), "little")
        f.seek(28)
        bit_depth = int.from_bytes(f.read(2), "little")

        # Hitung faktor skala
        scale_factor = scale_percentage / 100.0
        target_width = int(img_width * scale_factor)
        target_height = int(img_height * scale_factor)

        # Pastikan gambar tidak melampaui ukuran area yang diinginkan
        target_width = min(target_width, width)
        target_height = min(target_height, height)

        # Set window lokasi untuk area gambar
        tft._setwindowloc((x_pos, y_pos), (x_pos + target_width - 1, y_pos + target_height - 1))

        row_padded = ((img_width * (bit_depth // 8)) + 3) & ~3

        buffer = bytearray(target_width * 2)
        for y in range(target_height):
            src_y = int(y / scale_factor)
            f.seek(offset + (img_height - 1 - src_y) * row_padded)
            row = f.read(row_padded)

            color_index = 0
            for x in range(target_width):
                src_x = int(x / scale_factor)
                if bit_depth == 24:
                    r = row[src_x * 3 + 2] >> 3
                    g = row[src_x * 3 + 1] >> 2
                    b = row[src_x * 3] >> 3
                elif bit_depth == 16:
                    pixel = int.from_bytes(row[src_x * 2:src_x * 2 + 2], "little")
                    r = (pixel >> 11) & 0x1F
                    g = (pixel >> 5) & 0x3F
                    b = pixel & 0x1F
                color = (r << 11) | (g << 5) | b
                buffer[color_index * 2] = color >> 8
                buffer[color_index * 2 + 1] = color & 0xFF
                color_index += 1
            tft._writedata(buffer)


tft.fill(0x000)


display_image_rgb("bg.bmp", x_pos=0, y_pos=0, scale_percentage=100)

while True:
    #time.sleep(0.5)
    home()
    display_image_rgb("bg.bmp", x_pos=0, y_pos=0, scale_percentage=100)
    display_image_on_mask("bg.bmp", x_pos=0, y_pos=0, width=100, height=100, scale_percentage=100)
   