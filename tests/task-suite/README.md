# Task suite — C3 (Bab 5.1, G3)

20 tugas yang bisa dieksekusi, masing-masing dengan prompt, skill yang
diharapkan, dan checker deterministik (exit 0 = lolos). Target G3: ≥80%.

## Cara jalan

```text
python3 scripts/run_task_suite.py            # semua 20 tugas
python3 scripts/run_task_suite.py --list     # daftar tugas
python3 scripts/run_task_suite.py --only t03-tdd-heldout
python3 scripts/run_pass3.py                 # pass^3, tugas bermodel saja
python3 scripts/run_pass3.py --only t03-tdd-heldout
```

Hasil JSON: `tests/task-suite/results/<run_id>.json` (+ `latest.json`).
Workdir tiap run: `tests/task-suite/.runs/<run_id>/<task_id>/` (fixture
disalin ke sana; bukti run tersimpan).

## Struktur tugas

```text
tests/task-suite/<id>/
  task.yaml        # id, skill, model_involved, prompt, expected_*, solve, check
  check.py         # checker deterministik: argv = <workdir> <task_dir>
  fixture/         # disalin ke workdir sebelum solve
  hidden/          # HANYA untuk checker (tidak disalin) — tes held-out
```

Skema `task.yaml`: `setup` (opsional) dan `solve` adalah skrip shell
yang dijalankan di workdir dengan env `REPO`, `WORKDIR`, `TASK_DIR`,
`TASK_ID`, `TASK_PROMPT`, `VISUAL_CHECK_DIR`. `solve` yang exit != 0
membuat tugas FAIL sebelum checker jalan.

## Kejujuran baseline

`Solve` di tiap tugas adalah **solver referensi deterministik** yang
mengikuti prosedur skill — bukan model. Jadi skor suite ini mengukur
apakah prosedur skill bisa dieksekusi ujung-ke-ujung, BUKAN kemampuan
model. Untuk tugas bermodel (`model_involved: true`, 12 tugas), skor
yang berarti adalah `run_pass3.py` dengan solver berbasis model.
Baseline di bawah dicatat jujur apa adanya; checker TIDAK dilonggarkan
agar lolos.

Anti self-grading (M-02): checker yang butuh jawaban tersembunyi
memakai `hidden/` yang tidak pernah disalin ke workdir (lihat
`t03-tdd-heldout`: implementasi dinilai hidden test, bukan tes publik).

## Sebaran 20 tugas

| skill | tugas | model_involved |
|---|---|---|
| router | t01, t02 | tidak (deterministik) |
| fullstack-delivery | t03–t06 | ya |
| visual-check | t07–t09 | tidak (bagian tool; penilaian screenshot oleh model di luar checker) |
| office-corporate (= "dokumen") | t10–t12 | ya |
| rsi-loop | t13–t15 | tidak (prosedur + tool) |
| council | t16, t17 | ya |
| interrogate-claim | t18–t20 | ya |

Catatan: repo ini tidak punya skill bernama `dokumen`; pekerjaan
dokumen diwakili `office-corporate` (email, rapat, spreadsheet, deck).
`make-fun` sengaja TIDAK masuk — di luar repo ini.

## Larangan pass^k (Bab 7, M-04)

`run_pass3.py` MENOLAK tugas deterministik (router, visual-check tool,
prosedur rsi-loop). pass^k hanya untuk tugas yang melibatkan model.
Router diukur dengan top-1 ketat (`eval_routing.py --strict`, C1).

## Dependensi

- Python 3 + PyYAML (sudah dipakai repo).
- Tugas visual-check butuh tool di `~/workspace/tools/visual-check/`
  (atau `$VISUAL_CHECK_DIR`); bila tidak ada, solve exit 3 dan tugas
  FAIL dengan alasan jelas — bukan pass palsu.
- Tanpa API berbayar, tanpa network, tanpa login.
