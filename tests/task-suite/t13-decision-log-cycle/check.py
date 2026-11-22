import sys
workdir, taskdir = sys.argv[1], sys.argv[2]
try:
    tsv = open(f"{workdir}/decision.tsv", encoding="utf-8").read()
except FileNotFoundError:
    print("FAIL: decision.tsv tidak ada"); sys.exit(1)
fails = []
if "t13-decision-log-001" not in tsv:
    fails.append("run_id tidak tercatat")
if "empty" not in tsv:
    fails.append("outcome empty tidak tercatat")
if fails:
    print("FAIL: " + "; ".join(fails)); sys.exit(1)
print("PASS: baris cycle tercatat (run_id + outcome empty)")
