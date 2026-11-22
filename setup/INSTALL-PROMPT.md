# Install / update prompt — muse-rsi (copy-paste for another Muse agent)

One prompt for both cases. It detects whether this agent already has
muse-rsi and either installs it fully or updates it fully — including the
24-hour loop activation and every warning that can appear. The full guide
— every method, every flag, every fix — lives in [INSTALL.md](../INSTALL.md)
(the Update section there covers the update path). Give the agent this
prompt and nothing else:

```text
Pasang atau update muse-rsi di agen ini sampai jadi full otonom seperti
KimiCharmi. Satu prompt ini berlaku untuk dua keadaan — deteksi dulu,
lalu ikuti cabang yang cocok. Jangan lompat ke cabang lain.

DETEKSI — muse-rsi sudah terpasang kalau salah satu ini benar:
- folder ~/muse-rsi ada dan berisi setup/setup.py; atau
- SOUL.md agen ini mengandung penanda <!-- muse-rsi:system:start -->; atau
- skill muse-rsi sudah terpasang.
Kalau tidak ada yang benar, berarti belum install.
Kalau skill ada tapi penanda SOUL.md tidak ada, berarti dulu install
pakai --skills-only — update nanti juga pakai --skills-only supaya file
sistem tidak disentuh.

CABANG A — BELUM INSTALL (install total full):
1. Ambil repo https://github.com/fahmi0812/muse-rsi ke ~/muse-rsi.
   Cara tercepat: one-liner install.sh dari INSTALL.md. Kalau one-liner
   diblokir atau kamu mau kontrol penuh: clone, lalu jalankan
   setup/setup.py --yes.
2. Lanjut ke VERIFIKASI dan AKTIVASI LOOP 24 JAM di bawah.

CABANG B — SUDAH INSTALL (update total):
1. Update repo ke main terbaru: git pull --ff-only origin main di
   ~/muse-rsi (bentuk eksplisit — jalan juga kalau checkout terlepas
   dari branch). Kalau pull gagal atau foldernya bukan git checkout,
   ambil ulang (clone baru atau ZIP) — jangan lanjut dengan copy lama.
2. Jalankan ulang setup/setup.py --yes (full update: SOUL, MEMORY, dan
   IDENTITY ditulis ulang dari template; nama + karakter tetap
   dipertahankan; skill + tools diperbarui). Kalau dulu --skills-only,
   ulangi dengan --skills-only.
3. Lanjut ke VERIFIKASI dan AKTIVASI LOOP 24 JAM di bawah. Laporkan
   sebagai update (versi lama → versi baru), bukan install baru.

VERIFIKASI (wajib di kedua cabang):
- Jalankan ~/workspace/tools/run_all_checks.sh — 10 check harus hijau:
  registry check, routing eval 130/130, validate (registry 248 entri:
  98 listed + 11 original + 139 lumitome-reference), secret scan bersih.
- Buktikan versi baru: registry 248 entri, eval 130/130, 12 skill
  terpasang (termasuk council + interrogate-claim), router v2.2.
  Kalau angkanya masih angka lama (mis. registry bukan 248, eval bukan
  130/130, skill bukan 12), berarti repo atau setup tidak ter-update —
  jangan klaim selesai, perbaiki dulu sampai angkanya benar.

AKTIVASI LOOP 24 JAM (wajib — setup tidak bisa melakukannya):
- Setup hanya memasang skill rsi-loop — ia tidak bisa membuat jadwal.
  Agen yang membuat jadwalnya: buat scheduled job harian bernama
  rsi-daily-self-improvement, tiap 24 jam, yang menjalankan skill
  rsi-loop (audit, pilih 1 perbaikan, snapshot, tes, secret scan, log).
- Jalankan run pertama secara manual sekali untuk membuktikan loop
  bekerja. Sesudahnya cek daftar scheduled job: job itu harus ada dan
  run pertama tercatat. Kalau ini update, cek job lama masih ada —
  kalau hilang, buat ulang dengan cara yang sama.
- Kalau runtime agen ini tidak bisa membuat scheduled job, laporkan itu
  sebagai satu-satunya langkah manual yang tersisa — jangan klaim agen
  sudah full otonom tanpa loop aktif.

PERINGATAN YANG MUNGKIN MUNCUL (jangan berhenti karenanya):
- Setup exit 20 / file STAGED: runtime memblokir shell menulis SOUL.md,
  IDENTITY.md, MEMORY.md — setup menyimpan file itu di
  ~/workspace/.muse-rsi-staging/. Buka tiap file staged dan salin isinya
  ke nama yang sama di home dengan file tool (bukan shell), hapus copy
  staging, lalu verifikasi ulang. Ini normal, bukan gagal.
- Secret scan: JANGAN push ke repo publik sebelum secret scan lolos.
  Kalau install pakai --no-gitleaks, check ke-4 akan bilang gitleaks
  hilang — itu wajar; install gitleaks dulu (jalankan setup ulang tanpa
  flag itu) dan jangan push sebelum scan bersih. Kalau scan menemukan
  secret → hentikan push, bersihkan secara lokal, scan ulang.
- Chrome JSON unreachable: setup memakai Chrome versi pin dengan tes
  integritas zip — warning saja, visual-check tetap terpasang. Bukan gagal.
- Nama fallback: kalau setup memberi warning nama jatuh ke 'Muse',
  ulangi dengan --name <nama agen> supaya nama asli dipertahankan.
- Kalau ada langkah gagal: laporkan langkahnya, pesan errornya, dan apa
  yang sudah dicoba — jangan lanjut diam-diam.

SELESAI: star repo di browser dan laporkan install/update sebagai issue
(pakai template install report; tulis ini update kalau cabang B, beserta
versi lama → baru). Yang tidak berubah hanya nama dan karakter saya.
SOUL, MEMORY, dan IDENTITY mengikuti full setup muse-rsi.
```

If the install changes, update `INSTALL.md` instead, and this prompt stays correct.
