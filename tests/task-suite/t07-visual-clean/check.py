import json, os, sys
workdir, taskdir = sys.argv[1], sys.argv[2]
rep_path = os.path.join(workdir, "out", "clean-report.json")
if not os.path.exists(rep_path):
    print("FAIL: clean-report.json tidak ada"); sys.exit(1)
r = json.load(open(rep_path, encoding="utf-8"))
fails = []
if r.get("errors"):
    fails.append(f"console errors: {r['errors']}")
if r.get("failedRequests"):
    fails.append(f"failed requests: {r['failedRequests']}")
for w, o in r.get("overflow", {}).items():
    if o.get("hOverflow"):
        fails.append(f"overflow di lebar {w}")
if r.get("a11y", {}).get("violations", 99) != 0:
    fails.append(f"a11y violations: {r['a11y']['violations']}")
if r.get("a11y", {}).get("dark", {}).get("violations", 99) != 0:
    fails.append(f"a11y dark violations: {r['a11y']['dark']['violations']}")
for png in ("clean-360.png", "clean-768.png", "clean-1280.png", "clean-1280-dark.png"):
    if not os.path.exists(os.path.join(workdir, "out", png)):
        fails.append(f"screenshot hilang: {png}")
if fails:
    print("FAIL: " + "; ".join(fails)); sys.exit(1)
print("PASS: halaman bersih — 0 error, 0 overflow, 0 a11y (terang+gelap)")
