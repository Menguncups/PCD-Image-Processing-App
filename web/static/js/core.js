/* Aplikasi PCD versi web: antarmuka tanpa kerangka kerja.
   Seluruh keadaan citra disimpan di server, peramban hanya mengatur tampilan.
   Berkas 1 dari 4: utilitas, keadaan, dan gambar kartu/hasil. */
"use strict";

  const el = (pemilih, akar = document) => akar.querySelector(pemilih);
  const els = (pemilih, akar = document) => Array.from(akar.querySelectorAll(pemilih));

  const KUNCI_SIMPAN = {
    aktif: "pcd.aksi.aktif",
    buka: "pcd.menu.buka",
  };

  const MEDIA_SEMPIT = window.matchMedia("(max-width: 1000px)");

  const state = {
    info: null,
    operasi: null,
    butuhB: false,
    preset: {},
    aksiTertunda: null,
    pratinjau: false,
    pratinjauAwal: false,
    pratinjauSibuk: false,
    pratinjauDirty: false,
    pratinjauTimer: null,
    pratinjauVersi: 0,
    pesanValidasi: "",
    slotUnduh: "a",
    sibuk: false,
  };

  const DATA = (() => {
    try {
      return JSON.parse(el("#data-aplikasi").textContent);
    } catch {
      return {};
    }
  })();

  const AKSI_BUTUH_B = new Set(DATA.aksi_butuh_b || []);
  const OPERAN_CITRA = "Citra + Citra";
  const OPERAN_SKALAR = "Citra + Skalar";

  // Pesan baku ini sama persis dengan pesan di server.
  const PESAN_CITRA_KOSONG =
    "Belum ada citra yang dimuat. Silakan buka citra terlebih dahulu.";
  const PESAN_CITRA_B_KOSONG =
    "Belum ada citra referensi (Citra B). Silakan buka citra kedua terlebih dahulu.";
  const PESAN_UKURAN_BEDA =
    "Citra tidak memiliki ukuran yang sama. Harap gunakan citra dengan dimensi yang sama.";
  const BATAS_HASIL_PIKSEL = Number(DATA.batas_hasil_piksel) || 80_000_000;

  // -------------------------------------------------------------- utilitas

  function simpan(kunci, nilai) {
    try {
      localStorage.setItem(kunci, nilai);
    } catch {
      /* penyimpanan lokal bisa dimatikan pengguna */
    }
  }

  function ambil(kunci) {
    try {
      return localStorage.getItem(kunci);
    } catch {
      return null;
    }
  }

  let jamKabar = null;

  function kabar(teks, jenis = "info") {
    const simpul = el("#kabar");
    if (!simpul) return;
    if (jamKabar) {
      clearTimeout(jamKabar);
      jamKabar = null;
    }
    if (!teks) {
      simpul.hidden = true;
      return;
    }
    simpul.textContent = teks;
    simpul.dataset.jenis = jenis;
    simpul.hidden = false;
    jamKabar = setTimeout(() => {
      simpul.hidden = true;
      jamKabar = null;
    }, jenis === "galat" ? 8000 : 3200);
  }

  async function api(alamat, opsi = {}) {
    let balasan;
    try {
      balasan = await fetch(alamat, { credentials: "same-origin", ...opsi });
    } catch {
      throw new Error("Server tidak dapat dihubungi. Periksa koneksi lalu coba lagi.");
    }

    let data = null;
    try {
      data = await balasan.json();
    } catch {
      throw new Error(
        balasan.status === 413
          ? "Berkas terlalu besar untuk diunggah."
          : "Jawaban server tidak dapat dibaca."
      );
    }

    if (!balasan.ok || !data || data.ok !== true) {
      throw new Error((data && data.pesan) || "Permintaan gagal diproses.");
    }
    return data;
  }

  function labelCitra(info) {
    if (!info) return "Belum ada citra";
    const warna = info.kanal === 1 ? "Grayscale" : "RGB";
    return `${info.nama}  |  ${info.lebar} x ${info.tinggi}  |  ${warna}`;
  }

  function labelRingkas(info) {
    if (!info) return "Belum ada citra";
    return `${info.lebar} x ${info.tinggi}  |  ${info.kanal === 1 ? "Grayscale" : "RGB"}`;
  }

  // ----------------------------------------------------------- gambar kartu

  function aturKartu(slot, info) {
    const kartu = el(`[data-slot="${slot}"]`);
    if (!kartu) return;

    const kosong = el(`[data-peran="kosong-${slot}"]`, kartu);
    const gambar = el(`[data-peran="gambar-${slot}"]`, kartu);
    const img = el("img", gambar);
    const lencana = el(`[data-peran="meta-${slot}"]`, kartu);
    const kaki = el(`[data-peran="kaki-${slot}"]`, kartu);
    const ganti = el(`[data-peran="ganti-${slot}"]`, kartu);

    if (info) {
      img.src = `/api/citra/${slot}.png?v=${info.versi}`;
      gambar.hidden = false;
      kosong.hidden = true;
      lencana.textContent = labelRingkas(info);
      kaki.textContent = labelCitra(info);
      if (ganti) ganti.hidden = false;
      kartu.classList.add("terisi");
    } else {
      img.removeAttribute("src");
      gambar.hidden = true;
      kosong.hidden = false;
      lencana.textContent = "Belum ada citra";
      kaki.textContent = "Belum ada citra";
      if (ganti) ganti.hidden = true;
      kartu.classList.remove("terisi");
    }
  }

  function aturTombol(pemilih, nonaktif) {
    const tombol = el(pemilih);
    if (tombol) tombol.disabled = Boolean(nonaktif);
  }

  function angkaTampil(nilai) {
    if (!Number.isFinite(nilai)) return "-";
    return Number(nilai.toFixed(2)).toLocaleString("id-ID", {
      maximumFractionDigits: 2,
    });
  }

  function infoUkuranHasil(info, hasil) {
    const sesudah = hasil.sesudah || {};
    if (!sesudah.lebar || !sesudah.tinggi) return "";
    const bagian = [
      `Hasil ${sesudah.lebar} x ${sesudah.tinggi} px`,
      sesudah.kanal === 1 ? "1 kanal (grayscale)" : `${sesudah.kanal} kanal`,
    ];
    const a = info.a;
    if (a) {
      const skalaX = sesudah.lebar / a.lebar;
      const skalaY = sesudah.tinggi / a.tinggi;
      if (Math.abs(skalaX - 1) > 0.005 || Math.abs(skalaY - 1) > 0.005) {
        bagian.push(`skala ${angkaTampil(skalaX)}x / ${angkaTampil(skalaY)}x dari Citra A`);
      } else {
        bagian.push("ukuran sama dengan Citra A");
      }
    }
    return bagian.join(" | ");
  }

  function aturMenuSimpan(buka) {
    const btn = el("#btn-simpan-dropdown");
    const menu = el("#menu-simpan");
    if (!menu) return;
    menu.hidden = !buka;
    if (btn) {
      btn.classList.toggle("buka", buka);
      btn.setAttribute("aria-expanded", buka ? "true" : "false");
    }
  }

  function aturHasil(info) {
    const gambar = el("#gambar-hasil");
    const kosong = el("#kosong-hasil");
    const lencana = el("#lencana-operasi");
    const tombolTutup = el("#btn-tutup-hasil");
    const infoHasil = el("#info-hasil");
    if (!gambar || !kosong || !lencana) return;

    const hasil = info.hasil;
    if (!hasil) {
      el("#img-hasil").removeAttribute("src");
      gambar.hidden = true;
      kosong.hidden = false;
      lencana.textContent = "Belum ada hasil";
      lencana.removeAttribute("title");
      if (infoHasil) {
        infoHasil.textContent = "Belum ada citra";
        infoHasil.hidden = false;
      }
      if (tombolTutup) {
        tombolTutup.disabled = false;
        tombolTutup.hidden = false;
      }
      const btnSimpan = el("#btn-simpan-dropdown");
      if (btnSimpan) {
        btnSimpan.disabled = false;
        btnSimpan.hidden = false;
      }
      aturMenuSimpan(false);
      aturTombol("#btn-terapkan", false);
      return;
    }

    el("#img-hasil").src = `/api/citra/hasil.png?v=${hasil.versi}`;
    gambar.hidden = false;
    kosong.hidden = true;
    lencana.textContent = hasil.judul;
    lencana.title = lencana.textContent;
    if (infoHasil) {
      const teks = infoUkuranHasil(info, hasil);
      infoHasil.textContent = teks;
      infoHasil.hidden = !teks;
    }
    if (tombolTutup) {
      tombolTutup.disabled = false;
      tombolTutup.hidden = false;
    }
    const btnSimpan = el("#btn-simpan-dropdown");
    if (btnSimpan) {
      btnSimpan.disabled = false;
      btnSimpan.hidden = false;
    }
    aturTombol("#btn-terapkan", false);
  }

  function aturButuhB(nilai) {
    state.butuhB = Boolean(nilai);
    const wadah = el(".kartu-citra");
    if (wadah) wadah.classList.toggle("tanpa-b", !state.butuhB);
  }

  function aturPrasyarat(teks, jenis = "info") {
    const simpul = el("#ket-prasyarat");
    if (!simpul) return;
    simpul.textContent = teks || "";
    simpul.hidden = !teks;
    simpul.dataset.jenis = jenis;
    simpul.classList.toggle("galat", jenis === "galat");
  }

  function statusPrasyarat() {
    const info = state.info || {};
    if (!info.a) return { siap: false, pesan: PESAN_CITRA_KOSONG };
    if (!state.butuhB) return { siap: true, pesan: "" };
    if (!info.b) return { siap: false, pesan: PESAN_CITRA_B_KOSONG };
    if (info.a.lebar !== info.b.lebar || info.a.tinggi !== info.b.tinggi) {
      return { siap: false, pesan: PESAN_UKURAN_BEDA };
    }
    return { siap: true, pesan: "" };
  }

  function perbaruiJalankan() {
    const tombol = el("#tombol-jalankan");
    if (!tombol) return;

    const { siap, pesan } = statusPrasyarat();
    const pratinjau = Boolean(state.operasi && state.pratinjau);
    tombol.hidden = false;
    tombol.disabled = false;
    tombol.textContent = state.sibuk ? "Menjalankan..." : "Jalankan";
    const btnBatal = el("#btn-batal-parameter");
    if (btnBatal) btnBatal.disabled = false;

    if (state.pesanValidasi) {
      aturPrasyarat(state.pesanValidasi, "galat");
    } else if (state.aksiTertunda && !(state.info && state.info.a)) {
      aturPrasyarat(PESAN_CITRA_KOSONG, "info");
    } else if (!state.operasi) {
      aturPrasyarat("", "info");
    } else if (!siap) {
      aturPrasyarat(pesan, "info");
    } else if (pratinjau) {
      aturPrasyarat("Pratinjau diperbarui otomatis saat parameter berubah.", "info");
    } else {
      aturPrasyarat("", "info");
    }
  }

  function hentikanPratinjau() {
    if (state.pratinjauTimer) {
      clearTimeout(state.pratinjauTimer);
      state.pratinjauTimer = null;
    }
    state.pratinjauDirty = false;
    state.pratinjauVersi += 1;
  }

  function mungkinPratinjauAwal() {
    if (!state.operasi || !state.pratinjau || state.pratinjauAwal) return;
    state.pratinjauAwal = true;
    jadwalkanPratinjau(0);
  }

  function gambarHistogram(info) {
    const panel = el("#panel-histogram");
    const kanvasA = el("#kanvas-histogram-a");
    const kanvasB = el("#kanvas-histogram-b");
    const hist = (info.hasil && info.hasil.histogram) || info.histogram_statis;
    if (!panel || !kanvasA || !kanvasB || !hist || !hist.sebelum || !hist.sesudah) {
      if (panel) panel.hidden = true;
      return;
    }
    panel.hidden = false;

    const ambang = typeof hist.ambang === "number" ? hist.ambang : null;
    const ketAmbang = el("#ket-ambang");
    const nilaiAmbang = el("#nilai-ambang");
    if (ketAmbang && nilaiAmbang) {
      ketAmbang.hidden = ambang === null;
      nilaiAmbang.textContent = ambang === null ? "" : String(ambang);
    }

    // Gabungkan 256 nilai menjadi 8 bin, lalu ubah menjadi persen piksel.
    const keBin = (data) => {
      const bin = new Array(8).fill(0);
      for (let i = 0; i < 256; i += 1) bin[Math.floor(i / 32)] += data[i] || 0;
      const total = bin.reduce((s, v) => s + v, 0) || 1;
      return bin.map((v) => (v / total) * 100);
    };

    const rataRata = (data) => {
      const total = data.reduce((s, v) => s + v, 0) || 1;
      return data.reduce((s, v, i) => s + v * i, 0) / total;
    };
    const meanSebelum = rataRata(hist.sebelum);
    const meanSesudah = rataRata(hist.sesudah);

    const ketHist = el("#ket-histogram");
    if (ketHist) {
      const selisih = meanSesudah - meanSebelum;
      const banding = selisih > 2 ? "Hasil lebih terang." : selisih < -2 ? "Hasil lebih gelap." : "Hasil hampir sama terangnya.";
      ketHist.textContent =
        `Rata-rata keterangan Citra A: ${Math.round(meanSebelum)}, ` +
        `Hasil: ${Math.round(meanSesudah)}. ${banding} ` +
        "Sumbu horizontal adalah nilai terang 0 sampai 255, sumbu vertikal adalah persen piksel.";
    }

    // Satu grafik untuk satu gambar, skala persennya sama di kedua grafik.
    const gambarkanSatu = (kanvas, data, warna, mean, tampilAmbang) => {
      const rasio = window.devicePixelRatio || 1;
      const lebarCss = kanvas.clientWidth || 400;
      const tinggiCss = 260;
      kanvas.width = Math.round(lebarCss * rasio);
      kanvas.height = Math.round(tinggiCss * rasio);
      const ctx = kanvas.getContext("2d");
      ctx.scale(rasio, rasio);

      const padKiri = 38;
      const padKanan = 8;
      const padAtas = 8;
      const padBawah = 20;
      const lebarPlot = lebarCss - padKiri - padKanan;
      const tinggiPlot = tinggiCss - padAtas - padBawah;
      const bin = keBin(data);

      ctx.font = "11px sans-serif";
      ctx.textAlign = "right";
      ctx.textBaseline = "middle";
      for (const persen of [0, 25, 50, 75, 100]) {
        const y = padAtas + tinggiPlot - (persen / 100) * tinggiPlot;
        ctx.strokeStyle = persen === 0 ? "#c9cfda" : "#e6e9f0";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padKiri, y);
        ctx.lineTo(padKiri + lebarPlot, y);
        ctx.stroke();
        ctx.fillStyle = "#7a8394";
        ctx.fillText(`${persen}%`, padKiri - 6, y);
      }

      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.font = "9px sans-serif";
      for (let b = 0; b < 8; b += 1) {
        const x = padKiri + ((b + 0.5) / 8) * lebarPlot;
        ctx.fillStyle = "#7a8394";
        ctx.fillText(`${b * 32}-${b * 32 + 31}`, x, padAtas + tinggiPlot + 5);
      }
      ctx.font = "11px sans-serif";

      const lebarBin = lebarPlot / 8;
      const lebarBatang = Math.max(2, lebarBin * 0.62);
      ctx.fillStyle = warna;
      for (let b = 0; b < 8; b += 1) {
        const tinggi = Math.min(100, bin[b]) * (tinggiPlot / 100);
        ctx.fillRect(padKiri + b * lebarBin + lebarBin * 0.19, padAtas + tinggiPlot - tinggi, lebarBatang, tinggi);
      }

      const xMean = padKiri + (mean / 255) * lebarPlot;
      ctx.strokeStyle = warna;
      ctx.lineWidth = 1.2;
      ctx.setLineDash([3, 3]);
      ctx.beginPath();
      ctx.moveTo(xMean, padAtas);
      ctx.lineTo(xMean, padAtas + tinggiPlot);
      ctx.stroke();
      ctx.setLineDash([]);

      if (tampilAmbang && ambang !== null) {
        const x = padKiri + (ambang / 255) * lebarPlot;
        ctx.strokeStyle = "#c0392b";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(x, padAtas);
        ctx.lineTo(x, padAtas + tinggiPlot);
        ctx.stroke();
      }
    };

    gambarkanSatu(kanvasA, hist.sebelum, "rgba(154, 163, 178, 0.85)", meanSebelum, true);
    gambarkanSatu(kanvasB, hist.sesudah, "rgba(47, 111, 237, 0.85)", meanSesudah, false);
  }

  function terapkanState(info) {
    if (!info) return;
    state.info = info;
    aturKartu("a", info.a);
    aturKartu("b", info.b);
    aturHasil(info);
    gambarHistogram(info);
    aturButuhB(state.butuhB);
    el("#btn-reset").disabled = false;
    perbaruiJalankan();
    mungkinPratinjauAwal();
  }
