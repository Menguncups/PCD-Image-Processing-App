"""Sub-registri Basic Ops: dasar, geometri, dan warna."""

from __future__ import annotations

from . import ops_basic, ops_color, ops_filter, ops_frequency, ops_geom
from .registry import (
    JENIS_KERNEL,
    JENIS_PILIHAN,
    Operasi,
    Param,
    _daftar,
    _p,
)

# Mode warna untuk operasi aritmetika dan boolean
_MODE_WARNA = ops_basic.MODE_WARNA


# ---------------------------------------------------------------- Basic Ops
_daftar(
    Operasi(
        "basic.negative",
        "Negative",
        lambda a, b, p: ops_basic.negatif(a),
        ketik="Operasi negatif: nilai intensitas dibalik, F'(x, y) = 255 - F(x, y).",
    )
)

def _aritmetika(jenis: str):
    """Membuat fungsi operasi aritmetika yang sadar mode operan."""

    def fungsi(a, b, p):
        mode = p.get("mode", ops_basic.MODE_ABU)
        if p.get("operan", ops_basic.MODE_OPERAN_CITRA) == ops_basic.MODE_OPERAN_SKALAR:
            return ops_basic.aritmetika_skalar(a, p.get("skalar", 1), jenis, mode)
        return ops_basic.aritmetika(a, b, jenis, mode)

    return fungsi


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
            _aritmetika(_jenis),
            params=[
                _p(
                    "operan",
                    "Jenis operan",
                    ops_basic.MODE_OPERAN_SKALAR,
                    jenis=JENIS_PILIHAN,
                    pilihan=[
                        ops_basic.MODE_OPERAN_SKALAR,
                        ops_basic.MODE_OPERAN_CITRA,
                    ],
                    ketik=(
                        "Pilih Citra + Skalar untuk memakai satu nilai angka. "
                        "Pilih Citra + Citra untuk memakai Citra B."
                    ),
                ),
                _p(
                    "mode",
                    "Mode warna",
                    ops_basic.MODE_ABU,
                    jenis=JENIS_PILIHAN,
                    pilihan=[ops_basic.MODE_ABU, _MODE_WARNA],
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
            butuh_b_fn=lambda p: p.get(
                "operan", ops_basic.MODE_OPERAN_SKALAR
            )
            == ops_basic.MODE_OPERAN_CITRA,
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
        lambda a, b, p: ops_basic.boolean_not(a, p.get("mode", ops_basic.MODE_ABU)),
        params=[
            _p(
                "mode",
                "Mode warna",
                ops_basic.MODE_ABU,
                jenis=JENIS_PILIHAN,
                pilihan=[ops_basic.MODE_ABU, _MODE_WARNA],
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
            lambda a, b, p, jenis=_jenis: ops_basic.boolean_dua(
                a, b, jenis, p.get("mode", ops_basic.MODE_ABU)
            ),
            params=[
                _p(
                    "mode",
                    "Mode warna",
                    ops_basic.MODE_ABU,
                    jenis=JENIS_PILIHAN,
                    pilihan=[ops_basic.MODE_ABU, _MODE_WARNA],
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
        lambda a, b, p: ops_geom.translasi(a, p.get("geser_x", 0), p.get("geser_y", 0)),
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
        lambda a, b, p: ops_geom.rotasi(a, p.get("sudut", 0.0)),
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
        lambda a, b, p: ops_geom.zooming(a, p.get("skala_x", 1.0), p.get("skala_y", 1.0)),
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
        lambda a, b, p: ops_geom.flipping(a, p.get("arah", ops_geom.FLIP_HORIZONTAL)),
        params=[
            _p(
                "arah",
                "Arah pembalikan",
                ops_geom.FLIP_HORIZONTAL,
                jenis=JENIS_PILIHAN,
                pilihan=list(ops_geom.MODE_FLIP),
            )
        ],
        ketik="Membalik citra secara horizontal, vertikal, atau keduanya.",
    )
)

_daftar(
    Operasi(
        "geom.cropping",
        "Geometrics: Cropping",
        lambda a, b, p: ops_geom.cropping(
            a, p.get("x1", 0), p.get("y1", 0), p.get("x2", 0), p.get("y2", 0)
        ),
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
        lambda a, b, p: ops_basic.thresholding(
            a, p.get("nilai", 127), p.get("mode", ops_basic.MODE_BINER)
        ),
        params=[
            _p("nilai", "Nilai ambang (0 - 255)", 127, 0, 255),
            _p(
                "mode",
                "Mode",
                ops_basic.MODE_BINER,
                jenis=JENIS_PILIHAN,
                pilihan=list(ops_basic.MODE_THRESHOLD),
            ),
        ],
        ketik="Thresholding global pada citra grayscale.",
    )
)

_daftar(
    Operasi(
        "basic.convolution",
        "Convolution",
        lambda a, b, p: ops_filter.konvolusi_warna(
            a, ops_filter.matrix_ke_kernel(p.get("kernel", ops_filter.preset_ke_matrix("Sobel X")))
        ),
        params=[
            Param(
                kunci="kernel",
                label="Matriks kernel 3 x 3",
                jenis=JENIS_KERNEL,
                nilai=ops_filter.preset_ke_matrix("Sobel X"),
            )
        ],
        ketik="Konvolusi manual memakai fungsi convolution2d dari laporan PCD 5.",
    )
)

_daftar(
    Operasi(
        "basic.fourier",
        "Fourier Transform",
        lambda a, b, p: ops_frequency.fourier(a),
        ketik="Menampilkan spektrum magnituda transformasi Fourier.",
    )
)

for _kunci, _judul, _fungsi in (
    ("binary", "Colouring: Binary", ops_color.biner),
    ("grayscale", "Colouring: Grayscale", ops_color.grayscale),
    ("rgb", "Colouring: RGB", ops_color.rgb),
    ("hsv", "Colouring: HSV", ops_color.hsv),
    ("cmy", "Colouring: CMY", ops_color.cmy),
    ("yuv", "Colouring: YUV", ops_color.yuv),
    ("yiq", "Colouring: YIQ", ops_color.yiq),
    ("pseudo", "Colouring: Pseudo", ops_color.pseudo),
):
    _daftar(
        Operasi(
            f"color.{_kunci}",
            _judul,
            lambda a, b, p, fungsi=_fungsi: fungsi(a),
            ketik="Pengubahan ruang warna citra.",
        )
    )
