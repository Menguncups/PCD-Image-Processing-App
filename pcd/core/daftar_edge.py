"""Sub-registri Edge Detection."""

from __future__ import annotations

from . import ops_edge
from .registry import JENIS_PILIHAN, Operasi, _daftar, _p

# ---------------------------------------------------------------- Edge Detection
_daftar(
    Operasi(
        "edge.sobel",
        "Edge Detection: Sobel",
        lambda a, b, p: ops_edge.sobel(
            a, p.get("ukuran", 3), p.get("mode", ops_edge.MODE_MAGNITUDO), p.get("ambang", 0)
        ),
        params=[
            _p("ukuran", "Ukuran kernel", 3, 3, 7),
            _p(
                "mode",
                "Mode",
                ops_edge.MODE_MAGNITUDO,
                jenis=JENIS_PILIHAN,
                pilihan=list(ops_edge.MODE_MODE),
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
        lambda a, b, p: ops_edge.prewitt(
            a, p.get("mode", ops_edge.MODE_MAGNITUDO), p.get("ambang", 0)
        ),
        params=[
            _p(
                "mode",
                "Mode",
                ops_edge.MODE_MAGNITUDO,
                jenis=JENIS_PILIHAN,
                pilihan=list(ops_edge.MODE_MODE),
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
        lambda a, b, p: ops_edge.robert(
            a, p.get("mode", ops_edge.MODE_MAGNITUDO), p.get("ambang", 0)
        ),
        params=[
            _p(
                "mode",
                "Mode",
                ops_edge.MODE_MAGNITUDO,
                jenis=JENIS_PILIHAN,
                pilihan=list(ops_edge.MODE_MODE),
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
        lambda a, b, p: ops_edge.laplacian(a, p.get("ambang", 0)),
        params=[_p("ambang", "Ambang (0 = tanpa ambang)", 0, 0, 255)],
        ketik="Deteksi tepi turunan kedua dengan operator Laplacian.",
    )
)

_daftar(
    Operasi(
        "edge.log",
        "Edge Detection: Laplacian of Gaussian",
        lambda a, b, p: ops_edge.log(a, p.get("sigma", 1.0), p.get("ambang", 0)),
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
        lambda a, b, p: ops_edge.canny(a, p.get("ambang_bawah", 50), p.get("ambang_atas", 150)),
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
        lambda a, b, p: ops_edge.compass(a, p.get("ambang", 0)),
        params=[_p("ambang", "Ambang (0 = tanpa ambang)", 0, 0, 255)],
        ketik="Deteksi tepi dengan operator Compass pada delapan arah.",
    )
)
