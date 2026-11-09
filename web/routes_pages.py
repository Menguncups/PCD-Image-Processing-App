"""Rute halaman HTML."""

from __future__ import annotations

from flask import Blueprint, make_response, render_template

from pcd import config, menu
from pcd.core import registry

from . import ruang_kerja

halaman = Blueprint("halaman", __name__)


def _konteks_menu() -> dict:
    """Menyusun data menu yang dipakai templat sidebar."""
    return {
        "menu": menu.MENU,
        "tautan_luar": menu.TAUTAN_LUAR,
        "jumlah_aksi": menu.jumlah_action(),
        "kedalaman_menu": menu.kedalaman_maksimum(),
        "aplikasi": config,
        "aksi_butuh_b": sorted(
            action
            for action, operasi in registry.DAFTAR_OPERASI.items()
            if operasi.perlu_b({})
        ),
    }


@halaman.get("/")
def beranda():
    """Halaman utama aplikasi."""
    respons = make_response(
        render_template("index.html", info=ruang_kerja().info(), **_konteks_menu())
    )
    respons.headers["Cache-Control"] = "no-store"
    return respons
