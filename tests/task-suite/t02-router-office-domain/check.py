import json, sys
workdir, taskdir = sys.argv[1], sys.argv[2]
d = json.load(open(f"{workdir}/route.json", encoding="utf-8"))
names = [r["name"] for r in d.get("results", [])]
top_domain = d["results"][0]["domain"] if d.get("results") else None
fails = []
if top_domain != "Office & Corporate":
    fails.append(f"top-1 domain = {top_domain}")
if "office-corporate" not in names:
    fails.append("office-corporate tidak ada di top-3")
if fails:
    print("FAIL: " + "; ".join(fails)); sys.exit(1)
print("PASS: top-1 domain Office & Corporate, office-corporate di top-3")
