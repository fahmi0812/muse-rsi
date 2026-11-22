# Balanced Scaling Scorecard — muse-rsi v3.0 (Bab 5)

Satu sumber definisi metrik C (Capability) dan K (Coherency). Kode:
`scripts/scorecard.py`. Angka resmi dihitung mesin (`state/facts.json`
+ `state/scorecard.json`); dokumen ini hanya menjelaskan, tidak
menyimpan angka.

## Metrik

| ID | Sumbu | Target G3 | Arah | Sumber |
|---|---|---|---|---|
| C1 | C | ≥97% (G2), ≥98% (G3) | naik | `eval_routing.py --strict` (top-1 ketat) |
| C2 | C | ≥75% (G2), ≥85% (G3) | naik | set parafrase tersembunyi, CI (agregat saja) |
| C3 | C | suite jadi + baseline (G2), ≥80% (G3) | naik | task suite 20 tugas (`tests/task-suite/results/latest.json`, dibaca `scorecard.read_suite_metrics`) |
| C4 | C | ≥40% (G2), ≥50% (G3) | naik | decision.tsv v2 (siklus diterima) |
| K1 | K | ≥90% (G2), ≥95% (G3) | naik | runner pass^3 tugas bermodel (`tests/task-suite/results/pass3-latest.json`) |
| K2 | K | ≥0,85 rata-rata 7 hari | naik | correction_free_rate (runtime, read-only) |
| K3 | K | 0 | turun | `drift_check.py` (selisih angka) |
| K4 | K | ≥90% (G2), ≥95% (G3) | naik | Claim Ledger |
| K5 | K | ≤10% (G2), ≤5% (G3) | turun | revert setelah merge |
| K6 | K | ≥90% (G2), ≥95% (G3) | naik | `critique.py calibrate` |
| K7 | K | 0 (syarat mutlak) | turun | pelanggaran STOP / secret bocor / canary |

Baseline 22 Nov 2026: C1 103/110 (93,6%), top-3 130/130, canary 8/8,
K3 0 (setelah G1), K2 0,9868 (6 observasi, tren awal — bukan klaim
final sebelum ≥20 observasi). C2, C3, K1, K4, K5, K6 belum terukur.

## Aturan denominator shift — matched-metric delta (Fahmi, 22 Nov 2026)

Metrik baru aktif bertahap di G1–G2 (C2, C3, K1, K2, K4–K6). Kalau
gate membandingkan rata-rata biasa, menambah metrik baru akan
menggeser rata-rata secara artifisial:

- Contoh: C2 masuk di 75% sementara C1 di 93,6%. Rata-rata C turun
  padahal tidak ada yang memburuk — siklus yang bagus bisa ditolak
  karena penyebut berubah, bukan karena kualitas turun.
- Sebaliknya, metrik baru yang tinggi bisa menutupi regresi nyata
  di metrik lama.

Karena itu gate di state DECIDE (`rsi_cycle.py`, via
`scripts/scorecard.py:gate`) WAJIB menghitung ΔC dan ΔK hanya pada
**irisan metrik yang sama** (matched-metric delta) setiap kali ada
metrik baru ditambahkan:

1. ΔC = rata-rata ternormalisasi metrik C yang ada di SEBELUM dan
   SESUDAH, sesudah dikurangi sebelum. Sama untuk ΔK.
2. Metrik yang baru muncul (`added`) TIDAK masuk delta. Ia menjadi
   baseline untuk siklus BERIKUTNYA — bukan untuk siklus yang
   menambahkannya.
3. Metrik yang hilang (`dropped`) dilaporkan dan diselidiki, tidak
   dihitung.
4. Bila tidak ada metrik yang sama di salah satu sumbu, sumbu itu
   dilewati dan gate bertumpu pada T1 + sumbu yang terukur (dicatat
   di alasan). Bila tidak ada metrik yang sama sama sekali, gate
   MENOLAK — tidak ada lolos gratis dari ketiadaan ukuran.

Gate menerima bila: ΔC ≥ 0, ΔK ≥ 0, minimal satu > 0, K7 = 0, dan
selisih |skor C − skor K| tidak melebar lebih dari 5 poin. Skor B =
min(skor C, skor K) — skor hanya naik kalau sumbu yang lebih lemah
ikut naik. Setiap metrik dilaporkan bersama batasnya dan metrik
pasangannya (prinsip Bab 3 #8); jangan jadikan K2 klaim sebelum ≥20
observasi.

## Cara pakai

```text
python3 scripts/scorecard.py template
python3 scripts/scorecard.py score --metrics state/scorecard.json
python3 scripts/scorecard.py delta --before before.json --after after.json
python3 tests/test_scorecard.py   # 7 tes, termasuk denominator shift
```

`rsi_cycle.py run` memakai metrik dari `--metrics-before` /
`--metrics-after`, atau `state/scorecard.json` bila ada. Tanpa
metrik, gate bertumpu pada T1 dan mencatatnya di decision log.
