import json, sys
workdir, taskdir = sys.argv[1], sys.argv[2]
d = json.load(open(f"{workdir}/route.json", encoding="utf-8"))
top = d["results"][0]["name"] if d.get("results") else None
if top == "rsi-loop":
    print("PASS: top-1 = rsi-loop")
else:
    print(f"FAIL: top-1 = {top}, expected rsi-loop"); sys.exit(1)
