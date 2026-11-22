#!/usr/bin/env python3
"""flywheel.py — trajektori ter-redaksi + retensi 90 hari (Bab 4.8, G3).

Menyimpan trajektori (query, skill terpilih, file yang benar-benar
dibuka, perintah + exit code, verdict) sebagai JSONL ter-redaksi di
state/trajectories.jsonl. Log mentah dipertahankan 90 hari; agregat
permanen disimpan di state/trajectory-aggregates.json.

REDAKSI (aturan USER.md + Bab 4.8) — diterapkan ke SEMUA string
sebelum satu baris pun ditulis:
  * isi vault / secret: pola kunci API, token, password, dan nilai
    di bawah kunci bernama password/token/secret/api_key -> [REDACTED:secret]
  * data people/: path memory/people/ atau people/<nama> -> [REDACTED:people]
  * lokasi: nama tempat + koordinat + zona Asia/Jakarta -> [REDACTED:location]
  * path home absolut -> "~" (bukan lokasi, tapi higiene)
Redaksi adalah heuristik berbasis pola — bila sebuah string lolos,
laporkan; jangan pernah menulis record mentah untuk "memperbaiki".

RETENSI: `prune --days 90` menghitung AGREGAT DULU (per skill,
per verdict, jumlah perintah, rentang tanggal), menggabungkannya ke
file agregat permanen, BARU menghapus entri yang lebih tua dari N hari.
Tanpa --dry-run, penghapusan benar-benar terjadi; selalu ada jejak
agregatnya.

Usage:
  python3 scripts/flywheel.py record --json '{"query": "...", "skill": "...", "verdict": "pass", "commands": [{"cmd": "...", "exit_code": 0}]}'
  python3 scripts/flywheel.py record --json-file trajectory.json
  python3 scripts/flywheel.py stats
  python3 scripts/flywheel.py prune --days 90 --dry-run
  python3 scripts/flywheel.py prune --days 90
"""
import argparse
import datetime
import json
import os
import pathlib
import re
import sys
import uuid

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
DEFAULT_STORE = REPO / "state" / "trajectories.jsonl"
DEFAULT_AGGREGATES = REPO / "state" / "trajectory-aggregates.json"

HOME = os.path.expanduser("~")

# --- pola redaksi -------------------------------------------------------
SECRET_VALUE_RES = [
    re.compile(r"(?i)(api[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|secret|bearer)\s*[:=]\s*\S+"),
    re.compile(r"sk-[A-Za-z0-9\-_]{10,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}"),
]
SECRET_KEYS = {"password", "passwd", "token", "secret", "api_key", "apikey",
               "api-key", "access_token", "auth_token", "bearer"}
PEOPLE_RE = re.compile(r"(?:memory/)?people/[^\s\"'`,;\]]+")
VAULT_RE = re.compile(r"[~.]?/?\.?config/muse/vault[^\s\"'`,;\]]*|vault/[^\s\"'`,;\]]+")
LOCATION_TOKENS = [
    "Asia/Jakarta", "Jakarta", "Bandung", "Surabaya", "Medan", "Bekasi",
    "Tangerang", "Depok", "Semarang", "Palembang", "Makassar", "Bogor",
    "Batam", "Pekanbaru", "Yogyakarta", "Yogya", "Malang", "Solo",
    "Denpasar", "Balikpapan", "Bali", "Jawa Barat", "Jawa Timur",
    "Jawa Tengah", "Sumatera", "Sulawesi", "Kalimantan",
]
LOCATION_RES = [re.compile(r"\b" + re.escape(tok) + r"\b", re.IGNORECASE)
                for tok in LOCATION_TOKENS]
COORD_RE = re.compile(r"(?<![\w.])-?\d{1,3}\.\d{4,}\s*,\s*-?\d{1,3}\.\d{4,}")

REDACTED_SECRET = "[REDACTED:secret]"
REDACTED_PEOPLE = "[REDACTED:people]"
REDACTED_VAULT = "[REDACTED:vault]"
REDACTED_LOCATION = "[REDACTED:location]"


def redact_string(s, counter):
    """Redaksi satu string; counter['n'] dihitung per substitusi."""
    if HOME and HOME in s:
        s = s.replace(HOME, "~")
    def sub(pattern, repl, text):
        new, n = pattern.subn(repl, text)
        counter["n"] += n
        return new
    s = sub(VAULT_RE, REDACTED_VAULT, s)
    s = sub(PEOPLE_RE, REDACTED_PEOPLE, s)
    for rx in SECRET_VALUE_RES:
        s = sub(rx, REDACTED_SECRET, s)
    for rx in LOCATION_RES:
        s = sub(rx, REDACTED_LOCATION, s)
    s = sub(COORD_RE, REDACTED_LOCATION, s)
    return s


def redact(obj, counter):
    if isinstance(obj, str):
        return redact_string(obj, counter)
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            lk = str(k).lower()
            if lk in SECRET_KEYS:
                counter["n"] += 1
                out[k] = REDACTED_SECRET
            elif lk == "people":
                counter["n"] += 1
                out[k] = REDACTED_PEOPLE
            else:
                out[k] = redact(v, counter)
        return out
    if isinstance(obj, list):
        return [redact(v, counter) for v in obj]
    return obj


