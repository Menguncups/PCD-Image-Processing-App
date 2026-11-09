"""Rute JSON dan berkas untuk tampilan statis berbasis Flask & Jinja2."""

from __future__ import annotations

from functools import wraps
from io import BytesIO
from pathlib import Path

from flask import Blueprint, jsonify, request, send_file

from pcd import config, menu
from pcd.core import registry
from pcd.utils.errors import GalatAplikasi

from . import ruang_kerja

api = Blueprint("api", __name__, url_prefix="/api")

SLOT_GAMBAR = ("a", "b", "sebelum", "hasil")


def _ok(**data):
    """Membungkus respons sukses."""
    return jsonify({"ok": True, **data})


def _galat(pesan: str, kode: int = 400):
    """Membungkus respons gagal dengan pesan untuk pengguna."""
    return jsonify({"ok": False, "pesan": pesan}), kode


def _aman(fungsi):
    """Mengubah galat aplikasi menjadi respons JSON, bukan halaman galat."""

    @wraps(fungsi)
    def pembungkus(*args, **kwargs):
        try:
            return fungsi(*args, **kwargs)
        except GalatAplikasi as galat:
            return _galat(str(galat))
        except ValueError as galat:
            return _galat(str(galat) or "Nilai yang dikirim tidak valid.")

    return pembungkus


def _param_ke_json(param) -> dict:
    """Mengubah satu Param menjadi bentuk yang bisa dikirim sebagai JSON."""
    return {
        "kunci": param.kunci,
        "label": param.label,
        "jenis": param.jenis,
        "nilai": param.nilai,
        "minimum": param.minimum,
        "maksimum": param.maksimum,
        "pilihan": param.pilihan,
        "ketik": param.ketik,
        "bulat": param.bulat,
        "geser": param.geser,
        "langkah": param.langkah,
    }


def _preset_kernel() -> dict:
    """Menyusun daftar preset kernel beserta matriks siap tampil."""
    return {
        nama: {"matriks": registry.preset_ke_matrix(nama), "ketik": keterangan}
        for nama, (_matriks, keterangan) in registry.KERNEL_PRESET.items()
    }


# --------------------------------------------------------------------- keadaan
@api.get("/state")
def state():
    """Keadaan ruang kerja sesi saat ini."""
    return _ok(state=ruang_kerja().info())


@api.get("/info")
def info():
    """Identitas aplikasi dan tim pengembang."""
    return _ok(
        nama=config.APP_NAME,
        subjudul=config.APP_SUBTITLE,
        versi=config.APP_VERSION,
        deskripsi=config.APP_DESKRIPSI,
        tim=config.TEAM_MEMBERS,
        github=config.GITHUB_URL,
        youtube=config.YOUTUBE_URL,
        hak_cipta=config.COPYRIGHT,
        batas_unggah=config.BATAS_UNGGAH,
        format=list(config.FORMAT_UNDUH),
    )


@api.get("/menu")
def daftar_menu():
    """Pohon menu lengkap."""
    return _ok(
        menu=menu.MENU,
        jumlah=menu.jumlah_action(),
        kedalaman=menu.kedalaman_maksimum(),
    )


# --------------------------------------------------------------------- unggahan
@api.post("/unggah/<slot>")
@_aman
def unggah(slot: str):
    """Menerima berkas citra untuk slot A atau B."""
    if slot not in ("a", "b"):
        return _galat("Slot citra tidak dikenal.", 404)

    berkas = request.files.get("berkas")
    if berkas is None or not berkas.filename:
        return _galat("Tidak ada berkas yang dipilih.")

    nama = Path(berkas.filename).name
    if Path(nama).suffix.lower() not in config.EKSTENSI_DITERIMA:
        return _galat("Format berkas tidak didukung. Gunakan PNG, JPEG, BMP, atau TIFF.")

    data = berkas.read()
    if not data:
        return _galat("Berkas yang dipilih kosong.")

    ruang = ruang_kerja()
    ruang.unggah(slot, data, nama)
    pesan = f"Dimuat: {nama}" if slot == "a" else f"Citra referensi dimuat: {nama}"
    return _ok(state=ruang.info(), pesan=pesan)


