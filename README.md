# Micropython Fingerprint Access System

Sistem otentikasi berbasis fingerprint menggunakan MicroPython, OLED display, BLE, dan audio feedback. Cocok digunakan untuk proyek smart lock, sistem absensi, dan perangkat IoT lainnya.

## 🚀 Fitur

- ✅ Pendaftaran dan verifikasi sidik jari (enroll & match)
- 📟 Tampilan antarmuka lewat OLED
- 🔊 Umpan balik suara (audio feedback)
- 🔗 Komunikasi Bluetooth Low Energy (BLE)
- 🌐 Sinkronisasi waktu via NTP (jika Wi-Fi tersedia)
- 🧠 Desain modular dengan `main.py` sebagai entry-point

## 📂 Struktur Folder

```
micropython-fingerprint/
├── main.py             # Program utama
├── fingerprint.py      # Modul interaksi sensor sidik jari
├── oled.py             # Tampilan dan kontrol OLED
├── audio.py            # Umpan balik suara
├── data.py             # Konstanta atau penyimpanan lokal
├── lib/                # Library eksternal tambahan (aioble, dsb)
├── animation/          # Gambar animasi OLED
├── img/                # Gambar statis untuk tampilan OLED
├── files/              # Folder data tambahan (opsional)
└── .git/               # Versi kontrol (jika digunakan)
```

## 🛠️ Persyaratan Hardware

- ESP32 atau board lain yang mendukung MicroPython dan BLE
- Sensor sidik jari (misal: R503 atau ZFM-20)
- OLED display (SPI/I2C 128x64 atau 128x32)
- Speaker aktif (untuk audio feedback)
- (Opsional) Modul RTC & Wi-Fi

## 🧪 Cara Menggunakan

1. Flash MicroPython firmware ke board kamu.
2. Upload semua file dan folder ke board via Thonny atau `mpremote`.
3. Jalankan `main.py` secara otomatis (pastikan sudah di-setup `boot.py` jika diperlukan).
4. Ikuti petunjuk di layar OLED dan audio untuk pendaftaran/verifikasi.

## 📦 Library yang Digunakan

- `aioble` untuk BLE
- `uasyncio` untuk async loop
- `ntptime` untuk sinkronisasi waktu
- `machine`, `network` dari MicroPython core

---

Proyek ini dibuat untuk eksperimen dan pembelajaran, silakan sesuaikan sesuai kebutuhan perangkat dan sistemmu.
