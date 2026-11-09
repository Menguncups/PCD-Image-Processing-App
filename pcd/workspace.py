"""Ruang kerja satu sesi browser (versi antarmuka statis tanpa algoritma citra)."""

from __future__ import annotations

import json
import math
import re
import shutil
import struct
import threading
from dataclasses import replace
from pathlib import Path

from . import config
from .core import registry
from .utils.errors import (
    GalatAplikasi,
    GalatCitra,
    GalatOperasi,
    GalatParameter,
    PESAN_CITRA_B_KOSONG,
    PESAN_CITRA_GAGAL_DIBACA,
    PESAN_CITRA_KOSONG,
    PESAN_KERNEL,
    PESAN_TIDAK_ADA_HASIL,
    PESAN_UKURAN_BEDA,
)

# Akhiran yang tetap dipertahankan bila sesuai dengan format unduhan.
_AKHIRAN_UNDUH = {
    ".png": {".png"},
    ".jpg": {".jpg", ".jpeg"},
    ".bmp": {".bmp"},
    ".tif": {".tif", ".tiff"},
}

# 24 operasi yang menampilkan panel histogram (sesuai hasil git pull terbaru)
_AKSI_HISTOGRAM = {
    "enh.brightness",
    "enh.contrast",
    "enh.hist_equalization",
    "enh.lowpass",
    "enh.median",
    "enh.highpass",
    "enh.highboost",
    "basic.negative",
    "basic.boolean_not",
    "basic.thresholding",
    "basic.convolution",
    "noise.gaussian",
    "noise.rayleigh",
    "noise.erlang",
    "noise.exponential",
    "noise.uniform",
    "noise.impulse",
    "seg.otsu",
    "seg.adaptive_mean",
    "seg.adaptive_gaussian",
    "seg.multi_otsu",
    "seg.highlight",
    "color.binary",
    "color.grayscale",
}


def _nama_aman(nama: str) -> str:
    """Membersihkan nama berkas dari jalur dan karakter yang tidak aman."""
    dasar = re.split(r"[\\/]", str(nama).strip())[-1]
    dasar = re.sub(r'[\x00-\x1f<>:"/\\|?*]+', "_", dasar)
    return dasar.strip(" .")[:120]


SLOT_TULIS = ("a", "b")
SLOT_BACA = ("a", "b", "awal", "sebelum", "hasil")

META_BAWAAN: dict = {
    "a": None,
    "b": None,
    "awal": None,
    "hasil": None,
    "riwayat": [],
    "versi": 0,
}


def _baca_dimensi_citra(data: bytes) -> tuple[int, int, int]:
    """Membaca (lebar, tinggi, kanal) dari header berkas citra tanpa OpenCV."""
    if len(data) < 24:
        raise GalatCitra(PESAN_CITRA_GAGAL_DIBACA)

    # PNG
    if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        lebar, tinggi = struct.unpack(">II", data[16:24])
        color_type = data[25] if len(data) > 25 else 2
        kanal = 1 if color_type in (0, 3) else 3
        return int(lebar), int(tinggi), kanal

    # BMP
    if data[:2] == b"BM" and len(data) >= 30:
        lebar, tinggi = struct.unpack("<ii", data[18:26])
        bpp = struct.unpack("<H", data[28:30])[0]
        return abs(int(lebar)), abs(int(tinggi)), (1 if bpp <= 8 else 3)

    # JPEG
    if data[:2] == b"\xff\xd8":
        idx = 2
        panjang = len(data)
        while idx + 9 < panjang:
            if data[idx] != 0xFF:
                idx += 1
                continue
            marker = data[idx + 1]
            while marker == 0xFF and idx + 2 < panjang:
                idx += 1
                marker = data[idx + 1]
            if marker in (0xD8, 0xD9) or (0xD0 <= marker <= 0xD7):
                idx += 2
                continue
            if idx + 4 > panjang:
                break
            seg_len = struct.unpack(">H", data[idx + 2 : idx + 4])[0]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3) and idx + 9 < panjang:
                tinggi, lebar, komp = struct.unpack(">HHB", data[idx + 5 : idx + 10])
                return int(lebar), int(tinggi), (1 if komp == 1 else 3)
            idx += 2 + seg_len

    # TIFF (II / MM)
    if data[:2] in (b"II", b"MM"):
        return 512, 512, 3

    raise GalatCitra(PESAN_CITRA_GAGAL_DIBACA)


