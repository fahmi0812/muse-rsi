# Install / update prompt — muse-rsi (copy-paste for another Muse agent)

One prompt for both cases. It detects whether this agent already has
muse-rsi and either installs it fully or updates it fully — including the
24-hour loop activation and every warning that can appear. It never stops
to ask: a failed step is repaired (environment, dependency, permission,
folder, path, package), the install resumes from that step, and the fixes
are reported at the end. The full guide
— every method, every flag, every fix — lives in [INSTALL.md](../INSTALL.md)
(the Update section there covers the update path). Give the agent this
prompt and nothing else:

```text
Pasang atau update muse-rsi di agen ini sampai jadi full otonom seperti
KimiCharmi. Satu prompt ini berlaku untuk dua keadaan: deteksi dulu, lalu
ikuti cabang yang cocok. Jangan minta izin di tengah jalan. Kalau ada
langkah yang gagal, perbaiki sendiri dan lanjutkan (lihat KALAU ADA
LANGKAH GAGAL). Laporkan sekali di akhir.

DETEKSI — muse-rsi sudah terpasang kalau salah satu ini benar:
- folder ~/muse-rsi ada dan berisi setup/setup.py; atau
- SOUL.md agen ini mengandung penanda <!-- muse-rsi:system:start -->; atau
- skill muse-rsi sudah terpasang.
Kalau tidak ada yang benar, berarti belum install.
Kalau skill ada tapi penanda SOUL.md tidak ada, berarti dulu install
pakai --skills-only — update nanti juga pakai --skills-only supaya file
sistem tidak disentuh.

CABANG A — BELUM INSTALL dan CABANG B — SUDAH INSTALL (perintahnya sama):
1. Jalankan:
   curl -sSL https://raw.githubusercontent.com/fahmi0812/muse-rsi/main/install.sh | bash
   (tambahkan "-s -- --skills-only" setelah bash kalau dulu --skills-only).
   install.sh mengambil repo ke ~/muse-rsi (clone, atau update ke main
   terbaru), menjalankan setup, lalu semua check. Ia memperbaiki sendiri
   hambatan umum: retry jaringan, ZIP kalau git gagal, curl/unzip diganti
   Python, Node dipasang user-level, PyYAML lewat pip --user, /tmp kecil
   dialihkan ke ~/workspace/tmp, edit lokal disimpan ke git stash, branch
   yang menyimpang disimpan ke backup/pre-update-<waktu>.
2. Kalau one-liner diblokir: git clone https://github.com/fahmi0812/muse-rsi
   ~/muse-rsi (atau git -C ~/muse-rsi pull --ff-only origin main), lalu
   python3 ~/muse-rsi/setup/setup.py --yes.
3. Cabang B dilaporkan sebagai update (versi lama -> versi baru).

KALAU ADA LANGKAH GAGAL — PERBAIKI SENDIRI, JANGAN TANYA:
1. Baca pesan errornya dan cari penyebabnya.
2. Sesuaikan environment supaya langkah itu bisa jalan: install dependency
   (pip --user, npm lokal, Node/alat user-level di ~/workspace/tools),
   buat folder yang hilang, perbaiki permission file milikmu sendiri,
   set PATH/TMPDIR, ganti alat yang hilang dengan yang setara, ulangi
   unduhan yang putus, pakai sudo -n hanya kalau tersedia tanpa password.
3. Lanjut dari titik yang gagal: jalankan ulang perintah yang sama. Setup
   mencatat setiap langkah di ~/.muse-rsi/install_state.json dan otomatis
   melanjutkan dari langkah yang gagal (atau pakai setup.py --yes --resume).
   Jangan mulai dari awal dan jangan lewati langkah diam-diam.
4. Setelah lolos, laporkan: langkah apa, errornya apa, apa yang diperbaiki,
   dan bukti bahwa sekarang hijau (baris [fix] dan Self-heal di output).
Batas yang tetap berlaku walau ada yang gagal:
- jangan lewati atau lemahkan secret scan dan check apa pun;
- jangan ubah file hard core (trust, limits, critique, autonomy_gate,
  verifier_selftest, .github/, SOUL §1-4) supaya sebuah langkah lolos;
- jangan hapus data: pindahkan ke samping atau backup dulu;
- jangan sentuh isi vault, jangan sudo yang minta password, jangan bayar;
- jangan akali kartu persetujuan dari runtime.
Kalau satu langkah benar-benar tidak bisa diperbaiki, selesaikan semua
langkah lain dulu, lalu laporkan langkah itu dengan error dan apa saja yang
sudah dicoba.

VERIFIKASI (wajib):
- Jalankan ~/workspace/tools/run_all_checks.sh — kesepuluh langkah harus
  hijau dan baris terakhir ALL CHECKS PASSED.
- Angka harus sama dengan ~/muse-rsi/state/facts.json (registry_total,
  eval_top3, canary). Kalau berbeda, repo atau setup belum ter-update:
  jalankan ulang one-liner, jangan klaim selesai.

AKTIVASI LOOP 24 JAM (wajib — setup tidak bisa membuat jadwal):
- Buat scheduled job harian bernama rsi-daily-self-improvement yang
  menjalankan: cd ~/muse-rsi && python3 scripts/rsi_cycle.py run
- Jalankan sekali secara manual sekarang. Buktinya: perintah itu exit 0 dan
  ~/.muse-rsi/decision.tsv punya baris baru. Lalu cek daftar scheduled
  job: job itu harus ada. Kalau ini update, pastikan job lama masih ada;
  kalau hilang, buat ulang.
- Kalau runtime ini tidak bisa membuat scheduled job, laporkan itu sebagai
  satu-satunya langkah manual yang tersisa.

PERINGATAN YANG MUNGKIN MUNCUL (bukan gagal, jangan berhenti):
- Setup exit 20 / file STAGED: runtime memblokir shell menulis SOUL.md,
  IDENTITY.md, MEMORY.md. Buka tiap file di ~/workspace/.muse-rsi-staging/,
  salin isinya ke nama yang sama di home dengan file tool (bukan shell),
  hapus copy staging, lalu jalankan check lagi. Baseline SOUL §1-4 untuk
  Loop Engine sudah dicatat setup, jadi tidak perlu reset apa pun.
- Nama fallback: kalau setup memberi warning nama jatuh ke 'Muse', ulangi
  dengan --name <nama agen> supaya nama asli dipertahankan.
- Chrome JSON unreachable: setup memakai Chrome versi pin dengan tes
  integritas zip. Ini warning saja.

SELESAI: laporkan install/update (versi lama -> baru, daftar perbaikan
Self-heal, hasil check, bukti loop), star repo di browser, dan kirim
install report sebagai issue. Yang tidak berubah hanya nama dan karakter
saya. SOUL, MEMORY, dan IDENTITY mengikuti full setup muse-rsi.
```

If the install changes, update `INSTALL.md` instead, and this prompt stays correct.
