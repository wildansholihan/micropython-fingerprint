#-------------------------------DEPENDENCIES--------------------------------------
import uasyncio as asyncio
import network
import ntptime
from audio import beep, thanks, bye
from oled import (
    cycle_images,
    check,
    cross,
    home,
    menu,
    display,
    clock,
    rtc,
    interact_txt,
)
import aioble
import bluetooth
from machine import Pin
from fingerprint import (
    enroll_fingerprint,
    match_fingerprint,
    remove_fingerprint,
    clear_all_fingerprints,
    finger,
    initialize_sensor
)
import time
from data import create_log
#----------------------------------SETUP-------------------------------------------
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

# configurasi led untuk indicator wifi
led = Pin(26, Pin.OUT).value

# Variabel untuk menyimpan status koneksi dan tugas
connected_device = None
ble_respons_task = None
matchmaking_task = None  # Menyimpan task matchmaking_no_ble

# variable untuk mendeteksi apakah rtc sudah di adjust 1x menyesuaikan ntptime (realtime dari koneksi wifi)
is_rtc_adjust = None

# sensor fingerprint initialize
initialize_sensor()

#-------------------------------FUNCTION----------------------------------------------

async def check_wifi():
    """Memeriksa status koneksi Wi-Fi dan mengontrol LED."""
    while True:
        if wlan.isconnected():
            led(1)  # LED nyala jika Wi-Fi terhubung
            print("Wi-Fi terhubung.")
        else:
            led(0)  # LED mati jika Wi-Fi tidak terhubung
            print("Wi-Fi tidak terhubung.")

        await asyncio.sleep(3)  # Cek setiap 2 detik

def load_wifi():
    """Membaca konfigurasi Wi-Fi dari file."""
    print("Mencoba load Wi-Fi...")
    try:
        with open('/files/wifi_config.txt', 'r') as f:
            content = f.read().strip()
            data = content.split(':')  # Pisahkan berdasarkan ":"
            
            if len(data) == 2:  # Pastikan ada tepat 2 elemen
                ssid, password = data
                return ssid, password
            else:
                print("Format Wi-Fi tidak valid.")
                return None, None
    except OSError:
        print("Tidak ada konfigurasi Wi-Fi ditemukan.")
        return None, None

''' _____________Inisialisasi WiFi (setelah function load_wifi() terdefinisikan)_______________ '''
ssid, password = load_wifi()
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

if ssid and password:
    wlan.connect(ssid, password)
    for _ in range(2):  # Coba konek selama 10 detik
        if wlan.isconnected():
            print("WiFi terhubung:", wlan.ifconfig())
            break
        asyncio.sleep(1)  # Tunggu tanpa blocking
    else:
        print("Gagal terhubung ke WiFi.")
'''_______________________________________________________________________________________________'''

def save_wifi_config(ssid, password):
    """Menyimpan konfigurasi Wi-Fi ke file."""
    with open('/files/wifi_config.txt', 'w') as f:
        f.write(f"{ssid}:{password}")
    print("Konfigurasi Wi-Fi disimpan.")

async def connect_wifi(ssid=None, password=None):
    """Menghubungkan ke Wi-Fi dengan opsi mengatur ulang SSID dan password."""
    stored_ssid, stored_password= load_wifi()

    # Gunakan konfigurasi yang tersimpan jika tidak ada input baru
    ssid = ssid or stored_ssid
    password = password or stored_password
    
    if ssid and password:
        print(f"Mencoba menghubungkan ke {ssid}...")
        wlan.connect(ssid, password)

        if wlan.isconnected():
            print(f"Berhasil terhubung ke {ssid}!")
            print("Alamat IP:", wlan.ifconfig()[0])
            if is_rtc_adjust is None:
                sync_rtc()
                print("rtc telah disinkronkan dengan ntp!")
            return

        print("Koneksi gagal. Meminta SSID baru...")

    # Meminta SSID baru jika koneksi gagal atau SSID/password tidak ada
    while True:
        print("Masukkan SSID baru:")
        input_ssid = await recv_char.written()
        if input_ssid:
            ssid = input_ssid[1].decode("utf-8").strip()
            break  # Keluar dari loop setelah mendapatkan SSID yang valid

    # Meminta password baru
    while True:
        print("Masukkan password:")
        input_pass = await recv_char.written()
        if input_pass:
            password = input_pass[1].decode("utf-8").strip()
            break  # Keluar dari loop setelah mendapatkan password yang valid

    # Simpan konfigurasi WiFi jika ada perubahan
    if ssid and password:
        save_wifi_config(ssid, password)
        await asyncio.sleep(2)  # Tunggu sebentar agar penyimpanan selesai

    # Coba koneksi ulang dengan konfigurasi terbaru
    print(f"Mencoba menghubungkan ke {ssid}...")
    wlan.connect(ssid, password)

    timeout = 10
    while not wlan.isconnected() and timeout > 0:
        await asyncio.sleep(1)
        timeout -= 1
        print("Menghubungkan...")

    if wlan.isconnected():
        print(f"Koneksi berhasil dengan {ssid}!")
        print("Alamat IP:", wlan.ifconfig()[0])
        if is_rtc_adjust is None:
            sync_rtc()
            print("rtc telah disinkronkan dengan ntp!")
    else:
        print("Koneksi masih gagal.")
    

