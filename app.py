"""Titik masuk server Aplikasi PCD versi web.

Cara menjalankan:
    python app.py
    python app.py --host 0.0.0.0 --port 8080
"""

from __future__ import annotations

import argparse
import logging

from web import create_app


def utama() -> None:
    """Membaca argumen baris perintah lalu menjalankan server."""
    parser = argparse.ArgumentParser(
        description="Menjalankan Aplikasi PCD versi web.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Alamat bind server, default 127.0.0.1 (hanya komputer sendiri).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port server, default 5000.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Menjalankan Flask dalam mode pengembangan.",
    )
    argumen = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    aplikasi = create_app()
    alamat = argumen.host if argumen.host != "0.0.0.0" else "127.0.0.1"
    print(f"Aplikasi PCD berjalan di http://{alamat}:{argumen.port}")
    aplikasi.run(
        host=argumen.host,
        port=argumen.port,
        debug=argumen.debug,
        threaded=True,
    )


if __name__ == "__main__":
    utama()
