"""Sub-registri Basic Ops: dasar, geometri, dan warna (definisi statis)."""

from __future__ import annotations

from .registry import (
    JENIS_KERNEL,
    JENIS_PILIHAN,
    Operasi,
    Param,
    _daftar,
    _p,
    preset_ke_matrix,
)

MODE_ABU = "Grayscale"
MODE_WARNA = "Berwarna"
MODE_OPERAN_CITRA = "Citra + Citra"
MODE_OPERAN_SKALAR = "Citra + Skalar"
MODE_BINER = "Biner"
MODE_THRESHOLD = ["Biner", "Biner Invers", "Truncasi", "ToZero"]
FLIP_HORIZONTAL = "Horizontal"
MODE_FLIP = ["Horizontal", "Vertikal", "Horizontal & Vertikal"]


# ---------------------------------------------------------------- Basic Ops
_daftar(
    Operasi(
        "basic.negative",
        "Negative",
        lambda a, b, p: a,
        ketik="Operasi negatif: nilai intensitas dibalik, F'(x, y) = 255 - F(x, y).",
    )
)

for _jenis, _label in (
    ("add", "Add (+)"),
    ("subtract", "Subtract (-)"),
    ("multiply", "Multiply (*)"),
    ("divide", "Divide (/)"),
):
    _skalar_awal = {"add": 10, "subtract": 10, "multiply": 2, "divide": 2}[_jenis]
    _skalar_minimum = 0.1 if _jenis == "divide" else 0
    _daftar(
        Operasi(
            f"basic.{_jenis}",
            f"Arithmetic: {_label}",
            lambda a, b, p: a,
            params=[
                _p(
                    "operan",
                    "Jenis operan",
                    MODE_OPERAN_SKALAR,
                    jenis=JENIS_PILIHAN,
                    pilihan=[MODE_OPERAN_SKALAR, MODE_OPERAN_CITRA],
                    ketik=(
                        "Pilih Citra + Skalar untuk memakai satu nilai angka. "
                        "Pilih Citra + Citra untuk memakai Citra B."
                    ),
                ),
                _p(
                    "mode",
                    "Mode warna",
                    MODE_ABU,
                    jenis=JENIS_PILIHAN,
                    pilihan=[MODE_ABU, MODE_WARNA],
                    ketik="Pilih apakah operasi dijalankan pada citra grayscale atau berwarna.",
                ),
                _p(
                    "skalar",
                    "Nilai skalar",
                    _skalar_awal,
                    minimum=_skalar_minimum,
                    maksimum=255,
                    bulat=False,
                    ketik=(
                        "Dipakai saat memilih Citra + Skalar. "
                        "Hasil di-clip ke rentang 0-255."
                    ),
                ),
            ],
            butuh_b=True,
            butuh_b_fn=lambda p: p.get("operan", MODE_OPERAN_SKALAR)
            == MODE_OPERAN_CITRA,
            ketik=(
                "Operasi aritmetika dengan Citra B atau satu nilai skalar. "
                "Hasil selalu dijepit ke rentang 0-255."
            ),
        )
    )

_daftar(
    Operasi(
        "basic.boolean_not",
        "Boolean: NOT",
        lambda a, b, p: a,
        params=[
            _p(
                "mode",
                "Mode warna",
                MODE_ABU,
                jenis=JENIS_PILIHAN,
                pilihan=[MODE_ABU, MODE_WARNA],
                ketik="Grayscale memakai 255 - citra, sedangkan berwarna memakai bitwise NOT.",
            )
        ],
        ketik="Inversi intensitas pada satu citra.",
    )
)

for _jenis, _label in (("and", "AND"), ("or", "OR"), ("xor", "XOR")):
    _daftar(
        Operasi(
            f"basic.boolean_{_jenis}",
            f"Boolean: {_label}",
            lambda a, b, p: a,
            params=[
                _p(
                    "mode",
                    "Mode warna",
                    MODE_ABU,
                    jenis=JENIS_PILIHAN,
                    pilihan=[MODE_ABU, MODE_WARNA],
                )
            ],
            butuh_b=True,
            ketik="Operasi boolean dua citra, kedua citra harus memiliki ukuran sama.",
        )
    )

