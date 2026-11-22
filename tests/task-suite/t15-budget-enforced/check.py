import json, sys
workdir, taskdir = sys.argv[1], sys.argv[2]
try:
    s4 = open(f"{workdir}/spend4.exit", encoding="utf-8").read().strip()
    ck = open(f"{workdir}/check.exit", encoding="utf-8").read().strip()
    state = json.load(open(f"{workdir}/budget.json", encoding="utf-8"))
except FileNotFoundError as e:
    print(f"FAIL: file hilang: {e}"); sys.exit(1)
fails = []
if s4 != "1":
    fails.append(f"spend ke-4 exit {s4}, harus 1 (ditolak)")
if ck != "1":
    fails.append(f"check exit {ck}, harus 1 (exhausted)")
if state.get("spent", {}).get("steps") != 4:
    fails.append(f"spent.steps = {state.get('spent', {}).get('steps')}, harus 4")
if state.get("status") != "exhausted":
    fails.append(f"status = {state.get('status')}, harus exhausted")
if fails:
    print("FAIL: " + "; ".join(fails)); sys.exit(1)
print("PASS: budget 3 langkah ditegakkan — spend ke-4 ditolak, status exhausted")
