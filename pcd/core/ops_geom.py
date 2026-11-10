"""Operasi geometris citra: translasi, rotasi, zooming, flipping, dan cropping.

Port dari kode laporan praktikum PCD 4.
"""

from __future__ import annotations

import cv2
import numpy as np

from .. import config
from ..utils.errors import PESAN_CROP, GalatCitra

# Tipe larik citra
TipeCitra = np.ndarray

# Arah flipping
FLIP_HORIZONTAL = "Horizontal"
FLIP_VERTIKAL = "Vertikal"
FLIP_KEDUANYA = "Horizontal & Vertikal"
MODE_FLIP = [FLIP_HORIZONTAL, FLIP_VERTIKAL, FLIP_KEDUANYA]


def translasi(citra: TipeCitra, geser_x: int = 0, geser_y: int = 0) -> TipeCitra:
    """Menggeser citra pada sumbu horizontal dan vertikal.

    Parameter:
        citra: larik citra BGR uint8.
        geser_x: pergeseran pada sumbu x dalam piksel.
        geser_y: pergeseran pada sumbu y dalam piksel.

    Mengembalikan:
        Larik citra setelah digeser.
    """
    matriks = np.float32([[1, 0, geser_x], [0, 1, geser_y]])
    return cv2.warpAffine(citra, matriks, (citra.shape[1], citra.shape[0]))


def rotasi(citra: TipeCitra, sudut: float = 0.0) -> TipeCitra:
    """Memutar citra terhadap titik tengahnya tanpa mengubah skalanya.

    Parameter:
        citra: larik citra BGR uint8.
        sudut: sudut rotasi dalam derajat, positif berputar berlawanan arah jam.

    Mengembalikan:
        Larik citra setelah diputar dengan ukuran yang tetap.
    """
    pusat = (citra.shape[1] // 2, citra.shape[0] // 2)
    matriks = cv2.getRotationMatrix2D(pusat, float(sudut), 1.0)
    return cv2.warpAffine(citra, matriks, (citra.shape[1], citra.shape[0]))


def zooming(citra: TipeCitra, skala_x: float = 1.0, skala_y: float = 1.0) -> TipeCitra:
    """Memperbesar atau mengecilkan citra.

    Parameter:
        citra: larik citra BGR uint8.
        skala_x: faktor skala horizontal.
        skala_y: faktor skala vertikal.

    Mengembalikan:
        Larik citra berskala baru.
    """
    lebar_baru = max(int(citra.shape[1] * skala_x), 1)
    tinggi_baru = max(int(citra.shape[0] * skala_y), 1)
    if lebar_baru * tinggi_baru > config.BATAS_HASIL_PIKSEL:
        batas = config.BATAS_HASIL_PIKSEL // 1_000_000
        raise GalatCitra(
            f"Ukuran hasil Zooming melebihi batas {batas} megapiksel. "
            "Kecilkan faktor skala."
        )
    return cv2.resize(citra, (lebar_baru, tinggi_baru), interpolation=cv2.INTER_LINEAR)


def flipping(citra: TipeCitra, arah: str = FLIP_HORIZONTAL) -> TipeCitra:
    """Membalik citra secara horizontal, vertikal, atau keduanya.

    Parameter:
        citra: larik citra BGR uint8.
        arah: salah satu dari MODE_FLIP.

    Mengembalikan:
        Larik citra hasil pembalikan.
    """
    if arah == FLIP_HORIZONTAL:
        return cv2.flip(citra, 1)
    if arah == FLIP_VERTIKAL:
        return cv2.flip(citra, 0)
    if arah == FLIP_KEDUANYA:
        return cv2.flip(citra, -1)
    raise GalatCitra(f"Arah flipping tidak dikenal: {arah}")


def cropping(citra: TipeCitra, x1: int = 0, y1: int = 0, x2: int = 0, y2: int = 0) -> TipeCitra:
    """Memotong sebagian citra pada persegi panjang yang ditentukan.

    Parameter:
        citra: larik citra BGR uint8.
        x1: koordinat kiri area potong.
        y1: koordinat atas area potong.
        x2: koordinat kanan area potong.
        y2: koordinat bawah area potong.

    Mengembalikan:
        Larik citra hasil pemotongan.
    """
    tinggi, lebar = citra.shape[:2]
    x1 = max(0, min(int(x1), lebar))
    y1 = max(0, min(int(y1), tinggi))
    x2 = max(0, min(int(x2), lebar))
    y2 = max(0, min(int(y2), tinggi))

    if x2 <= x1 or y2 <= y1:
        raise GalatCitra(PESAN_CROP)
    return citra[y1:y2, x1:x2].copy()


def koreksi_geometris(citra: TipeCitra, geser_shear: float = 0.0, sudut: float = 0.0) -> TipeCitra:
    """Koreksi geometris berupa shearing yang disertai rotasi kecil.

    Parameter:
        citra: larik citra BGR uint8.
        geser_shear: pergeseran mendatar bagian bawah sebagai fraksi lebar citra.
        sudut: sudut rotasi tambahan dalam derajat.

    Mengembalikan:
        Larik citra terkoreksi.
    """
    tinggi, lebar = citra.shape[:2]
    if lebar == 0 or tinggi == 0:
        raise GalatCitra("Citra memiliki ukuran tidak valid.")

    # Shear 0.5 berarti bagian bawah bergeser setengah lebar citra.
    faktor_shear = float(geser_shear) * lebar / tinggi
    matriks_shear = np.float32([[1, faktor_shear, 0], [0, 1, 0]])
    hasil = cv2.warpAffine(citra, matriks_shear, (lebar, tinggi))

    if sudut:
        pusat = (lebar // 2, tinggi // 2)
        matriks_rotasi = cv2.getRotationMatrix2D(pusat, float(sudut), 1.0)
        hasil = cv2.warpAffine(hasil, matriks_rotasi, (lebar, tinggi))

    return hasil
