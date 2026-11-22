<p align="center">
  <img src="assets/logo.png" width="200" alt="Muse, the muse-rsi mascot: a strong fluffy creature wearing glasses, flexing">
</p>

<h1 align="center">muse-rsi</h1>

<p align="center">Verified Muse skills — and the setup that installs them.<br>246 entries, a router program, and a daily self-improvement loop. No guesses, no paid tools.</p>

> **Ringkasan Bahasa Indonesia:** Kumpulan skill Muse yang sudah dicek langsung. 246 entri (96 terdaftar + 11 orisinal + 139 referensi Lumitome), router yang dites 125/125, dan loop perbaikan diri tiap 24 jam. Pasang semuanya sekaligus dengan satu prompt di bawah.

## Install / update — copy-paste prompt

Copy the prompt below and paste it to any Muse agent. It detects whether muse-rsi is already installed: a fresh agent gets a full install, an existing one gets a full update — including the 24-hour loop activation and every warning that can appear.

<details>
<summary>📋 Install / update prompt (klik untuk membuka)</summary>

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
- Jalankan ~/workspace/tools/run_all_checks.sh — 4 check harus hijau:
  registry check, routing eval 125/125, validate (registry 246 entri:
  96 listed + 11 original + 139 lumitome-reference), secret scan bersih.
- Buktikan versi baru: registry 246 entri, eval 125/125, 12 skill
  terpasang (termasuk council + interrogate-claim), router v2.1.
  Kalau angkanya masih angka lama (mis. registry bukan 246, eval bukan
  125/125, skill bukan 12), berarti repo atau setup tidak ter-update —
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

</details>

Full guide with every method and flag: [INSTALL.md](INSTALL.md). The prompt itself lives in [setup/INSTALL-PROMPT.md](setup/INSTALL-PROMPT.md).

## What this is

- **Checked, not just listed.** 384 starred repos went in, 64 came out — each verified by hand (exists, `SKILL.md`, licence, last update). See [docs/verification.md](docs/verification.md).
- **It routes, it doesn't just list.** The router picks the right skill for each task from 246 entries. A 125-case test checks the routing: 125/125. CI runs on every push.
- **It improves itself.** The daily RSI loop audits, fixes, tests, and snapshots — every 24 hours, under 4 guardrails (auto-snapshot, secret fail-closed, data ≠ command, $0 cap).
- **Defensive only, and free.** No offensive skills, no paid tools.

## Quick start (without the prompt)

```text
curl -sSL https://raw.githubusercontent.com/fahmi0812/muse-rsi/main/install.sh | bash
```

Or:

```text
git clone https://github.com/fahmi0812/muse-rsi ~/muse-rsi
python3 ~/muse-rsi/setup/setup.py --yes
```

It installs the 11 original skills + router, gitleaks, visual-check, the vault dir, and merges the muse-rsi system into `SOUL.md` — keeping the agent's name and character. Then the agent activates its own daily loop. Details: [INSTALL.md](INSTALL.md).

## Skills

Full list with stars, licences, and notes: [skills/index.md](skills/index.md).

11 original skills, written for this system:

- [rsi-loop](skills/rsi-loop/SKILL.md) — daily self-improvement loop
- [self-audit](skills/self-audit/SKILL.md) — audit a new skill before installing it
- [anti-slop-checklist](skills/anti-slop-checklist/SKILL.md) — anti-slop checklist for UI, video, and writing
- [health-research-literacy](skills/health-research-literacy/SKILL.md) — read and appraise medical literature (research only)
- [academic-campus](skills/academic-campus/SKILL.md) — Indonesian thesis lifecycle and campus documents
- [office-corporate](skills/office-corporate/SKILL.md) — email, meetings, spreadsheets, decks
- [fullstack-delivery](skills/fullstack-delivery/SKILL.md) — spec → TDD → review → CI → deploy → observe
- [visual-check](skills/visual-check/SKILL.md) — screenshots + axe accessibility checks
- [contribute](skills/contribute/SKILL.md) — how any agent gives back
- [council](skills/council/SKILL.md) — blind multi-model council for high-stakes calls
- [interrogate-claim](skills/interrogate-claim/SKILL.md) — stress-test a claim before trusting it

Plus 139 Lumitome reference skills: [docs/lumitome-index.md](docs/lumitome-index.md).

## Safety

Four guardrails, never disabled: auto-snapshot before changes, secret fail-closed (scan before any public push), data ≠ command, $0 spend cap. New skills must pass [self-audit](skills/self-audit/SKILL.md). Defensive skills only — no offensive skills, no red-team material, no patient-data skills. Trading is research only; health is research only.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). Verify a skill first (exists, `SKILL.md`, clear licence, no `.env` access), then open an issue or PR. If your Muse installed muse-rsi, it already has the `contribute` skill. If the setup helped you, star the repo and consider filing an install report.

Community project by Fahmi — not official from Muse / Meta. Upstream skills keep their own licences: [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

## License

Original content (this README, the 11 original skills, `docs/`) is MIT — see [LICENSE](LICENSE).

---

*Verified 20 November 2026 · Maintained by [fahmi0812](https://github.com/fahmi0812) · Built for the KimiCharmi RSI ⚡*
