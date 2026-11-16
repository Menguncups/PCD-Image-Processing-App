"""Deteksi tepi citra.

Metode yang tersedia: Sobel, Prewitt, Robert, Laplacian, Laplacian of
Gaussian, Canny, dan Compass.
"""

from __future__ import annotations

import cv2
import numpy as np

from ..utils.errors import GalatCitra

from .ops_filter import konvolusi_sama_ukuran

# Tipe larik citra
TipeCitra = np.ndarray

# Kernel Prewitt
KERNEL_PREWITT_X = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float64)
KERNEL_PREWITT_Y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float64)

# Kernel Robert 2 x 2
KERNEL_ROBERT_X = np.array([[1, 0], [0, -1]], dtype=np.float64)
KERNEL_ROBERT_Y = np.array([[0, 1], [-1, 0]], dtype=np.float64)

# Kernel Laplacian 3 x 3
KERNEL_LAPLACIAN = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float64)

# Arah compass: 8 kernel untuk perubahan intensitas pada tiap arah
KERNEL_COMPASS: dict[str, np.ndarray] = {
    "Timur": np.array([[0, 0, 0], [0, -1, 1], [0, 0, 0]], dtype=np.float64),
    "Timur Laut": np.array([[0, 0, 0], [0, -1, 1], [0, -1, 0]], dtype=np.float64),
    "Utara": np.array([[0, 0, 0], [0, -1, 0], [0, 1, 0]], dtype=np.float64),
    "Barat Laut": np.array([[0, 0, 0], [0, -1, 1], [0, 1, 0]], dtype=np.float64),
    "Barat": np.array([[0, 0, 0], [0, 1, -1], [0, 0, 0]], dtype=np.float64),
    "Barat Daya": np.array([[0, 1, 0], [0, -1, 1], [0, 0, 0]], dtype=np.float64),
    "Selatan": np.array([[0, 1, 0], [0, -1, 0], [0, 0, 0]], dtype=np.float64),
    "Tenggara": np.array([[0, 1, 0], [0, -1, 1], [0, 0, 0]], dtype=np.float64),
}

# Mode tampilan hasil deteksi tepi
MODE_MAGNITUDO = "Magnitudo"
MODE_X = "Gradien X"
MODE_Y = "Gradien Y"
MODE_MODE = [MODE_MAGNITUDO, MODE_X, MODE_Y]


def _ke_abu(citra: TipeCitra) -> np.ndarray:
    """Mengubah citra menjadi grayscale satu kanal."""
    return cv2.cvtColor(citra, cv2.COLOR_BGR2GRAY) if citra.ndim == 3 else citra


def _normalisasi(hasil: np.ndarray) -> np.ndarray:
    """Menormalkan nilai hasil konvolusi ke rentang 0 sampai 255."""
    hasil = np.abs(hasil)
    maks = hasil.max()
    if maks > 0:
        hasil = hasil / maks * 255.0
    return np.clip(hasil, 0, 255).astype(np.uint8)


def sobel(citra: TipeCitra, ukuran: int = 3, mode: str = MODE_MAGNITUDO, ambang: int = 0) -> TipeCitra:
    """Deteksi tepi dengan operator Sobel.

    Parameter:
        citra: larik citra BGR uint8.
        ukuran: ukuran kernel, hanya 3, 5, atau 7 yang didukung OpenCV.
        mode: magnitudo, gradien X, atau gradien Y.
        ambang: bila lebih besar dari nol, hasil diambangkan menjadi biner.

    Mengembalikan:
        Larik citra uint8 hasil deteksi tepi.
    """
    if ukuran not in (3, 5, 7):
        raise GalatCitra("Ukuran kernel Sobel harus 3, 5, atau 7.")

    abu = _ke_abu(citra)
    grad_x = cv2.Sobel(abu, cv2.CV_64F, 1, 0, ksize=ukuran)
    grad_y = cv2.Sobel(abu, cv2.CV_64F, 0, 1, ksize=ukuran)

    if mode == MODE_X:
        hasil = _normalisasi(grad_x)
    elif mode == MODE_Y:
        hasil = _normalisasi(grad_y)
    else:
        hasil = _normalisasi(np.sqrt(grad_x**2 + grad_y**2))

    return _beri_ambang(hasil, ambang)


def prewitt(citra: TipeCitra, mode: str = MODE_MAGNITUDO, ambang: int = 0) -> TipeCitra:
    """Deteksi tepi dengan operator Prewitt memakai konvolusi manual.

    Parameter:
        citra: larik citra BGR uint8.
        mode: magnitudo, gradien X, atau gradien Y.
        ambang: bila lebih besar dari nol, hasil diambangkan menjadi biner.

    Mengembalikan:
        Larik citra uint8 hasil deteksi tepi.
    """
    abu = _ke_abu(citra)
    grad_x = konvolusi_sama_ukuran(abu, KERNEL_PREWITT_X)
    grad_y = konvolusi_sama_ukuran(abu, KERNEL_PREWITT_Y)

    if mode == MODE_X:
        hasil = _normalisasi(grad_x)
    elif mode == MODE_Y:
        hasil = _normalisasi(grad_y)
    else:
        hasil = _normalisasi(np.sqrt(grad_x**2 + grad_y**2))

    return _beri_ambang(hasil, ambang)


