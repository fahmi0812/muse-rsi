import sys
workdir, taskdir = sys.argv[1], sys.argv[2]
try:
    code = open(f"{workdir}/drift-exit.txt", encoding="utf-8").read().strip()
    out = open(f"{workdir}/drift.txt", encoding="utf-8").read()
except FileNotFoundError as e:
    print(f"FAIL: file hilang: {e}"); sys.exit(1)
if code != "0":
    print(f"FAIL: drift_check exit {code}: {out[-500:]}"); sys.exit(1)
if "DRIFT OK" not in out or "0 mismatches" not in out:
    print(f"FAIL: output drift_check tidak berisi DRIFT OK / 0 mismatches: {out[-500:]}"); sys.exit(1)
print("PASS: drift_check exit 0, 0 mismatches")
