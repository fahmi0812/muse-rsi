import json, os, sys
workdir, taskdir = sys.argv[1], sys.argv[2]
rep_path = os.path.join(workdir, "out", "overflow-report.json")
if not os.path.exists(rep_path):
    print("FAIL: overflow-report.json tidak ada"); sys.exit(1)
r = json.load(open(rep_path, encoding="utf-8"))
verdict = open(os.path.join(workdir, "verdict.txt"), encoding="utf-8").read() if os.path.exists(os.path.join(workdir, "verdict.txt")) else ""
fails = []
if not r.get("overflow", {}).get("360", {}).get("hOverflow", False):
    fails.append("overflow 360px TIDAK terdeteksi (tool gagal menangkap cacat nyata)")
if "overflow" not in verdict.lower():
    fails.append("verdict.txt tidak menyebut overflow")
if fails:
    print("FAIL: " + "; ".join(fails)); sys.exit(1)
print("PASS: overflow 360px terdeteksi dan verdict mencatatnya")
