"""Pengubahan warna citra: biner, grayscale, RGB, HSV, CMY, YUV, YIQ, dan pseudo.

Referensi utama adalah laporan praktikum PCD 1 yang membahas jenis citra
digital dan konversi ruang warna.
"""

from __future__ import annotations

import cv2
import numpy as np

from ..utils.errors import GalatCitra

# Tipe larik citra
TipeCitra = np.ndarray


def _panel(kanal: np.ndarray, warna_bgr: tuple[int, int, int]) -> TipeCitra:
    """Memberi tint warna pada satu kanal supaya panelnya tidak terlihat abu-abu.

    Warna ditulis dalam urutan BGR sesuai kebiasaan OpenCV. Nilai kanal
    diskalakan ke warna tersebut, sehingga kanal yang terang tampil
    berwarna penuh dan yang gelap tampil mendekati hitam.
    """
    skala = np.array(warna_bgr, dtype=np.float64) / 255.0
    return (kanal.astype(np.float64)[:, :, None] * skala).astype(np.uint8)


def biner(citra: TipeCitra, ambang: int = 127) -> TipeCitra:
    """Mengubah citra menjadi citra biner satu kanal.

    Parameter:
        citra: larik citra BGR uint8.
        ambang: nilai ambang 0 sampai 255.

    Mengembalikan:
        Larik citra biner uint8.
    """
    abu = cv2.cvtColor(citra, cv2.COLOR_BGR2GRAY) if citra.ndim == 3 else citra
    _, hasil = cv2.threshold(abu, int(ambang), 255, cv2.THRESH_BINARY)
    return hasil


def grayscale(citra: TipeCitra) -> TipeCitra:
    """Mengubah citra berwarna menjadi citra grayscale satu kanal."""
    if citra.ndim == 2:
        return citra
    return cv2.cvtColor(citra, cv2.COLOR_BGR2GRAY)


def rgb(citra: TipeCitra) -> TipeCitra:
    """Memisahkan citra berwarna menjadi kanal R, G, dan B.

    Parameter:
        citra: larik citra BGR uint8.

    Mengembalikan:
        Citra tiga kanal berisi kanal R, G, dan B disusun mendatar.
    """
    if citra.ndim == 2:
        abu = citra
        return np.hstack(
            [_panel(abu, (0, 0, 255)), _panel(abu, (0, 255, 0)), _panel(abu, (255, 0, 0))]
        )
    kanal_b, kanal_g, kanal_r = cv2.split(citra)
    return np.hstack(
        [_panel(kanal_r, (0, 0, 255)), _panel(kanal_g, (0, 255, 0)), _panel(kanal_b, (255, 0, 0))]
    )


def hsv(citra: TipeCitra) -> TipeCitra:
    """Mengubah citra ke ruang HSV lalu menampilkan kanal H, S, dan V.

    Parameter:
        citra: larik citra BGR uint8.

    Mengembalikan:
        Citra tiga kanal berisi kanal H, S, dan V disusun mendatar.
    """
    if citra.ndim == 2:
        citra = cv2.cvtColor(citra, cv2.COLOR_GRAY2BGR)
    kanal_h, kanal_s, kanal_v = cv2.split(cv2.cvtColor(citra, cv2.COLOR_BGR2HSV))
    # Panel H digambar dengan warna hue aslinya per piksel (S=V=255),
    # supaya tampil seperti visualisasi hue pada umumnya.
    hue = cv2.cvtColor(
        cv2.merge([kanal_h, np.full_like(kanal_h, 255), np.full_like(kanal_h, 255)]),
        cv2.COLOR_HSV2BGR,
    )
    return np.hstack(
        [hue, _panel(kanal_s, (255, 0, 255)), _panel(kanal_v, (255, 255, 255))]
    )


