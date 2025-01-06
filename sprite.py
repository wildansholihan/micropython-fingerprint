import machine
import ST7735
from ST7735 import TFT, TFTColor
from machine import SPI, Pin
import time
import framebuf

# Inisialisasi pin SPI
spi = SPI(1, baudrate=40000000, polarity=0, phase=0, sck=Pin(10), mosi=Pin(11), miso=None)
tft = TFT(spi, 6, 7, 13)  # Pin konfigurasi: DC=19, Reset=17, CS=18

tft.initr()
tft.rgb(True)

# Bersihkan layar
tft.fill(0)

# Buat buffer frame untuk sprite
sprite_width = 16
sprite_height = 16
sprite_buffer = bytearray(sprite_width * sprite_height // 8)  # 1 bit per pixel

# Menggambar sprite sederhana: sebuah kotak kecil
sprite_buffer[0] = 0b11111111
sprite_buffer[1] = 0b11111111
sprite_buffer[2] = 0b11111111
sprite_buffer[3] = 0b11111111

# Membuat objek framebuf (buffer grafis)
sprite = framebuf.FrameBuffer(sprite_buffer, sprite_width, sprite_height, framebuf.MONO_HLSB)

# Fungsi untuk menampilkan sprite di layar
def draw_sprite(x, y):
    for i in range(sprite_height):
        for j in range(sprite_width):
            if sprite.pixel(j, i):  # Mengecek jika piksel aktif (1)
                tft.pixel((x + j, y + i), TFT.WHITE)  # Menggambar piksel di layar

# Menampilkan sprite di posisi (50, 50)
draw_sprite(50, 50)

# Menunggu beberapa detik untuk melihat hasil
time.sleep(5)

# Menggerakkan sprite
for i in range(50, 100):
    tft.fill(0)  # Bersihkan layar
    draw_sprite(i, 50)  # Pindahkan sprite
    time.sleep(0.05)
