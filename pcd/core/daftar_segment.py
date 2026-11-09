"""Sub-registri Segmentation (definisi statis)."""

from __future__ import annotations

from .registry import JENIS_CENTANG, Operasi, Param, _daftar, _p

# ---------------------------------------------------------------- Segmentation
_PARAM_ISI_RONGGA = Param(
    kunci="isi_rongga",
    label="Isi rongga di tengah objek",
    jenis=JENIS_CENTANG,
    nilai=True,
    ketik="Mengisi lubang pada hasil ambang supaya objek menjadi padat.",
)

_daftar(
    Operasi(
        "seg.otsu",
        "Segmentation: Global Threshold (Otsu)",
        lambda a, b, p: a,
        params=[_PARAM_ISI_RONGGA],
        ketik="Segmentasi dengan ambang global Otsu.",
    )
)

_daftar(
    Operasi(
        "seg.adaptive_mean",
        "Segmentation: Adaptive Threshold (Mean)",
        lambda a, b, p: a,
        params=[
            _p("konstanta", "Nilai C", 5, -20, 20),
            _p("ukuran", "Ukuran jendela", 11, 3, 99),
            _PARAM_ISI_RONGGA,
        ],
        ketik="Segmentasi dengan ambang adaptif berbasis rata-rata lokal.",
    )
)

_daftar(
    Operasi(
        "seg.adaptive_gaussian",
        "Segmentation: Adaptive Threshold (Gaussian)",
        lambda a, b, p: a,
        params=[
            _p("konstanta", "Nilai C", 5, -20, 20),
            _p("ukuran", "Ukuran jendela", 11, 3, 99),
            _PARAM_ISI_RONGGA,
        ],
        ketik="Segmentasi dengan ambang adaptif berbasis Gaussian.",
    )
)

_daftar(
    Operasi(
        "seg.multi_otsu",
        "Segmentation: Multi-Level Otsu (3 kelas)",
        lambda a, b, p: a,
        params=[_PARAM_ISI_RONGGA],
        ketik="Segmentasi dengan ambang Otsu bertingkat tiga kelas.",
    )
)

_daftar(
    Operasi(
        "seg.highlight",
        "Segmentation: Highlight Segmentation",
        lambda a, b, p: a,
        params=[_p("ambang", "Ambang brightness", 180, 0, 255), _PARAM_ISI_RONGGA],
        ketik="Segmentasi bagian citra yang terang.",
    )
)

_daftar(
    Operasi(
        "seg.contour",
        "Segmentation: Kontur (Find & Draw)",
        lambda a, b, p: a,
        params=[
            _p("ketebalan", "Ketebalan garis", 2, 1, 10),
            _PARAM_ISI_RONGGA,
        ],
        ketik="Segmentasi objek pada citra biner lalu menggambar kontur terluar objek berwarna hijau di atas citra asli.",
    )
)
