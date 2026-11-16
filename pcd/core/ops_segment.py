"""Segmentasi citra berbasis ambang.

Ruang lingkup segmentasi dibatasi pada metode berbasis ambang karena
materi referensi pada folder PCD tidak memuat segmentasi watershed maupun
region growing.

Hasil ambang biner sering menyisakan rongga di tengah objek. Karena itu
setiap fungsi di berkas ini menyediakan pilihan mengisi rongga memakai
`scipy.ndimage.binary_fill_holes`.
"""

from __future__ import annotations

import cv2
import numpy as np
from scipy import ndimage

from ..utils.errors import GalatCitra

# Tipe larik citra
TipeCitra = np.ndarray


def _ke_abu(citra: TipeCitra) -> np.ndarray:
    """Mengubah citra menjadi grayscale satu kanal."""
    return cv2.cvtColor(citra, cv2.COLOR_BGR2GRAY) if citra.ndim == 3 else citra


def isi_rongga(mask: np.ndarray) -> np.ndarray:
    """Mengisi rongga di dalam wilayah objek pada citra biner.

    Parameter:
        mask: citra biner uint8 dengan nilai 0 dan 255.

    Mengembalikan:
        Citra biner uint8 tanpa rongga di tengah objek.
    """
    if mask.size == 0:
        return mask
    biner = (mask > 0).astype(np.uint8)
    tertutup = ndimage.binary_fill_holes(biner).astype(np.uint8)
    return tertutup * 255


def _terapkan_isi_rongga(mask: np.ndarray, aktif: bool) -> np.ndarray:
    """Mengisi rongga pada mask bila pengisi rongga diaktifkan."""
    if not aktif:
        return mask
    return isi_rongga(mask)


def otsu(citra: TipeCitra, isi_rongga_aktif: bool = True) -> TipeCitra:
    """Segmentasi dengan ambang global Otsu.

    Parameter:
        citra: larik citra BGR uint8.
        isi_rongga_aktif: bila True, rongga di tengah objek diisi.

    Mengembalikan:
        Larik citra biner uint8.
    """
    abu = _ke_abu(citra)
    _, hasil = cv2.threshold(abu, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return _terapkan_isi_rongga(hasil, isi_rongga_aktif)


def adaptive_mean(
    citra: TipeCitra,
    konstanta: int = 5,
    ukuran_jendela: int = 11,
    isi_rongga_aktif: bool = True,
) -> TipeCitra:
    """Segmentasi dengan ambang adaptif berbasis rata-rata lokal.

    Parameter:
        citra: larik citra BGR uint8.
        konstanta: nilai C yang dikurangi dari rata-rata lokal.
        ukuran_jendela: ukuran jendela neighborhood, harus ganjil.
        isi_rongga_aktif: bila True, rongga di tengah objek diisi.

    Mengembalikan:
        Larik citra biner uint8.
    """
    ukuran_jendela = max(3, int(ukuran_jendela))
    if ukuran_jendela % 2 == 0:
        ukuran_jendela += 1

    abu = _ke_abu(citra)
    hasil = cv2.adaptiveThreshold(
        abu,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        ukuran_jendela,
        int(konstanta),
    )
    return _terapkan_isi_rongga(hasil, isi_rongga_aktif)


def adaptive_gaussian(
    citra: TipeCitra,
    konstanta: int = 5,
    ukuran_jendela: int = 11,
    isi_rongga_aktif: bool = True,
) -> TipeCitra:
    """Segmentasi dengan ambang adaptif berbasis Gaussian.

    Parameter:
        citra: larik citra BGR uint8.
        konstanta: nilai C yang dikurangi dari rata-rata lokal.
        ukuran_jendela: ukuran jendela neighborhood, harus ganjil.
        isi_rongga_aktif: bila True, rongga di tengah objek diisi.

    Mengembalikan:
        Larik citra biner uint8.
    """
    ukuran_jendela = max(3, int(ukuran_jendela))
    if ukuran_jendela % 2 == 0:
        ukuran_jendela += 1

    abu = _ke_abu(citra)
    hasil = cv2.adaptiveThreshold(
        abu,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        ukuran_jendela,
        int(konstanta),
    )
    return _terapkan_isi_rongga(hasil, isi_rongga_aktif)


def multi_level_otsu(
    citra: TipeCitra,
    jumlah_kelas: int = 3,
    isi_rongga_aktif: bool = True,
) -> TipeCitra:
    """Segmentasi dengan ambang Otsu bertingkat pada tiga kelas.

    Ambang dihitung sendiri dari histogram citra, lalu tiap piksel diberi
    label kelas 0, 1, atau 2 berdasarkan posisinya terhadap kedua ambang.

    Parameter:
        citra: larik citra BGR uint8.
        jumlah_kelas: jumlah kelas, saat ini hanya 3 yang didukung.
        isi_rongga_aktif: bila True, rongga di setiap kelas diisi.

    Mengembalikan:
        Larik citra uint8 dengan nilai visual 0, 127, dan 255 untuk tiga kelas.
    """
    if jumlah_kelas != 3:
        raise GalatCitra("Multi level Otsu saat ini hanya mendukung tiga kelas.")

    abu = _ke_abu(citra)
    histogram = np.bincount(abu.ravel(), minlength=256).astype(np.float64)
    total = histogram.sum()
    if total == 0:
        return abu.copy()

    # Cari satu ambang Otsu terlebih dahulu
    ambang_otsu = _otsu_ambang(histogram, total)

    # Histogram dibelah menjadi dua bagian, lalu dicari ambang pada bagian kedua
    bagian = slice(ambang_otsu + 1, 256)
    histogram_bawah = histogram[: ambang_otsu + 1]
    histogram_atas = histogram[bagian]
    if histogram_atas.sum() == 0:
        hasil = np.where(abu > ambang_otsu, 255, 0).astype(np.uint8)
        return _terapkan_isi_rongga(hasil, isi_rongga_aktif)

    ambang_kedua = _otsu_ambang(
        histogram_atas,
        histogram_atas.sum(),
        offset=ambang_otsu + 1,
    )

    label = np.zeros_like(abu, dtype=np.uint8)
    label[abu > ambang_otsu] = 1
    label[abu > ambang_kedua] = 2

    if isi_rongga_aktif:
        # Setiap kelas diperlakukan sebagai wilayah terpisah
        for kelas in (1, 2):
            wilayah = isi_rongga((label == kelas).astype(np.uint8) * 255)
            label[wilayah > 0] = kelas

    # Label 0, 1, 2 terlalu gelap untuk ditampilkan. Petakan ke tiga tingkat
    # abu yang jelas agar hasil segmentasi langsung terlihat.
    return np.take(np.array([0, 127, 255], dtype=np.uint8), label)


def _otsu_ambang(histogram: np.ndarray, total: float, offset: int = 0) -> int:
    """Menghitung nilai ambang Otsu dari sebuah histogram.

    Parameter:
        histogram: jumlah piksel pada tiap nilai intensitas.
        total: jumlah piksel keseluruhan.
        offset: nilai intensitas awal dari histogram ini.

    Mengembalikan:
        Nilai ambang Otsu.
    """
    intensitas = np.arange(len(histogram), dtype=np.float64) + offset
    bobot = histogram / total
    jumlah_kumulatif = np.cumsum(bobot)
    jumlah_kumulatif = np.concatenate(([0.0], jumlah_kumulatif[:-1]))

    rerata = intensitas
    rerata_kumulatif = np.cumsum(bobot * intensitas)
    total_rerata = rerata_kumulatif[-1]
    rerata_kumulatif = np.concatenate(([0.0], rerata_kumulatif[:-1]))

    # Varian antar kelas
    pembilang = (total_rerata * jumlah_kumulatif - rerata_kumulatif) ** 2
    penyebut = jumlah_kumulatif * (1.0 - jumlah_kumulatif)
    dengan_nonzero = penyebut > 0
    varian = np.zeros_like(pembilang)
    varian[dengan_nonzero] = pembilang[dengan_nonzero] / penyebut[dengan_nonzero]

    return int(np.argmax(varian)) + offset


def highlight(citra: TipeCitra, ambang: int = 180, isi_rongga_aktif: bool = True) -> TipeCitra:
    """Segmentasi bagian citra yang terang (highlight).

    Kanal brightness pada ruang HSV dipakai sebagai acuan, lalu citra asli
    disalin hanya pada piksel yang melewati ambang.

    Parameter:
        citra: larik citra BGR uint8.
        ambang: ambang brightness 0 sampai 255.
        isi_rongga_aktif: bila True, rongga di tengah objek diisi.

    Mengembalikan:
        Larik citra BGR uint8 dengan bagian gelap menjadi hitam.
    """
    ambang = int(max(0, min(255, ambang)))
    if citra.ndim == 2:
        abu = citra
    else:
        kanal_v = cv2.cvtColor(citra, cv2.COLOR_BGR2HSV)[:, :, 2]
        abu = kanal_v

    _, mask = cv2.threshold(abu, ambang, 255, cv2.THRESH_BINARY)
    mask = _terapkan_isi_rongga(mask, isi_rongga_aktif)

    if citra.ndim == 2:
        return cv2.bitwise_and(abu, mask)

    hasil = cv2.bitwise_and(citra, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR))
    return hasil