_daftar(
    Operasi(
        "geom.translation",
        "Geometrics: Translation",
        lambda a, b, p: a,
        params=[
            _p("geser_x", "Geser horizontal (px)", 0, -1000, 1000),
            _p("geser_y", "Geser vertikal (px)", 0, -1000, 1000),
        ],
        ketik="Menggeser citra pada sumbu x dan y.",
    )
)

_daftar(
    Operasi(
        "geom.rotation",
        "Geometrics: Rotation",
        lambda a, b, p: a,
        params=[
            _p("sudut", "Sudut (derajat)", 0.0, -360.0, 360.0, bulat=False),
        ],
        ketik="Memutar citra terhadap titik tengahnya tanpa mengubah ukuran.",
    )
)

_daftar(
    Operasi(
        "geom.zooming",
        "Geometrics: Zooming",
        lambda a, b, p: a,
        params=[
            _p("skala_x", "Skala horizontal", 2.0, 0.1, 10.0, bulat=False),
            _p("skala_y", "Skala vertikal", 2.0, 0.1, 10.0, bulat=False),
        ],
        ketik="Memperbesar atau mengecilkan citra.",
    )
)

_daftar(
    Operasi(
        "geom.flipping",
        "Geometrics: Flipping",
        lambda a, b, p: a,
        params=[
            _p(
                "arah",
                "Arah pembalikan",
                FLIP_HORIZONTAL,
                jenis=JENIS_PILIHAN,
                pilihan=list(MODE_FLIP),
            )
        ],
        ketik="Membalik citra secara horizontal, vertikal, atau keduanya.",
    )
)

_daftar(
    Operasi(
        "geom.cropping",
        "Geometrics: Cropping",
        lambda a, b, p: a,
        params=[
            _p("x1", "Kiri (px)", 0, 0, 20000),
            _p("y1", "Atas (px)", 0, 0, 20000),
            _p("x2", "Kanan (px)", 0, 0, 20000),
            _p("y2", "Bawah (px)", 0, 0, 20000),
        ],
        ketik="Memotong area persegi panjang dari citra.",
    )
)

_daftar(
    Operasi(
        "basic.thresholding",
        "Thresholding",
        lambda a, b, p: a,
        params=[
            _p("nilai", "Nilai ambang (0 - 255)", 127, 0, 255),
            _p(
                "mode",
                "Mode",
                MODE_BINER,
                jenis=JENIS_PILIHAN,
                pilihan=list(MODE_THRESHOLD),
            ),
        ],
        ketik="Thresholding global pada citra grayscale.",
    )
)

_daftar(
    Operasi(
        "basic.convolution",
        "Convolution",
        lambda a, b, p: a,
        params=[
            Param(
                kunci="kernel",
                label="Matriks kernel 3 x 3",
                jenis=JENIS_KERNEL,
                nilai=preset_ke_matrix("Sobel X"),
            )
        ],
        ketik="Konvolusi manual memakai fungsi convolution2d dari laporan PCD 5.",
    )
)

_daftar(
    Operasi(
        "basic.fourier",
        "Fourier Transform",
        lambda a, b, p: a,
        ketik="Menampilkan spektrum magnituda transformasi Fourier.",
    )
)

for _kunci, _judul in (
    ("binary", "Colouring: Binary"),
    ("grayscale", "Colouring: Grayscale"),
    ("rgb", "Colouring: RGB"),
    ("hsv", "Colouring: HSV"),
    ("cmy", "Colouring: CMY"),
    ("yuv", "Colouring: YUV"),
    ("yiq", "Colouring: YIQ"),
    ("pseudo", "Colouring: Pseudo"),
):
    _daftar(
        Operasi(
            f"color.{_kunci}",
            _judul,
            lambda a, b, p: a,
            ketik="Pengubahan ruang warna citra.",
        )
    )
