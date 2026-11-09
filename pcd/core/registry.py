"""Daftar operasi yang memetakan aksi menu ke definisi parameter dan rumus.

Modul ini mendefinisikan `Param`, `Operasi`, preset kernel, dan daftar utama
`DAFTAR_OPERASI`, lalu memuat sub-registri per famili menu (`daftar_sistem`,
`daftar_basic`, `daftar_enhance`, `daftar_noise`, `daftar_edge`,
`daftar_segment`) untuk tampilan antarmuka statis tanpa algoritma pemrosesan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .rumus import RUMUS, RUMUS_SKALAR

# Tipe citra generik (tanpa ketergantungan pustaka komputasi)
TipeCitra = Any

# Jenis parameter yang bisa diminta ke pengguna
JENIS_ANGKA = "angka"
JENIS_PILIHAN = "pilihan"
JENIS_KERNEL = "kernel"
JENIS_CENTANG = "centang"

# Daftar kernel preset yang dipakai pada pilihan kernel 3 x 3
KERNEL_PRESET: dict[str, tuple[list[list[float]], str]] = {
    "Identity": (
        [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]],
        "Tidak mengubah citra.",
    ),
    "Average (Blur)": (
        [[1.0 / 9.0] * 3 for _ in range(3)],
        "Filter rata-rata 3 x 3 untuk pengaburan.",
    ),
    "Gaussian": (
        [
            [1.0 / 16.0, 2.0 / 16.0, 1.0 / 16.0],
            [2.0 / 16.0, 4.0 / 16.0, 2.0 / 16.0],
            [1.0 / 16.0, 2.0 / 16.0, 1.0 / 16.0],
        ],
        "Kernel Gaussian 3 x 3 untuk pengaburan halus.",
    ),
    "Sharpen": (
        [[0.0, -1.0, 0.0], [-1.0, 5.0, -1.0], [0.0, -1.0, 0.0]],
        "Kernel penajaman 3 x 3.",
    ),
    "Sobel X": (
        [[1.0, 0.0, -1.0], [2.0, 0.0, -2.0], [1.0, 0.0, -1.0]],
        "Deteksi tepi arah horizontal.",
    ),
    "Sobel Y": (
        [[-1.0, -2.0, -1.0], [0.0, 0.0, 0.0], [1.0, 2.0, 1.0]],
        "Deteksi tepi arah vertikal.",
    ),
    "Laplacian": (
        [[0.0, 1.0, 0.0], [1.0, -4.0, 1.0], [0.0, 1.0, 0.0]],
        "Deteksi tepi berbasis turunan kedua.",
    ),
    "Prewitt": (
        [[-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0]],
        "Deteksi tepi arah vertikal dengan bobot rata.",
    ),
    "Robert": (
        [[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 0.0]],
        "Deteksi tepi diagonal dengan kernel 2 x 2.",
    ),
}


def preset_ke_matrix(nama: str) -> list[list[float]]:
    """Mengubah kernel preset menjadi matriks 3 x 3 siap ditampilkan."""
    matriks = KERNEL_PRESET.get(nama, KERNEL_PRESET["Identity"])[0]
    return [[float(nilai) for nilai in baris] for baris in matriks]


@dataclass
class Param:
    """Satu parameter yang diminta kepada pengguna sebelum operasi dijalankan."""

    kunci: str
    label: str
    jenis: str = JENIS_ANGKA
    nilai: object = 0
    minimum: float | None = None
    maksimum: float | None = None
    pilihan: list[str] | None = None
    ketik: str | None = None
    bulat: bool = True
    geser: bool = False
    langkah: float | None = None

    def coerce(self, teks: str) -> object:
        """Mengubah teks yang diketik pengguna menjadi nilai parameter."""
        if self.jenis == JENIS_PILIHAN:
            if self.pilihan and teks not in self.pilihan:
                raise ValueError(f"Nilai '{teks}' tidak tersedia.")
            return teks

        if self.jenis == JENIS_CENTANG:
            return teks.strip().lower() in ("1", "true", "ya", "on", "benar")

        teks = teks.strip().replace(",", ".")
        if not teks:
            raise ValueError("Nilai parameter tidak boleh kosong.")
        nilai = float(teks)
        if self.minimum is not None and nilai < self.minimum:
            raise ValueError(f"Nilai minimal yang diperbolehkan adalah {self.minimum:g}.")
        if self.maksimum is not None and nilai > self.maksimum:
            raise ValueError(f"Nilai maksimal yang diperbolehkan adalah {self.maksimum:g}.")
        if self.bulat:
            return int(round(nilai))
        return nilai


@dataclass
class Operasi:
    """Satu operasi citra beserta parameter yang dibutuhkannya."""

    action: str
    judul: str
    fungsi: Callable[..., TipeCitra] = lambda a, b, p: a
    params: list[Param] = field(default_factory=list)
    butuh_b: bool = False
    ketik: str = ""
    pratinjau: bool = False
    rumus: str = ""
    rumus_skalar: str = ""
    butuh_b_fn: Callable[[dict], bool] | None = None

    def perlu_b(self, params: dict | None = None) -> bool:
        """Menentukan apakah Citra B diperlukan untuk nilai parameter ini."""
        if self.butuh_b_fn is None:
            return self.butuh_b
        return bool(self.butuh_b_fn(params or {}))


def _p(
    kunci: str,
    label: str,
    nilai: object,
    minimum: float | None = None,
    maksimum: float | None = None,
    jenis: str = JENIS_ANGKA,
    pilihan: list[str] | None = None,
    ketik: str | None = None,
    bulat: bool = True,
    geser: bool = False,
    langkah: float | None = None,
) -> Param:
    """Membuat objek Param dengan ringkasan yang lebih pendek."""
    return Param(
        kunci=kunci,
        label=label,
        jenis=jenis,
        nilai=nilai,
        minimum=minimum,
        maksimum=maksimum,
        pilihan=pilihan,
        ketik=ketik,
        bulat=bulat,
        geser=geser,
        langkah=langkah,
    )


# Daftar seluruh operasi, dikunci dengan action dari spec.json
DAFTAR_OPERASI: dict[str, Operasi] = {}


def _daftar(operasi: Operasi) -> Operasi:
    """Memasukkan satu operasi ke daftar utama."""
    operasi.rumus = RUMUS.get(operasi.action, "")
    operasi.rumus_skalar = RUMUS_SKALAR.get(operasi.action, "")
    DAFTAR_OPERASI[operasi.action] = operasi
    return operasi


# Sub-registri per famili menu
from . import daftar_sistem  # noqa: E402,F401
from . import daftar_basic  # noqa: E402,F401
from . import daftar_enhance  # noqa: E402,F401
from . import daftar_noise  # noqa: E402,F401
from . import daftar_edge  # noqa: E402,F401
from . import daftar_segment  # noqa: E402,F401

_AKSI_PRATINJAU = {
    "basic.thresholding",
    "edge.canny",
    "edge.log",
    "edge.sobel",
    "enh.brightness",
    "enh.contrast",
    "enh.geom_correction",
    "enh.highboost",
    "enh.median",
    "seg.adaptive_gaussian",
    "seg.adaptive_mean",
    "seg.highlight",
    "seg.multi_otsu",
    "seg.otsu",
}

_LANGKAH_GESER = {
    "basic.thresholding": {"nilai": 1},
    "edge.canny": {"ambang_bawah": 1, "ambang_atas": 1},
    "edge.log": {"sigma": 0.1, "ambang": 1},
    "edge.sobel": {"ukuran": 2, "ambang": 1},
    "enh.brightness": {"nilai": 1},
    "enh.contrast": {"nilai_min": 1, "nilai_max": 1},
    "enh.geom_correction": {"shear": 0.01, "sudut": 1},
    "enh.highboost": {"faktor": 0.01, "ukuran": 2},
    "enh.median": {"ukuran": 2},
    "geom.cropping": {"x1": 1, "y1": 1, "x2": 1, "y2": 1},
    "geom.rotation": {"sudut": 1},
    "geom.translation": {"geser_x": 1, "geser_y": 1},
    "geom.zooming": {"skala_x": 0.1, "skala_y": 0.1},
    "seg.adaptive_gaussian": {"konstanta": 1, "ukuran": 2},
    "seg.adaptive_mean": {"konstanta": 1, "ukuran": 2},
    "seg.highlight": {"ambang": 1},
}

for _action in _AKSI_PRATINJAU:
    DAFTAR_OPERASI[_action].pratinjau = True

for _action, _langkah in _LANGKAH_GESER.items():
    for _param in DAFTAR_OPERASI[_action].params:
        if _param.kunci in _langkah and _param.jenis == JENIS_ANGKA:
            _param.geser = True
            _param.langkah = _langkah[_param.kunci]


def ambil(action: str) -> Operasi | None:
    """Mengambil deskripsi operasi berdasarkan nama aksi pada menu."""
    return DAFTAR_OPERASI.get(action)


def daftar_action() -> list[str]:
    """Mengembalikan seluruh nama aksi yang dikenali aplikasi."""
    return sorted(DAFTAR_OPERASI.keys())
