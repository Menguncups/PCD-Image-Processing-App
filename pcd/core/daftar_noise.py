"""Sub-registri Noise."""

from __future__ import annotations

from . import ops_noise
from .registry import Operasi, _daftar, _p

# ---------------------------------------------------------------- Noise
for _kunci, _judul, _fungsi, _params in (
    (
        "gaussian",
        "Gaussian Noise",
        ops_noise.gaussian,
        [
            _p("mean", "Mean (rata-rata)", 0.0, -100.0, 100.0, bulat=False),
            _p("sigma", "Sigma", 20.0, 0.0, 100.0, bulat=False),
        ],
    ),
    (
        "rayleigh",
        "Rayleigh Noise",
        ops_noise.rayleigh,
        [_p("sigma", "Sigma", 20.0, 0.1, 100.0, bulat=False)],
    ),
    (
        "erlang",
        "Erlang (Gamma) Noise",
        ops_noise.erlang,
        [
            _p("bentuk", "Bentuk k", 2.0, 0.1, 100.0, bulat=False),
            _p("skala", "Skala lambda", 10.0, 0.1, 100.0, bulat=False),
        ],
    ),
    (
        "exponential",
        "Exponential Noise",
        ops_noise.eksponensial,
        [_p("mean", "Mean (rata-rata)", 20.0, 0.1, 100.0, bulat=False)],
    ),
    (
        "uniform",
        "Uniform Noise",
        ops_noise.seragam,
        [
            _p("bawah", "Batas bawah", 0.0, -100.0, 100.0, bulat=False),
            _p("atas", "Batas atas", 30.0, -100.0, 100.0, bulat=False),
        ],
    ),
    (
        "impulse",
        "Impulse Noise",
        ops_noise.impuls,
        [_p("amount", "Porsi noise (0 - 1)", 0.02, 0.0, 1.0, bulat=False)],
    ),
):
    _daftar(
        Operasi(
            f"noise.{_kunci}",
            _judul,
            lambda a, b, p, fungsi=_fungsi: fungsi(a, **p),
            params=_params,
            ketik="Penambahan noise pada citra.",
        )
    )
