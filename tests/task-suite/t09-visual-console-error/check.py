import json, os, sys
workdir, taskdir = sys.argv[1], sys.argv[2]
rep_path = os.path.join(workdir, "out", "err-report.json")
if not os.path.exists(rep_path):
    print("FAIL: err-report.json tidak ada"); sys.exit(1)
r = json.load(open(rep_path, encoding="utf-8"))
errs = r.get("errors", [])
if not errs:
    print("FAIL: console error TIDAK tercatat"); sys.exit(1)
if not any("kesalahan uji konsol" in e for e in errs):
    print(f"FAIL: error tercatat tapi bukan yang diharapkan: {errs}"); sys.exit(1)
print(f"PASS: console error terdeteksi ({len(errs)} entri)")
