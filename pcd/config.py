"""Konfigurasi umum Aplikasi PCD versi web.

Nilai yang sering berubah (identitas, tautan, batas unggah, umur sesi)
dikumpulkan di berkas ini supaya tidak tersebar di kode rute maupun templat.
"""

from __future__ import annotations

from pathlib import Path

# Letak folder proyek: induk dari folder pcd/
AKAR_PROYEK: Path = Path(__file__).resolve().parent.parent
FOLDER_DATA: Path = AKAR_PROYEK / "data"
FOLDER_INSTANCE: Path = AKAR_PROYEK / "instance"
FOLDER_SESI: Path = FOLDER_INSTANCE / "sesi"
BERKAS_MENU: Path = FOLDER_DATA / "menu.json"
BERKAS_KUNCI: Path = FOLDER_INSTANCE / "kunci_rahasia"

# Identitas aplikasi
APP_NAME = "Sistem Image Processing (SIMPRO)"
APP_SUBTITLE = "Copyright © Mengasah (2026)"
APP_VERSION = "0.1.0"
APP_DESKRIPSI = (
    "Aplikasi pengolahan citra digital dengan 56 operasi citra, enhancement, "
    "noise, deteksi tepi, dan segmentasi. Setiap operasi citra menampilkan "
    "rumus pada panel parameter dan hasilnya pada kartu Hasil. Operasi "
    "Geometric hanya berjalan lewat tombol Jalankan. Citra B hanya ditampilkan "
    "untuk operasi yang membutuhkan dua citra, dan panel parameter selalu "
    "terbuka, termasuk saat Citra B belum dimuat."
)

# Tombol Terapkan pada kartu Hasil. Endpoint dan riwayat tetap tersedia agar
# fitur ini bisa diaktifkan kembali tanpa mengubah alur kerja.
TAMPILKAN_TERAPKAN = False

# Panel histogram di samping panel parameter. Bila False, server tidak
# menghitung histogram dan panelnya disembunyikan.
TAMPILKAN_HISTOGRAM = True

# Placeholder, akan diganti sendiri oleh pengembang
TEAM_MEMBERS = [
    "Afdhal Fidi Ansori",
    "Muhammad Rifqi Fathurrahman",
    "Yusuf Budiawan Azri",
]
GITHUB_URL = "https://github.com/Menguncups/PCD-Image-Processing-App"
YOUTUBE_URL = "https://www.youtube.com/@username"

COPYRIGHT = "© 2026 Mengasah. Hak cipta dilindungi."

# Format unduhan: kunci -> (mimetype, ekstensi, label)
FORMAT_UNDUH: dict[str, tuple[str, str, str]] = {
    "png": ("image/png", ".png", "PNG"),
    "jpg": ("image/jpeg", ".jpg", "JPEG"),
    "bmp": ("image/bmp", ".bmp", "BMP"),
    "tiff": ("image/tiff", ".tif", "TIFF"),
}

# Ekstensi berkas yang boleh diunggah
EKSTENSI_DITERIMA = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}

# Batas unggahan dan ukuran citra
BATAS_UNGGAH = 20 * 1024 * 1024
BATAS_PIKSEL = 40_000_000

# Batas hasil operasi yang memperbesar ukuran citra, misalnya Zooming.
BATAS_HASIL_PIKSEL = 80_000_000

# Umur ruang kerja sebelum dibersihkan otomatis (detik)
UMUR_SESI = 24 * 60 * 60

# Jeda pemeriksaan sesi kedaluwarsa (detik)
JEDA_BERSIH = 10 * 60