def _histogram_statis(action: str, params: dict) -> dict | None:
    """Menyusun data histogram dummy untuk 24 operasi yang mendukung histogram."""
    if action not in _AKSI_HISTOGRAM:
        return None

    sebelum = [
        int(100 + 800 * math.exp(-((i - 118) ** 2) / (2 * 42**2)))
        for i in range(256)
    ]
    geser = 25 if action == "enh.brightness" else (-15 if "noise" in action else 12)
    sesudah = [
        int(100 + 760 * math.exp(-((i - (118 + geser)) ** 2) / (2 * 48**2)))
        for i in range(256)
    ]

    ambang = None
    if action == "basic.thresholding":
        ambang = int(params.get("nilai", 127))
    elif action == "color.binary":
        ambang = 127
    elif action == "seg.highlight":
        ambang = int(params.get("ambang", 180))
    elif action == "seg.otsu":
        ambang = 128

    return {
        "sebelum": sebelum,
        "sesudah": sesudah,
        "ambang": ambang,
    }


def _teks(nilai) -> str:
    """Mengubah nilai kiriman JSON menjadi teks untuk Param.coerce."""
    if isinstance(nilai, bool):
        return "1" if nilai else "0"
    if nilai is None:
        return ""
    return str(nilai)


class RuangKerja:
    """Keadaan citra dan riwayat untuk satu sesi (mode statis)."""

    def __init__(self, folder: Path) -> None:
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        (self.folder / "riwayat").mkdir(exist_ok=True)
        self.kunci = threading.RLock()
        self.meta = self._muat_meta()

    def _muat_meta(self) -> dict:
        meta = json.loads(json.dumps(META_BAWAAN))
        jalur = self.folder / "meta.json"
        if jalur.exists():
            try:
                isi = json.loads(jalur.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                isi = {}
            if isinstance(isi, dict):
                meta.update(isi)
        return meta

    def _tulis_meta(self) -> None:
        jalur = self.folder / "meta.json"
        sementara = jalur.with_suffix(".tmp")
        sementara.write_text(
            json.dumps(self.meta, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        sementara.replace(jalur)

    def _naikkan_versi(self) -> int:
        self.meta["versi"] = int(self.meta.get("versi") or 0) + 1
        return self.meta["versi"]

    def _jalur(self, slot: str) -> Path:
        return self.folder / f"{slot}.png"

    def _hapus_slot(self, *slot: str) -> None:
        for nama in slot:
            jalur = self._jalur(nama)
            if jalur.exists():
                jalur.unlink()

    def ada(self, slot: str) -> bool:
        return self._jalur(slot).exists()

    def baca_bytes(self, slot: str) -> bytes | None:
        if slot not in SLOT_BACA:
            return None
        jalur = self._jalur(slot)
        if not jalur.exists():
            return None
        return jalur.read_bytes()

    def unggah(self, slot: str, data: bytes, nama: str) -> dict:
        """Menyimpan berkas citra untuk pratinjau kartu A atau B."""
        if slot not in SLOT_TULIS:
            raise GalatCitra("Slot citra tidak dikenal.")
        with self.kunci:
            lebar, tinggi, kanal = _baca_dimensi_citra(data)
            if lebar * tinggi > config.BATAS_PIKSEL:
                batas = config.BATAS_PIKSEL // 1_000_000
                raise GalatCitra(f"Citra terlalu besar. Maksimum {batas} megapiksel.")

            versi = self._naikkan_versi()
            jalur = self._jalur(slot)
            jalur.parent.mkdir(parents=True, exist_ok=True)
            jalur.write_bytes(data)

            info = {
                "nama": nama,
                "versi": versi,
                "lebar": lebar,
                "tinggi": tinggi,
                "kanal": kanal,
            }
            ekstensi = None
            akhiran = Path(nama).suffix.lower().lstrip(".")
            if akhiran in {"png", "jpg", "jpeg", "bmp", "tif", "tiff"}:
                ekstensi = (
                    "jpg"
                    if akhiran == "jpeg"
                    else ("tiff" if akhiran in {"tif", "tiff"} else akhiran)
                )
            info["format_asal"] = ekstensi
            self.meta[slot] = info

            if slot == "a":
                self._jalur("awal").write_bytes(data)
                self.meta["awal"] = dict(info)
                self.meta["riwayat"] = []
                self._hapus_riwayat()
                self._bersihkan_hasil()

            self._tulis_meta()
            return info

    def _hapus_riwayat(self) -> None:
        folder = self.folder / "riwayat"
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(exist_ok=True)

    def _bersihkan_hasil(self) -> None:
        self.meta["hasil"] = None
        self._hapus_slot("sebelum", "hasil")

    def siapkan(
        self,
        action: str,
        *,
        periksa_b: bool = True,
        params: dict | None = None,
    ) -> registry.Operasi:
        operasi = registry.ambil(action)
        if operasi is None:
            raise GalatOperasi(f"Aksi '{action}' belum tersedia.")
        if periksa_b:
            if not self.ada("a"):
                raise GalatCitra(PESAN_CITRA_KOSONG)
            if operasi.perlu_b(params):
                if not self.ada("b"):
                    raise GalatCitra(PESAN_CITRA_B_KOSONG)
                if self.meta.get("a") and self.meta.get("b"):
                    a = self.meta["a"]
                    b = self.meta["b"]
                    if (a["lebar"], a["tinggi"]) != (b["lebar"], b["tinggi"]):
                        raise GalatCitra(PESAN_UKURAN_BEDA)
        return operasi

    def parameter_awal(self, operasi: registry.Operasi) -> list[registry.Param]:
        params = [replace(p) for p in operasi.params]
        info = self.meta.get("a")
        lebar = int(info["lebar"]) if info else 512
        tinggi = int(info["tinggi"]) if info else 512

        if operasi.action == "geom.translation":
            for p in params:
                if p.kunci == "geser_x":
                    p.minimum = -lebar
                    p.maksimum = lebar
                    p.nilai = 0
                elif p.kunci == "geser_y":
                    p.minimum = -tinggi
                    p.maksimum = tinggi
                    p.nilai = 0
        elif operasi.action == "geom.cropping":
            for p in params:
                if p.kunci == "x1":
                    p.minimum = 0
                    p.maksimum = lebar
                    p.nilai = 0
                elif p.kunci == "y1":
                    p.minimum = 0
                    p.maksimum = tinggi
                    p.nilai = 0
                elif p.kunci == "x2":
                    p.minimum = 0
                    p.maksimum = lebar
                    p.nilai = lebar
                elif p.kunci == "y2":
                    p.minimum = 0
                    p.maksimum = tinggi
                    p.nilai = tinggi
        return params

    def _baca_kernel(self, nilai) -> list[list[float]]:
        try:
            if not isinstance(nilai, (list, tuple)) or len(nilai) != 3:
                raise ValueError
            hasil: list[list[float]] = []
            for baris in nilai:
                if not isinstance(baris, (list, tuple)) or len(baris) != 3:
                    raise ValueError
                angka = []
                for sel in baris:
                    teks = _teks(sel).strip().replace(",", ".")
                    if not teks:
                        raise ValueError
                    nilai_sel = float(teks)
                    if not math.isfinite(nilai_sel):
                        raise ValueError
                    angka.append(nilai_sel)
                hasil.append(angka)
            return hasil
        except (TypeError, ValueError) as galat:
            raise GalatParameter(PESAN_KERNEL) from galat

    def baca_parameter(self, operasi: registry.Operasi, mentah: dict) -> dict:
        if not isinstance(mentah, dict):
            raise GalatParameter("Format parameter tidak dikenal.")
        hasil: dict = {}
        for p in self.parameter_awal(operasi):
            nilai = mentah.get(p.kunci, p.nilai)
            if p.jenis == registry.JENIS_KERNEL:
                hasil[p.kunci] = self._baca_kernel(nilai)
                continue
            if p.jenis == registry.JENIS_CENTANG and isinstance(nilai, bool):
                hasil[p.kunci] = nilai
                continue
            try:
                hasil[p.kunci] = p.coerce(_teks(nilai))
            except ValueError as galat:
                raise GalatParameter(str(galat)) from galat
        return hasil

    def jalankan(self, action: str, params: dict) -> dict:
        """Simulasi eksekusi statis: tidak ada pemrosesan citra yang dilakukan."""
        with self.kunci:
            operasi = self.siapkan(action, periksa_b=False, params=params)
            petunjuk = (
                "Klik Terapkan untuk memakai hasilnya."
                if config.TAMPILKAN_TERAPKAN
                else "Hasil ditampilkan pada kartu Hasil."
            )
            pesan = f"Operasi '{operasi.judul}' selesai. {petunjuk}"
            keadaan = self.info()
            keadaan["pesan_terakhir"] = pesan
            keadaan["histogram_statis"] = _histogram_statis(action, params)
            return keadaan

    def terapkan(self) -> tuple[dict, str]:
        with self.kunci:
            if not self.meta.get("hasil"):
                raise GalatOperasi(PESAN_TIDAK_ADA_HASIL)
            return self.info(), "Hasil operasi diterapkan ke Citra A."

    def undo(self) -> tuple[dict, str]:
        with self.kunci:
            raise GalatOperasi("Tidak ada riwayat untuk dibatalkan.")

    def reset(self) -> tuple[dict, str]:
        with self.kunci:
            for slot in ("a", "b", "awal", "sebelum", "hasil"):
                if self.ada(slot):
                    self._hapus_slot(slot)
            self.meta["a"] = None
            self.meta["b"] = None
            self.meta["awal"] = None
            self.meta["hasil"] = None
            self.meta["riwayat"] = []
            self._hapus_riwayat()
            self._naikkan_versi()
            self._tulis_meta()
            return self.info(), "Semua citra dan hasil telah direset."

    def tutup_hasil(self) -> tuple[dict, str]:
        with self.kunci:
            self._bersihkan_hasil()
            self._tulis_meta()
            return self.info(), "Area hasil ditutup."

    def info(self) -> dict:
        return {
            "a": self.meta.get("a"),
            "b": self.meta.get("b"),
            "hasil": self.meta.get("hasil"),
            "riwayat": len(self.meta.get("riwayat") or []),
            "versi": int(self.meta.get("versi") or 0),
        }

    def nama_unduh(self, slot: str, ekstensi: str, nama: str | None = None) -> str:
        if nama:
            bersih = _nama_aman(nama)
            if bersih:
                akar = Path(bersih).stem.strip(" .") or f"citra-{slot}"
                akhiran = Path(bersih).suffix.lower()
                if akhiran in _AKHIRAN_UNDUH.get(ekstensi, {ekstensi}):
                    return f"{akar}{akhiran}"
                return f"{akar}{ekstensi}"
        dasar = f"citra-{slot}"
        if slot in ("a", "b") and self.meta.get(slot):
            dasar = Path(str(self.meta[slot].get("nama") or slot)).stem
        return f"{dasar}{ekstensi}"


__all__ = [
    "RuangKerja",
    "SLOT_BACA",
    "SLOT_TULIS",
    "GalatCitra",
    "GalatOperasi",
    "GalatParameter",
    "PESAN_CITRA_GAGAL_DIBACA",
]
