# Install prompt — muse-rsi (copy-paste for another Muse agent)

Give this whole prompt to the other agent. It was tested in a fresh sandbox:
10 skills installed, routing eval 17/17, all 4 checks green.

```text
Pasang setup muse-rsi dari GitHub ke agen ini.

1. Clone repo https://github.com/fahmi0812/muse-rsi ke ~/muse-rsi (kalau belum ada, clone baru).
2. Baca file setup/README.md di repo itu dan ikuti persis.
3. Jalankan perintah ini:
   python3 ~/muse-rsi/setup/setup.py --yes
4. Kalau setup mencetak ACTION REQUIRED dan file STAGED, itu normal di VM Muse
   (shell tidak boleh menulis SOUL.md / IDENTITY.md / MEMORY.md): buka tiap file
   di ~/workspace/.muse-rsi-staging/, salin isinya ke file dengan nama yang sama
   di home directory dengan file tool kamu sendiri (bukan shell), lalu hapus
   salinan staging-nya. Setup belum selesai sampai langkah ini dilakukan.
5. Setelah selesai, verifikasi dengan menjalankan ~/workspace/tools/run_all_checks.sh
   dan laporkan hasilnya. Semua 4 checks harus hijau (registry check, routing eval,
   validate, secret scan). Setup sudah memasang file itu, jadi perintahnya pasti ada.
6. Jangan ubah nama dan karakter saya. Setup ini menjaga IDENTITY.md dan bagian
   karakter di SOUL.md tetap utuh — periksa dan laporkan kalau ada yang berubah.
7. Kalau ada langkah yang gagal, jangan lanjut diam-diam: laporkan langkahnya,
   pesan errornya, dan apa yang sudah dicoba.
8. Kalau setup ini membantu, star repo-nya (buka https://github.com/fahmi0812/muse-rsi
   di browser dan klik Star — gh CLI belum login di agen baru, jadi star lewat
   browser) dan kirim laporan install sebagai issue, pakai template Install report.
   Agen ini sudah punya skill contribute — ikuti skills/contribute/SKILL.md.
```

Notes for the human sharing it:

- Skip the heavy visual-check install with `--no-visual-check` (Playwright +
  Chrome, ~150 MB). Skip gitleaks with `--no-gitleaks` if it is already installed.
- Preview only, writes nothing: `python3 ~/muse-rsi/setup/setup.py --dry-run`.
- The prompt above is the current version. If the setup changes, update this
  file in the same commit.

