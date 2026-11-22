#!/usr/bin/env python3
"""run_task_suite.py — runner task suite C3 (Bab 5.1, G3).

Menjalankan 20 tugas di tests/task-suite/: tiap tugas menyiapkan fixture
di workdir segar, menjalankan `solve` (solver referensi deterministik
yang mengikuti prosedur skill — lihat README suite), lalu menjalankan
checker deterministik (exit 0 = lolos). Melaporkan X/20 lolos + per-tugas
dan menulis hasil JSON ke tests/task-suite/results/.

Catatan kejujuran (Bab 5.3, noise): baseline ini mengukur apakah
PROSEDUR skill bisa dieksekusi ujung-ke-ujung dengan solver referensi
deterministik, bukan kemampuan model. Tugas bermodel (model_involved)
nantinya dijalankan dengan solver berbasis model; skornya baru berarti
bila diulang (lihat run_pass3.py). Jangan klaim skor ini sebagai skor
model.

Usage:
  python3 scripts/run_task_suite.py [--list] [--only ID] [--suite DIR]
  python3 scripts/run_task_suite.py --only t03-tdd-heldout
Exit 0 iff semua tugas yang dijalankan lolos, 1 bila ada yang gagal,
2 bila argumen/task id tidak valid.
"""
import argparse
import datetime
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

import yaml

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
DEFAULT_SUITE = REPO / "tests" / "task-suite"
VISUAL_CHECK_DIR = os.environ.get(
    "VISUAL_CHECK_DIR",
    str(pathlib.Path.home() / "workspace" / "tools" / "visual-check"))


def load_tasks(suite):
    tasks = []
    for task_yaml in sorted((suite).glob("t*/task.yaml")):
        with open(task_yaml, encoding="utf-8") as fh:
            t = yaml.safe_load(fh)
        t["_dir"] = task_yaml.parent
        tasks.append(t)
    tasks.sort(key=lambda t: t["id"])
    return tasks


def run_one(task, run_dir, repo):
    """Run one task. Returns a result dict."""
    tid = task["id"]
    workdir = run_dir / tid
    workdir.mkdir(parents=True)
    fixture = task["_dir"] / "fixture"
    if fixture.exists():
        shutil.copytree(fixture, workdir, dirs_exist_ok=True)
    env = dict(os.environ)
    env.update({
        "REPO": str(repo),
        "WORKDIR": str(workdir),
        "TASK_DIR": str(task["_dir"]),
        "TASK_ID": tid,
        "TASK_PROMPT": task.get("prompt", ""),
        "VISUAL_CHECK_DIR": VISUAL_CHECK_DIR,
    })
    started = time.time()
    result = {"id": tid, "skill": task["skill"],
              "model_involved": bool(task.get("model_involved")),
              "title": task.get("title", ""), "passed": False,
              "solve_exit": None, "check_exit": None,
              "duration_s": 0.0, "detail": ""}
    timeout = int(task.get("timeout_s", 60))
    # --- setup (opsional) ---
    for phase, script in (("setup", task.get("setup")), ("solve", task.get("solve"))):
        if not script:
            continue
        try:
            proc = subprocess.run(["bash", "-c", script], cwd=workdir, env=env,
                                  capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            result["detail"] = f"{phase} TIMEOUT>{timeout}s"
            result["duration_s"] = round(time.time() - started, 2)
            return result
        if phase == "setup" and proc.returncode != 0:
            result["detail"] = (f"setup exit {proc.returncode}: "
                                + (proc.stdout + proc.stderr)[-500:])
            result["duration_s"] = round(time.time() - started, 2)
            return result
        if phase == "solve":
            result["solve_exit"] = proc.returncode
            result["solve_tail"] = (proc.stdout + proc.stderr)[-800:]
            if proc.returncode != 0:
                result["detail"] = (f"solve exit {proc.returncode}: "
                                    + (proc.stdout + proc.stderr)[-500:])
                result["duration_s"] = round(time.time() - started, 2)
                return result
    # --- checker deterministik ---
    checker = task["_dir"] / task.get("check", "check.py")
    try:
        proc = subprocess.run(
            [sys.executable, str(checker), str(workdir), str(task["_dir"])],
            capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        result["detail"] = "check TIMEOUT>60s"
        result["duration_s"] = round(time.time() - started, 2)
        return result
    result["check_exit"] = proc.returncode
    result["passed"] = proc.returncode == 0
    result["detail"] = (proc.stdout + proc.stderr).strip()[-800:]
    result["duration_s"] = round(time.time() - started, 2)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list", action="store_true", help="daftar tugas lalu keluar")
    ap.add_argument("--only", default=None, help="jalankan hanya satu task id")
    ap.add_argument("--suite", default=str(DEFAULT_SUITE))
    args = ap.parse_args()
    suite = pathlib.Path(args.suite)
    tasks = load_tasks(suite)
    if not tasks:
        print(f"tidak ada tugas di {suite}")
        return 2
    if args.list:
        for t in tasks:
            flag = "model" if t.get("model_involved") else "determ"
            print(f"{t['id']:32s} {flag:6s} {t['skill']:20s} {t.get('title','')}")
        print(f"{len(tasks)} tugas")
        return 0
    if args.only:
        tasks = [t for t in tasks if t["id"] == args.only]
        if not tasks:
            print(f"task id tidak dikenal: {args.only}")
            return 2
    # run_id unik per proses: pass^3 menjalankan suite berkali-kali dalam
    # satu detik yang sama — timestamp saja bertabrakan (FileExistsError).
    run_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + f"-{os.getpid()}"
    run_dir = suite / ".runs" / run_id
    run_dir.mkdir(parents=True)
    results_dir = suite / "results"
    results_dir.mkdir(exist_ok=True)
    results = []
    for t in tasks:
        r = run_one(t, run_dir, REPO)
        results.append(r)
        mark = "PASS" if r["passed"] else "FAIL"
        print(f"[{mark}] {r['id']:32s} {r['skill']:20s} {r['duration_s']:6.2f}s  {r['detail'].splitlines()[0] if r['detail'] else ''}")
    n_pass = sum(1 for r in results if r["passed"])
    total = len(results)
    pct = 100.0 * n_pass / total if total else 0.0
    summary = {"run_id": run_id,
               "run_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "passed": n_pass, "total": total, "pct": round(pct, 1),
               "results": results}
    out_path = results_dir / f"{run_id}.json"
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (results_dir / "latest.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nC3 task suite: {n_pass}/{total} passed ({pct:.1f}%)  [target G3 >=80%]")
    print(f"workdirs: {run_dir}")
    print(f"results: {out_path}")
    return 0 if n_pass == total else 1


if __name__ == "__main__":
    sys.exit(main())
