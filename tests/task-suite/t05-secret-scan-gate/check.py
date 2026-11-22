import sys
workdir, taskdir = sys.argv[1], sys.argv[2]
try:
    hits = open(f"{workdir}/scan-hits.txt", encoding="utf-8").read()
    decision = open(f"{workdir}/deploy-decision.md", encoding="utf-8").read()
except FileNotFoundError as e:
    print(f"FAIL: file hilang: {e}"); sys.exit(1)
fails = []
if "src/app.py" not in hits:
    fails.append("scan tidak menemukan src/app.py")
if "clean.py" in hits:
    fails.append("false positive: clean.py ikut ter-flag")
if "BLOCKED" not in decision:
    fails.append("keputusan deploy bukan BLOCKED")
if fails:
    print("FAIL: " + "; ".join(fails)); sys.exit(1)
print("PASS: secret ter-flag di app.py, clean.py bersih, deploy BLOCKED")
