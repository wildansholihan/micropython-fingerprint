import storage
import json
import wifi
import socketpool
import ssl
import adafruit_requests

storage.remount('/', readonly=False)
# Fungsi untuk membaca data Wi-Fi yang ada di file JSON
def load_wifi_data():
    try:
        with open('wifi_config.json', 'r') as f:
            return json.load(f)
    except OSError:  # Menangani error file tidak ditemukan atau tidak dapat dibuka
        print("File wifi_config.json tidak ditemukan atau rusak. Membuat struktur data baru.")
        return {"users": []}
    except ValueError:  # Jika file JSON ada tetapi isinya rusak
        print("File wifi_config.json rusak. Membuat struktur data baru.")
        return {"users": []}

# Fungsi untuk menyimpan data Wi-Fi ke file JSON
def save_wifi_data(data):
    try:
        # Mengubah data menjadi string JSON tanpa indentasi dan urutan kunci
        json_string = json.dumps(data)  # Tanpa indentasi

        # Menambahkan newline dan spasi agar lebih mudah dibaca
        json_string = json_string.replace(",", ",\n")  # Menambahkan newline setelah setiap koma
        json_string = json_string.replace("{", "{\n ")  # Menambahkan newline setelah '{' dan spasi
        json_string = json_string.replace("}", "\n}")  # Menambahkan newline sebelum '}' dan spasi

        # Menyimpan string JSON yang sudah diformat ke dalam file
        with open('wifi_config.json', 'w') as f:
            f.write(json_string)

        print("Data Wi-Fi berhasil disimpan ke wifi_config.json.")
    except Exception as e:
        print("Gagal menyimpan data Wi-Fi:", e)

# Fungsi untuk menambah pengguna baru
def add_user():
    username = input("Masukkan Username: ")
    ssid = input("Masukkan SSID Wi-Fi: ")
    password = input("Masukkan Password Wi-Fi: ")
    data = load_wifi_data()
    data['users'].append({'username': username, 'ssid': ssid, 'password': password})
    save_wifi_data(data)
    print(f"User {username} telah ditambahkan!")

# Fungsi untuk menghapus pengguna berdasarkan username
def delete_user():
    username = input("Masukkan Username yang ingin dihapus: ")
    data = load_wifi_data()
    data['users'] = [user for user in data['users'] if user['username'] != username]
    save_wifi_data(data)
    print(f"User {username} telah dihapus!")

# Fungsi untuk mengedit pengguna berdasarkan username
def edit_user():
    username = input("Masukkan Username yang ingin diedit: ")
    new_ssid = input("Masukkan SSID Wi-Fi baru: ")
    new_password = input("Masukkan Password Wi-Fi baru: ")
    data = load_wifi_data()
    for user in data['users']:
        if user['username'] == username:
            user['ssid'] = new_ssid
            user['password'] = new_password
            print(f"Data pengguna {username} berhasil diperbarui.")
            break
    else:
        print(f"Pengguna {username} tidak ditemukan.")
    save_wifi_data(data)

# Fungsi untuk menampilkan data Wi-Fi yang tersimpan
def load_users():
    data = load_wifi_data()
    if data['users']:
        print("Data pengguna yang tersimpan:")
        for user in data['users']:
            print(f"- Username: {user['username']}, SSID: {user['ssid']}, Password: {user['password']}")
    else:
        print("Tidak ada data pengguna yang tersimpan.")

# Fungsi untuk menyambungkan ke Wi-Fi
def connect_wifi(ssid, password):
    print(f"Menyambungkan ke Wi-Fi: {ssid}...")
    try:
        wifi.radio.connect(ssid, password)
        print(f"Tersambung ke Wi-Fi! Alamat IP: {wifi.radio.ipv4_address}")
    except Exception as e:
        print("Gagal menyambung ke Wi-Fi:", e)
        return False
    return True

# Fungsi untuk mengambil data dari API
def fetch_data():
    # Membuat socket pool dan objek requests dengan SSL context
    pool = socketpool.SocketPool(wifi.radio)
    ssl_context = ssl.create_default_context()
    requests = adafruit_requests.Session(pool, ssl_context)
    url = "https://jsonplaceholder.typicode.com/todos/1"
    
    print(f"Mengambil data dari {url}...")
    try:
        if wifi.radio.ipv4_address == "0.0.0.0":  # Periksa jika belum tersambung
            print("Tidak ada koneksi Wi-Fi. Tidak dapat mengambil data.")
            return
        response = requests.get(url)
        print("Kode Status Response:", response.status_code)
        print("Response JSON:", response.json())
        response.close()
    except Exception as e:
        print("Gagal mengambil data:", e)

# Menu utama
while True:
    print("\n=== Menu ===")
    print("1. Tambah Pengguna")
    print("2. Edit Pengguna")
    print("3. Hapus Pengguna")
    print("4. Tampilkan Semua Pengguna")
    print("5. Ambil Data API")
    print("0. Keluar")

    choice = input("Pilih opsi: ")

    if choice == '1':
        add_user()
    elif choice == '2':
        edit_user()
    elif choice == '3':
        delete_user()
    elif choice == '4':
        load_users()
    elif choice == '5':
        ssid = input("Masukkan SSID Wi-Fi: ")
        password = input("Masukkan Password Wi-Fi: ")
        if connect_wifi(ssid, password):
            fetch_data()
    elif choice == '0':
        print("Keluar dari program.")
        break
    else:
        print("Opsi tidak valid. Silakan pilih lagi.")