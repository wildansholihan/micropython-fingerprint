import asyncio
import aioble
import bluetooth
from machine import Pin

# Konfigurasi LED indikator
led = Pin(14, Pin.OUT)
led.off()

# UUID untuk layanan dan karakteristik
SERVICE_UUID = bluetooth.UUID("90D3D001-C950-4DD6-9410-2B7AEB1DD7D8")  # UUID untuk layanan BLE
RECV_CHAR_UUID = bluetooth.UUID("90D3D002-C950-4DD6-9410-2B7AEB1DD7D8")  # Karakteristik untuk menerima data

# Interval advertising dalam mikrodetik
_ADV_INTERVAL_MS = 250_000

# Membuat layanan BLE custom
ble_service = aioble.Service(SERVICE_UUID)
recv_char = aioble.Characteristic(
    ble_service,
    RECV_CHAR_UUID,
    write=True,
    notify=True,
    capture=True,
)

# Register layanan BLE
aioble.register_services(ble_service)


def check_ble_status():
    """Periksa status koneksi BLE."""
    return aioble.is_connected()  # Mengembalikan True jika terhubung, False jika tidak

def _decode_data(data):
    """Decode data yang diterima (UTF-8)."""
    try:
        if data:
            return data.decode("utf-8")
    except Exception as e:
        print(f"Error decoding data: {e}")
    return None


async def peripheral_task():
    """Tugas BLE peripheral untuk advertising dan menangani koneksi."""
    while True:
        try:
            async with await aioble.advertise(
                _ADV_INTERVAL_MS,
                name="ESP32-BLE",
                services=[SERVICE_UUID],
            ) as connection:
                print(f"Koneksi dari perangkat: {connection.device}")
                await connection.disconnected()
                print(f"Perangkat terputus: {connection.device}")
        except asyncio.CancelledError:
            print("Tugas peripheral dibatalkan.")
        except Exception as e:
            print(f"Error dalam peripheral_task: {e}")
        finally:
            await asyncio.sleep_ms(100)


async def wait_for_write():
    """Tugas untuk menangani data yang dikirim oleh klien melalui karakteristik."""
    while True:
        try:
            connection, data = await recv_char.written(timeout_ms=5000)  # Set timeout 5 detik
            if data:
                command = _decode_data(data)
                print(f"Data diterima: {command}")

                if command == "RUN_COMMAND":
                    print("Menyalakan LED.")
                    led.value(1)
                elif command == "STOP_COMMAND":
                    print("Mematikan LED.")
                    led.value(0)
                else:
                    print(f"Perintah tidak dikenal: {command}")
        except asyncio.TimeoutError:
            print("Tidak ada data yang diterima dalam waktu yang ditentukan.")
        except Exception as e:
            print(f"Error dalam wait_for_write: {e}")
        finally:
            await asyncio.sleep_ms(500)


async def ble_task():
    """Fungsi utama untuk menjalankan semua tugas."""
    try:
        # Jalankan tugas peripheral dan wait_for_write
        asyncio.create_task(peripheral_task())
        asyncio.create_task(wait_for_write())
        while True:
            await asyncio.sleep(1)  # Menjaga loop tetap hidup
    except Exception as e:
        print(f"Exception dalam main(): {e}")


# Jalankan program utama
try:
    asyncio.run(ble_task())
except Exception as e:
    print(f"Exception saat menjalankan main(): {e}")