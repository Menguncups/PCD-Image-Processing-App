"""Ruang kerja satu sesi browser.

Citra A, Citra B, citra awal, pratinjau hasil, dan riwayat pembatalan disimpan
sebagai berkas PNG di dalam satu folder sesi. Dengan cara ini citra besar tidak
perlu dimasukkan ke cookie atau ditahan di memori proses, dan keadaan sesi
tetap utuh meski halaman dimuat ulang.
"""

from __future__ import annotations

import json
import logging
import math
import re
import shutil
import threading
from dataclasses import replace
from pathlib import Path

import numpy as np

from . import config
from .core import registry
from .utils import images, kodek
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

catatan = logging.getLogger(__name__)

# Akhiran yang tetap dipertahankan bila sesuai dengan format unduhan.
_AKHIRAN_UNDUH = {
    ".png": {".png"},
    ".jpg": {".jpg", ".jpeg"},
    ".bmp": {".bmp"},
    ".tif": {".tif", ".tiff"},
}

# Operasi yang histogramnya bermakna untuk ditampilkan. Di luar daftar ini
# histogram tidak dihitung dan panel histogram disembunyikan.
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

# Menu yang benar-benar memproses citra. Basic Ops memakai awalan basic.,
# geom., dan color. Menu lain masih tampilan antarmuka saja.
_AKSI_AKTIF = ("basic.", "geom.", "color.")

# Pesan untuk menu yang belum punya mesin pemrosesan.
PESAN_UI_SAJA = "Menu ini masih tampilan antarmuka saja."


def _nama_aman(nama: str) -> str:
    """Membersihkan nama berkas dari jalur dan karakter yang tidak aman."""
    dasar = re.split(r"[\\/]", str(nama).strip())[-1]
    dasar = re.sub(r'[\x00-\x1f<>:"/\\|?*]+', "_", dasar)
    return dasar.strip(" .")[:120]


# Slot citra yang boleh ditulis atau dibaca
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


def _ukuran(citra: np.ndarray) -> dict:
    """Mengambil dimensi dan jumlah kanal citra."""
    tinggi, lebar = citra.shape[:2]
    kanal = 1 if citra.ndim == 2 else int(citra.shape[2])
    return {"lebar": int(lebar), "tinggi": int(tinggi), "kanal": kanal}


def _info(nama: str, citra: np.ndarray, versi: int) -> dict:
    """Menyusun keterangan satu citra untuk dikirim ke peramban."""
    return {"nama": nama, "versi": versi, **_ukuran(citra)}


def _histogram_abu(citra: np.ndarray) -> list[int]:
    """Menghitung histogram grayscale 256 kotak untuk satu citra."""
    abu = images.ke_abu(citra)
    return np.bincount(abu.ravel(), minlength=256).astype(int).tolist()


def _teks(nilai) -> str:
    """Mengubah nilai kiriman JSON menjadi teks untuk Param.coerce."""
    if isinstance(nilai, bool):
        return "1" if nilai else "0"
    if nilai is None:
        return ""
    return str(nilai)


