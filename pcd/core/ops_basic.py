"""Operasi dasar citra: negatif, aritmetika, boolean, dan thresholding.

Seluruh fungsi di berkas ini merupakan port dari kode pada laporan
praktikum PCD 2, PCD 3, dan PCD 5. Fungsi murni tanpa GUI, sehingga bisa
dipanggil langsung dari notebook maupun dari aplikasi.
"""

from __future__ import annotations

import cv2
import numpy as np

from ..utils.errors import GalatCitra, GalatParameter, PESAN_UKURAN_BEDA

# Tipe larik citra
TipeCitra = np.ndarray

# Mode warna untuk operasi aritmetika dan boolean
MODE_ABU = "Grayscale"
MODE_WARNA = "Berwarna"

# Mode operan untuk operasi aritmetika
MODE_OPERAN_CITRA = "Citra + Citra"
MODE_OPERAN_SKALAR = "Citra + Skalar"

# Mode thresholding
MODE_BINER = "Biner"
MODE_BINER_INVERS = "Biner Invers"
MODE_TRUNCASI = "Truncasi"
MODE_TOZERO = "ToZero"

MODE_THRESHOLD = [MODE_BINER, MODE_BINER_INVERS, MODE_TRUNCASI, MODE_TOZERO]


def _siap_abu(citra: TipeCitra, mode: str) -> TipeCitra:
    """Menyiapkan citra sesuai mode warna yang dipilih.

    Pada mode grayscale citra dikembalikan sebagai satu kanal, pada mode
    berwarna citra tetap memakai tiga kanal BGR.
    """
    if mode == MODE_ABU:
        return cv2.cvtColor(citra, cv2.COLOR_BGR2GRAY) if citra.ndim == 3 else citra
    return citra


def periksa_ukuran(citra_a: TipeCitra, citra_b: TipeCitra) -> None:
    """Memastikan dua citra memiliki ukuran yang sama.

    Galat yangdimunculkan memakai kalimat baku dari laporan praktikum.
    """
    if citra_a.shape != citra_b.shape:
        raise GalatCitra(PESAN_UKURAN_BEDA)


def negatif(citra: TipeCitra) -> TipeCitra:
    """Operasi negatif: F'(x, y) = 255 - F(x, y).

    Parameter:
        citra: larik citra BGR uint8.

    Mengembalikan:
        Larik citra uint8 berisi kebalikan intensitas.
    """
    return np.clip(255 - citra, 0, 255).astype(np.uint8)


def aritmetika(citra_a: TipeCitra, citra_b: TipeCitra, jenis: str, mode: str = MODE_ABU) -> TipeCitra:
    """Operasi aritmetika dua citra: tambah, kurang, kali, atau bagi.

    Parameter:
        citra_a: larik citra pertama.
        citra_b: larik citra kedua.
        jenis: salah satu dari "add", "subtract", "multiply", "divide".
        mode: MODE_ABU atau MODE_WARNA.

    Mengembalikan:
        Larik citra hasil operasi.
    """
    periksa_ukuran(citra_a, citra_b)
    a = _siap_abu(citra_a, mode)
    b = _siap_abu(citra_b, mode)

    if jenis == "add":
        hasil = cv2.add(a, b)
    elif jenis == "subtract":
        hasil = cv2.subtract(a, b)
    elif jenis == "multiply":
        hasil = cv2.multiply(a, b)
    elif jenis == "divide":
        # cv2.divide aman terhadap pembagi nol tanpa perlu epsilon manual
        hasil = cv2.divide(a, b)
    else:
        raise GalatCitra(f"Operasi aritmetika tidak dikenal: {jenis}")

    return hasil


