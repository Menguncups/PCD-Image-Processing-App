"""Pabrik aplikasi Flask untuk Aplikasi PCD versi web.

Modul ini mengatur kunci rahasia, penyimpanan ruang kerja per sesi, pembersihan
sesi kedaluwarsa, serta pendaftaran seluruh rute.
"""

from __future__ import annotations

import logging
import os
import secrets
import shutil
import threading
import time
import uuid

from flask import Flask, jsonify, render_template, request, session

from pcd import config
from pcd.workspace import RuangKerja

catatan = logging.getLogger(__name__)

# Ruang kerja yang sedang dipakai proses ini, dikunci per id sesi
_RUANG: dict[str, RuangKerja] = {}
_KUNCI = threading.Lock()
_TERAKHIR_BERSIH = 0.0


def _kunci_rahasia() -> str:
    """Mengambil kunci rahasia dari lingkungan atau berkas instance."""
    dari_lingkungan = os.environ.get("PCD_SECRET_KEY")
    if dari_lingkungan:
        return dari_lingkungan

    config.FOLDER_INSTANCE.mkdir(parents=True, exist_ok=True)
    jalur = config.BERKAS_KUNCI
    if jalur.exists():
        tersimpan = jalur.read_text(encoding="utf-8").strip()
        if tersimpan:
            return tersimpan

    baru = secrets.token_hex(32)
    jalur.write_text(baru, encoding="utf-8")
    return baru


def _id_sesi_sah(nilai: object) -> bool:
    """Memeriksa bentuk id sesi agar tidak bisa dipakai untuk path traversal."""
    return (
        isinstance(nilai, str)
        and len(nilai) == 32
        and all(huruf in "0123456789abcdef" for huruf in nilai)
    )


def _bersihkan_sesi_lama(jaga: str | None = None) -> None:
    """Menghapus folder sesi yang lebih tua dari batas umur."""
    global _TERAKHIR_BERSIH
    sekarang = time.time()
    if sekarang - _TERAKHIR_BERSIH < config.JEDA_BERSIH:
        return
    _TERAKHIR_BERSIH = sekarang

    if not config.FOLDER_SESI.exists():
        return
    batas = sekarang - config.UMUR_SESI
    for anak in config.FOLDER_SESI.iterdir():
        if not anak.is_dir() or anak.name == jaga:
            continue
        try:
            if anak.stat().st_mtime >= batas:
                continue
            shutil.rmtree(anak, ignore_errors=True)
            with _KUNCI:
                _RUANG.pop(anak.name, None)
            catatan.info("Sesi kedaluwarsa dihapus: %s", anak.name)
        except OSError:
            continue


def ruang_kerja() -> RuangKerja:
    """Mengembalikan ruang kerja milik sesi peramban yang sedang aktif."""
    sid = session.get("ruang")
    if not _id_sesi_sah(sid):
        sid = uuid.uuid4().hex
        session["ruang"] = sid

    with _KUNCI:
        ruang = _RUANG.get(sid)
        if ruang is None:
            ruang = RuangKerja(config.FOLDER_SESI / sid)
            _RUANG[sid] = ruang

    _bersihkan_sesi_lama(sid)
    return ruang


def kosongkan_cache_ruang() -> None:
    """Mengosongkan cache ruang kerja, dipakai oleh pengujian."""
    with _KUNCI:
        _RUANG.clear()


def _penanganan_galat(app: Flask) -> None:
    """Mendaftarkan handler galat HTTP yang konsisten untuk HTML dan JSON."""
    @app.errorhandler(413)
    def _terlalu_besar(_galat):
        batas = config.BATAS_UNGGAH // (1024 * 1024)
        pesan = f"Berkas terlalu besar. Maksimum {batas} MB."
        if request.path.startswith("/api/"):
            return jsonify({"ok": False, "pesan": pesan}), 413
        return render_template("galat.html", kode=413, pesan=pesan, aplikasi=config), 413

    @app.errorhandler(404)
    def _tidak_ditemukan(_galat):
        if request.path.startswith("/api/"):
            return jsonify({"ok": False, "pesan": "Alamat tidak ditemukan."}), 404
        return (
            render_template(
                "galat.html",
                kode=404,
                pesan="Halaman tidak ditemukan.",
                aplikasi=config,
            ),
            404,
        )

    @app.errorhandler(500)
    def _galat_server(_galat):
        catatan.exception("Kesalahan server pada %s", request.path)
        if request.path.startswith("/api/"):
            return jsonify({"ok": False, "pesan": "Terjadi kesalahan pada server."}), 500
        return (
            render_template(
                "galat.html",
                kode=500,
                pesan="Terjadi kesalahan pada server.",
                aplikasi=config,
            ),
            500,
        )


def create_app(konfigurasi: dict | None = None) -> Flask:
    """Membuat dan menyiapkan aplikasi Flask.

    Parameter:
        konfigurasi: nilai konfigurasi tambahan, biasanya untuk pengujian.

    Mengembalikan:
        Objek Flask yang siap dijalankan.
    """
    config.FOLDER_SESI.mkdir(parents=True, exist_ok=True)

    app = Flask(__name__, instance_relative_config=False)
    app.config.update(
        SECRET_KEY=_kunci_rahasia(),
        MAX_CONTENT_LENGTH=config.BATAS_UNGGAH,
        JSON_SORT_KEYS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SEND_FILE_MAX_AGE_DEFAULT=0,
        TEMPLATES_AUTO_RELOAD=True,
    )
    if konfigurasi:
        app.config.update(konfigurasi)

    from .routes_api import api
    from .routes_pages import halaman

    app.register_blueprint(halaman)
    app.register_blueprint(api)
    _penanganan_galat(app)

    return app


__all__ = ["create_app", "ruang_kerja", "kosongkan_cache_ruang"]
