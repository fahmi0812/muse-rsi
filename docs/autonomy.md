# Otonomi maksimal — muse-rsi v3.1

Keputusan Fahmi, 22 Nov 2026: tekan permintaan izin serendah mungkin.
Polanya seperti agen yang me-merge PR-nya sendiri semalaman di balik
verifier: **agen bertindak, me-merge, dan melapor; Fahmi meninjau
sesudahnya** (digest harian, sampling, label `veto`, STOP), bukan
menyetujui sebelumnya.

## Tiga kelas, ditentukan dari diff

`scripts/autonomy_gate.py` membaca diff, bukan klaim agen:

| Kelas gate | Trust Ladder | Contoh | Yang terjadi |
|---|---|---|---|
| AUTO | A2 / A3 | skill, router, registri, docs, tools, template, file root VM | merge begitu CI hijau |
| VETO | A4 | kasus eval baru, canary baru, perbaikan engine/verifier, `MODELS.yaml`, setup, diff lebih besar dari batas per siklus | merge otomatis setelah 24 jam kecuali diberi label `veto` |
| HARD | A5 | trust/limits/critique, protected/veto paths, gate, self-test, `.github/`, SOUL §1–4; hapus/ubah kasus eval, hapus canary, ubah sampel known-bad, hapus file verifier | tidak di-merge otomatis; masuk digest untuk Fahmi |

Aksi di luar repo yang tetap A5: uang atau API berbayar, pesan ke orang
lain, deploy produksi, publish di luar repo sendiri, vault dan kunci API,
hapus permanen.

Aturan gate hanya bisa menambah review, tidak pernah mengurangi: error,
JSON yang tidak terbaca, atau situasi tak dikenal = HARD.

## Alur satu perubahan

1. Siklus (`rsi_cycle.py run`) menerapkan patch, VERIFY dan CRITIQUE hijau,
   DECIDE menerima.
2. COMMIT membuat commit di branch `rsi/<run_id>` (main lokal tidak
   bergerak) dan menulis rencana push di `~/.muse-rsi/outbox/<run_id>.json`.
3. Agen mem-push branch itu (connector `push_files`). Tidak ada permintaan
   merge ke Fahmi.
4. `.github/workflows/auto-merge.yml` membuka PR, menjalankan gate dari
   **main** (SHA-256 di-pin), menunggu check `validate`, lalu me-merge:
   AUTO langsung, VETO setelah veto window. HARD diberi label
   `needs-fahmi`.
5. Patch HARD tidak pernah diterapkan: engine mencatatnya di
   `~/.muse-rsi/escalations.jsonl`, siklus selesai dengan outcome
   `escalated` (bukan merah).

## Kendali Fahmi (semuanya sesudah, bukan sebelum)

- Label PR `veto`, atau komentar berisi "veto" / "stop" → PR tidak di-merge.
- Variabel repo `AUTOMERGE_PAUSED=true` (Settings → Secrets and variables
  → Actions → Variables) → workflow tidak me-merge apa pun.
- STOP (`scripts/stop_cycle.py` atau pesan "STOP muse-rsi") → loop HALT
  dalam satu langkah.
- Revert PR yang sudah ter-merge → siklus berikutnya mencatat demosi:
  kelas itu 7 hari di mode veto window (merge ditunda, tetap tidak bertanya).
- Rem otomatis tanpa manusia: maksimal 10 merge per hari, dan 3 siklus
  merah berturut-turut membuat loop jeda sendiri 24 jam
  (`config/limits.yaml`, blok `autonomy`).

## Kenapa ini tetap aman

- **Loop tidak bisa melonggarkan pagarnya sendiri.** Daftar hard core dan
  veto dibaca dari sisi BASE diff, jadi perubahan tidak bisa mengecilkan
  review-nya sendiri. Gate dan self-test ada di hard core, dan workflow
  me-pin SHA-256 gate: gate yang berubah menghentikan semua auto-merge
  sampai Fahmi me-pin ulang.