async def matchmaking_no_ble():
    """Pencocokan sidik jari tanpa BLE dengan timeout."""
    print("Place your finger on the sensor...")
    home()
    # Tunggu hingga sidik jari terdeteksi, tidak terus menerus
    while True:
        # Cek apakah sidik jari dapat dibaca
        if finger.readImage():
            break

        await asyncio.sleep(1)

    beep()  # Suara indikator
    cycle_images() # animation
        
    try:
        # Proses konversi dan pencocokan sidik jari
        finger.convertImage(0x01)
        position, accuracy = finger.searchTemplate()

        if position >= 0:
            print(f"Fingerprint matched at position {position} with accuracy {accuracy}")
            create_log(position)
            check()
            thanks()
            interact_txt("terima kasih!")
            await asyncio.sleep(2)
        else:
            print("No matching fingerprint found.")
            cross()
            bye()
            interact_txt("Sidik jari\n tidak dikenali!")
            await asyncio.sleep(2)
    except Exception as e:
        print(f"Error during fingerprint matching: {e}")
        print("Skipping this fingerprint attempt.")
        cross()
        bye()  # Penanganan error, keluar dari pencocokan
        interact_txt("Sidik jari\n tidak dikenali!")
        await asyncio.sleep(2)

async def ble_ads():
    """Tugas BLE peripheral untuk advertising."""
    home()
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

async def ble_respons():
    """Tugas menangani data yang dikirim oleh klien melalui BLE."""
    menu()
    while connected_device is not None:  # Berhenti jika koneksi terputus
        try:
            connection, data = await recv_char.written()
            if not data:
                await asyncio.sleep(1)  # Jika tidak ada data, lanjut loop

            command = data.decode("utf-8").strip()
            print(f"Data diterima: {command}")

            if command == "1":
                print("Masukkan ID...")
                interact_txt("Masukkan ID:")
                id_data = await recv_char.written()
                if id_data:
                    id_input = id_data[1].decode("utf-8").strip()
                    if id_input.isdigit():
                        print("Masukkan NIK...")
                        interact_txt("Masukkan NIK:")
                        nik_data = await recv_char.written()
                        if nik_data:
                            nik_input = nik_data[1].decode("utf-8").strip()
                            
                            print("Masukkan Nama...")
                            interact_txt("Masukkan Nama:")
                            name_data = await recv_char.written()
                            if name_data:
                                name_input = name_data[1].decode("utf-8").strip()

                                # ✅ Panggil fungsi dengan 3 argumen
                                await enroll_fingerprint(int(id_input), nik_input, name_input)
                            else:
                                print("Timeout saat menunggu Nama.")
                        else:
                            print("Timeout saat menunggu NIK.")
                    else:
                        print("ID tidak valid.")
                else:
                    print("Timeout saat menunggu ID.")


            elif command == "2":
                await match_fingerprint()

            elif command == "3":
                print("Masukkan ID...")
                interact_txt("Masukkan ID\n untuk dihapus:")
                id_data = await recv_char.written()
                if id_data:
                    id_input = id_data[1].decode("utf-8").strip()
                    if id_input.isdigit():
                        await remove_fingerprint(int(id_input))
                    else:
                        print("ID tidak valid.")
                else:
                    print("Timeout saat menunggu ID.")

            elif command == "4":
                while True:
                    print("Konfirmasi hapus semua sidik jari? (y/n)")
                    confirm_data = await recv_char.written()
                    if confirm_data:
                        confirm_input = confirm_data[1].decode("utf-8").strip().lower()
                        if confirm_input == "y":
                            await clear_all_fingerprints(True)
                            break  # Keluar dari loop setelah konfirmasi "y"
                        elif confirm_input == "n":
                            print("Operasi dibatalkan.")
                            break  # Keluar dari loop jika pengguna membatalkan
                        else:
                            print("Input tidak valid. Silakan masukkan 'y' untuk ya atau 'n' untuk tidak.")


            elif command == "5":
                print("Connecting...")
                await connect_wifi()

            else:
                print("Invalid command!")

        except Exception as e:
            print(f"Error handling BLE data: {e}")

        finally:
            if connected_device is None:
                print("BLE disconnect, keluar dari loop.")
                break
            print("ble respons mencapai finally.")


