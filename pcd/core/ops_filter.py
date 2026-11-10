"""Konvolusi dan penambahan noise yang dipakai ulang apa adanya.

Kedua fungsi di berkas ini diambil langsung dari laporan praktikum PCD 5 dan
PCD 7 dan tidak diubah sama sekali, sesuai ketentuan memakai ulang kode yang
sudah ada. Fungsi pembungkus di bawahnya hanya menambahkan penanganan kanal
warna agar bisa dipakai di aplikasi.
"""

from __future__ import annotations

import random

import numpy as np

# Tipe larik citra
TipeCitra = np.ndarray


# Fungsi untuk melakukan konvolusi
def convolution2d(image, kernel):
    # Menyimpan dimensi citra dan kernel
    image_height, image_width = image.shape
    kernel_height, kernel_width = kernel.shape

    # Menentukan ukuran output citra
    output_height = image_height - kernel_height + 1
    output_width = image_width - kernel_width + 1

    # Menyiapkan array kosong untuk menyimpan hasil konvolusi
    output_image = np.zeros((output_height, output_width))

    # Melakukan konvolusi
    for i in range(output_height):
        for j in range(output_width):
            # Menentukan region citra yang akan dikonvolusi dengan kernel
            region = image[i:i+kernel_height, j:j+kernel_width]
            # Melakukan operasi perkalian dan penjumlahan antara region dan kernel
            output_image[i, j] = np.sum(region * kernel)

    return output_image


# Menambahkan noise salt-and-pepper ke gambar
def add_salt_and_pepper_noise(image, amount=0.02):
    noisy_image = image.copy()
    num_salt = int(amount * image.size * 0.5)
    num_pepper = int(amount * image.size * 0.5)

    # Tambahkan salt (putih)
    for _ in range(num_salt):
        x = random.randint(0, image.shape[0] - 1)
        y = random.randint(0, image.shape[1] - 1)
        noisy_image[x, y] = 255

    # Tambahkan pepper (hitam)
    for _ in range(num_pepper):
        x = random.randint(0, image.shape[0] - 1)
        y = random.randint(0, image.shape[1] - 1)
        noisy_image[x, y] = 0

    return noisy_image


def pad_sama_ukuran(image: TipeCitra, kernel: np.ndarray) -> TipeCitra:
    """Menambah padding pada citra agar konvolusi menghasilkan ukuran yang sama.

    Fungsi `convolution2d` memakai konvolusi valid, sehingga keluarannya
    lebih kecil daripada citra masukan. Padding ini membuat hasilnya
    berukuran sama, sama seperti perilaku bawaan `cv2.filter2D`.

    Parameter:
        image: larik citra dua dimensi.
        kernel: matriks kernel.

    Mengembalikan:
        Larik citra yang sudah dipadding.
    """
    tinggi_kernel = kernel.shape[0]
    lebar_kernel = kernel.shape[1]
    atas = tinggi_kernel // 2
    bawah = tinggi_kernel - 1 - atas
    kiri = lebar_kernel // 2
    kanan = lebar_kernel - 1 - kiri
    return np.pad(image, ((atas, bawah), (kiri, kanan)), mode="edge")


def konvolusi_sama_ukuran(image: TipeCitra, kernel: np.ndarray) -> np.ndarray:
    """Menjalankan konvolusi manual dengan hasil berukuran sama dengan citra.

    Parameter:
        image: larik citra dua dimensi.
        kernel: matriks kernel.

    Mengembalikan:
        Larik hasil konvolusi berupa float.
    """
    kernel = np.asarray(kernel, dtype=np.float64)
    return convolution2d(pad_sama_ukuran(image, kernel), kernel)


