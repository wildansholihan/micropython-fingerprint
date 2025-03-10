from dfplayer import Player
from machine import Pin
from time import sleep

# Inisialisasi DFPlayer
df = Player(busy_pin=Pin(15))  # BUSY terhubung ke GPIO 15
df.volume(1)

def beep():
    df.play(1, 1)
    while df.playing():
        sleep(0.5)  # Menunggu hingga audio selesai diputar
    
def thanks():
    df.play(1, 5)
    while df.playing():
        sleep(0.5)  # Menunggu hingga audio selesai diputar
        
def bye():
    df.play(1, 4)
    while df.playing():
        sleep(0.5)  # Menunggu hingga audio selesai diputar
        
def wificonn():
    df.play(1, 2)
    while df.playing():
        sleep(0.5)

def wificross():
    df.play(1, 3)
    while df.playing():
        sleep(0.5)
        
def again():
    df.play(1, 6)
    while df.playing():
        sleep(0.5)
        
def needinput():
    df.play(1, 7)
    while df.playing():
        sleep(0.5)
        
def touch():
    df.play(1, 8)
    while df.playing():
        sleep(0.5)
        
def notvalid():
    df.play(1, 10)
    while df.playing():
        sleep(0.5)
        
def cancelopt():
    df.play(1, 9)
    while df.playing():
        sleep(0.5)
        
def btconn():
    df.play(1, 11)
    while df.playing():
        sleep(0.5)