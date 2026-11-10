"""Pengubahan citra ke dan dari byte.

Web menerima citra sebagai unggahan berkas dan mengirimnya kembali sebagai
respons HTTP. Modul ini menjembatani keduanya tanpa menyentuh disk.
"""

from __future__ import annotations

import cv2
import numpy as np

from .errors import GalatCitra, PESAN_CITRA_GAGAL_DIBACA

# Format unduhan -> ekstensi yang dikenal cv2.imencode
EKSTENSI_ENCODE: dict[str, str] = {
    "png": ".png",
    "jpg": ".jpg",
    "jpeg": ".jpg",
    "bmp": ".bmp",
    "tif": ".tif",
    "tiff": ".tif",
}


def dari_bytes(data: bytes) -> np.ndarray:
    """Mengubah isi berkas menjadi larik citra BGR.

    Parameter:
        data: isi berkas citra yang diunggah.

    Mengembalikan:
        Larik numpy bentuk (tinggi, lebar, 3) bertipe uint8.

    Raises:
        GalatCitra: bila isi berkas tidak bisa dibaca sebagai citra.
    """
    if not data:
        raise GalatCitra(PESAN_CITRA_GAGAL_DIBACA)
    larik = np.frombuffer(data, dtype=np.uint8)
    citra = cv2.imdecode(larik, cv2.IMREAD_COLOR)
    if citra is None:
        raise GalatCitra(PESAN_CITRA_GAGAL_DIBACA)
    return citra


def ke_bytes(citra: np.ndarray, format: str = "png") -> bytes:
    """Mengubah citra menjadi isi berkas pada format tertentu.

    Parameter:
        citra: larik citra BGR uint8.
        format: kunci format unduhan, misal "png" atau "jpg".

    Raises:
        GalatCitra: bila format tidak didukung atau proses gagal.
    """
    ekstensi = EKSTENSI_ENCODE.get(format.lower())
    if ekstensi is None:
        raise GalatCitra(f"Format unduhan tidak didukung: {format}")
    berhasil, data = cv2.imencode(ekstensi, citra)
    if not berhasil:
        raise GalatCitra("Citra tidak dapat diubah menjadi berkas.")
    return data.tobytes()


def ke_png(citra: np.ndarray) -> bytes:
    """Mengubah citra menjadi isi berkas PNG."""
    return ke_bytes(citra, "png")
