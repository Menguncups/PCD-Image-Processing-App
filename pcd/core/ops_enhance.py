"""Peningkatan kualitas citra: kecerahan, kontras, histogram, dan penghalusan.

Port dari kode laporan praktikum PCD 6 (kecerahan dan kontras) serta PCD 7
(low pass, median, high pass, dan high boost).
"""

from __future__ import annotations

import cv2
import numpy as np

from ..utils.errors import GalatCitra

# Tipe larik citra
TipeCitra = np.ndarray

# Kernel high pass 3 x 3 dipakai pada laporan PCD 7
KERNEL_HIGHPASS = np.array(
    [
        [-1, -1, -1],
        [-1, 8, -1],
        [-1, -1, -1],
    ],
    dtype=np.float64,
)

# Kernel rata-rata 3 x 3
KERNEL_MEAN = np.ones((3, 3), np.float32) / 9


def kecerahan(citra: TipeCitra, nilai: int = 50) -> TipeCitra:
    """Mengubah kecerahan citra.

    Nilai positif mencerahkan citra, nilai negatif menggelapkan.

    Parameter:
        citra: larik citra BGR uint8.
        nilai: besar perubahan intensitas, antara -255 dan 255.

    Mengembalikan:
        Larik citra uint8 hasil perubahan kecerahan.
    """
    nilai = int(max(-255, min(255, nilai)))
    if nilai >= 0:
        return cv2.add(citra, np.full(citra.shape, nilai, dtype=np.uint8))
    return cv2.subtract(citra, np.full(citra.shape, -nilai, dtype=np.uint8))


def kontras(citra: TipeCitra, nilai_min: int = 0, nilai_max: int = 255) -> TipeCitra:
    """Meregangkan kontras citra pada rentang intensitas baru secara per kanal.

    Parameter:
        citra: larik citra BGR uint8.
        nilai_min: batas bawah intensitas baru.
        nilai_max: batas atas intensitas baru.

    Mengembalikan:
        Larik citra BGR uint8 hasil peregangan kontras.
    """
    if citra.ndim == 2:
        return _kontras_single(citra, nilai_min, nilai_max)

    # Proses per kanal B, G, R
    b, g, r = cv2.split(citra)
    return cv2.merge([
        _kontras_single(b, nilai_min, nilai_max),
        _kontras_single(g, nilai_min, nilai_max),
        _kontras_single(r, nilai_min, nilai_max)
    ])


def _kontras_single(abu: np.ndarray, nilai_min: int, nilai_max: int) -> np.ndarray:
    i_min, i_max = float(abu.min()), float(abu.max())
    if i_max - i_min == 0:
        return abu.copy()
    l_min, l_max = float(nilai_min), float(nilai_max)
    regangan = ((abu.astype(np.float64) - i_min) / (i_max - i_min) * (l_max - l_min) + l_min)
    return np.clip(regangan, 0, 255).astype(np.uint8)


def histogram_ekualisasi(citra: TipeCitra) -> TipeCitra:
    """Menyamakan histogram citra agar rentang intensitas lebih merata.

    Parameter:
        citra: larik citra BGR uint8.

    Mengembalikan:
        Larik citra uint8 hasil ekualisasi histogram.
    """
    if citra.ndim == 2:
        return cv2.equalizeHist(citra)

    # Citra berwarna: ekualisasi dijalankan pada kanal lightness di ruang Lab
    ruang_lab = cv2.cvtColor(citra, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(ruang_lab)
    l = cv2.equalizeHist(l)
    return cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)


def lowpass(citra: TipeCitra) -> TipeCitra:
    """Low pass filtering dengan filter rata-rata 3 x 3.

    Parameter:
        citra: larik citra BGR uint8.

    Mengembalikan:
        Larik citra uint8 hasil pengaburan.
    """
    return cv2.filter2D(citra, -1, KERNEL_MEAN)


def median(citra: TipeCitra, ukuran: int = 3) -> TipeCitra:
    """Median filtering dengan jendela berukuran ganjil.

    Parameter:
        citra: larik citra BGR uint8.
        ukuran: ukuran jendela, harus ganjil dan minimal 3.

    Mengembalikan:
        Larik citra uint8 hasil median filtering.
    """
    ukuran = max(3, int(ukuran))
    if ukuran % 2 == 0:
        ukuran += 1
    return cv2.medianBlur(citra, ukuran)


def highpass(citra: TipeCitra) -> TipeCitra:
    """High pass filtering memakai kernel 3 x 3 dari laporan PCD 7.

    Parameter:
        citra: larik citra BGR uint8.

    Mengembalikan:
        Larik citra uint8 hasil high pass filtering.
    """
    return cv2.filter2D(citra, -1, KERNEL_HIGHPASS)


def highboost(citra: TipeCitra, faktor: float = 1.5, ukuran_kernel: int = 5) -> TipeCitra:
    """High boost filtering: g(x, y) = A * f(x, y) - f_lowpass(x, y).

    Low pass memakai Gaussian blur, lalu digabung dengan `cv2.addWeighted`
    seperti pada laporan praktikum PCD 7.

    Parameter:
        citra: larik citra BGR uint8.
        faktor: faktor penguatan A, nilainya lebih besar dari 1.
        ukuran_kernel: ukuran kernel Gaussian low pass.

    Mengembalikan:
        Larik citra uint8 hasil high boost filtering.
    """
    faktor = float(faktor)
    if faktor <= 1.0:
        raise GalatCitra("Faktor high boost harus lebih besar dari 1.")

    ukuran_kernel = max(3, int(ukuran_kernel))
    if ukuran_kernel % 2 == 0:
        ukuran_kernel += 1

    low_pass = cv2.GaussianBlur(citra, (ukuran_kernel, ukuran_kernel), 0)
    return cv2.addWeighted(citra, faktor, low_pass, -(faktor - 1), 0)


def histogram(citra: TipeCitra) -> tuple[np.ndarray, np.ndarray]:
    """Menghitung histogram dan binning untuk citra grayscale.

    Parameter:
        citra: larik citra BGR uint8.

    Mengembalikan:
        Pasangan (nilai bin, jumlah piksel).
    """
    abu = cv2.cvtColor(citra, cv2.COLOR_BGR2GRAY) if citra.ndim == 3 else citra
    return np.histogram(abu.ravel(), bins=256, range=(0, 256))
