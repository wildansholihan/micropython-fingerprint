import machine
import sdcard
import os

# Inisialisasi SPI 0
spi = machine.SPI(0, baudrate=1000000, polarity=0, phase=0)  # Mengatur SPI0 dengan baudrate 1 MHz
cs = machine.Pin(17, machine.Pin.OUT)  # Pin Chip Select untuk kartu SD

# Inisialisasi Kartu SD
sd = sdcard.SDCard(spi, cs)

# Mount kartu SD ke sistem file
os.mount(sd, '/sd')

# Menampilkan isi direktori root
print(os.listdir('/'))