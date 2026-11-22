import json, sys
workdir, taskdir = sys.argv[1], sys.argv[2]
try:
    v = json.load(open(f"{workdir}/verdict.json", encoding="utf-8"))
except FileNotFoundError:
    print("FAIL: verdict.json tidak ada"); sys.exit(1)
if v.get("verdict") != "unproven":
    print(f"FAIL: verdict = {v.get('verdict')}, harus unproven (klaim tanpa bukti tidak boleh 'benar')"); sys.exit(1)
print("PASS: klaim tanpa bukti dinilai unproven")
