#!/usr/bin/env python3
"""run_pass3.py — runner pass^3 untuk K1 (Bab 5.2, G3).

Menjalankan tugas-tugas BERMODEL dari task suite sebanyak k kali
(default k=3) dan melaporkan berapa tugas yang lolos di SEMUA k run
(pass^k). K1 = tugas lolos k/k dibagi tugas bermodel yang dijalankan.

LARANGAN EKSPLISIT (Bab 7, M-04): pass^k TIDAK BOLEH dipakai untuk
tugas deterministik — router (route.py) deterministik, jadi pass^k
== pass^1 dan tidak membuktikan konsistensi apa pun. Runner ini
MENOLAK tugas dengan model_involved=false: `--only` pada tugas
deterministik keluar dengan exit 2 dan pesan penolakan. Tidak ada
flag untuk memaksa; jangan tambahkan satu.

Tugas deterministik diukur dengan metriknya sendiri: router dengan
top-1 ketat (eval_routing.py --strict, C1), tool visual-check dan
prosedur rsi-loop dengan task suite sekali jalan (C3).

Usage:
  python3 scripts/run_pass3.py [--k N] [--only ID]
  python3 scripts/run_pass3.py --k 3 --only t03-tdd-heldout
Exit 0 iff semua tugas terpilih lolos di semua k run, 1 bila ada
yang gagal/flaky, 2 bila tugas yang diminta bukan tugas bermodel.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
SUITE = REPO / "tests" / "task-suite"
RUNNER = HERE / "run_task_suite.py"

RESULTS_RE = re.compile(r"^results: (.+)$", re.M)


def load_model_tasks():
    tasks = []
    for task_yaml in sorted(SUITE.glob("t*/task.yaml")):
        with open(task_yaml, encoding="utf-8") as fh:
            t = yaml.safe_load(fh)
        tasks.append(t)
    return tasks


def run_once(task_id):
    """Satu run task suite --only ID; kembalikan True bila lolos."""
    proc = subprocess.run(
        [sys.executable, str(RUNNER), "--only", task_id],
        capture_output=True, text=True, encoding="utf-8")
    m = RESULTS_RE.search(proc.stdout)
    if not m:
        print(f"  run {task_id}: tidak bisa parse output runner (exit {proc.returncode})")
        print(proc.stdout[-1500:])
        print(proc.stderr[-1500:], file=sys.stderr)
        return None
    summary = json.loads(pathlib.Path(m.group(1)).read_text(encoding="utf-8"))
    row = summary["results"][0]
    return bool(row["passed"])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--k", type=int, default=3, help="jumlah pengulangan (default 3)")
    ap.add_argument("--only", default=None, help="satu task id bermodel")
    args = ap.parse_args()
    if args.k < 1:
        ap.error("--k must be >= 1")
    tasks = load_model_tasks()
    by_id = {t["id"]: t for t in tasks}
    if args.only:
        if args.only not in by_id:
            print(f"task id tidak dikenal: {args.only}")
            return 2
        if not by_id[args.only].get("model_involved"):
            t = by_id[args.only]
            print(f"DITOLAK: {args.only} ({t['skill']}) adalah tugas DETERMINISTIK "
                  f"(model_involved=false).")
            print("pass^k tidak bermakna untuk tugas deterministik: route.py / tool "
                  "yang sama selalu memberi hasil yang sama, jadi pass^k == pass^1.")
            print("Ukur tugas ini dengan metriknya sendiri: router -> top-1 ketat "
                  "(eval_routing.py --strict, C1); prosedur/tool -> task suite sekali jalan (C3).")
            return 2
        selected = [by_id[args.only]]
    else:
        selected = [t for t in tasks if t.get("model_involved")]
    n_determ = sum(1 for t in tasks if not t.get("model_involved"))
    print(f"pass^{args.k} atas {len(selected)} tugas bermodel "
          f"(suite berisi {len(tasks)} tugas; {n_determ} deterministik tidak pernah masuk pass^k)")
    per_task = {}
    for t in selected:
        runs = []
        for i in range(1, args.k + 1):
            ok = run_once(t["id"])
            if ok is None:
                return 2
            runs.append(ok)
            print(f"  {t['id']}: run {i}/{args.k} {'PASS' if ok else 'FAIL'}")
        per_task[t["id"]] = runs
        print(f"  {t['id']}: {''.join('P' if r else 'F' for r in runs)}")
    n_pass_k = sum(1 for runs in per_task.values() if all(runs))
    total = len(per_task)
    pct = 100.0 * n_pass_k / total if total else 0.0
    # Persist for the scorecard (K1): scripts/scorecard.py reads this
    # file. Baseline is procedural (reference solver), not a model
    # score — see tests/task-suite/README.md.
    results_dir = pathlib.Path(__file__).resolve().parent.parent / 'tests' / 'task-suite' / 'results'
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / 'pass3-latest.json').write_text(json.dumps(
        {'k': args.k, 'passed': n_pass_k, 'total': total, 'pct': pct,
         'per_task': {tid: [bool(x) for x in runs] for tid, runs in per_task.items()}},
        indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\nK1 pass^{args.k}: {n_pass_k}/{total} tugas lolos semua {args.k} run ({pct:.1f}%)  [target G3 >=95%]")
    flaky = {tid: runs for tid, runs in per_task.items() if not all(runs)}
    if flaky:
        print(f"tugas gagal/flaky ({len(flaky)}):")
        for tid, runs in sorted(flaky.items()):
            print(f"  {''.join('P' if r else 'F' for r in runs)}  {tid}")
        return 1
    print(f"ALL {total} MODEL TASKS PASSED ALL {args.k} RUNS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
