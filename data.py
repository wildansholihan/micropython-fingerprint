import json
import time
from oled import rtc

DB_FILE = '/files/attendance.json'  # Sesuaikan path jika perlu
LOG_FILE = '/files/log.json' # LOkasi Log File

def check_database():
    try:
        with open(DB_FILE, 'r') as db:
            content = db.read().strip()
            if not content:
                raise ValueError("Empty file")
            json.loads(content)
    except (OSError, ValueError):
        print("File database rusak atau kosong, menginisialisasi ulang...")
        with open(DB_FILE, 'w') as db:
            db.write(json.dumps([]))
    try:
        with open(LOG_FILE, 'r') as log:
            content = log.read().strip()
            if not content:
                raise ValueError("Empty file")
            json.loads(content)
    except (OSError, ValueError):
        print("File database rusak atau kosong, menginisialisasi ulang...")
        with open(LOG_FILE, 'w') as log:
            log.write(json.dumps([]))

check_database()


def create_data(new_entry):
    try:
        with open(DB_FILE, 'r') as db:
            data = json.load(db)
    except (ValueError, FileNotFoundError):
        data = []
    
    data.append(new_entry)
    
    with open(DB_FILE, 'w') as db:
        db.write("[\n")
        for entry in data[:-1]:
            db.write(json.dumps(entry) + ",\n")
        if data:
            db.write(json.dumps(data[-1]) + "\n")
        db.write("]")

def create_log(entry_id):
    data = read_data()  # Ambil data dari attendance.json

    # Cari entry secara manual (tanpa next())
    entry = None
    for item in data:
        if item.get('id') == entry_id:
            entry = item
            break  # Langsung keluar jika ditemukan

    if entry is not None:  # Pastikan entry ditemukan
        nama = entry.get('nama', 'Tidak Diketahui')
        nik = entry.get('nik', 'Tidak Diketahui')

        # Ambil data log lama
        try:
            with open(LOG_FILE, 'r') as log:
                log_data = json.load(log)
        except (ValueError, OSError):  # OSError untuk file tidak ditemukan
            log_data = []

        # definisi variable waktu dan tanggal, diambil dari waktu rtc di oled.py
        waktu = "{:02}:{:02}".format(rtc.date_time()[4], rtc.date_time()[5])
        tanggal = "{:02}-{:02}-{:04}".format(rtc.date_time()[2], rtc.date_time()[1], rtc.date_time()[0])
        
        # tambahkan log baru
        new_log = {"keterangan": "{} dengan id {}, dan nik {}, telah melakukan absensi pada jam {} tanggal {}!".format(nama, entry_id, nik, waktu, tanggal)}
        log_data.append(new_log)

        # Simpan kembali ke file log tanpa indent
        with open(LOG_FILE, 'w') as log:
            log.write("[\n")
            for entry in log_data[:-1]:
                log.write(json.dumps(entry) + ",\n")
            if log_data:
                log.write(json.dumps(log_data[-1]) + "\n")
            log.write("]")

    else:
        print("ID {} tidak ditemukan dalam database!".format(entry_id))


def read_data():
    try:
        with open(DB_FILE, 'r') as db:
            return json.load(db)
    except ValueError:
        return []
    
def read_log():
    try:
        with open(LOG_FILE, 'r') as log:
            return json.load(log)
    except ValueError:
        return []

def delete_id(entry_id):
    try:
        with open(DB_FILE, 'r') as db:
            data = json.load(db)
    except ValueError:
        data = []
    
    data = [entry for entry in data if entry.get('id') != entry_id]
    
    with open(DB_FILE, 'w') as db:
        db.write("[\n")
        for entry in data[:-1]:
            db.write(json.dumps(entry) + ",\n")
        if data:
            db.write(json.dumps(data[-1]) + "\n")
        db.write("]")
        
def clear_log():
    print("Mengosongkan log...")
    with open(LOG_FILE, 'w') as log:
        log.write(json.dumps([]))
        
def clear_all_id():
    print("Mengosongkan data...")
    with open(DB_FILE, 'w') as db:
        db.write(json.dumps([]))
    
'''
# Uji coba
create_data({'id': 1, 'nik': 'GMI-002', 'nama': 'galuh', 'masuk': '11:13'})
create_data({'id': 2, 'nik': 'GMI-001', 'nama': 'wildan', 'masuk': '12:20'})
print(read_data())

update_data(1, {'id': 1, 'nik': 'GMI-004', 'nama': 'wildan', 'masuk': '12:20'})
print(read_data())

delete_data(2)
print(read_data())
'''