class RuangKerja:
    """Keadaan citra dan riwayat untuk satu sesi."""

    def __init__(self, folder: Path) -> None:
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        (self.folder / "riwayat").mkdir(exist_ok=True)
        self.kunci = threading.RLock()
        self.meta = self._muat_meta()

    # ------------------------------------------------------------ berkas meta
    def _muat_meta(self) -> dict:
        """Membaca meta.json bila ada, selain itu memakai nilai bawaan."""
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
        """Menulis meta.json secara atomik agar tidak terbaca separuh."""
        jalur = self.folder / "meta.json"
        sementara = jalur.with_suffix(".tmp")
        sementara.write_text(
            json.dumps(self.meta, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        sementara.replace(jalur)

    def _naikkan_versi(self) -> int:
        """Menaikkan nomor versi untuk pemecahan cache gambar di peramban."""
        self.meta["versi"] = int(self.meta.get("versi") or 0) + 1
        return self.meta["versi"]

    def _jalur(self, slot: str) -> Path:
        """Mengembalikan letak berkas PNG satu slot."""
        return self.folder / f"{slot}.png"

    def _tulis_slot(self, slot: str, citra: np.ndarray) -> None:
        """Menulis citra ke berkas slot sebagai PNG."""
        jalur = self._jalur(slot)
        jalur.parent.mkdir(parents=True, exist_ok=True)
        jalur.write_bytes(kodek.ke_png(citra))

    def _hapus_slot(self, *slot: str) -> None:
        """Menghapus berkas beberapa slot bila ada."""
        for nama in slot:
            jalur = self._jalur(nama)
            if jalur.exists():
                jalur.unlink()

    # ------------------------------------------------------------- baca citra
    def baca(self, slot: str) -> np.ndarray | None:
        """Membaca citra pada satu slot, atau None bila belum ada."""
        if slot not in SLOT_BACA:
            return None
        jalur = self._jalur(slot)
        if not jalur.exists():
            return None
        return images.baca_citra(jalur)

    def ada(self, slot: str) -> bool:
        """Memeriksa apakah slot sudah berisi citra."""
        return self._jalur(slot).exists()

    # ---------------------------------------------------------------- unggah
    def unggah(self, slot: str, data: bytes, nama: str) -> dict:
        """Menyimpan citra hasil unggahan ke salah satu slot.

        Citra A yang baru dimuat juga menjadi citra awal, riwayat dikosongkan,
        dan pratinjau hasil ditutup. Perilaku ini sama dengan versi desktop.

        Parameter:
            slot: "a" atau "b".
            data: isi berkas yang diunggah.
            nama: nama berkas asli untuk ditampilkan.

        Mengembalikan:
            Keterangan citra yang baru disimpan.

        Raises:
            GalatCitra: bila berkas tidak terbaca atau terlalu besar.
        """
        if slot not in SLOT_TULIS:
            raise GalatCitra("Slot citra tidak dikenal.")
        with self.kunci:
            citra = kodek.dari_bytes(data)
            tinggi, lebar = citra.shape[:2]
            if lebar * tinggi > config.BATAS_PIKSEL:
                batas = config.BATAS_PIKSEL // 1_000_000
                raise GalatCitra(f"Citra terlalu besar. Maksimum {batas} megapiksel.")

            versi = self._naikkan_versi()
            self._tulis_slot(slot, citra)
            info = _info(nama, citra, versi)
            ekstensi = None
            akhiran = Path(nama).suffix.lower().lstrip(".")
            if akhiran in {"png", "jpg", "jpeg", "bmp", "tif", "tiff"}:
                ekstensi = "jpg" if akhiran == "jpeg" else ("tiff" if akhiran in {"tif", "tiff"} else akhiran)
            info["format_asal"] = ekstensi
            self.meta[slot] = info

            if slot == "a":
                self._tulis_slot("awal", citra)
                awal = dict(info)
                self.meta["awal"] = awal
                self.meta["riwayat"] = []
                self._hapus_riwayat()
                self._bersihkan_hasil()

            self._tulis_meta()
            return info

    # --------------------------------------------------------------- riwayat
    def _hapus_riwayat(self) -> None:
        """Mengosongkan folder riwayat."""
        folder = self.folder / "riwayat"
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(exist_ok=True)

    def _bersihkan_hasil(self) -> None:
        """Menutup pratinjau hasil tanpa menyentuh Citra A."""
        self.meta["hasil"] = None
        self._hapus_slot("sebelum", "hasil")

    # ------------------------------------------------------------- parameter
    def siapkan(
        self,
        action: str,
        *,
        periksa_b: bool = True,
        params: dict | None = None,
    ) -> registry.Operasi:
        """Mengambil operasi dan memeriksa prasyarat citranya.

        Parameter:
            action: nama aksi yang akan dijalankan.
            periksa_b: bila False, Citra B dan kesamaan ukurannya tidak
                diwajibkan. Endpoint form memakai nilai ini agar kartu Citra B
                dapat ditampilkan lebih dahulu, sedangkan endpoint eksekusi
                tetap memeriksa keduanya.
            params: parameter yang sudah dibaca, dipakai untuk operasi yang
                kebutuhan Citra B-nya bergantung pada pilihan pengguna.

        Raises:
            GalatOperasi: bila action tidak dikenal.
            GalatCitra: bila Citra A belum siap, atau Citra B belum siap saat
                pemeriksaan Citra B diminta.
        """
        operasi = registry.ambil(action)
        if operasi is None:
            raise GalatOperasi(f"Aksi '{action}' belum tersedia.")
        if action.startswith(_AKSI_AKTIF) and not self.ada("a"):
            raise GalatCitra(PESAN_CITRA_KOSONG)
        if periksa_b and operasi.perlu_b(params):
            if not self.ada("b"):
                raise GalatCitra(PESAN_CITRA_B_KOSONG)
            if self.meta.get("a") and self.meta.get("b"):
                a = self.meta["a"]
                b = self.meta["b"]
                if (a["lebar"], a["tinggi"]) != (b["lebar"], b["tinggi"]):
                    raise GalatCitra(PESAN_UKURAN_BEDA)
        return operasi

    def parameter_awal(self, operasi: registry.Operasi) -> list[registry.Param]:
        """Menyiapkan salinan parameter dengan nilai awal yang relevan.

        Batas translation mengikuti lebar dan tinggi Citra A. Translation boleh
        bergeser ke dua arah, sehingga x memakai rentang ``-lebar..lebar`` dan
        y memakai ``-tinggi..tinggi``. Cropping dimulai dari area penuh, dengan
        kiri/atas di 0 dan kanan/bawah di ukuran citra.
        """
        params = [replace(p) for p in operasi.params]
        info = self.meta.get("a")
        if not info:
            return params

        lebar = int(info["lebar"])
        tinggi = int(info["tinggi"])

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
        """Memeriksa matriks kernel 3 x 3 dari kiriman JSON.

        Raises:
            GalatParameter: bila bentuk atau isinya tidak sah.
        """
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
        """Mengubah parameter kiriman peramban menjadi nilai siap pakai.

        Parameter:
            operasi: operasi yang akan dijalankan.
            mentah: kamus nilai dari formulir.

        Raises:
            GalatParameter: bila ada nilai yang tidak sah.
        """
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

    # --------------------------------------------------------------- operasi
    def jalankan(self, action: str, params: dict) -> dict:
        """Menjalankan satu operasi dan menyimpan pratinjau hasilnya.

        Mengembalikan:
            Keadaan ruang kerja setelah operasi selesai.
        """
        with self.kunci:
            if not action.startswith(_AKSI_AKTIF):
                operasi = registry.ambil(action)
                if operasi is None:
                    raise GalatOperasi(f"Aksi '{action}' belum tersedia.")
                self._bersihkan_hasil()
                self._tulis_meta()
                keadaan = self.info()
                keadaan["pesan_terakhir"] = f"{PESAN_UI_SAJA} Pemrosesan citra baru tersedia di Basic Ops."
                return keadaan

            operasi = self.siapkan(action, params=params)
            a = self.baca("a")
            b = self.baca("b") if operasi.perlu_b(params) else None
            if a is None:
                raise GalatCitra(PESAN_CITRA_KOSONG)

            try:
                hasil = operasi.fungsi(a, b, params)
            except GalatAplikasi:
                raise
            except Exception as galat:  # noqa: BLE001 - pesan pengguna dibuat aman
                catatan.exception("Operasi %s gagal", action)
                raise GalatOperasi(
                    f"Operasi '{operasi.judul}' gagal dijalankan. "
                    "Periksa kembali parameter yang dipakai."
                ) from galat

            if not isinstance(hasil, np.ndarray) or hasil.size == 0:
                raise GalatOperasi(f"Operasi '{operasi.judul}' tidak menghasilkan citra.")
            if hasil.dtype != np.uint8:
                hasil = np.clip(hasil, 0, 255).astype(np.uint8)

            histogram = None
            if config.TAMPILKAN_HISTOGRAM and operasi.action in _AKSI_HISTOGRAM:
                try:
                    hist_sebelum = _histogram_abu(a)
                    ambang = None
                    if operasi.action == "basic.thresholding":
                        ambang = int(params.get("nilai", 127))
                    histogram = {
                        "sebelum": hist_sebelum,
                        "sesudah": _histogram_abu(hasil),
                        "ambang": ambang,
                    }
                except Exception:  # noqa: BLE001 - visualisasi bersifat opsional
                    histogram = None

            versi = self._naikkan_versi()
            self._tulis_slot("sebelum", a)
            self._tulis_slot("hasil", hasil)
            self.meta["hasil"] = {
                "judul": operasi.judul,
                "action": operasi.action,
                "pesan": self._pesan_hasil(operasi, hasil),
                "versi": versi,
                "sebelum": _info((self.meta.get("a") or {}).get("nama", "Citra A"), a, versi),
                "sesudah": _info("Hasil", hasil, versi),
                "histogram": histogram,
            }
            self._tulis_meta()
            return self.info()

    @staticmethod
    def _pesan_hasil(operasi: registry.Operasi, hasil: np.ndarray) -> str:
        """Menyusun pesan status setelah operasi selesai."""
        if config.TAMPILKAN_TERAPKAN:
            petunjuk = "Klik Terapkan untuk memakai hasilnya."
        else:
            petunjuk = "Hasil ditampilkan pada kartu Hasil."
        return f"Operasi '{operasi.judul}' selesai. {petunjuk}"

    def terapkan(self) -> tuple[dict, str]:
        """Menyalin hasil pratinjau ke Citra A dan menyimpannya ke riwayat."""
        with self.kunci:
            if not self.meta.get("hasil"):
                raise GalatOperasi(PESAN_TIDAK_ADA_HASIL)
            hasil = self.baca("hasil")
            if hasil is None:
                raise GalatOperasi(PESAN_TIDAK_ADA_HASIL)

            a = self.baca("a")
            if a is not None:
                nomor = len(self.meta.get("riwayat") or []) + 1
                self._tulis_slot(f"riwayat/{nomor:04d}", a)
                self.meta.setdefault("riwayat", []).append(nomor)

            versi = self._naikkan_versi()
            self._tulis_slot("a", hasil)
            nama = (self.meta.get("a") or {}).get("nama", "citra-a.png")
            self.meta["a"] = _info(nama, hasil, versi)
            self._bersihkan_hasil()
            self._tulis_meta()
            return self.info(), "Hasil operasi diterapkan ke Citra A."

    def undo(self) -> tuple[dict, str]:
        """Membatalkan operasi terakhir yang sudah diterapkan."""
        with self.kunci:
            riwayat = self.meta.get("riwayat") or []
            if not riwayat:
                raise GalatOperasi("Tidak ada riwayat untuk dibatalkan.")

            nomor = riwayat.pop()
            jalur = self.folder / "riwayat" / f"{nomor:04d}.png"
            if not jalur.exists():
                raise GalatOperasi("Berkas riwayat tidak ditemukan.")

            citra = images.baca_citra(jalur)
            versi = self._naikkan_versi()
            self._tulis_slot("a", citra)
            nama = (self.meta.get("a") or {}).get("nama", "citra-a.png")
            self.meta["a"] = _info(nama, citra, versi)
            self.meta["riwayat"] = riwayat
            jalur.unlink()
            self._bersihkan_hasil()
            self._tulis_meta()
            return self.info(), "Operasi terakhir dibatalkan."

    def reset(self) -> tuple[dict, str]:
        """Mengosongkan seluruh citra (A, B) dan hasil."""
        with self.kunci:
            for slot in ("a", "b", "awal", "sebelum", "hasil"):
                if self.ada(slot):
                    self._hapus_slot(slot)
            self.meta["a"] = None
            self.meta["b"] = None
            self.meta["awal"] = None
            self.meta["hasil"] = None
            self.meta["riwayat"] = []
            self._naikkan_versi()
            self._hapus_riwayat()
            self._tulis_meta()
            return self.info(), "Semua citra dan hasil telah direset."

    def tutup_hasil(self) -> tuple[dict, str]:
        """Menutup pratinjau hasil tanpa menerapkannya."""
        with self.kunci:
            self._bersihkan_hasil()
            self._tulis_meta()
            return self.info(), "Area hasil ditutup."

    def info(self) -> dict:
        """Menyusun ringkasan keadaan untuk dikirim ke peramban."""
        return {
            "a": self.meta.get("a"),
            "b": self.meta.get("b"),
            "hasil": self.meta.get("hasil"),
            "riwayat": len(self.meta.get("riwayat") or []),
            "versi": int(self.meta.get("versi") or 0),
        }

    # ------------------------------------------------------------------ nama
    def nama_unduh(self, slot: str, ekstensi: str, nama: str | None = None) -> str:
        """Menyusun nama berkas unduhan yang masuk akal.

        Bila pengguna memberi nama sendiri, jalur dan karakter berbahaya
        dibuang. Akhiran nama dipertahankan hanya bila cocok dengan format
        unduhan yang dipilih, sehingga isi PNG tidak pernah diberi akhiran JPEG.
        """
        if nama:
            bersih = _nama_aman(nama)
            if bersih:
                akar = Path(bersih).stem.strip(" .") or f"citra-{slot}"
                akhiran = Path(bersih).suffix.lower()
                if akhiran in _AKHIRAN_UNDUH.get(ekstensi, {ekstensi}):
                    return f"{akar}{akhiran}"
                return f"{akar}{ekstensi}"

        if slot == "hasil":
            sumber = self.meta.get("a") or {}
            dasar = f"{Path(str(sumber.get('nama') or 'citra-a')).stem}-hasil"
        elif slot in ("a", "b") and self.meta.get(slot):
            dasar = Path(str(self.meta[slot].get("nama") or slot)).stem
        elif slot == "awal" and self.meta.get("awal"):
            dasar = Path(str(self.meta["awal"].get("nama") or slot)).stem
        else:
            dasar = f"citra-{slot}"
        dasar = dasar.strip() or f"citra-{slot}"
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