def aritmetika_skalar(
    citra_a: TipeCitra,
    skalar: float,
    jenis: str,
    mode: str = MODE_ABU,
) -> TipeCitra:
    """Operasi aritmetika antara citra dan satu nilai skalar.

    Nilai dihitung dalam float agar tidak mengalami overflow ``uint8``,
    kemudian di-clip ke rentang 0-255 sebelum disimpan sebagai ``uint8``.

    Parameter:
        citra_a: larik citra pertama.
        skalar: nilai skalar yang dipakai.
        jenis: salah satu dari "add", "subtract", "multiply", "divide".
        mode: MODE_ABU atau MODE_WARNA.

    Mengembalikan:
        Larik citra uint8 hasil operasi.
    """
    a = _siap_abu(citra_a, mode).astype(np.float32)
    nilai = float(skalar)
    if not np.isfinite(nilai):
        raise GalatParameter("Nilai skalar harus berupa angka yang valid.")
    if jenis == "divide" and nilai == 0:
        raise GalatParameter("Nilai skalar pembagi tidak boleh nol.")

    if jenis == "add":
        hasil = a + nilai
    elif jenis == "subtract":
        hasil = a - nilai
    elif jenis == "multiply":
        hasil = a * nilai
    elif jenis == "divide":
        hasil = a / nilai
    else:
        raise GalatCitra(f"Operasi aritmetika tidak dikenal: {jenis}")

    # Penjepitan wajib dilakukan sebelum cast ke uint8 agar nilai negatif
    # tidak membungkus dan nilai terang tidak melewati 255.
    return np.clip(np.rint(hasil), 0, 255).astype(np.uint8)


def boolean_not(citra: TipeCitra, mode: str = MODE_WARNA) -> TipeCitra:
    """Operasi boolean NOT pada satu citra.

    Citra grayscale memakai `255 - citra`, sedangkan citra berwarna memakai
    `cv2.bitwise_not`, sesuai pola pada laporan praktikum PCD 3.

    Parameter:
        citra: larik citra BGR uint8.
        mode: MODE_ABU atau MODE_WARNA.

    Mengembalikan:
        Larik citra hasil inversi.
    """
    if mode == MODE_ABU:
        abu = cv2.cvtColor(citra, cv2.COLOR_BGR2GRAY) if citra.ndim == 3 else citra
        return np.clip(255 - abu, 0, 255).astype(np.uint8)
    return cv2.bitwise_not(citra)


def boolean_dua(
    citra_a: TipeCitra,
    citra_b: TipeCitra,
    jenis: str,
    mode: str = MODE_ABU,
) -> TipeCitra:
    """Operasi boolean AND, OR, atau XOR pada dua citra.

    Parameter:
        citra_a: larik citra pertama.
        citra_b: larik citra kedua.
        jenis: salah satu dari "and", "or", "xor".
        mode: MODE_ABU atau MODE_WARNA.

    Mengembalikan:
        Larik citra hasil operasi.
    """
    periksa_ukuran(citra_a, citra_b)
    a = _siap_abu(citra_a, mode)
    b = _siap_abu(citra_b, mode)

    if jenis == "and":
        hasil = cv2.bitwise_and(a, b)
    elif jenis == "or":
        hasil = cv2.bitwise_or(a, b)
    elif jenis == "xor":
        hasil = cv2.bitwise_xor(a, b)
    else:
        raise GalatCitra(f"Operasi boolean tidak dikenal: {jenis}")

    return hasil


def thresholding(citra: TipeCitra, nilai: int = 127, mode: str = MODE_BINER) -> TipeCitra:
    """Thresholding global pada citra grayscale.

    Parameter:
        citra: larik citra BGR uint8.
        nilai: nilai ambang 0 sampai 255.
        mode: salah satu dari MODE_THRESHOLD.

    Mengembalikan:
        Larik citra biner atau grayscale uint8.
    """
    abu = cv2.cvtColor(citra, cv2.COLOR_BGR2GRAY) if citra.ndim == 3 else citra
    ambang = int(max(0, min(255, nilai)))

    if mode == MODE_BINER:
        _, hasil = cv2.threshold(abu, ambang, 255, cv2.THRESH_BINARY)
    elif mode == MODE_BINER_INVERS:
        _, hasil = cv2.threshold(abu, ambang, 255, cv2.THRESH_BINARY_INV)
    elif mode == MODE_TRUNCASI:
        _, hasil = cv2.threshold(abu, ambang, 255, cv2.THRESH_TRUNC)
    elif mode == MODE_TOZERO:
        _, hasil = cv2.threshold(abu, ambang, 255, cv2.THRESH_TOZERO)
    else:
        raise GalatCitra(f"Mode thresholding tidak dikenal: {mode}")
    return hasil


def thresholding_biner(citra: TipeCitra, ambang: int = 127) -> TipeCitra:
    """Mengubah citra menjadi citra biner dengan ambang baku 127."""
    abu = cv2.cvtColor(citra, cv2.COLOR_BGR2GRAY) if citra.ndim == 3 else citra
    _, hasil = cv2.threshold(abu, int(ambang), 255, cv2.THRESH_BINARY)
    return hasil
