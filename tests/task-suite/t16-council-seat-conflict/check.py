import json, sys
workdir, taskdir = sys.argv[1], sys.argv[2]
try:
    d = json.load(open(f"{workdir}/council-decision.json", encoding="utf-8"))
except FileNotFoundError:
    print("FAIL: council-decision.json tidak ada"); sys.exit(1)
fails = []
if d.get("abstentions") != ["anthropic"]:
    fails.append(f"abstentions = {d.get('abstentions')}, harus ['anthropic']")
if d.get("eligible_count") != 2:
    fails.append(f"eligible_count = {d.get('eligible_count')}, harus 2")
if d.get("quorum") != 2 or d.get("quorum_met") is not True:
    fails.append(f"quorum = {d.get('quorum')}, quorum_met = {d.get('quorum_met')}")
if fails:
    print("FAIL: " + "; ".join(fails)); sys.exit(1)
print("PASS: kursi anthropic abstain, 2 kursi tersisa memenuhi kuorum 2")
