import json, sys
workdir, taskdir = sys.argv[1], sys.argv[2]
try:
    v = json.load(open(f"{workdir}/verdict.json", encoding="utf-8"))
    ev = open(f"{workdir}/evidence/eval.log", encoding="utf-8").read()
except FileNotFoundError as e:
    print(f"FAIL: file hilang: {e}"); sys.exit(1)
fails = []
if v.get("verdict") != "contradicted":
    fails.append(f"verdict = {v.get('verdict')}, harus contradicted")
if "118/125" not in ev:
    fails.append("checker tidak menemukan 118/125 di bukti")
if fails:
    print("FAIL: " + "; ".join(fails)); sys.exit(1)
print("PASS: kontradiksi tertangkap — klaim 125/125 vs bukti 118/125")
