import os, subprocess, sys
workdir, taskdir = sys.argv[1], sys.argv[2]
fails = []
if not os.path.exists(os.path.join(workdir, "src", "calc.py")):
    fails.append("src/calc.py tidak ada")
if not os.path.exists(os.path.join(workdir, "tdd-green.txt")):
    fails.append("tdd-green.txt tidak ada (TDD hijau tidak tercatat)")
proc = subprocess.run([sys.executable, os.path.join(taskdir, "hidden", "hidden_test.py"), workdir],
                      capture_output=True, text=True, timeout=60)
if proc.returncode != 0:
    fails.append("hidden test gagal:\n" + proc.stdout[-1200:] + proc.stderr[-500:])
if fails:
    print("FAIL: " + "; ".join(fails)); sys.exit(1)
print("PASS: implementasi lolos hidden test (5 kasus)")
