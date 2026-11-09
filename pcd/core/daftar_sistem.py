"""Sub-registri File dan About."""

from __future__ import annotations

from .registry import Operasi, _daftar

# ---------------------------------------------------------------- File
_daftar(Operasi("file.open", "Buka Citra", lambda a, b, p: a))
_daftar(Operasi("file.save", "Simpan Citra", lambda a, b, p: a))
_daftar(Operasi("file.save_as", "Simpan Citra Sebagai", lambda a, b, p: a))
_daftar(Operasi("file.exit", "Keluar", lambda a, b, p: a))

# ---------------------------------------------------------------- About
_daftar(Operasi("about.info", "Info Tim Developer", lambda a, b, p: a))
_daftar(Operasi("about.github", "Link Github", lambda a, b, p: a))
_daftar(Operasi("about.youtube", "Link Youtube", lambda a, b, p: a))
