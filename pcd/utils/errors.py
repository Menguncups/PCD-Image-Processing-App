"""Pesan error baku dan kelas galat aplikasi.

Pesan error memakai kalimat baku yang sudah dipakai pada laporan praktikum
sehingga konsisten antara aplikasi dan dokumen.
"""

from __future__ import annotations

# Pesan baku yang wajib dipertahankan
PESAN_UKURAN_BEDA = (
    "Citra tidak memiliki ukuran yang sama. Harap gunakan citra dengan dimensi yang sama."
)
PESAN_CITRA_KOSONG = "Belum ada citra yang dimuat. Silakan buka citra terlebih dahulu."
PESAN_CITRA_B_KOSONG = (
    "Belum ada citra referensi (Citra B). Silakan buka citra kedua terlebih dahulu."
)
PESAN_CITRA_GAGAL_DIBACA = "Citra tidak dapat dibaca. Pastikan berkas bukan hasil rusak."
PESAN_PARAMETER = "Nilai parameter tidak valid. Mohon periksa kembali isian Anda."
PESAN_KERNEL = "Matriks kernel harus berukuran 3 x 3 dan hanya berisi angka."
PESAN_TIDAK_ADA_HASIL = "Belum ada hasil operasi untuk diterapkan."
PESAN_CROP = (
    "Area cropping tidak valid. Pastikan titik kanan bawah lebih besar "
    "dari titik kiri atas."
)


class GalatAplikasi(Exception):
    """Galat umum yang aman ditampilkan ke pengguna."""


class GalatCitra(GalatAplikasi):
    """Galat yang berkaitan dengan isi atau ukuran citra."""


class GalatParameter(GalatAplikasi):
    """Galat yang berkaitan dengan nilai parameter operasi."""


class GalatOperasi(GalatAplikasi):
    """Galat yang terjadi saat menjalankan algoritma."""
