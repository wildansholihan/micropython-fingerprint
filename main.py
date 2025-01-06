import uasyncio as asyncio
import network
from tft import phone_menu, display_clear, home
from audio import beep, thanks, bye
import aioble
import bluetooth
from machine import Pin
from fingerprint import (
    enroll_fingerprint,
    match_fingerprint,
    remove_fingerprint,
    clear_all_fingerprints,
    finger,
)
import time
# Konfigurasi LED indikator
# UUID untuk layanan dan karakteristik
SERVICE_UUID = bluetooth.UUID("90D3D001-C950-4DD6-9410-2B7AEB1DD7D8")
RECV_CHAR_UUID = bluetooth.UUID("90D3D002-C950-4DD6-9410-2B7AEB1DD7D8")

# Interval advertising dalam mikrodetik
_ADV_INTERVAL_MS = 250_000

# Membuat layanan BLE custom
ble_service = aioble.Service(SERVICE_UUID)
recv_char = aioble.Characteristic(
    ble_service, RECV_CHAR_UUID, write=True, notify=True, capture=True
)
aioble.register_services(ble_service)

# Variabel untuk menyimpan status koneksi dan tugas
connected_device = None
wait_for_write_task = None

# Konfigurasi Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

async def is_wifi_connected():
    """Memeriksa koneksi Wi-Fi."""
    return wlan.isconnected()

async def load_wifi():
    """Membaca konfigurasi Wi-Fi dari file."""
    try:
        with open('wifi_config.txt', 'r') as f:
            content = f.read().strip()
            ssid, password = content.split(':')
            return ssid, password
    except OSError:
        print("Tidak ada konfigurasi Wi-Fi ditemukan.")
        return None, None

async def save_wifi_config(ssid, password):
    """Menyimpan konfigurasi Wi-Fi ke file."""
    with open('wifi_config.txt', 'w') as f:
        f.write(f"{ssid}:{password}")
    print("Konfigurasi Wi-Fi disimpan.")

async def connect_wifi(ssid=None, password=None):
    """Menghubungkan ke Wi-Fi."""
    stored_ssid, stored_password = await load_wifi()
    ssid = ssid or stored_ssid
    password = password or stored_password

    if not ssid or not password:
        print("Konfigurasi Wi-Fi tidak lengkap.")
        return False

    wlan.connect(ssid, password)
    for _ in range(10):  # Tunggu maksimal 10 detik
        if wlan.isconnected():
            print(f"Wi-Fi terkoneksi: {ssid}")
            return True
        await asyncio.sleep(1)

    print("Koneksi Wi-Fi gagal.")
    return False

async def match_fingerprint_no_bt(timeout_ms=10000):
    """Pencocokan sidik jari tanpa BLE dengan timeout."""
    print("Place your finger on the sensor...")
    start_time = time.ticks_ms()

    while not finger.readImage():
        if connected_device is not None:
            print("BLE connected, exiting fingerprint check.")
            return
        
        # Periksa timeout
        if time.ticks_diff(time.ticks_ms(), start_time) > timeout_ms:
            print("Timeout: No fingerprint detected.")
            return
        
        await asyncio.sleep(0.1)  # Hindari blocking dengan delay kecil
    beep()
    try:
        finger.convertImage(0x01)
        position, accuracy = finger.searchTemplate()
        if position >= 0:
            thanks()
            print(f"Fingerprint matched at position {position} with accuracy {accuracy}")
        else:
            print("No matching fingerprint found.")
            bye()
    except Exception as e:
        print(f"Error during fingerprint matching: {e}")
        print("Skipping this fingerprint attempt.")
        bye()

async def peripheral_task():
    """Tugas BLE peripheral untuk advertising."""
    global connected_device
    while True:  # Loop terus-menerus untuk memulai ulang advertising
        print("Mulai Advertising BLE...")
        async with await aioble.advertise(
            _ADV_INTERVAL_MS, name="PicoW-BLE", services=[SERVICE_UUID]
        ) as connection:
            print(f"Koneksi dari perangkat: {connection.device}")
            connected_device = connection.device
            try:
                await connection.disconnected()  # Tunggu hingga perangkat terputus
            except Exception as e:
                print(f"Error during BLE connection: {e}")
            finally:
                print("Perangkat terputus.")
                connected_device = None

async def wait_for_write():
    """Tugas menangani data yang dikirim oleh klien melalui BLE."""
    while connected_device is not None:  # Berhenti jika koneksi terputus
        try:
            connection, data = await recv_char.written(timeout_ms=5000)
            if data:
                command = data.decode("utf-8").strip()
                print(f"Data diterima: {command}")
                if command == "1":
                    print("Masukkan ID...")
                    id_input = (await recv_char.written())[1].decode("utf-8").strip()
                    if id_input.isdigit():
                        enroll_fingerprint(int(id_input))
                elif command == "2":
                    match_fingerprint()
                elif command == "3":
                    print("Masukkan ID...")
                    id_input = (await recv_char.written())[1].decode("utf-8").strip()
                    if id_input.isdigit():
                        remove_fingerprint(int(id_input))
                elif command == "4":
                    clear_all_fingerprints()
                elif command == "5":
                    print("Connecting...")
                    connect_wifi()
                    break
                else:
                    print("Invalid command!")
        except asyncio.TimeoutError:
            print("Timeout menunggu data BLE.")
        except Exception as e:
            print(f"Error handling BLE data: {e}")
        finally:
            print("Tugas wait_for_write selesai.")

async def ble_task():
    """Fungsi utama untuk BLE."""
    global wait_for_write_task

    asyncio.create_task(peripheral_task())

    while True:
        try:
            if connected_device is None:
                # Jika tidak terkoneksi BLE, jalankan pencocokan fingerprint tanpa BLE
                if wait_for_write_task and not wait_for_write_task.done():
                    wait_for_write_task.cancel()
                home()
                
                await match_fingerprint_no_bt()
            else:
                # Jika terkoneksi BLE, jalankan `wait_for_write` jika belum berjalan
                if wait_for_write_task is None or wait_for_write_task.done():
                    wait_for_write_task = asyncio.create_task(wait_for_write())
                phone_menu()

            await asyncio.sleep(1)
        except Exception as e:
            print(f"Unhandled error in BLE task: {e}")
            print("Continuing main loop...")

home()
load_wifi()

async def main():
    """Fungsi utama."""
    try:
        if not await connect_wifi():
            print("Koneksi Wi-Fi gagal. Input melalui BLE diperlukan.")
            await wait_for_write()  # Gunakan BLE untuk input Wi-Fi
        await ble_task()
    except Exception as e:
        print(f"Unhandled exception in main(): {e}")
        print("Restarting main loop...")
        await main()  # Restart ulang jika terjadi kesalahan besar

try:
    asyncio.run(main())
except Exception as e:
    print(f"Exception saat menjalankan main(): {e}")