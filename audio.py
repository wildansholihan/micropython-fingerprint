from dfplayer import Player
from machine import Pin
from time import sleep

# Inisialisasi DFPlayer
df = Player(busy_pin=Pin(15))  # BUSY terhubung ke GPIO 15
df.volume(1)

def beep():
    df.play(1,4)
    while df.playing():
        sleep(0.5)  # Menunggu hingga audio selesai diputar
    
def thanks():
    df.play(1, 1)
    while df.playing():
        sleep(0.5)  # Menunggu hingga audio selesai diputar
        
def bye():
    df.play(1, 2)
    while df.playing():
        sleep(0.5)  # Menunggu hingga audio selesai diputar