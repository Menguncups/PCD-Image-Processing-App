"""Pembacaan dan penyimpanan berkas citra.

Fungsi di sini memakai `cv2.imdecode` dan `cv2.imencode` sebagai pengganti
`cv2.imread` dan `cv2.imwrite` karena pada Windows fungsi bawaan OpenCV
gagal menangani path yang mengandung huruf non ASCII seperti "Documents".
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from .errors import GalatCitra, PESAN_CITRA_GAGAL_DIBACA

# Tipe larik citra yang dipakai di seluruh aplikasi
TipeCitra = np.ndarray


def baca_citra(path: str | Path) -> TipeCitra:
    """Membaca citra dari berkas dan mengembalikannya sebagai larik BGR uint8.

    Parameter:
        path: lokasi berkas citra.

    Mengembalikan:
        Larik numpy dengan bentuk (tinggi, lebar, 3) dan tipe uint8.
    """
    berkas = Path(path)
    if not berkas.exists():
        raise GalatCitra(f"Berkas citra tidak ditemukan: {berkas}")

    # np.fromfile + imdecode agar path berhuruf non ASCII tetap terbaca
    data = np.fromfile(str(berkas), dtype=np.uint8)
    citra = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if citra is None:
        raise GalatCitra(PESAN_CITRA_GAGAL_DIBACA)
    return citra


def tulis_citra(path: str | Path, citra: TipeCitra) -> None:
    """Menyimpan citra ke berkas sesuai ekstensi yang diberikan.

    Parameter:
        path: lokasi berkas tujuan.
        citra: larik citra BGR uint8.
    """
    berkas = Path(path)
    if berkas.suffix == "":
        berkas = berkas.with_suffix(".png")

    ekstensi = berkas.suffix.lower()
    if ekstensi not in (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"):
        raise GalatCitra(f"Format berkas tidak didukung: {berkas.suffix}")

    # imencode + tofile agar path berhuruf non ASCII tetap bisa ditulis
    berhasil, data = cv2.imencode(ekstensi, citra)
    if not berhasil:
        raise GalatCitra("Citra tidak dapat disimpan ke berkas tersebut.")
    data.tofile(str(berkas))


def ke_abu(citra: TipeCitra) -> TipeCitra:
    """Mengubah citra berwarna menjadi citra grayscale satu kanal."""
    if citra is None:
        raise GalatCitra("Citra kosong tidak dapat diubah.")
    if citra.ndim == 2:
        return citra
    return cv2.cvtColor(citra, cv2.COLOR_BGR2GRAY)


def ke_bgr(citra: TipeCitra) -> TipeCitra:
    """Memastikan citra memiliki tiga kanal BGR."""
    if citra is None:
        raise GalatCitra("Citra kosong tidak dapat diubah.")
    if citra.ndim == 3 and citra.shape[2] == 3:
        return citra
    if citra.ndim == 3 and citra.shape[2] == 4:
        return cv2.cvtColor(citra, cv2.COLOR_BGRA2BGR)
    return cv2.cvtColor(citra, cv2.COLOR_GRAY2BGR)


def ukuran_sama(citra_a: TipeCitra, citra_b: TipeCitra) -> bool:
    """Memeriksa apakah dua citra memiliki dimensi piksel yang sama."""
    return citra_a.shape == citra_b.shape


def deskripsi(citra: TipeCitra, nama_berkas: str = "") -> str:
    """Menyusun keterangan ringkas citra untuk notifikasi dan metadata."""
    if citra is None:
        return "Tidak ada citra"
    tinggi, lebar = citra.shape[:2]
    warna_teks = "RGB" if citra.ndim == 3 and citra.shape[2] == 3 else "Grayscale"
    bagian = [bagian for bagian in (nama_berkas, f"{lebar} x {tinggi}", warna_teks) if bagian]
    return "  |  ".join(bagian)