- **Verifier tidak bisa dilemahkan diam-diam.** `scripts/verifier_selftest.py`
  berjalan di CI dan di `run_all_checks.sh`: drift_check, gen_facts,
  run_budget, kalibrasi critique, gate, tamper, dan STOP masing-masing
  diberi input yang pasti jelek dan harus menolaknya.
- **Push langsung ke main ketahuan.** `envelope-guard` di `validate.yml`
  membuat main merah bila perubahan HARD masuk tanpa Fahmi atau perubahan
  VETO melewati veto window; PRECHECK siklus berikutnya HALT.
- **Workflow di luar jangkauan loop.** GitHub App tidak bisa menulis
  `.github/workflows/` (403), jadi cara merge tidak bisa diubah loop.

## Langkah sekali untuk Fahmi

1. Terapkan dua workflow (`validate.yml` v3.1 dan `auto-merge.yml`) bila
   belum masuk lewat PR ini.
2. Settings → Actions → General → Workflow permissions: pilih **Read and
   write permissions** dan centang **Allow GitHub Actions to create and
   approve pull requests** (auto-merge membuka PR dengan token workflow).
3. Setelah PR ini di-merge, di VM: jalankan ulang setup supaya SOUL §1
   baru terpasang, lalu hapus `~/.muse-rsi/soul_hash.txt` sekali supaya
   PRECHECK mencatat baseline baru. Tanpa ini PRECHECK HALT karena hash
   SOUL §1–4 berubah.
4. Setiap kali `scripts/autonomy_gate.py` berubah (PR hard core), perbarui
   `GATE_SHA256` di kedua workflow dengan `sha256sum scripts/autonomy_gate.py`.

## Peta bottleneck (laporan Muse 22 Nov) setelah v3.1

| # | Bottleneck | Status v3.1 |
|---|---|---|
| B1 | Pemeriksaan keamanan runtime | Di luar repo. Jalur sah: allowlist untuk repo sendiri di pengaturan runtime bila ada, dan simpan instruksi untuk agen hanya di `setup/INSTALL-PROMPT.md` supaya dokumen biasa tidak terbaca sebagai perintah. Tidak boleh diakali. |
| B2 | Approval card konektor | Di luar repo. Sekarang tinggal 1 kartu per perubahan (push branch `rsi/`); buka PR dan merge dikerjakan workflow. Hilang total hanya bila runtime menyediakan "selalu izinkan" untuk repo ini. |
| B3 | Merge oleh Fahmi | **Hilang** untuk AUTO dan VETO (auto-merge.yml). |
| B4 | Workflow 403 | Tetap, dan sengaja: loop tidak boleh mengubah aturan merge-nya. Hanya saat workflow berubah. |
| B5 | Staging exit 20 | Quirk runtime tetap, tetapi A3 kini otomatis: agen menerapkan file staged lewat file tool tanpa bertanya. |
| B6 | A3 butuh persetujuan | **Hilang** (snapshot + T2 + digest). |
| B7 | A4 hanya usulan | **Menyempit** ke hard core yang melonggarkan; menambah/mengetatkan verifier dan memperbaiki engine = auto setelah 24 jam. |
| B8 | A5 eksternal/berbayar | Tetap. Uang, pesan ke orang lain, deploy produksi, vault, hapus permanen tidak diotomatiskan. |
| B9 | Siklus nyata pertama | Terjawab oleh jadwal; jalur AUTO/VETO/HARD sudah diuji end-to-end di salinan repo. |
| B10 | Promosi trust | **Tidak diperlukan lagi**: otonomi tidak perlu diraih, hanya bisa hilang lewat demosi. |
| B11 | Secret held-out + contract | Tetap manual sekali. |
| B12 | Browser ~1 jam | Tetap (batas runtime). |
| B13 | facts head | Sudah diperbaiki sebelumnya. |
