import sys
workdir, taskdir = sys.argv[1], sys.argv[2]
try:
    recap = open(f"{workdir}/recap.md", encoding="utf-8").read()
except FileNotFoundError:
    print("FAIL: recap.md tidak ada"); sys.exit(1)
need = ["v3-base", "INSTALL-PROMPT", "sensus model", "Fahmi", "KimiCharmi",
        "23 Nov 2026", "24 Nov 2026", "1 Des 2026"]
missing = [n for n in need if n not in recap]
if missing:
    print("FAIL: recap kehilangan: " + ", ".join(missing)); sys.exit(1)
print("PASS: rekap berisi 3 keputusan + pemilik + tenggat")
