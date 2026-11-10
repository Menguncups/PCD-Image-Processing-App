"""Operasi pada domain frekuensi: transformasi Fourier dan filter frekuensi.

Filter yang tersedia: ILPF (ideal low pass), BLPF (Butterworth low pass),
IHPF (ideal high pass), dan BHPF (Butterworth high pass).
"""

from __future__ import annotations

import cv2
import numpy as np

from ..utils.errors import GalatCitra

# Tipe larik citra
TipeCitra = np.ndarray


def _ke_abu(citra: TipeCitra) -> np.ndarray:
    """Mengubah citra menjadi grayscale satu kanal."""
    return cv2.cvtColor(citra, cv2.COLOR_BGR2GRAY) if citra.ndim == 3 else citra


def _jarak_freq(tinggi: int, lebar: int) -> np.ndarray:
    """Menyusun matriks jarak frekuensi dari titik tengah spektrum."""
    baris = np.arange(tinggi, dtype=np.float64) - tinggi // 2
    kolom = np.arange(lebar, dtype=np.float64) - lebar // 2
    jarak_y = np.repeat(baris[:, None], lebar, axis=1)
    jarak_x = np.repeat(kolom[None, :], tinggi, axis=0)
    return np.sqrt(jarak_y**2 + jarak_x**2)


def fourier(citra: TipeCitra) -> TipeCitra:
    """Menampilkan spektrum magnituda transformasi Fourier.

    Parameter:
        citra: larik citra BGR uint8.

    Mengembalikan:
        Citra grayscale uint8 berisi spektrum magnituda.
    """
    abu = _ke_abu(citra)
    spectrum = np.fft.fftshift(np.fft.fft2(abu))

    # Ubah magnituda ke skala logaritmik supaya detail tetap terlihat
    magnituda = np.abs(spectrum)
    magnituda = np.log1p(magnituda)

    maks = magnituda.max()
    if maks > 0:
        magnituda = magnituda / maks * 255.0
    return np.clip(magnituda, 0, 255).astype(np.uint8)


def _terapkan_filter(citra: TipeCitra, filter_freq: np.ndarray) -> TipeCitra:
    """Menjalankan filter pada domain frekuensi lalu kembali ke domain citra."""
    abu = _ke_abu(citra)
    spectrum = np.fft.fftshift(np.fft.fft2(abu))
    hasil = np.fft.ifft2(np.fft.ifftshift(spectrum * filter_freq))
    hasil = np.abs(hasil)
    return np.clip(hasil, 0, 255).astype(np.uint8)


def ideal_low_pass(citra: TipeCitra, frekuensi_batas: float = 30.0) -> TipeCitra:
    """Ideal Low Pass Filter.

    Parameter:
        citra: larik citra BGR uint8.
        frekuensi_batas: radius cutoff D0 pada spektrum.

    Mengembalikan:
        Larik citra uint8 hasil filter.
    """
    abu = _ke_abu(citra)
    jarak = _jarak_freq(*abu.shape)
    filter_freq = np.where(jarak <= frekuensi_batas, 1.0, 0.0)
    return _terapkan_filter(citra, filter_freq)


def butterworth_low_pass(citra: TipeCitra, frekuensi_batas: float = 30.0, orde: int = 2) -> TipeCitra:
    """Butterworth Low Pass Filter.

    Parameter:
        citra: larik citra BGR uint8.
        frekuensi_batas: radius cutoff D0 pada spektrum.
        orde: orde filter, semakin besar semakin mendekati filter ideal.

    Mengembalikan:
        Larik citra uint8 hasil filter.
    """
    abu = _ke_abu(citra)
    jarak = _jarak_freq(*abu.shape)
    d0 = max(float(frekuensi_batas), 1e-6)
    n = max(int(orde), 1)
    rasio = (jarak / d0) ** (2 * n)
    filter_freq = 1.0 / (1.0 + rasio)
    return _terapkan_filter(citra, filter_freq)


def ideal_high_pass(citra: TipeCitra, frekuensi_batas: float = 30.0) -> TipeCitra:
    """Ideal High Pass Filter.

    Parameter:
        citra: larik citra BGR uint8.
        frekuensi_batas: radius cutoff D0 pada spektrum.

    Mengembalikan:
        Larik citra uint8 hasil filter.
    """
    abu = _ke_abu(citra)
    jarak = _jarak_freq(*abu.shape)
    filter_freq = np.where(jarak <= frekuensi_batas, 0.0, 1.0)
    return _terapkan_filter(citra, filter_freq)


def butterworth_high_pass(citra: TipeCitra, frekuensi_batas: float = 30.0, orde: int = 2) -> TipeCitra:
    """Butterworth High Pass Filter.

    Parameter:
        citra: larik citra BGR uint8.
        frekuensi_batas: radius cutoff D0 pada spektrum.
        orde: orde filter, semakin besar semakin mendekati filter ideal.

    Mengembalikan:
        Larik citra uint8 hasil filter.
    """
    abu = _ke_abu(citra)
    jarak = _jarak_freq(*abu.shape)
    d0 = max(float(frekuensi_batas), 1e-6)
    n = max(int(orde), 1)
    rasio = (jarak / d0) ** (2 * n)
    filter_freq = 1.0 - 1.0 / (1.0 + rasio)
    return _terapkan_filter(citra, filter_freq)


def filter_frekuensi(citra: TipeCitra, jenis: str, frekuensi_batas: float, orde: int = 2) -> TipeCitra:
    """Menjalankan filter frekuensi berdasarkan nama jenis."""
    tabel = {
        "ilpf": ideal_low_pass,
        "blpf": butterworth_low_pass,
        "ihpf": ideal_high_pass,
        "bhpf": butterworth_high_pass,
    }
    if jenis not in tabel:
        raise GalatCitra(f"Filter frekuensi tidak dikenal: {jenis}")
    if jenis in ("ilpf", "ihpf"):
        return tabel[jenis](citra, frekuensi_batas)
    return tabel[jenis](citra, frekuensi_batas, orde)