# fungsi untuk rtc di sinkron`kan dengan ntp
def sync_rtc():
    global is_rtc_adjust
    if is_rtc_adjust is None:
        try:
            ntptime.settime()
            print("Time synchronized with NTP.")
            
            current_time = time.gmtime()
            adjusted_time = time.localtime(time.mktime(current_time) + 7 * 3600)
            
            rtc.date_time((
                adjusted_time[0], adjusted_time[1], adjusted_time[2], 0,
                adjusted_time[3], adjusted_time[4], adjusted_time[5], 0
            ))
            
            is_rtc_adjust = True
            print("RTC adjusted to UTC+7.")
        except Exception as e:
            print("Failed to sync time:", e)
    else:
        print("RTC already adjusted.")

async def device_task():
    """Fungsi utama untuk BLE."""
    global ble_respons_task, matchmaking_task, is_rtc_adjust

    if wlan.isconnected():
        print("telah terkoneksi!")
        if is_rtc_adjust is None:
            sync_rtc()
            print("rtc telah disinkronkan dengan ntp!")
        led(1)
    else:
        print("timdakkkk!")
        is_rtc_adjust = None
        ssid, password = load_wifi()
        if ssid and password:
            wlan.connect(ssid, password)
        led(0)

    # Jalankan ble_ads() di latar belakang
    asyncio.create_task(ble_ads())

    while True:
        try:
            if connected_device is None:
                # Jika perangkat BLE tidak terkoneksi, jalankan matchmaking_no_ble
                if matchmaking_task is None or matchmaking_task.done():
                    matchmaking_task = asyncio.create_task(matchmaking_no_ble())
            else:
                # Jika perangkat BLE terkoneksi, hentikan matchmaking_no_ble jika berjalan
                if matchmaking_task is not None and not matchmaking_task.done():
                    matchmaking_task.cancel()  # Batalkan task matchmaking_no_ble
                    try:
                        await matchmaking_task  # Tunggu task dibatalkan dengan aman
                    except asyncio.CancelledError:
                        print("Matchmaking tanpa BLE dibatalkan.")

                # Jalankan BLE respons jika perangkat terkoneksi
                if ble_respons_task is None or ble_respons_task.done():
                    ble_respons_task = asyncio.create_task(ble_respons())

            # Tunggu sejenak sebelum mencoba lagi
            await asyncio.sleep(1)

        except Exception as e:
            print(f"Error dalam BLE task: {e}")


async def main():
    """Menjalankan device_task secara terus-menerus dengan restart jika terjadi error."""
    # Membuat task check_wifi berjalan di background
    asyncio.create_task(check_wifi())
    asyncio.create_task(clock())
    while True:
        try:
            await device_task()
        except Exception as e:
            print(f"Exception saat menjalankan device_task: {e}")
            await asyncio.sleep(1)  # Tunggu sebentar sebelum restart

#-----------------------------------EVENT_LOOP-----------------------------------------------
# Menjalankan event loop dengan metode yang lebih aman
try:
    asyncio.run(main())
except Exception as e:
    print(f"Exception saat menjalankan event loop: {e}")