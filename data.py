import json
import time

DB_FILE = '/files/attendance.json'  # Sesuaikan path jika perlu

def initialize_db():
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

initialize_db()


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

def read_data():
    try:
        with open(DB_FILE, 'r') as db:
            return json.load(db)
    except ValueError:
        return []

def update_data(entry_id, updated_entry):
    try:
        with open(DB_FILE, 'r') as db:
            data = json.load(db)
    except ValueError:
        data = []
    
    for i, entry in enumerate(data):
        if entry.get('id') == entry_id:
            data[i] = updated_entry
            break
    
    with open(DB_FILE, 'w') as db:
        db.write("[\n")
        for entry in data[:-1]:
            db.write(json.dumps(entry) + ",\n")
        if data:
            db.write(json.dumps(data[-1]) + "\n")
        db.write("]")

def delete_data(entry_id):
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