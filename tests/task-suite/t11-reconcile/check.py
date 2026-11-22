import sys
workdir, taskdir = sys.argv[1], sys.argv[2]
try:
    rec = open(f"{workdir}/reconciliation.md", encoding="utf-8").read()
except FileNotFoundError:
    print("FAIL: reconciliation.md tidak ada"); sys.exit(1)
need = ["400000", "395000", "5000", "A3"]
missing = [n for n in need if n not in rec]
if missing:
    print("FAIL: rekonsiliasi kehilangan: " + ", ".join(missing)); sys.exit(1)
print("PASS: total 400000 vs 395000, selisih 5000, baris A3 ter-flag")
