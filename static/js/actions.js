/* Aplikasi PCD versi web: antarmuka tanpa kerangka kerja.
   Berkas 4 dari 4: unggah, unduhan, tindakan, dan pemasangan. Dimuat berurutan setelah core.js; seluruh
   fungsi dan keadaan dibuat bersama lewat cakupan global skrip klasik. */
"use strict";

  // ----------------------------------------------------------------- unggah

  const EKSTENSI_DITERIMA = new Set(["png", "jpg", "jpeg", "bmp", "tif", "tiff"]);

  function klikUnggah(slot) {
    const masukan = el(`[data-unggah="${slot}"]`);
    if (masukan) {
      masukan.click();
    } else {
      window.location.href = "index.html";
    }
  }

  function unggah(slot, berkas) {
    if (!berkas) return;
    const nama = berkas.name || `citra-${slot}.png`;
    const akhiran = nama.split(".").pop().toLowerCase();
    if (!EKSTENSI_DITERIMA.has(akhiran)) {
      kabar("Format berkas tidak didukung. Gunakan PNG, JPEG, BMP, atau TIFF.", "galat");
      return;
    }

    const kartu = el(`[data-slot="${slot}"]`);
    if (kartu) kartu.classList.add("memuat");

    const url = URL.createObjectURL(berkas);
    const img = new Image();

    const selesaiMuat = (lebar, tinggi) => {
      if (state.info[slot] && state.info[slot].url) {
        try {
          URL.revokeObjectURL(state.info[slot].url);
        } catch {
          /* abaikan */
        }
      }

      const formatAsal =
        akhiran === "jpeg"
          ? "jpg"
          : akhiran === "tif" || akhiran === "tiff"
            ? "tiff"
            : akhiran;

      state.info[slot] = {
        nama,
        lebar,
        tinggi,
        kanal: 3,
        url,
        format_asal: formatAsal,
        versi: (state.info.versi || 0) + 1,
      };
      state.info.versi = state.info[slot].versi;

      terapkanState(state.info);
      if (kartu) kartu.classList.remove("memuat");

      const pesan =
        slot === "a" ? `Dimuat: ${nama}` : `Citra referensi dimuat: ${nama}`;
      kabar(pesan, "sukses");

      const tertunda = state.aksiTertunda;
      if (slot === "a" && tertunda) {
        state.aksiTertunda = null;
        jalankanAksi(tertunda);
      } else if (
        slot === "a" &&
        state.operasi &&
        state.operasi.startsWith("geom.")
      ) {
        jalankanAksi(state.operasi);
      }
    };

    img.onload = () => {
      selesaiMuat(img.naturalWidth || 512, img.naturalHeight || 512);
    };
    img.onerror = () => {
      if (kartu) kartu.classList.remove("memuat");
      URL.revokeObjectURL(url);
      kabar("Citra tidak dapat dibaca. Pastikan berkas bukan hasil rusak.", "galat");
    };
    img.src = url;
  }

  // --------------------------------------------------------------- unduhan

  function ekstensiFormat(format) {
    if (format === "jpg") return ".jpg";
    if (format === "bmp") return ".bmp";
    if (format === "tiff") return ".tif";
    return ".png";
  }

  function formatDariNama(nama) {
    const akhiran = String(nama || "").toLowerCase().split(".").pop();
    if (akhiran === "jpg" || akhiran === "jpeg") return "jpg";
    if (akhiran === "bmp") return "bmp";
    if (akhiran === "tif" || akhiran === "tiff") return "tiff";
    return "png";
  }

  function namaDasar(nama) {
    const teks = String(nama || "").trim();
    const tanpaJalur = teks.split(/[\\/]/).pop() || "";
    const titik = tanpaJalur.lastIndexOf(".");
    return titik > 0 ? tanpaJalur.slice(0, titik) : tanpaJalur;
  }

  function formatAsalSlot(slot) {
    if (state.info && state.info[slot] && state.info[slot].format_asal) {
      return state.info[slot].format_asal;
    }
    if (state.info && state.info[slot] && state.info[slot].nama) {
      return formatDariNama(state.info[slot].nama);
    }
    return "png";
  }

  function simpanHasilLangsung() {
    if (!state.info || !state.info.hasil) {
      kabar("Belum ada hasil yang bisa disimpan.", "galat");
      return;
    }
  }

  function simpanLangsung() {
    const info = state.info && state.info.a;
    if (!info) {
      kabar(PESAN_CITRA_KOSONG, "galat");
      return;
    }
  }

  function bukaUnduh(slot, mode = "save_as") {
    const dlg = el("#dlg-unduh");
    if (!dlg) {
      window.location.href = "index.html";
      return;
    }
    if (!(state.info && state.info[slot])) {
      kabar(PESAN_CITRA_KOSONG, "galat");
      return;
    }

    state.slotUnduh = slot;
    const sumber = state.info[slot];
    let nama = sumber ? sumber.nama : `citra-${slot}`;
    if (slot === "hasil" && mode === "save_as") {
      const namaA = state.info && state.info.a && state.info.a.nama ? namaDasar(state.info.a.nama) : "citra";
      const namaB = state.info && state.info.b && state.info.b.nama ? namaDasar(state.info.b.nama) : "";
      nama = namaB ? `hasil-${namaA}-${namaB}` : `hasil-${namaA}`;
      nama = `${namaDasar(nama) || "hasil"}${ekstensiFormat(formatAsalSlot("a"))}`;
    }

    el("#judul-unduh").textContent =
      mode === "save_as" ? "Simpan Citra Sebagai" : "Unduh citra";
    el("#btn-unduh-submit").textContent = mode === "save_as" ? "Simpan" : "Unduh";
    el("#nama-unduh").value = nama;
    el("#format-unduh").value = formatAsalSlot(slot === "hasil" ? "a" : slot);
    if (slot === "hasil") {
      el("#format-unduh").value = formatAsalSlot("a");
    } else {
      el("#format-unduh").value = formatDariNama(nama);
    }
    const keterangan = {
      a: "Citra A akan disimpan.",
      b: "Citra B akan disimpan.",
      hasil: "Hasil operasi akan disimpan.",
    };
    el("#ket-unduh").textContent =
      `${keterangan[slot] || ""} Pilih nama dan format berkas.`;
    dlg.showModal();
    el("#nama-unduh").focus();
    el("#nama-unduh").select();
  }

  // -------------------------------------------------------------- tindakan

  const AKSI_KHUSUS = {
    "file.open": () => klikUnggah("a"),
    "file.save": () => simpanLangsung(),
    "file.save_as": () => bukaUnduh("a", "save_as"),
    "about.info": () => tampilkanTentang(),
    "about.github": () => window.open(DATA.github, "_blank", "noopener"),
    "about.youtube": () => window.open(DATA.youtube, "_blank", "noopener"),
  };

  function intAtau(nilai, baku) {
    const n = parseInt(nilai, 10);
    return Number.isFinite(n) && n > 0 ? n : baku;
  }

  function siapkanDataOperasi(action) {
    const asal = DAFTAR_OPERASI[action];
    if (!asal) return null;

    const salinan = JSON.parse(JSON.stringify(asal));
    const infoA = state.info && state.info.a;
    if (!infoA) return salinan;

    const lebar = intAtau(infoA.lebar, 512);
    const tinggi = intAtau(infoA.tinggi, 512);

    if (salinan.action === "geom.translation") {
      for (const p of salinan.params) {
        if (p.kunci === "geser_x") {
          p.minimum = -lebar;
          p.maksimum = lebar;
          p.nilai = 0;
        } else if (p.kunci === "geser_y") {
          p.minimum = -tinggi;
          p.maksimum = tinggi;
          p.nilai = 0;
        }
      }
    } else if (salinan.action === "geom.cropping") {
      for (const p of salinan.params) {
        if (p.kunci === "x1") {
          p.minimum = 0;
          p.maksimum = lebar;
          p.nilai = 0;
        } else if (p.kunci === "y1") {
          p.minimum = 0;
          p.maksimum = tinggi;
          p.nilai = 0;
        } else if (p.kunci === "x2") {
          p.minimum = 0;
          p.maksimum = lebar;
          p.nilai = lebar;
        } else if (p.kunci === "y2") {
          p.minimum = 0;
          p.maksimum = tinggi;
          p.nilai = tinggi;
        }
      }
    }
    return salinan;
  }

  function jalankanAksi(action) {
    if (!action) return;
    if (action !== "about.info") {
      if (!el("#ruang-kerja")) {
        window.location.href = "index.html";
        return;
      }
      tutupTentang();
    }
    if (AKSI_KHUSUS[action]) {
      AKSI_KHUSUS[action]();
      return;
    }

    hentikanPratinjau();
    const data = siapkanDataOperasi(action);
    if (!data) {
      kabar(`Aksi '${action}' belum tersedia.`, "galat");
      return;
    }

    state.preset = PRESET_KERNEL_BAKU;
    aturButuhB(Boolean(data.butuh_b));
    state.aksiTertunda = null;
    bangunForm(data);

    const bKosong = Boolean(data.butuh_b) && !(state.info && state.info.b);
    if (bKosong) {
      el('[data-slot="b"]').scrollIntoView({ block: "nearest", behavior: "smooth" });
    } else {
      el("#panel-parameter").scrollIntoView({ block: "nearest", behavior: "smooth" });
    }
  }

  function resetSemua() {
    for (const slot of ["a", "b"]) {
      if (state.info[slot] && state.info[slot].url) {
        try {
          URL.revokeObjectURL(state.info[slot].url);
        } catch {
          /* abaikan */
        }
      }
      state.info[slot] = null;
    }
    state.info.hasil = null;
    terapkanState(state.info);
    kabar("Semua citra dan hasil telah direset.", "sukses");
  }

  // --------------------------------------------------------------- pemasangan

  function pasangPeristiwa() {
    el("#pohon").addEventListener("click", (peristiwa) => {
      const tombolGrup = peristiwa.target.closest("[data-toggle]");
      if (tombolGrup) {
        alihGrup(tombolGrup);
        return;
      }

      const daun = peristiwa.target.closest("[data-action]");
      if (!daun) return;
      const aksi = daun.dataset.action;
      tandaiAktif(daun);
      bukaJalur(daun);
      tutupLaci();
      jalankanAksi(aksi);
    });

    el("#btn-sisi").addEventListener("click", () => {
      if (el("#aplikasi").classList.contains("sisi-buka")) tutupLaci();
      else bukaLaci();
    });
    el("#btn-tutup-sisi").addEventListener("click", tutupLaci);
    el("#tirai").addEventListener("click", tutupLaci);
    if (typeof MEDIA_SEMPIT.addEventListener === "function") {
      MEDIA_SEMPIT.addEventListener("change", perbaruiTataSisi);
    }
    document.addEventListener("keydown", (peristiwa) => {
      if (peristiwa.key !== "Escape") return;
      if (el("#aplikasi").classList.contains("sisi-buka")) tutupLaci();
    });

    for (const tombol of els("[data-aksi]")) {
      tombol.addEventListener("click", () => {
        const aksi = tombol.dataset.aksi;
        if (aksi === "reset") resetSemua();
      });
    }

    for (const masukan of els("[data-unggah]")) {
      masukan.addEventListener("change", () => {
        const berkas = masukan.files && masukan.files[0];
        unggah(masukan.dataset.unggah, berkas);
        masukan.value = "";
      });
    }

    for (const slot of ["a", "b"]) {
      const kartu = el(`[data-slot="${slot}"]`);
      if (!kartu) continue;
      const bingkai = el(`[data-peran="bingkai-${slot}"]`, kartu);
      let hitung = 0;

      kartu.addEventListener("dragenter", (peristiwa) => {
        if (!peristiwa.dataTransfer || !peristiwa.dataTransfer.types.includes("Files")) return;
        peristiwa.preventDefault();
        hitung += 1;
        bingkai.classList.add("seret");
      });
      kartu.addEventListener("dragover", (peristiwa) => {
        if (!peristiwa.dataTransfer || !peristiwa.dataTransfer.types.includes("Files")) return;
        peristiwa.preventDefault();
        peristiwa.dataTransfer.dropEffect = "copy";
      });
      kartu.addEventListener("dragleave", () => {
        hitung = Math.max(0, hitung - 1);
        if (!hitung) bingkai.classList.remove("seret");
      });
      kartu.addEventListener("drop", (peristiwa) => {
        peristiwa.preventDefault();
        hitung = 0;
        bingkai.classList.remove("seret");
        const berkas = peristiwa.dataTransfer && peristiwa.dataTransfer.files[0];
        if (berkas) unggah(slot, berkas);
      });
    }

    const formParam = el("#form-parameter");
    if (formParam) {
      formParam.addEventListener("submit", (peristiwa) => {
        peristiwa.preventDefault();
        kirimOperasi();
      });
    }

    const btnBatal = el("#btn-batal-parameter");
    if (btnBatal) {
      btnBatal.addEventListener("click", () => {
        resetParameter();
        el("#panel-parameter").scrollIntoView({ block: "nearest", behavior: "smooth" });
      });
    }

    const tombolTerapkan = el("#btn-terapkan");
    if (tombolTerapkan) {
      tombolTerapkan.addEventListener("click", () => {
        if (!state.info || !state.info.hasil) {
          kabar("Belum ada hasil operasi untuk diterapkan.", "galat");
          return;
        }
        kabar("Hasil operasi diterapkan ke Citra A.", "sukses");
      });
    }

    const btnTutupHasil = el("#btn-tutup-hasil");
    if (btnTutupHasil) {
      btnTutupHasil.addEventListener("click", () => {
        kabar("Area hasil ditutup.", "sukses");
      });
    }

    const btnSimpanDropdown = el("#btn-simpan-dropdown");
    const menuSimpan = el("#menu-simpan");
    if (btnSimpanDropdown && menuSimpan) {
      btnSimpanDropdown.addEventListener("click", (peristiwa) => {
        peristiwa.stopPropagation();
        aturMenuSimpan(menuSimpan.hidden);
      });
      document.addEventListener("click", () => {
        aturMenuSimpan(false);
      });
      menuSimpan.addEventListener("click", (peristiwa) => {
        peristiwa.stopPropagation();
      });
      for (const tombol of els("[data-simpan]", menuSimpan)) {
        tombol.addEventListener("click", () => {
          aturMenuSimpan(false);
          if (tombol.dataset.simpan === "sebagai") {
            bukaUnduh("hasil", "save_as");
          } else {
            simpanHasilLangsung();
          }
        });
      }
    }

    const formatUnduh = el("#format-unduh");
    if (formatUnduh) {
      formatUnduh.addEventListener("change", () => {
        const nama = el("#nama-unduh").value.trim();
        if (!nama) return;
        const akar = namaDasar(nama) || "citra";
        el("#nama-unduh").value = `${akar}${ekstensiFormat(formatUnduh.value)}`;
      });
    }

    const formUnduh = el("#form-unduh");
    if (formUnduh) {
      formUnduh.addEventListener("submit", (peristiwa) => {
        peristiwa.preventDefault();
        const nama = el("#nama-unduh").value.trim();
        if (!nama) {
          kabar("Nama berkas tidak boleh kosong.", "galat");
          el("#nama-unduh").focus();
          return;
        }
        el("#dlg-unduh").close();
      });
    }

    for (const tombol of els("[data-tutup]")) {
      tombol.addEventListener("click", () => {
        const dialog = tombol.closest("dialog");
        if (dialog) dialog.close();
      });
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    pulihkanBuka();

    const diHalamanTentang = !el("#ruang-kerja") && Boolean(el("#panel-tentang"));
    if (diHalamanTentang) {
      const daunTentang = el('[data-action="about.info"]');
      if (daunTentang) {
        tandaiAktif(daunTentang, false);
        bukaJalur(daunTentang);
      }
      pasangPeristiwa();
      return;
    }

    const dataAwal = el("#data-awal");
    if (dataAwal) {
      try {
        terapkanState(JSON.parse(dataAwal.textContent));
      } catch {
        kabar("Keadaan awal tidak dapat dibaca.", "galat");
      }
    }

    pasangPeristiwa();

    const aksiTersimpan = ambil(KUNCI_SIMPAN.aktif);
    if (aksiTersimpan && aksiTersimpan !== "about.info") {
      const daun = el(`[data-action="${CSS.escape(aksiTersimpan)}"]`);
      if (daun) {
        tandaiAktif(daun, false);
        bukaJalur(daun);
        if (DAFTAR_OPERASI[aksiTersimpan]) {
          jalankanAksi(aksiTersimpan);
        }
      }
    }
  });