def _parse_ts(value):
    try:
        return datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def cmd_record(args):
    if args.json == "-":
        raw = sys.stdin.read()
    elif args.json:
        raw = args.json
    elif args.json_file:
        raw = pathlib.Path(args.json_file).read_text(encoding="utf-8")
    else:
        print("record butuh --json atau --json-file")
        return 2
    try:
        rec = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON tidak valid: {e}")
        return 2
    if not isinstance(rec, dict):
        print("record harus objek JSON")
        return 2
    missing = [f for f in ("query", "skill", "verdict") if f not in rec]
    if missing:
        print(f"field wajib hilang: {', '.join(missing)}")
        return 2
    rec.setdefault("ts", datetime.datetime.now(datetime.timezone.utc).isoformat())
    rec.setdefault("run_id", uuid.uuid4().hex[:12])
    counter = {"n": 0}
    clean = redact(rec, counter)
    store = pathlib.Path(args.store)
    store.parent.mkdir(parents=True, exist_ok=True)
    with open(store, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(clean, ensure_ascii=False) + "\n")
    print(f"recorded run_id={clean['run_id']} skill={clean['skill']} "
          f"verdict={clean['verdict']} redactions={counter['n']} -> {store}")
    return 0


def _load_lines(store):
    if not store.exists():
        return []
    rows = []
    for line in store.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _aggregate(rows):
    by_skill, by_verdict = {}, {}
    n_commands = 0
    for r in rows:
        by_skill[r.get("skill", "?")] = by_skill.get(r.get("skill", "?"), 0) + 1
        by_verdict[r.get("verdict", "?")] = by_verdict.get(r.get("verdict", "?"), 0) + 1
        cmds = r.get("commands") or []
        n_commands += len(cmds) if isinstance(cmds, list) else 0
    ts_list = sorted(filter(None, (str(r.get("ts", "")) for r in rows)))
    return {"entries": len(rows), "by_skill": by_skill,
            "by_verdict": by_verdict, "total_commands": n_commands,
            "ts_min": ts_list[0] if ts_list else None,
            "ts_max": ts_list[-1] if ts_list else None}


def cmd_prune(args):
    store = pathlib.Path(args.store)
    rows = _load_lines(store)
    if not rows:
        print(f"tidak ada entri di {store} — tidak ada yang di-prune")
        return 0
    cutoff = (datetime.datetime.now(datetime.timezone.utc)
              - datetime.timedelta(days=args.days))
    keep, drop = [], []
    for r in rows:
        ts = _parse_ts(r.get("ts", ""))
        (drop if (ts is not None and ts < cutoff) else keep).append(r)
    agg_path = pathlib.Path(args.aggregates)
    print(f"total={len(rows)} keep={len(keep)} drop={len(drop)} "
          f"(lebih tua dari {args.days} hari, cutoff {cutoff.date()})")
    if drop:
        batch = _aggregate(drop)
        batch["pruned_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        batch["retention_days"] = args.days
        if args.dry_run:
            print("DRY-RUN: agregat yang AKAN disimpan (entri tidak dihapus):")
            print(json.dumps(batch, indent=2, ensure_ascii=False))
            return 0
        # Agregat dulu, hapus kemudian — urutan ini yang menjamin tidak ada
        # data hilang tanpa jejak agregat permanen.
        existing = {}
        if agg_path.exists():
            try:
                existing = json.loads(agg_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                existing = {}
        batches = existing.get("pruned_batches", [])
        batches.append(batch)
        totals_skill, totals_verdict = dict(existing.get("totals_by_skill", {})), dict(existing.get("totals_by_verdict", {}))
        for k, v in batch["by_skill"].items():
            totals_skill[k] = totals_skill.get(k, 0) + v
        for k, v in batch["by_verdict"].items():
            totals_verdict[k] = totals_verdict.get(k, 0) + v
        agg = {"totals_by_skill": totals_skill, "totals_by_verdict": totals_verdict,
               "total_pruned_entries": existing.get("total_pruned_entries", 0) + len(drop),
               "total_pruned_commands": existing.get("total_pruned_commands", 0) + batch["total_commands"],
               "pruned_batches": batches}
        agg_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = agg_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(agg, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(agg_path)
        tmp_store = store.with_suffix(".tmp")
        tmp_store.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in keep), encoding="utf-8")
        tmp_store.replace(store)
        print(f"pruned {len(drop)} entri; agregat permanen di {agg_path}")
    else:
        print("tidak ada entri yang lebih tua dari retensi — tidak ada yang dihapus")
    return 0


def cmd_stats(args):
    rows = _load_lines(pathlib.Path(args.store))
    if not rows:
        print(f"tidak ada entri di {args.store}")
        return 0
    agg = _aggregate(rows)
    print(f"entri: {agg['entries']}  perintah: {agg['total_commands']}  "
          f"rentang: {agg['ts_min']} .. {agg['ts_max']}")
    print("per skill: " + json.dumps(agg["by_skill"], ensure_ascii=False))
    print("per verdict: " + json.dumps(agg["by_verdict"], ensure_ascii=False))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--store", default=str(DEFAULT_STORE))
    ap.add_argument("--aggregates", default=str(DEFAULT_AGGREGATES))
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_rec = sub.add_parser("record")
    p_rec.add_argument("--json", default=None)
    p_rec.add_argument("--json-file", default=None)
    p_rec.set_defaults(fn=cmd_record)
    p_pr = sub.add_parser("prune")
    p_pr.add_argument("--days", type=int, default=90)
    p_pr.add_argument("--dry-run", action="store_true")
    p_pr.set_defaults(fn=cmd_prune)
    p_st = sub.add_parser("stats")
    p_st.set_defaults(fn=cmd_stats)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
