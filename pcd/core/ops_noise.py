"""Penambahan noise pada citra.

Seluruh noise dibangkitkan secara acak pada citra grayscale lalu hasilnya
dibuka kembali ke tiga kanal, sehingga struktur warna citra tetap terjaga.
"""

from __future__ import annotations

import cv2
import numpy as np

from ..utils.errors import GalatCitra

from .ops_filter import salt_pepper_warna

# Tipe larik citra
TipeCitra = np.ndarray


def _ke_abu(citra: TipeCitra) -> np.ndarray:
    """Mengubah citra menjadi grayscale satu kanal."""
    return cv2.cvtColor(citra, cv2.COLOR_BGR2GRAY) if citra.ndim == 3 else citra


def _kembalikan_abu(citra: TipeCitra, abu: np.ndarray) -> TipeCitra:
    """Menyalakan kembali citra grayscale ke tiga kanal bila perlu."""
    if citra.ndim == 3:
        return cv2.cvtColor(abu, cv2.COLOR_GRAY2BGR)
    return abu


def gaussian(citra: TipeCitra, mean: float = 0.0, sigma: float = 20.0, benih: int | None = None) -> TipeCitra:
    """Menambahkan Gaussian noise.

    Parameter:
        citra: larik citra BGR uint8.
        mean: rata-rata distribusi noise.
        sigma: simpangan baku distribusi noise.
        benih: bila diisi, acakan menjadi deterministik.

    Mengembalikan:
        Larik citra uint8 hasil penambahan noise.
    """
    if sigma < 0:
        raise GalatCitra("Simpangan baku noise tidak boleh negatif.")

    abu = _ke_abu(citra)
    if benih is not None:
        np.random.seed(benih)
    noise = np.random.normal(mean, sigma, abu.shape)
    hasil = np.clip(abu.astype(np.float64) + noise, 0, 255).astype(np.uint8)
    return _kembalikan_abu(citra, hasil)


def rayleigh(citra: TipeCitra, sigma: float = 20.0, benih: int | None = None) -> TipeCitra:
    """Menambahkan Rayleigh noise.

    Parameter:
        citra: larik citra BGR uint8.
        sigma: parameter skala distribusi Rayleigh.
        benih: bila diisi, acakan menjadi deterministik.

    Mengembalikan:
        Larik citra uint8 hasil penambahan noise.
    """
    if sigma <= 0:
        raise GalatCitra("Parameter sigma Rayleigh harus lebih besar dari nol.")

    abu = _ke_abu(citra)
    if benih is not None:
        np.random.seed(benih)
    noise = np.random.rayleigh(sigma, abu.shape)
    hasil = np.clip(abu.astype(np.float64) + noise, 0, 255).astype(np.uint8)
    return _kembalikan_abu(citra, hasil)


def erlang(citra: TipeCitra, bentuk: float = 2.0, skala: float = 10.0, benih: int | None = None) -> TipeCitra:
    """Menambahkan Erlang (Gamma) noise.

    Parameter:
        citra: larik citra BGR uint8.
        bentuk: parameter bentuk (k) distribusi gamma.
        skala: parameter skala (lambda) distribusi gamma.
        benih: bila diisi, acakan menjadi deterministik.

    Mengembalikan:
        Larik citra uint8 hasil penambahan noise.
    """
    if bentuk <= 0 or skala <= 0:
        raise GalatCitra("Parameter Erlang harus lebih besar dari nol.")

    abu = _ke_abu(citra)
    if benih is not None:
        np.random.seed(benih)
    noise = np.random.gamma(bentuk, skala, abu.shape)
    hasil = np.clip(abu.astype(np.float64) + noise, 0, 255).astype(np.uint8)
    return _kembalikan_abu(citra, hasil)


def eksponensial(citra: TipeCitra, mean: float = 20.0, benih: int | None = None) -> TipeCitra:
    """Menambahkan Exponential noise.

    Parameter:
        citra: larik citra BGR uint8.
        mean: rata-rata distribusi eksponensial.
        benih: bila diisi, acakan menjadi deterministik.

    Mengembalikan:
        Larik citra uint8 hasil penambahan noise.
    """
    if mean <= 0:
        raise GalatCitra("Rata-rata noise eksponensial harus lebih besar dari nol.")

    abu = _ke_abu(citra)
    if benih is not None:
        np.random.seed(benih)
    noise = np.random.exponential(mean, abu.shape)
    hasil = np.clip(abu.astype(np.float64) + noise, 0, 255).astype(np.uint8)
    return _kembalikan_abu(citra, hasil)


def seragam(citra: TipeCitra, bawah: float = 0.0, atas: float = 30.0, benih: int | None = None) -> TipeCitra:
    """Menambahkan Uniform noise.

    Parameter:
        citra: larik citra BGR uint8.
        bawah: batas bawah distribusi seragam.
        atas: batas atas distribusi seragam.
        benih: bila diisi, acakan menjadi deterministik.

    Mengembalikan:
        Larik citra uint8 hasil penambahan noise.
    """
    if atas < bawah:
        raise GalatCitra("Batas atas noise harus lebih besar atau sama dengan batas bawah.")

    abu = _ke_abu(citra)
    if benih is not None:
        np.random.seed(benih)
    noise = np.random.uniform(bawah, atas, abu.shape)
    hasil = np.clip(abu.astype(np.float64) + noise, 0, 255).astype(np.uint8)
    return _kembalikan_abu(citra, hasil)


def impuls(citra: TipeCitra, amount: float = 0.02, benih: int | None = None) -> TipeCitra:
    """Menambahkan Impulse noise (salt and pepper).

    Memakai fungsi `add_salt_and_pepper_noise` dari laporan PCD 7 secara
    langsung tanpa mengubahnya.

    Parameter:
        citra: larik citra BGR uint8.
        amount: porsi piksel yang terkena noise, antara 0 dan 1.
        benih: bila diisi, acakan menjadi deterministik.

    Mengembalikan:
        Larik citra uint8 hasil penambahan noise.
    """
    if not 0 <= amount <= 1:
        raise GalatCitra("Porsi noise impuls harus antara 0 dan 1.")
    return salt_pepper_warna(citra, amount, benih)
