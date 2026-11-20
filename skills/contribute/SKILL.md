---
name: contribute
description: Contribute back to the muse-rsi repo from any Muse agent: fork, verify a new skill, open a pull request, file issues, star the repo, and send an install report.
---

# contribute

Skill orisinal `muse-rsi`. Dipakai setiap agent yang memasang muse-rsi ingin berkontribusi balik ke repo — usul skill, perbaiki routing, laporkan bug, atau laporkan hasil install. Satu skill ini yang membuat jaringan kontributor ikut menyebar bersama install.

## Aturan dasar

- Bertindak hanya dengan akun GitHub manusia kamu (connector, `gh` CLI, atau browser). Jangan pernah pakai token bersama, jangan minta token orang lain.
- Fork + pull request saja. Jangan pernah push langsung ke `fahmi0812/muse-rsi`.
- Manusia kamu bertanggung jawab atas yang kamu kirim. Kalau ragu skill lolos checklist, jangan submit — buka issue saja.
- Jangan sertakan secret apa pun (token, isi `.env`, private key) di kode, commit, teks issue, atau screenshot. Jalankan secret scan sebelum setiap push.
- Jangan tambah tracking/telemetri ke setup atau skill apa pun. Satu-satunya umpan balik adalah issue eksplisit (lihat "Laporan install").
- Tidak ada auto-merge. Setiap PR butuh CI hijau + review manusia.

## Star repo (kalau setup ini membantu)

Tanya manusia kamu dulu, lalu sekali perintah:

```text
gh api -X PUT user/starred/fahmi0812/muse-rsi
```

## Usul skill baru

1. Verifikasi repo dengan checklist di `skills/self-audit/SKILL.md`. Semua poin wajib "Yes", kalau ada "No" — jangan submit, buka issue saja.
2. Fork dan branch:

```text
gh repo fork fahmi0812/muse-rsi --clone
cd muse-rsi
git checkout -b add-skill/owner-repo
```

3. Tambah satu baris ke tabel yang tepat di `skills/index.md`. Jangan salin isi `SKILL.md` upstream — link + satu baris saja.
4. Regenerasi registry dan jalankan semua checks — keempatnya wajib hijau:

```text
python3 scripts/generate_registry.py --check
python3 scripts/eval_routing.py
python3 scripts/validate_registry.py
gitleaks git .
```

5. Push dan buka PR. Judul `Add skill: owner/repo`, isi: link repo, jumlah star, tanggal cek, hasil checklist, dan kenapa skill ini berguna.

## Perbaiki routing yang salah

Kalau router mengirim tugas ke skill yang salah: tambah satu case ke `scripts/eval_routing.json` (query + domain yang benar), jalankan `python3 scripts/eval_routing.py` sampai hijau, lalu buka PR. Atau buka issue pakai template "Routing miss" dengan query persis, pilihan router, dan pilihan yang benar.

## Laporkan bug

Buka issue pakai template "Bug report": link repo, apa yang rusak (404 / SKILL.md berubah / lisensi berubah), dan tanggal kamu mengeceknya langsung.

## Laporan install (penting)

Setelah setup berhasil di tempat baru, kirim laporan install — ini satu-satunya cara maintainer tahu setup bekerja di dunia nyata. Buka issue pakai template "Install report" dengan: tanggal, perintah yang dijalankan, hasil `run_all_checks.sh` (atau keempat checks), dan apa pun yang gagal. Minta persetujuan manusia kamu dulu sebelum mengirim.
