"""Sub-registri Noise (definisi statis)."""

from __future__ import annotations

from .registry import Operasi, _daftar, _p

# ---------------------------------------------------------------- Noise
for _kunci, _judul, _params in (
    (
        "gaussian",
        "Gaussian Noise",
        [
            _p("mean", "Mean (rata-rata)", 0.0, -100.0, 100.0, bulat=False),
            _p("sigma", "Sigma", 20.0, 0.0, 100.0, bulat=False),
        ],
    ),
    (
        "rayleigh",
        "Rayleigh Noise",
        [_p("sigma", "Sigma", 20.0, 0.1, 100.0, bulat=False)],
    ),
    (
        "erlang",
        "Erlang (Gamma) Noise",
        [
            _p("bentuk", "Bentuk k", 2.0, 0.1, 100.0, bulat=False),
            _p("skala", "Skala lambda", 10.0, 0.1, 100.0, bulat=False),
        ],
    ),
    (
        "exponential",
        "Exponential Noise",
        [_p("mean", "Mean (rata-rata)", 20.0, 0.1, 100.0, bulat=False)],
    ),
    (
        "uniform",
        "Uniform Noise",
        [
            _p("bawah", "Batas bawah", 0.0, -100.0, 100.0, bulat=False),
            _p("atas", "Batas atas", 30.0, -100.0, 100.0, bulat=False),
        ],
    ),
    (
        "impulse",
        "Impulse Noise",
        [_p("amount", "Porsi noise (0 - 1)", 0.02, 0.0, 1.0, bulat=False)],
    ),
):
    _daftar(
        Operasi(
            f"noise.{_kunci}",
            _judul,
            lambda a, b, p: a,
            params=_params,
            ketik="Penambahan noise pada citra.",
        )
    )
