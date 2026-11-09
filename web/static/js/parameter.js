/* Aplikasi PCD versi web: antarmuka tanpa kerangka kerja.
   Berkas 3 dari 4: parameter, validasi, dan pratinjau. Dimuat berurutan setelah core.js; seluruh
   fungsi dan keadaan dibuat bersama lewat cakupan global skrip klasik. */
"use strict";

  // -------------------------------------------------------------- parameter

  function tampilkanRumus(latex) {
    const kotak = el("#rumus-operasi");
    const isi = el("#isi-rumus");
    if (!kotak || !isi) return;

    isi.replaceChildren();
    const teks = String(latex || "").trim();
    kotak.hidden = !teks;
    if (!teks) return;

    if (window.katex && typeof window.katex.render === "function") {
      try {
        window.katex.render(teks, isi, {
          displayMode: true,
          throwOnError: false,
          strict: "ignore",
          trust: false,
        });
        return;
      } catch {
        /* tampilkan sumber LaTeX bila mesin rumus gagal */
      }
    }
    isi.textContent = teks;
  }

  function sinkronAritmetika(data, wadah) {
    const operan = el('[data-kunci="operan"]', wadah);
    if (!operan) return;

    const skalar = operan.value === OPERAN_SKALAR;
    const medanSkalar = el('[data-kunci="skalar"]', wadah)?.closest(".medan");
    const inputSkalar = medanSkalar
      ? el('[data-kunci="skalar"]', medanSkalar)
      : null;

    if (medanSkalar) {
      medanSkalar.hidden = !skalar;
      if (inputSkalar) inputSkalar.disabled = !skalar;
    }

    aturButuhB(!skalar);
    tampilkanRumus(skalar ? data.rumus_skalar || data.rumus : data.rumus);
    perbaruiJalankan();
  }

  function bangunForm(data) {
    hentikanPratinjau();
    state.operasi = data.action;
    state.pratinjau = Boolean(data.pratinjau);
    state.pratinjauAwal = false;
    state.pratinjauSibuk = false;
    state.pratinjauDirty = false;
    state.pesanValidasi = "";

    el("#judul-operasi").textContent = data.judul;
    el("#jalur-operasi").textContent = data.jalur;
    el("#ketik-operasi").textContent = data.ketik || "";
    tampilkanRumus(data.rumus);

    const wadah = el("#grid-parameter");
    wadah.innerHTML = "";
    for (const param of data.params) {
      wadah.appendChild(bangunMedan(param, data));
    }
    if (!data.params.length) {
      const catatan = document.createElement("p");
      catatan.className = "ketik";
      catatan.textContent = "Operasi ini tidak membutuhkan parameter.";
      wadah.appendChild(catatan);
    }

    const operan = el('[data-kunci="operan"]', wadah);
    if (operan) {
      operan.addEventListener("change", () => sinkronAritmetika(data, wadah));
      sinkronAritmetika(data, wadah);
    }

    for (const kendali of els("[data-kunci]", wadah)) {
      if (kendali.dataset.jenis === "kernel") continue;
      kendali.addEventListener("input", () => jadwalkanPratinjau());
      kendali.addEventListener("change", () => jadwalkanPratinjau());
    }

    el("#btn-batal-parameter").disabled = false;
    perbaruiJalankan();
    mungkinPratinjauAwal();
  }

  function resetParameter(bersihkanPilihan = true) {
    hentikanPratinjau();
    state.operasi = null;
    state.preset = {};
    state.aksiTertunda = null;
    state.pratinjau = false;
    state.pratinjauAwal = false;
    state.pratinjauSibuk = false;
    state.pesanValidasi = "";
    aturButuhB(false);

    el("#judul-operasi").textContent = "Parameter";
    el("#jalur-operasi").textContent = "Belum ada operasi";
    el("#ketik-operasi").textContent =
      "Pilih operasi dari menu untuk mengatur parameter.";
    tampilkanRumus("");
    el("#grid-parameter").innerHTML = "";
    el("#btn-batal-parameter").disabled = false;
    el("#tombol-jalankan").hidden = false;
    el("#tombol-jalankan").disabled = false;
    el("#tombol-jalankan").textContent = "Jalankan";
    const panelHist = el("#panel-histogram");
    if (panelHist) panelHist.hidden = true;

    if (bersihkanPilihan) {
      bersihkanAktif();
      el("#remah").textContent = "Belum ada operasi dipilih";
    }
    perbaruiJalankan();
  }

  function bangunMedan(param, data) {
    if (param.jenis === "kernel") return medanKernel(param, data);
    if (param.jenis === "centang") return medanCentang(param);

    const bungkus = document.createElement("label");
    bungkus.className = "medan";

    const judul = document.createElement("span");
    judul.className = "medan-label";
    judul.textContent = param.label;
    bungkus.appendChild(judul);

    let kendali;
    if (param.jenis === "pilihan") {
      kendali = document.createElement("select");
      for (const pilihan of param.pilihan || []) {
        const opsi = document.createElement("option");
        opsi.value = pilihan;
        opsi.textContent = pilihan;
        opsi.selected = pilihan === param.nilai;
        kendali.appendChild(opsi);
      }
      kendali.dataset.kunci = param.kunci;
      kendali.dataset.jenis = param.jenis;
      bungkus.appendChild(kendali);
    } else {
      kendali = document.createElement("input");
      kendali.type = "number";
      kendali.value = String(param.nilai);
      kendali.step =
        param.langkah !== null && param.langkah !== undefined
          ? String(param.langkah)
          : param.bulat
            ? "1"
            : "any";
      if (param.minimum !== null && param.minimum !== undefined) {
        kendali.min = String(param.minimum);
      }
      if (param.maksimum !== null && param.maksimum !== undefined) {
        kendali.max = String(param.maksimum);
      }
      kendali.dataset.kunci = param.kunci;
      kendali.dataset.jenis = param.jenis;

      if (param.geser) {
        const baris = document.createElement("div");
        baris.className = "medan-angka";

        const geser = document.createElement("input");
        geser.type = "range";
        geser.value = String(param.nilai);
        geser.step =
          param.langkah !== null && param.langkah !== undefined
            ? String(param.langkah)
            : param.bulat
              ? "1"
              : "0.1";
        if (param.minimum !== null && param.minimum !== undefined) {
          geser.min = String(param.minimum);
        }
        if (param.maksimum !== null && param.maksimum !== undefined) {
          geser.max = String(param.maksimum);
        }
        geser.setAttribute("aria-label", `Penggeser ${param.label}`);

        const nilaiDalamBatas = (nilai) => {
          let angka = Number(nilai);
          if (!Number.isFinite(angka)) return null;
          if (param.minimum !== null && param.minimum !== undefined) {
            angka = Math.max(Number(param.minimum), angka);
          }
          if (param.maksimum !== null && param.maksimum !== undefined) {
            angka = Math.min(Number(param.maksimum), angka);
          }
          if (param.bulat) angka = Math.round(angka);
          return angka;
        };

        const sinkron = (sumber) => {
          const angka = nilaiDalamBatas(sumber.value);
          if (angka === null) return;
          kendali.value = String(angka);
          geser.value = String(angka);
          jadwalkanPratinjau();
        };

        geser.addEventListener("input", () => sinkron(geser));
        kendali.addEventListener("input", () => sinkron(kendali));
        kendali.addEventListener("change", () => sinkron(kendali));

        baris.append(geser, kendali);
        bungkus.appendChild(baris);
      } else {
        bungkus.appendChild(kendali);
      }
    }

    if (param.ketik) {
      const ket = document.createElement("span");
      ket.className = "medan-ketik";
      ket.textContent = param.ketik;
      bungkus.appendChild(ket);
    }
    return bungkus;
  }

  function medanCentang(param) {
    const bungkus = document.createElement("div");
    bungkus.className = "medan";

    const label = document.createElement("label");
    label.className = "medan-centang";

    const kotak = document.createElement("input");
    kotak.type = "checkbox";
    kotak.checked = Boolean(param.nilai);
    kotak.dataset.kunci = param.kunci;
    kotak.dataset.jenis = "centang";

    const teks = document.createElement("span");
    teks.textContent = param.label;

    label.append(kotak, teks);
    bungkus.appendChild(label);

    if (param.ketik) {
      const ket = document.createElement("span");
      ket.className = "medan-ketik";
      ket.textContent = param.ketik;
      bungkus.appendChild(ket);
    }
    return bungkus;
  }

  function medanKernel(param, data) {
    const bungkus = document.createElement("div");
    bungkus.className = "medan medan-penuh";

    const judul = document.createElement("span");
    judul.className = "medan-label";
    judul.textContent = param.label;
    bungkus.appendChild(judul);

    const baris = document.createElement("div");
    baris.className = "kernel";

    const wadahPreset = document.createElement("label");
    wadahPreset.className = "kernel-preset";

    const labelPreset = document.createElement("span");
    labelPreset.textContent = "Preset kernel";

    const pilih = document.createElement("select");
    pilih.id = "preset-kernel";
    const daftar = Object.keys(state.preset);
    for (const nama of daftar) {
      const opsi = document.createElement("option");
      opsi.value = nama;
      opsi.textContent = nama;
      pilih.appendChild(opsi);
    }
    wadahPreset.append(labelPreset, pilih);

    const grid = document.createElement("div");
    grid.className = "kernel-grid";
    grid.id = "kernel-grid";
    grid.dataset.kunci = param.kunci;
    grid.dataset.jenis = "kernel";

    const matriks = Array.isArray(param.nilai)
      ? param.nilai
      : [
          [0, 0, 0],
          [0, 1, 0],
          [0, 0, 0],
        ];

    for (let i = 0; i < 9; i += 1) {
      const kotak = document.createElement("input");
      kotak.type = "number";
      kotak.step = "any";
      kotak.value = String(matriks[Math.floor(i / 3)][i % 3]);
      kotak.setAttribute(
        "aria-label",
        `Kernel baris ${Math.floor(i / 3) + 1} kolom ${(i % 3) + 1}`
      );
      grid.appendChild(kotak);
    }

    const ket = document.createElement("p");
    ket.className = "medan-ketik";
    ket.id = "kernel-ketik";

    // Pilih preset yang matriksnya sama dengan nilai awal, selain itu Sobel X
    const cocok = daftar.find((nama) => {
      const preset = state.preset[nama];
      if (!preset || !Array.isArray(preset.matriks)) return false;
      return preset.matriks.every((barisPreset, r) =>
        barisPreset.every((sel, c) => Number(sel) === Number(matriks[r][c]))
      );
    });
    const awal = cocok || (daftar.includes("Sobel X") ? "Sobel X" : daftar[0]);
    if (awal) pilih.value = awal;

    pilih.addEventListener("change", () => {
      const preset = state.preset[pilih.value];
      if (!preset || !Array.isArray(preset.matriks)) return;
      els("input", grid).forEach((kotak, i) => {
        kotak.value = String(preset.matriks[Math.floor(i / 3)][i % 3]);
      });
      ket.textContent = preset.ketik || "";
    });

    const keteranganAwal = awal ? state.preset[awal] : null;
    ket.textContent = keteranganAwal ? keteranganAwal.ketik || "" : "";

    baris.append(wadahPreset, grid);
    bungkus.append(baris, ket);
    return bungkus;
  }

  function kumpulkanParam() {
    const params = {};
    for (const kendali of els("[data-kunci]", el("#form-parameter"))) {
      const kunci = kendali.dataset.kunci;
      const jenis = kendali.dataset.jenis;
      if (jenis === "kernel") continue;
      if (kendali.disabled) continue;
      const medan = kendali.closest(".medan");
      if (medan && medan.hidden) continue;
      if (jenis === "centang") params[kunci] = kendali.checked;
      else params[kunci] = kendali.value;
    }

    const grid = el("#kernel-grid");
    if (grid) {
      const kotak = els("input", grid);
      const matriks = [];
      for (let baris = 0; baris < 3; baris += 1) {
        const isi = [];
        for (let kolom = 0; kolom < 3; kolom += 1) {
          isi.push(kotak[baris * 3 + kolom].value);
        }
        matriks.push(isi);
      }
      params[grid.dataset.kunci || "kernel"] = matriks;
    }
    return params;
  }

  function validasiParameter() {
    if (!state.operasi) return "";
    const form = el("#form-parameter");
    for (const kendali of els('input[type="number"][data-kunci]', form)) {
      if (kendali.disabled) continue;
      const medan = kendali.closest(".medan");
      if (medan && medan.hidden) continue;
      const nilaiTeks = String(kendali.value).trim();
      const label = kendali
        .closest(".medan")
        ?.querySelector(".medan-label")?.textContent;
      const nama = label || "Parameter";
      if (!nilaiTeks) return `${nama} tidak boleh kosong.`;
      const nilai = Number(nilaiTeks);
      if (!Number.isFinite(nilai)) return `${nama} harus berupa angka.`;
      if (kendali.min !== "" && nilai < Number(kendali.min)) {
        return `${nama} minimal ${kendali.min}.`;
      }
      if (kendali.max !== "" && nilai > Number(kendali.max)) {
        return `${nama} maksimal ${kendali.max}.`;
      }
    }

    const params = kumpulkanParam();
    if (
      state.operasi === "enh.contrast" &&
      Number(params.nilai_min) >= Number(params.nilai_max)
    ) {
      return "Batas bawah intensitas harus lebih kecil dari batas atas.";
    }
    if (
      state.operasi === "edge.canny" &&
      Number(params.ambang_bawah) >= Number(params.ambang_atas)
    ) {
      return "Ambang bawah Canny harus lebih kecil dari ambang atas.";
    }
    if (
      state.operasi === "basic.divide" &&
      params.operan === OPERAN_SKALAR &&
      Number(params.skalar) === 0
    ) {
      return "Nilai skalar pembagi tidak boleh nol.";
    }
    if (state.operasi === "geom.cropping") {
      const x1 = Number(params.x1);
      const y1 = Number(params.y1);
      const x2 = Number(params.x2);
      const y2 = Number(params.y2);
      if (x2 <= x1 || y2 <= y1) {
        return (
          "Area cropping tidak valid. Pastikan titik kanan bawah lebih besar " +
          "dari titik kiri atas."
        );
      }
    }
    if (state.operasi === "geom.zooming" && state.info && state.info.a) {
      const luas =
        state.info.a.lebar *
        Number(params.skala_x) *
        state.info.a.tinggi *
        Number(params.skala_y);
      if (Number.isFinite(luas) && luas > BATAS_HASIL_PIKSEL) {
        const batas = Math.round(BATAS_HASIL_PIKSEL / 1_000_000);
        return (
          `Ukuran hasil Zooming melebihi batas ${batas} megapiksel. ` +
          "Kecilkan faktor skala."
        );
      }
    }
    return "";
  }

  function jadwalkanPratinjau(jeda = 220) {
    if (!state.operasi) return;
    if (!state.pratinjau) {
      // Operasi manual (termasuk seluruh Geometrics) baru dijalankan lewat
      // tombol Jalankan. Perubahan parameter membersihkan pesan lama.
      if (state.pesanValidasi) {
        state.pesanValidasi = "";
        perbaruiJalankan();
      }
      return;
    }
    if (state.pratinjauTimer) {
      clearTimeout(state.pratinjauTimer);
      state.pratinjauTimer = null;
    }

    const pesan = validasiParameter();
    state.pesanValidasi = pesan;
    if (pesan) {
      state.pratinjauDirty = false;
      aturPrasyarat(pesan, "galat");
      return;
    }
    perbaruiJalankan();
    state.pratinjauDirty = true;
    state.pratinjauTimer = setTimeout(() => {
      state.pratinjauTimer = null;
      kirimPratinjau();
    }, jeda);
  }

  async function kirimPratinjau() {
    if (!state.operasi || !state.pratinjau) return;
    if (state.pratinjauSibuk || state.sibuk) {
      state.pratinjauDirty = true;
      return;
    }


    const pesan = validasiParameter();
    state.pesanValidasi = pesan;
    if (pesan) {
      aturPrasyarat(pesan, "galat");
      return;
    }

    const action = state.operasi;
    const params = kumpulkanParam();
    const versi = ++state.pratinjauVersi;
    state.pratinjauSibuk = true;
    state.pratinjauDirty = false;

    try {
      const data = await api(`/api/operasi/${encodeURIComponent(action)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ params }),
      });
      if (versi !== state.pratinjauVersi || action !== state.operasi) return;
      terapkanState(data.state);
    } catch (galat) {
      if (versi === state.pratinjauVersi && action === state.operasi) {
        kabar(galat.message, "galat");
      }
    } finally {
      state.pratinjauSibuk = false;
      if (
        state.pratinjauDirty &&
        action === state.operasi &&
        versi === state.pratinjauVersi
      ) {
        jadwalkanPratinjau(120);
      }
    }
  }

  async function kirimOperasi() {
    if (state.sibuk) return;
    if (!state.operasi) {
      kabar(PESAN_CITRA_KOSONG, "galat");
      return;
    }

    const pesan = validasiParameter();
    state.pesanValidasi = pesan;
    if (pesan) {
      aturPrasyarat(pesan, "galat");
      kabar(pesan, "galat");
      return;
    }

    const action = state.operasi;
    const tombolBatal = el("#btn-batal-parameter");
    state.sibuk = true;
    perbaruiJalankan();
    if (tombolBatal) tombolBatal.disabled = true;

    try {
      const data = await api(`/api/operasi/${encodeURIComponent(action)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ params: kumpulkanParam() }),
      });
      if (action !== state.operasi) return;
      terapkanState(data.state);
      kabar(data.pesan, "sukses");
      const panelHist = el("#panel-histogram");
      if (panelHist && !panelHist.hidden) {
        panelHist.scrollIntoView({ block: "nearest", behavior: "smooth" });
      } else {
        el("#panel-parameter").scrollIntoView({ block: "nearest", behavior: "smooth" });
      }
    } catch (galat) {
      kabar(galat.message, "galat");
    } finally {
      state.sibuk = false;
      if (tombolBatal) tombolBatal.disabled = false;
      perbaruiJalankan();
    }
  }