def hitung_komponen(citra: TipeCitra) -> int:
    """Menghitung banyaknya wilayah terhubung pada citra biner.

    Parameter:
        citra: larik citra BGR uint8 atau citra biner satu kanal.

    Mengembalikan:
        Banyaknya wilayah terhubung yang ditemukan.
    """
    abu = _ke_abu(citra)
    biner = (abu > 0).astype(np.uint8)
    label, jumlah = ndimage.label(biner)
    return int(jumlah)


def kontur(citra: TipeCitra, ketebalan: int = 2, isi_rongga_aktif: bool = True) -> TipeCitra:
    """Deteksi dan gambar kontur terluar objek pada citra.

    Masalah segmentasi diselesaikan lewat ambang Otsu, lalu
    `cv2.findContours` dipanggil dengan `RETR_EXTERNAL` untuk mengambil
    kontur terluar setiap objek dan `CHAIN_APPROX_SIMPLE` untuk
    memadatkan kontur menjadi segmen garis lurus saja. Kontur digambar
    berwarna hijau di atas citra masukan.

    Parameter:
        citra: larik citra BGR uint8.
        ketebalan: ketebalan garis kontur, nilai 1 sampai 10 piksel.
        isi_rongga_aktif: bila True, rongga di tengah objek diisi.

    Mengembalikan:
        Larik citra BGR uint8 dengan kontur terluar berwarna hijau.
    """
    ketebalan = int(max(1, min(10, ketebalan)))
    abu = _ke_abu(citra)
    _, biner = cv2.threshold(abu, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    biner = _terapkan_isi_rongga(biner, isi_rongga_aktif)
    contours, _ = cv2.findContours(biner, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    hasil = citra.copy() if citra.ndim == 3 else cv2.cvtColor(citra, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(hasil, contours, -1, (0, 255, 0), ketebalan)
    return hasil