def konvolusi_warna(citra: TipeCitra, kernel: np.ndarray) -> TipeCitra:
    """Menerapkan konvolusi pada setiap kanal citra berwarna.

    Citra grayscale langsung dikonvolusi. Untuk citra berwarna, konvolusi
    dijalankan pada kanal B, G, dan R secara terpisah, lalu digabung kembali
    dengan `np.stack`, sama seperti pola pada laporan PCD 5.

    Parameter:
        citra: larik citra BGR uint8.
        kernel: matriks kernel 2 dimensi.

    Mengembalikan:
        Larik citra uint8 dengan bentuk sama seperti citra masukan.
    """
    kernel = np.asarray(kernel, dtype=np.float64)

    if citra.ndim == 2:
        hasil = konvolusi_sama_ukuran(citra, kernel)
        return np.clip(hasil, 0, 255).astype(np.uint8)

    # Konvolusi diterapkan per kanal B, G, R
    kanal_b = konvolusi_sama_ukuran(citra[:, :, 0], kernel)
    kanal_g = konvolusi_sama_ukuran(citra[:, :, 1], kernel)
    kanal_r = konvolusi_sama_ukuran(citra[:, :, 2], kernel)

    # Gabungkan hasil konvolusi ketiga kanal menjadi citra berwarna
    hasil = np.stack([kanal_b, kanal_g, kanal_r], axis=2)
    return np.clip(hasil, 0, 255).astype(np.uint8)


def salt_pepper_warna(citra: TipeCitra, amount: float = 0.02, benih: int | None = None) -> TipeCitra:
    """Menambahkan noise salt and pepper pada citra berwarna.

    Fungsi `add_salt_and_pepper_noise` dipanggil apa adanya untuk setiap kanal
    agar kegunaannya tetap sama persis dengan kode pada laporan PCD 7.

    Parameter:
        citra: larik citra BGR uint8.
        amount: porsi piksel yang terkena noise, antara 0 dan 1.
        benih: bila diisi, acakan dibuat deterministik agar hasil dapat diulang.

    Mengembalikan:
        Larik citra uint8 dengan bentuk sama seperti citra masukan.
    """
    if benih is not None:
        random.seed(benih)

    if citra.ndim == 2:
        return add_salt_and_pepper_noise(citra, amount)

    kanal_b = add_salt_and_pepper_noise(citra[:, :, 0], amount)
    kanal_g = add_salt_and_pepper_noise(citra[:, :, 1], amount)
    kanal_r = add_salt_and_pepper_noise(citra[:, :, 2], amount)
    return np.stack([kanal_b, kanal_g, kanal_r], axis=2)


# Daftar kernel preset yang dipakai pada dialog pilihan kernel
KERNEL_PRESET: dict[str, tuple[np.ndarray, str]] = {
    "Identity": (
        np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]], dtype=np.float64),
        "Tidak mengubah citra.",
    ),
    "Average (Blur)": (
        np.ones((3, 3), dtype=np.float64) / 9.0,
        "Filter rata-rata 3 x 3 untuk pengaburan.",
    ),
    "Gaussian": (
        np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], dtype=np.float64) / 16.0,
        "Kernel Gaussian 3 x 3 untuk pengaburan halus.",
    ),
    "Sharpen": (
        np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float64),
        "Kernel penajaman 3 x 3.",
    ),
    "Sobel X": (
        np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]], dtype=np.float64),
        "Deteksi tepi arah horizontal.",
    ),
    "Sobel Y": (
        np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float64),
        "Deteksi tepi arah vertikal.",
    ),
    "Laplacian": (
        np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float64),
        "Deteksi tepi berbasis turunan kedua.",
    ),
    "Prewitt": (
        np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float64),
        "Deteksi tepi arah vertikal dengan bobot rata.",
    ),
    "Robert": (
        np.array([[1, 0], [0, -1]], dtype=np.float64),
        "Deteksi tepi diagonal dengan kernel 2 x 2.",
    ),
}


def preset_ke_matrix(nama: str) -> list[list[float]]:
    """Mengubah kernel preset menjadi matriks 3 x 3 siap ditampilkan."""
    kernel = KERNEL_PRESET.get(nama, KERNEL_PRESET["Identity"])[0]
    if kernel.shape == (2, 2):
        # Kernel 2 x 2 (Robert) disisipkan dalam matriks 3 x 3 agar seragam
        embedding = np.zeros((3, 3), dtype=np.float64)
        embedding[:2, :2] = kernel
        kernel = embedding
    return [[float(nilai) for nilai in baris] for baris in kernel]


def matrix_ke_kernel(matrix: list[list[float]]) -> np.ndarray:
    """Mengubah matriks dari dialog menjadi larik kernel siap pakai."""
    return np.array(matrix, dtype=np.float64)