def robert(citra: TipeCitra, mode: str = MODE_MAGNITUDO, ambang: int = 0) -> TipeCitra:
    """Deteksi tepi dengan operator Robert memakai konvolusi manual.

    Parameter:
        citra: larik citra BGR uint8.
        mode: magnitudo, gradien X, atau gradien Y.
        ambang: bila lebih besar dari nol, hasil diambangkan menjadi biner.

    Mengembalikan:
        Larik citra uint8 hasil deteksi tepi.
    """
    abu = _ke_abu(citra)
    grad_x = konvolusi_sama_ukuran(abu, KERNEL_ROBERT_X)
    grad_y = konvolusi_sama_ukuran(abu, KERNEL_ROBERT_Y)

    if mode == MODE_X:
        hasil = _normalisasi(grad_x)
    elif mode == MODE_Y:
        hasil = _normalisasi(grad_y)
    else:
        hasil = _normalisasi(np.sqrt(grad_x**2 + grad_y**2))

    return _beri_ambang(hasil, ambang)


def laplacian(citra: TipeCitra, ambang: int = 0) -> TipeCitra:
    """Deteksi tepi dengan operator Laplacian.

    Parameter:
        citra: larik citra BGR uint8.
        ambang: bila lebih besar dari nol, hasil diambangkan menjadi biner.

    Mengembalikan:
        Larik citra uint8 hasil deteksi tepi.
    """
    abu = _ke_abu(citra)
    hasil = _normalisasi(konvolusi_sama_ukuran(abu, KERNEL_LAPLACIAN))
    return _beri_ambang(hasil, ambang)


def log(citra: TipeCitra, sigma: float = 1.0, ambang: int = 0) -> TipeCitra:
    """Deteksi tepi dengan Laplacian of Gaussian.

    Parameter:
        citra: larik citra BGR uint8.
        sigma: parameter sigma pada filter Gaussian.
        ambang: bila lebih besar dari nol, hasil diambangkan menjadi biner.

    Mengembalikan:
        Larik citra uint8 hasil deteksi tepi.
    """
    if sigma <= 0:
        raise GalatCitra("Parameter sigma harus lebih besar dari nol.")

    abu = _ke_abu(citra)
    blur = cv2.GaussianBlur(abu, (0, 0), float(sigma))
    hasil = cv2.Laplacian(blur, cv2.CV_64F, ksize=3)
    hasil = _normalisasi(hasil)
    return _beri_ambang(hasil, ambang)


def canny(citra: TipeCitra, ambang_bawah: int = 50, ambang_atas: int = 150) -> TipeCitra:
    """Deteksi tepi dengan algoritma Canny.

    Parameter:
        citra: larik citra BGR uint8.
        ambang_bawah: ambang bawah deteksi tepi.
        ambang_atas: ambang atas deteksi tepi.

    Mengembalikan:
        Larik citra uint8 berupa citra biner hasil deteksi tepi.
    """
    if ambang_bawah >= ambang_atas:
        raise GalatCitra("Ambang bawah Canny harus lebih kecil dari ambang atas.")

    abu = _ke_abu(citra)
    hasil = cv2.Canny(abu, int(ambang_bawah), int(ambang_atas))
    return hasil


def compass(citra: TipeCitra, ambang: int = 0) -> TipeCitra:
    """Deteksi tepi dengan operator Compass.

    Nilai respon terbesar dari delapan arah diambil untuk setiap piksel.

    Parameter:
        citra: larik citra BGR uint8.
        ambang: bila lebih besar dari nol, hasil diambangkan menjadi biner.

    Mengembalikan:
        Larik citra uint8 hasil deteksi tepi.
    """
    abu = _ke_abu(citra)
    maks_respon = np.zeros_like(abu, dtype=np.float64)
    for kernel in KERNEL_COMPASS.values():
        respons = konvolusi_sama_ukuran(abu, kernel)
        maks_respon = np.maximum(maks_respon, np.abs(respons))

    hasil = _normalisasi(maks_respon)
    return _beri_ambang(hasil, ambang)


def _beri_ambang(hasil: np.ndarray, ambang: int) -> np.ndarray:
    """Mengambangkan hasil deteksi tepi menjadi citra biner bila diminta."""
    if ambang and ambang > 0:
        _, biner = cv2.threshold(hasil, int(ambang), 255, cv2.THRESH_BINARY)
        return biner
    return hasil

