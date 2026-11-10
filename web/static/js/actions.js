/* Aplikasi PCD versi web: antarmuka tanpa kerangka kerja.
   Berkas 4 dari 4: unggah, unduhan, tindakan, dan pemasangan. Dimuat berurutan setelah core.js; seluruh
   fungsi dan keadaan dibuat bersama lewat cakupan global skrip klasik. */
"use strict";

  // ----------------------------------------------------------------- unggah

  function klikUnggah(slot) {
    const masukan = el(`[data-unggah="${slot}"]`);
    if (masukan) masukan.click();
  }

  async function unggah(slot, berkas) {
    if (!berkas) return;
    const kartu = el(`[data-slot="${slot}"]`);
    if (kartu) kartu.classList.add("memuat");

    try {
      const data = new FormData();
      data.append("berkas", berkas);
      const hasil = await api(`/api/unggah/${slot}`, { method: "POST", body: data });
      terapkanState(hasil.state);
      kabar(hasil.pesan, "sukses");

      const tertunda = state.aksiTertunda;
      if (slot === "a" && tertunda) {
        state.aksiTertunda = null;
        await jalankanAksi(tertunda);
      } else if (
        slot === "a" &&
        state.operasi &&
        state.operasi.startsWith("geom.")
      ) {
        await jalankanAksi(state.operasi);
      }
    } catch (galat) {
      kabar(galat.message, "galat");
    } finally {
      if (kartu) kartu.classList.remove("memuat");
    }
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

  function pemicuUnduh(slot, format, nama) {
    const params = new URLSearchParams({ slot, format });
    if (nama) params.set("nama", nama);
    window.location.href = `/api/unduh?${params.toString()}`;
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
    const format = formatAsalSlot("a");
    const namaA = state.info && state.info.a && state.info.a.nama ? namaDasar(state.info.a.nama) : "citra";
    const namaB = state.info && state.info.b && state.info.b.nama ? namaDasar(state.info.b.nama) : "";
    let nama = namaB ? `hasil-${namaA}-${namaB}` : `hasil-${namaA}`;
    const dasar = namaDasar(nama) || "hasil";
    pemicuUnduh("hasil", format, `${dasar}${ekstensiFormat(format)}`);
  }

  function simpanLangsung() {
    const info = state.info && state.info.a;
    if (!info) {
      kabar(PESAN_CITRA_KOSONG, "galat");
      return;
    }
    const format = formatAsalSlot("a");
    const akar = namaDasar(info.nama) || "citra";
    pemicuUnduh("a", format, `${akar}${ekstensiFormat(format)}`);
  }

  function bukaUnduh(slot, mode = "save_as") {
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
    el("#dlg-unduh").showModal();
    el("#nama-unduh").focus();
    el("#nama-unduh").select();
  }

  // -------------------------------------------------------------- tindakan

  async function aksiSederhana(alamat, setelahSukses) {
    try {
      const data = await api(alamat, { method: "POST" });
      terapkanState(data.state);
      kabar(data.pesan, "sukses");
      if (setelahSukses) setelahSukses();
    } catch (galat) {
      kabar(galat.message, "galat");
    }
  }

  const AKSI_KHUSUS = {
    "file.open": () => klikUnggah("a"),
    "file.save": () => simpanLangsung(),
    "file.save_as": () => bukaUnduh("a", "save_as"),
    "about.info": () => tampilkanTentang(),
    "about.github": () => window.open(DATA.github, "_blank", "noopener"),
    "about.youtube": () => window.open(DATA.youtube, "_blank", "noopener"),
  };

  function labelAksi(action) {
    const daun = el(`[data-action="${CSS.escape(action)}"]`);
    if (!daun) return action;
    const label = el(":scope > .label", daun);
    return label ? label.textContent.trim() : action;
  }

  function tampilkanTertunda(action) {
    hentikanPratinjau();
    state.operasi = null;
    state.preset = {};
    state.pratinjau = false;
    state.pratinjauAwal = false;
    state.pratinjauSibuk = false;
    state.pesanValidasi = "";
    aturButuhB(AKSI_BUTUH_B.has(action));

    const daun = el(`[data-action="${CSS.escape(action)}"]`);
    const jalur = daun ? jalurElemen(daun).join(" / ") : action;
    el("#judul-operasi").textContent = labelAksi(action);
    el("#jalur-operasi").textContent = jalur;
    const butuhB = AKSI_BUTUH_B.has(action);
    const aritmetika = action.startsWith("basic.add") || action.startsWith("basic.subtract") ||
                       action.startsWith("basic.multiply") || action.startsWith("basic.divide");
    el("#ketik-operasi").textContent = butuhB
      ? (aritmetika
         ? "Operasi menunggu Citra A. Pilih Citra + Citra untuk memerlukan Citra B."
         : "Operasi menunggu Citra A. Citra B boleh diunggah lebih dahulu.")
      : "Operasi menunggu Citra A. Unggah Citra A untuk membuka parameter.";
    tampilkanRumus("");
    el("#grid-parameter").innerHTML = "";
    el("#btn-batal-parameter").disabled = false;
    el("#tombol-jalankan").hidden = false;
    perbaruiJalankan();
    el('[data-slot="a"]').scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  async function jalankanAksi(action) {
    if (!action) return;
    if (action !== "about.info") tutupTentang();
    if (AKSI_KHUSUS[action]) {
      AKSI_KHUSUS[action]();
      return;
    }

    hentikanPratinjau();
    try {
      const data = await api(`/api/operasi/${encodeURIComponent(action)}/form`);

      if (
        state.info &&
        state.info.hasil &&
        state.operasi !== data.action
      ) {
        try {
          const tutup = await api("/api/tutup-hasil", { method: "POST" });
          terapkanState(tutup.state);
        } catch {
          /* hasil lama tetap ditampilkan bila gagal ditutup */
        }
      }

      state.preset = data.preset_kernel || {};
      aturButuhB(Boolean(data.butuh_b));
      state.aksiTertunda = null;
      bangunForm(data);

      const bKosong = Boolean(data.butuh_b) && !(state.info && state.info.b);
      if (bKosong) {
        el('[data-slot="b"]').scrollIntoView({ block: "nearest", behavior: "smooth" });
      } else {
        el("#panel-parameter").scrollIntoView({ block: "nearest", behavior: "smooth" });
      }
    } catch (galat) {
      if (galat.message === PESAN_CITRA_KOSONG) {
        state.aksiTertunda = action;
        tampilkanTertunda(action);
        return;
      }
      kabar(galat.message, "galat");
    }
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
        if (aksi === "reset") {
          aksiSederhana("/api/reset", () => resetParameter());
        }
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

    el("#form-parameter").addEventListener("submit", (peristiwa) => {
      peristiwa.preventDefault();
      kirimOperasi();
    });

    const btnBatal = el("#btn-batal-parameter");
    if (btnBatal) {
      btnBatal.addEventListener("click", () => {
        resetParameter();
        el("#panel-parameter").scrollIntoView({ block: "nearest", behavior: "smooth" });
      });
    }

    const tombolTerapkan = el("#btn-terapkan");
    if (tombolTerapkan) {
      tombolTerapkan.addEventListener("click", () => aksiSederhana("/api/terapkan"));
    }
    el("#btn-tutup-hasil").addEventListener("click", () =>
      aksiSederhana("/api/tutup-hasil")
    );

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

    el("#format-unduh").addEventListener("change", () => {
      const nama = el("#nama-unduh").value.trim();
      if (!nama) return;
      const akar = namaDasar(nama) || "citra";
      el("#nama-unduh").value = `${akar}${ekstensiFormat(el("#format-unduh").value)}`;
    });

    el("#form-unduh").addEventListener("submit", (peristiwa) => {
      peristiwa.preventDefault();
      const format = el("#format-unduh").value;
      const nama = el("#nama-unduh").value.trim();
      if (!nama) {
        kabar("Nama berkas tidak boleh kosong.", "galat");
        el("#nama-unduh").focus();
        return;
      }
      el("#dlg-unduh").close();
      pemicuUnduh(state.slotUnduh, format, nama);
    });

    for (const tombol of els("[data-tutup]")) {
      tombol.addEventListener("click", () => {
        const dialog = tombol.closest("dialog");
        if (dialog) dialog.close();
      });
    }

    window.addEventListener("pageshow", (peristiwa) => {
      if (!peristiwa.persisted) return;
      api("/api/state")
        .then((data) => terapkanState(data.state))
        .catch(() => {
          /* keadaan lama tetap ditampilkan */
        });
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    pulihkanBuka();
    const aksiTersimpan = pulihkanAktif();

    const dataAwal = el("#data-awal");
    if (dataAwal) {
      try {
        terapkanState(JSON.parse(dataAwal.textContent));
      } catch {
        kabar("Keadaan awal tidak dapat dibaca.", "galat");
      }
    }

    // Bangun ulang formulir parameter untuk operasi yang tersimpan,
    // supaya panel parameter tidak kosong setelah halaman dimuat ulang.
    if (aksiTersimpan && state.info && state.info.a && aksiTersimpan !== "about.info") {
      jalankanAksi(aksiTersimpan);
    }

    pasangPeristiwa();
  });
