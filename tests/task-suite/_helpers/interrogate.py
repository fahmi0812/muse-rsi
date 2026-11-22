#!/usr/bin/env python3
"""Interogasi klaim — prosedur skill interrogate-claim, langkah 1-2.

Bukan model: ini prosedur deterministik yang dipakai solver referensi
di task suite. Cara pakai:
  interrogate.py <claim.txt> <evidence_dir> <verdict.json>
Aturan verdict (Bab 4.8: bukti harus bisa dibuka):
  - tidak ada file bukti            -> unproven
  - bukti memuat angka klaim (N/D)  -> supported
  - bukti memuat N'/D dengan N'!=N  -> contradicted
  - selain itu                      -> unproven
"""
import json
import re
import sys
from pathlib import Path

claim_path, evidence_dir, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
claim = next((ln.strip() for ln in Path(claim_path).read_text(encoding="utf-8").splitlines() if ln.strip()), "")
files = sorted(p for p in Path(evidence_dir).iterdir() if p.is_file() and p.name != ".keep")
texts = {p.name: p.read_text(encoding="utf-8", errors="replace") for p in files}
m = re.search(r"(\d+)\s*/\s*(\d+)", claim)
verdict, reason = "unproven", "tidak ada bukti yang bisa dibuka"
if not files:
    verdict, reason = "unproven", "tidak ada file bukti"
elif m:
    want_num, want_den = int(m.group(1)), int(m.group(2))
    found = []
    for name, text in texts.items():
        for a, b in re.findall(r"(\d+)\s*/\s*(\d+)\s+passed", text):
            found.append((name, int(a), int(b)))
    if any(a == want_num and b == want_den for _, a, b in found):
        verdict, reason = "supported", f"bukti cocok: {want_num}/{want_den} passed"
    elif any(b == want_den and a != want_num for _, a, b in found):
        bad = next((f"{a}/{b} di {n}" for n, a, b in found if b == want_den and a != want_num), "")
        verdict, reason = "contradicted", f"bukti melawan klaim: {bad}"
    else:
        verdict, reason = "unproven", "bukti tidak menyebut angka klaim"
Path(out_path).write_text(json.dumps(
    {"claim": claim, "evidence_files": [p.name for p in files],
     "verdict": verdict, "reason": reason},
    indent=2, ensure_ascii=False), encoding="utf-8")
print(f"{verdict}: {reason}")
