/* Aplikasi PCD versi web: antarmuka tanpa kerangka kerja.
   Berkas 2 dari 4: sidebar, tentang, dan laci. Dimuat berurutan setelah core.js; seluruh
   fungsi dan keadaan dibuat bersama lewat cakupan global skrip klasik. */
"use strict";

  // ---------------------------------------------------------------- sidebar

  function labelGrup(grup) {
    const simpul = el(":scope > .grup-baris > .label", grup);
    return simpul ? simpul.textContent.trim() : "";
  }

  function jalurElemen(unsur) {
    const bagian = [];
    let grup = unsur.closest(".grup");
    while (grup) {
      const label = labelGrup(grup);
      if (label) bagian.unshift(label);
      grup = grup.parentElement.closest(".grup");
    }
    const label = el(":scope > .label", unsur);
    if (label) bagian.push(label.textContent.trim());
    return bagian;
  }

  function setBuka(grup, buka) {
    const tombol = el(":scope > .grup-baris", grup);
    const anak = el(":scope > .anak", grup);
    grup.classList.toggle("buka", buka);
    if (tombol) tombol.setAttribute("aria-expanded", buka ? "true" : "false");
    if (anak) {
      anak.hidden = !buka;
      if (!buka) {
        for (const turunan of els(".grup", anak)) setBuka(turunan, false);
      }
    }
  }

  function alihGrup(tombol) {
    const grup = tombol.closest(".grup");
    if (!grup) return;

    const buka = !grup.classList.contains("buka");
    if (buka) {
      for (const kakak of Array.from(grup.parentElement.children)) {
        if (kakak !== grup && kakak.classList.contains("grup")) setBuka(kakak, false);
      }
    }
    setBuka(grup, buka);
    simpanBuka();
  }

  function simpanBuka() {
    const terbuka = els(".grup.buka")
      .map((grup) => jalurElemen(el(":scope > .grup-baris", grup)).join(" / "))
      .filter(Boolean);
    simpan(KUNCI_SIMPAN.buka, JSON.stringify(terbuka));
  }

  function pulihkanBuka() {
    let tersimpan = [];
    try {
      tersimpan = JSON.parse(ambil(KUNCI_SIMPAN.buka) || "[]");
    } catch {
      tersimpan = [];
    }
    if (!Array.isArray(tersimpan) || !tersimpan.length) {
      // Tampilkan satu cabang pertama agar isi menu langsung terlihat.
      const pertama = el(".pohon > .cabang > .grup");
      if (pertama) setBuka(pertama, true);
      return;
    }

    for (const jalur of tersimpan) {
      const grup = els(".grup").find(
        (kandidat) =>
          jalurElemen(el(":scope > .grup-baris", kandidat)).join(" / ") === jalur
      );
      if (grup) setBuka(grup, true);
    }
  }

  function bukaJalur(unsur) {
    const rantai = [];
    let grup = unsur.closest(".grup");
    while (grup) {
      rantai.unshift(grup);
      grup = grup.parentElement.closest(".grup");
    }
    for (const bagian of rantai) setBuka(bagian, true);
    simpanBuka();
  }

  function bersihkanAktif() {
    for (const lain of els(".daun.aktif")) lain.classList.remove("aktif");
    simpan(KUNCI_SIMPAN.aktif, "");
  }

  function tandaiAktif(daun, simpanPilihan = true) {
    for (const lain of els(".daun.aktif")) lain.classList.remove("aktif");
    daun.classList.add("aktif");
    el("#remah").textContent = jalurElemen(daun).join(" / ");
    if (simpanPilihan) simpan(KUNCI_SIMPAN.aktif, daun.dataset.action || "");
  }

  function pulihkanAktif() {
    const aksi = ambil(KUNCI_SIMPAN.aktif);
    if (!aksi) return;
    const daun = el(`[data-action="${CSS.escape(aksi)}"]`);
    if (!daun) return;
    tandaiAktif(daun, false);
    bukaJalur(daun);
  }

  // ----------------------------------------------------------------- tentang

  function tampilkanTentang() {
    hentikanPratinjau();
    const ruangKerja = el("#ruang-kerja");
    const panelTentang = el("#panel-tentang");
    if (!panelTentang) {
      window.location.href = "tentang.html";
      return;
    }
    if (ruangKerja) ruangKerja.hidden = true;
    panelTentang.hidden = false;
    el("#aplikasi").classList.add("tentang-buka");
    el("#gulir").scrollTop = 0;
  }

  function tutupTentang() {
    const ruangKerja = el("#ruang-kerja");
    const panel = el("#panel-tentang");
    if (!ruangKerja) {
      window.location.href = "index.html";
      return;
    }
    if (!panel || panel.hidden) return;
    panel.hidden = true;
    ruangKerja.hidden = false;
    el("#aplikasi").classList.remove("tentang-buka");
  }

  // ------------------------------------------------------------------- laci

  function perbaruiTataSisi() {
    if (!MEDIA_SEMPIT.matches && el("#aplikasi").classList.contains("sisi-buka")) {
      tutupLaci();
    }
  }

  function bukaLaci() {
    el("#aplikasi").classList.add("sisi-buka");
    el("#tirai").hidden = false;
    el("#btn-sisi").setAttribute("aria-expanded", "true");
  }

  function tutupLaci() {
    el("#aplikasi").classList.remove("sisi-buka");
    el("#tirai").hidden = true;
    el("#btn-sisi").setAttribute("aria-expanded", "false");
  }