def cmy(citra: TipeCitra) -> TipeCitra:
    """Menghitung komponen CMY dari citra berwarna.

    Parameter:
        citra: larik citra BGR uint8.

    Mengembalikan:
        Citra tiga kanal berisi kanal C, M, dan Y disusun mendatar.
    """
    if citra.ndim == 2:
        citra = cv2.cvtColor(citra, cv2.COLOR_GRAY2BGR)
    bgr = citra.astype(np.float64)
    rgb_nilai = bgr[:, :, ::-1]
    cmy_nilai = 255.0 - rgb_nilai
    kanal_c, kanal_m, kanal_y = np.split(cmy_nilai, 3, axis=2)
    return np.hstack(
        [
            _panel(kanal_c[:, :, 0], (255, 255, 0)),
            _panel(kanal_m[:, :, 0], (255, 0, 255)),
            _panel(kanal_y[:, :, 0], (0, 255, 255)),
        ]
    )


def yuv(citra: TipeCitra) -> TipeCitra:
    """Mengubah citra ke ruang YUV lalu menampilkan kanal Y, U, dan V.

    Parameter:
        citra: larik citra BGR uint8.

    Mengembalikan:
        Citra tiga kanal berisi kanal Y, U, dan V disusun mendatar.
    """
    if citra.ndim == 2:
        citra = cv2.cvtColor(citra, cv2.COLOR_GRAY2BGR)
    kanal_y, kanal_u, kanal_v = cv2.split(cv2.cvtColor(citra, cv2.COLOR_BGR2YUV))
    return np.hstack(
        [_panel(kanal_y, (255, 255, 255)), _panel(kanal_u, (255, 0, 0)), _panel(kanal_v, (0, 0, 255))]
    )


def yiq(citra: TipeCitra) -> TipeCitra:
    """Menghitung komponen YIQ dari citra berwarna.

    Parameter:
        citra: larik citra BGR uint8.

    Mengembalikan:
        Citra tiga kanal berisi kanal Y, I, dan Q disusun mendatar.
    """
    if citra.ndim == 2:
        citra = cv2.cvtColor(citra, cv2.COLOR_GRAY2BGR)
    rgb_nilai = citra[:, :, ::-1].astype(np.float64)

    # Rumus YIQ standar untuk citra RGB
    y = 0.299 * rgb_nilai[:, :, 0] + 0.587 * rgb_nilai[:, :, 1] + 0.114 * rgb_nilai[:, :, 2]
    i = 0.596 * rgb_nilai[:, :, 0] - 0.274 * rgb_nilai[:, :, 1] - 0.322 * rgb_nilai[:, :, 2]
    q = 0.211 * rgb_nilai[:, :, 0] - 0.523 * rgb_nilai[:, :, 1] + 0.312 * rgb_nilai[:, :, 2]

    # Kanal I dan Q berpusat di 128; jepit sebelum diubah ke uint8 agar tidak
    # membungkus nilai negatif menjadi terang.
    i = np.clip(i + 128.0, 0, 255)
    q = np.clip(q + 128.0, 0, 255)
    return np.hstack(
        [_panel(y, (255, 255, 255)), _panel(i, (0, 165, 255)), _panel(q, (0, 255, 255))]
    )


def pseudo(citra: TipeCitra) -> TipeCitra:
    """Memberi warna semu pada citra grayscale memakai palet Turbo.

    Parameter:
        citra: larik citra BGR uint8.

    Mengembalikan:
        Citra berwarna hasil pemetaan palet semu.
    """
    abu = cv2.cvtColor(citra, cv2.COLOR_BGR2GRAY) if citra.ndim == 3 else citra
    abu = cv2.normalize(abu, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # Palet TURBO lebih halus dibanding JET, dan sudah tersedia di OpenCV
    palet = getattr(cv2, "COLORMAP_TURBO", cv2.COLORMAP_JET)
    return cv2.applyColorMap(abu, palet)


def ruang_warna(nama: str, citra: TipeCitra) -> TipeCitra:
    """Menjalankan konversi ruang warna berdasarkan nama."""
    tabel = {
        "biner": biner,
        "grayscale": grayscale,
        "rgb": rgb,
        "hsv": hsv,
        "cmy": cmy,
        "yuv": yuv,
        "yiq": yiq,
        "pseudo": pseudo,
    }
    if nama not in tabel:
        raise GalatCitra(f"Ruang warna tidak dikenal: {nama}")
    return tabel[nama](citra)
