import sys
workdir, taskdir = sys.argv[1], sys.argv[2]
try:
    plan = open(f"{workdir}/deploy-plan.md", encoding="utf-8").read().lower()
except FileNotFoundError:
    print("FAIL: deploy-plan.md tidak ada"); sys.exit(1)
need = ["staging", "produksi", "rollback", "tes lolos", "monitor"]
missing = [n for n in need if n not in plan]
if missing:
    print("FAIL: deploy-plan.md kehilangan: " + ", ".join(missing)); sys.exit(1)
print("PASS: deploy plan berisi staging + produksi + rollback + tes lolos + monitor")
