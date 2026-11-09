"""Sub-registri Edge Detection (definisi statis)."""

from __future__ import annotations

from .registry import JENIS_PILIHAN, Operasi, _daftar, _p

MODE_MAGNITUDO = "Magnitudo"
MODE_MODE = ["Magnitudo", "Gradien X", "Gradien Y"]

# ---------------------------------------------------------------- Edge Detection
_daftar(
    Operasi(
        "edge.sobel",
        "Edge Detection: Sobel",
        lambda a, b, p: a,
        params=[
            _p("ukuran", "Ukuran kernel", 3, 3, 7),
            _p(
                "mode",
                "Mode",
                MODE_MAGNITUDO,
                jenis=JENIS_PILIHAN,
                pilihan=list(MODE_MODE),
            ),
            _p("ambang", "Ambang (0 = tanpa ambang)", 0, 0, 255),
        ],
        ketik="Deteksi tepi turunan pertama dengan operator Sobel.",
    )
)

_daftar(
    Operasi(
        "edge.prewitt",
        "Edge Detection: Prewitt",
        lambda a, b, p: a,
        params=[
            _p(
                "mode",
                "Mode",
                MODE_MAGNITUDO,
                jenis=JENIS_PILIHAN,
                pilihan=list(MODE_MODE),
            ),
            _p("ambang", "Ambang (0 = tanpa ambang)", 0, 0, 255),
        ],
        ketik="Deteksi tepi turunan pertama dengan operator Prewitt.",
    )
)

_daftar(
    Operasi(
        "edge.roberts",
        "Edge Detection: Robert",
        lambda a, b, p: a,
        params=[
            _p(
                "mode",
                "Mode",
                MODE_MAGNITUDO,
                jenis=JENIS_PILIHAN,
                pilihan=list(MODE_MODE),
            ),
            _p("ambang", "Ambang (0 = tanpa ambang)", 0, 0, 255),
        ],
        ketik="Deteksi tepi diagonal dengan operator Robert.",
    )
)

_daftar(
    Operasi(
        "edge.laplacian",
        "Edge Detection: Laplacian",
        lambda a, b, p: a,
        params=[_p("ambang", "Ambang (0 = tanpa ambang)", 0, 0, 255)],
        ketik="Deteksi tepi turunan kedua dengan operator Laplacian.",
    )
)

_daftar(
    Operasi(
        "edge.log",
        "Edge Detection: Laplacian of Gaussian",
        lambda a, b, p: a,
        params=[
            _p("sigma", "Sigma", 1.0, 0.1, 10.0, bulat=False),
            _p("ambang", "Ambang (0 = tanpa ambang)", 0, 0, 255),
        ],
        ketik="Deteksi tepi dengan Laplacian of Gaussian.",
    )
)

_daftar(
    Operasi(
        "edge.canny",
        "Edge Detection: Canny",
        lambda a, b, p: a,
        params=[
            _p("ambang_bawah", "Ambang bawah", 50, 0, 255),
            _p("ambang_atas", "Ambang atas", 150, 0, 255),
        ],
        ketik="Deteksi tepi dengan algoritma Canny.",
    )
)

_daftar(
    Operasi(
        "edge.compass",
        "Edge Detection: Compass",
        lambda a, b, p: a,
        params=[_p("ambang", "Ambang (0 = tanpa ambang)", 0, 0, 255)],
        ketik="Deteksi tepi dengan operator Compass pada delapan arah.",
    )
)
