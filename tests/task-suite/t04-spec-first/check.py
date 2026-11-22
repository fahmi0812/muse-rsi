import sys
workdir, taskdir = sys.argv[1], sys.argv[2]
try:
    spec = open(f"{workdir}/SPEC.md", encoding="utf-8").read()
except FileNotFoundError:
    print("FAIL: SPEC.md tidak ada"); sys.exit(1)
need = ["Kontrak API", "Model data", "Verifikasi",
        "/auth/reset-request", "/auth/reset-confirm", "reset_token"]
missing = [n for n in need if n not in spec]
if missing:
    print("FAIL: SPEC.md kehilangan: " + ", ".join(missing)); sys.exit(1)
print("PASS: SPEC.md berisi kontrak API + model data + verifikasi")
