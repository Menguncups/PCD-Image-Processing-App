"""Sub-registri Enhancement: peningkatan dan domain frekuensi."""

from __future__ import annotations

from . import ops_enhance, ops_frequency, ops_geom
from .registry import Operasi, _daftar, _p

# ---------------------------------------------------------------- Enhancement
_daftar(
    Operasi(
        "enh.brightness",
        "Brightness",
        lambda a, b, p: ops_enhance.kecerahan(a, p.get("nilai", 50)),
        params=[_p("nilai", "Nilai kecerahan (-255 - 255)", 50, -255, 255)],
        ketik="Nilai positif mencerahkan citra, nilai negatif menggelapkan.",
    )
)

_daftar(
    Operasi(
        "enh.contrast",
        "Contrast",
        lambda a, b, p: ops_enhance.kontras(a, p.get("nilai_min", 0), p.get("nilai_max", 255)),
        params=[
            _p("nilai_min", "Batas bawah intensitas", 0, 0, 255),
            _p("nilai_max", "Batas atas intensitas", 255, 0, 255),
        ],
        ketik="Peregangan kontras pada rentang intensitas baru.",
    )
)

_daftar(
    Operasi(
        "enh.hist_equalization",
        "Hist. Equalization",
        lambda a, b, p: ops_enhance.histogram_ekualisasi(a),
        ketik="Menyamakan histogram citra.",
    )
)

_daftar(
    Operasi(
        "enh.lowpass",
        "Smoothing: Lowpass Filtering",
        lambda a, b, p: ops_enhance.lowpass(a),
        ketik="Low pass filtering dengan filter rata-rata 3 x 3.",
    )
)

_daftar(
    Operasi(
        "enh.median",
        "Smoothing: Median Filtering",
        lambda a, b, p: ops_enhance.median(a, p.get("ukuran", 3)),
        params=[_p("ukuran", "Ukuran kernel", 3, 3, 15)],
        ketik="Median filtering dengan jendela ganjil.",
    )
)

_daftar(
    Operasi(
        "freq.ilpf",
        "Frequency Domain: ILPF",
        lambda a, b, p: ops_frequency.ideal_low_pass(a, p.get("frekuensi", 30.0)),
        params=[_p("frekuensi", "Frekuensi batas D0", 30.0, 1.0, 1000.0, bulat=False)],
        ketik="Ideal Low Pass Filter pada domain frekuensi.",
    )
)

_daftar(
    Operasi(
        "freq.blpf",
        "Frequency Domain: BLPF",
        lambda a, b, p: ops_frequency.butterworth_low_pass(
            a, p.get("frekuensi", 30.0), p.get("orde", 2)
        ),
        params=[
            _p("frekuensi", "Frekuensi batas D0", 30.0, 1.0, 1000.0, bulat=False),
            _p("orde", "Orde filter n", 2, 1, 10),
        ],
        ketik="Butterworth Low Pass Filter pada domain frekuensi.",
    )
)

_daftar(
    Operasi(
        "enh.highpass",
        "Sharpening: Highpass Filtering",
        lambda a, b, p: ops_enhance.highpass(a),
        ketik="High pass filtering dengan kernel 3 x 3 dari laporan PCD 7.",
    )
)

_daftar(
    Operasi(
        "enh.highboost",
        "Sharpening: Highboost Filtering",
        lambda a, b, p: ops_enhance.highboost(a, p.get("faktor", 1.5), p.get("ukuran", 5)),
        params=[
            _p("faktor", "Faktor penguatan A", 1.5, 1.01, 10.0, bulat=False),
            _p("ukuran", "Ukuran kernel low pass", 5, 3, 15),
        ],
        ketik="High boost filtering: g = A * f - f_lowpass.",
    )
)

_daftar(
    Operasi(
        "freq.ihpf",
        "Frequency Domain: IHPF",
        lambda a, b, p: ops_frequency.ideal_high_pass(a, p.get("frekuensi", 30.0)),
        params=[_p("frekuensi", "Frekuensi batas D0", 30.0, 1.0, 1000.0, bulat=False)],
        ketik="Ideal High Pass Filter pada domain frekuensi.",
    )
)

_daftar(
    Operasi(
        "freq.bhpf",
        "Frequency Domain: BHPF",
        lambda a, b, p: ops_frequency.butterworth_high_pass(
            a, p.get("frekuensi", 30.0), p.get("orde", 2)
        ),
        params=[
            _p("frekuensi", "Frekuensi batas D0", 30.0, 1.0, 1000.0, bulat=False),
            _p("orde", "Orde filter n", 2, 1, 10),
        ],
        ketik="Butterworth High Pass Filter pada domain frekuensi.",
    )
)

_daftar(
    Operasi(
        "enh.geom_correction",
        "Geometrics correction",
        lambda a, b, p: ops_geom.koreksi_geometris(
            a, p.get("shear", 0.0), p.get("sudut", 0.0)
        ),
        params=[
            _p("shear", "Geser shear (fraksi lebar)", 0.0, -1.0, 1.0, bulat=False),
            _p("sudut", "Rotasi tambahan (derajat)", 0.0, -45.0, 45.0, bulat=False),
        ],
        ketik=(
            "Koreksi geometris berupa shearing dan rotasi kecil. Nilai shear 0,5 "
            "berarti bagian bawah bergeser setengah lebar citra."
        ),
    )
)
