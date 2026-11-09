"""Pohon menu sidebar.

Isi menu dibaca dari `data/menu.json` yang disalin dari `wireframe/spec.json`
aplikasi desktop. Dengan begitu urutan, label, dan kedalaman menu tetap sama
antara versi desktop dan versi web.
"""

from __future__ import annotations

import json
from functools import lru_cache

from . import config


@lru_cache(maxsize=1)
def muat_menu() -> list[dict]:
    """Membaca pohon menu dari berkas JSON.

    Mengembalikan:
        Daftar simpul menu tingkat teratas.

    Raises:
        RuntimeError: bila berkas menu tidak ditemukan atau rusak.
    """
    try:
        isi = json.loads(config.BERKAS_MENU.read_text(encoding="utf-8"))
    except FileNotFoundError as galat:
        raise RuntimeError(
            f"Berkas menu tidak ditemukan: {config.BERKAS_MENU}"
        ) from galat
    except json.JSONDecodeError as galat:
        raise RuntimeError("Berkas menu tidak dapat dibaca.") from galat

    menu = isi.get("menu") if isinstance(isi, dict) else None
    if not isinstance(menu, list):
        raise RuntimeError("Struktur berkas menu tidak sesuai.")
    hasil = []
    for item in menu:
        if isinstance(item, dict) and item.get("sidebar") is False:
            continue
        hasil.append(item)
    return hasil


MENU: list[dict] = muat_menu()

# Tautan luar yang dibuka di tab baru, bukan dijalankan sebagai operasi
TAUTAN_LUAR: dict[str, str] = {
    "about.github": config.GITHUB_URL,
    "about.youtube": config.YOUTUBE_URL,
}


def _telusuri(items: list[dict], jalur: list[str]):
    """Menelusuri pohon menu dan menghasilkan (jalur, simpul)."""
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("items"):
            yield from _telusuri(item["items"], jalur + [str(item.get("label", ""))])
        elif item.get("action"):
            yield jalur, item


def semua_action() -> list[str]:
    """Mengembalikan seluruh action pada menu, sesuai urutan tampil."""
    return [item["action"] for _, item in _telusuri(MENU, [])]


def label_action(action: str) -> str:
    """Mengembalikan label menu untuk satu action."""
    for _, item in _telusuri(MENU, []):
        if item.get("action") == action:
            return str(item.get("label", action))
    return action


def jalur_action(action: str) -> list[str]:
    """Mengembalikan jalur menu menuju satu action.

    Contoh hasil: ["Enhancement", "Smoothing", "Spatial Domain", "Lowpass"].
    """
    for jalur, item in _telusuri(MENU, []):
        if item.get("action") == action:
            return jalur + [str(item.get("label", action))]
    return [action]


def jumlah_action() -> int:
    """Menghitung banyaknya action pada menu."""
    return len(semua_action())


def kedalaman_maksimum(items: list[dict] | None = None, tingkat: int = 1) -> int:
    """Menghitung kedalaman pohon menu, termasuk tingkat teratas."""
    if items is None:
        items = MENU
    dalam = tingkat
    for item in items:
        anak = item.get("items") if isinstance(item, dict) else None
        if anak:
            dalam = max(dalam, kedalaman_maksimum(anak, tingkat + 1))
    return dalam
