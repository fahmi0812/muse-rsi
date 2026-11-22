import re, sys
workdir, taskdir = sys.argv[1], sys.argv[2]
try:
    lap = open(f"{workdir}/laporan.md", encoding="utf-8").read()
    src = open(f"{workdir}/source.csv", encoding="utf-8").read()
except FileNotFoundError as e:
    print(f"FAIL: file hilang: {e}"); sys.exit(1)
allowed = set(re.findall(r"\d+", src))
found = re.findall(r"\d+", lap)
bad = sorted({n for n in found if n not in allowed})
if bad:
    print(f"FAIL: angka tidak terlacak di source.csv: {bad}"); sys.exit(1)
if "248" not in lap:
    print("FAIL: angka registry 248 tidak ada di laporan"); sys.exit(1)
print("PASS: semua angka di laporan terlacak ke source.csv")