# --------------------------------------------------------------------- operasi
@api.get("/operasi/<action>/form")
@_aman
def form_operasi(action: str):
    """Mengembalikan definisi parameter untuk satu operasi."""
    ruang = ruang_kerja()
    operasi = ruang.siapkan(action, periksa_b=False)
    return _ok(
        action=operasi.action,
        judul=operasi.judul,
        jalur=" / ".join(menu.jalur_action(operasi.action)),
        ketik=operasi.ketik,
        rumus=operasi.rumus,
        rumus_skalar=operasi.rumus_skalar,
        butuh_b=operasi.perlu_b(),
        pratinjau=operasi.pratinjau,
        params=[_param_ke_json(p) for p in ruang.parameter_awal(operasi)],
        preset_kernel=_preset_kernel(),
    )


@api.post("/operasi/<action>")
@_aman
def jalankan(action: str):
    """Menjalankan simulasi statis tanpa memproses citra hasil."""
    kiriman = request.get_json(silent=True) or {}
    ruang = ruang_kerja()
    operasi = ruang.siapkan(action, periksa_b=False)
    parameter = ruang.baca_parameter(operasi, kiriman.get("params") or {})
    keadaan = ruang.jalankan(action, parameter)
    pesan = keadaan.pop("pesan_terakhir", f"Operasi '{operasi.judul}' selesai. Hasil ditampilkan pada kartu Hasil.")
    return _ok(state=keadaan, pesan=pesan)


# ------------------------------------------------------------ area hasil dan sesi
@api.post("/terapkan")
@_aman
def terapkan():
    """Menyalin hasil operasi ke Citra A."""
    keadaan, pesan = ruang_kerja().terapkan()
    return _ok(state=keadaan, pesan=pesan)


@api.post("/undo")
@_aman
def undo():
    """Membatalkan operasi terakhir yang sudah diterapkan."""
    keadaan, pesan = ruang_kerja().undo()
    return _ok(state=keadaan, pesan=pesan)


@api.post("/reset")
@_aman
def reset():
    """Mengembalikan Citra A ke citra saat pertama dimuat."""
    keadaan, pesan = ruang_kerja().reset()
    return _ok(state=keadaan, pesan=pesan)


@api.post("/tutup-hasil")
@_aman
def tutup_hasil():
    """Menutup pratinjau hasil tanpa menerapkannya."""
    keadaan, pesan = ruang_kerja().tutup_hasil()
    return _ok(state=keadaan, pesan=pesan)


# ------------------------------------------------------------------ berkas citra
@api.get("/citra/<slot>.png")
@_aman
def citra(slot: str):
    """Mengirim citra slot tanpa cache peramban."""
    if slot not in SLOT_GAMBAR:
        return _galat("Slot citra tidak dikenal.", 404)

    ruang = ruang_kerja()
    jalur = ruang.folder / f"{slot}.png"
    if not jalur.exists():
        return _galat("Citra belum tersedia.", 404)

    balasan = send_file(
        BytesIO(jalur.read_bytes()), mimetype="image/png", max_age=0
    )
    balasan.headers["Cache-Control"] = "no-store"
    return balasan


@api.get("/unduh")
@_aman
def unduh():
    """Mengirim citra sebagai lampiran unduhan bila tersedia."""
    slot = request.args.get("slot", "a")
    format_unduh = request.args.get("format", "png").lower()
    nama = request.args.get("nama")

    if slot not in ("a", "b", "awal", "hasil"):
        return _galat("Slot citra tidak dikenal.", 404)
    if format_unduh not in config.FORMAT_UNDUH:
        return _galat("Format unduhan tidak didukung.")

    ruang = ruang_kerja()
    data = ruang.baca_bytes(slot)
    if data is None:
        return _galat("Belum ada citra untuk diunduh.")

    mimetype, ekstensi, _label = config.FORMAT_UNDUH[format_unduh]
    return send_file(
        BytesIO(data),
        mimetype=mimetype,
        as_attachment=True,
        download_name=ruang.nama_unduh(slot, ekstensi, nama),
        max_age=0,
    )
