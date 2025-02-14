import time
from machine import Pin
from ds1302 import DS1302

# Inisialisasi pin dan DS1302
clk_pin = Pin(5)
dio_pin = Pin(4)
rst_pin = Pin(3)  # Bisa diganti sesuai pin yang digunakan

ds = DS1302(clk=clk_pin, dio=dio_pin, cs=rst_pin)

'''
# Fungsi untuk menampilkan waktu setiap detik
while True:
    current_time = ds.date_time()  # Mengambil waktu saat ini
    print("Tahun: {}, Bulan: {}, Hari: {}, Jam: {}, Menit: {}, Detik: {}".format(
        current_time[0], current_time[1], current_time[2],
        current_time[4], current_time[5], current_time[6]))
    time.sleep(1)  # Menunggu 1 detik sebelum memperbarui waktu lagi
'''