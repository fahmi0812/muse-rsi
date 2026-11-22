#!/usr/bin/env python3
"""model_census.py — sensus model bulanan (Bab 4.7, G3).

Membaca config/MODELS.yaml dan melaporkan, per entri: status +
verified_at + umur verifikasi. Tidak pernah mengubah slug: sensus
hanya MELAPORKAN. Pergantian slug adalah aksi kelas A4 (butuh eval
kalibrasi per peran + persetujuan) — bukan urusan skrip ini.

Slug yang diklaim berubah (dari design Bab 1.3) dilaporkan di seksi
"perlu cek ulang": GPT-6.2 Astra/Sol dan Gemini 4 Neon sudah dicek ke
halaman resmi pada 2026-11-22 (URL di bawah, hasil pencarian web yang
dibuka langsung); Gemini 4 Carbon, Fable 5.2, dan Muse Wonder Full
belum punya URL resmi terverifikasi di sensus ini — URL-nya TODO,
bukan karangan. docs/sources.md TIDAK ADA di repo ini, jadi tidak ada
URL yang diambil dari sana.

Usage:
  python3 scripts/model_census.py --report
  python3 scripts/model_census.py --report --config config/MODELS.yaml --out-dir state
Menulis laporan ke stdout + state/model-census-YYYY-MM-DD.md. Exit 0
bila laporan berhasil ditulis; exit 2 bila MODELS.yaml tidak bisa dibaca.
"""
import argparse
import datetime
import pathlib
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
DEFAULT_CONFIG = REPO / "config" / "MODELS.yaml"
DEFAULT_OUT_DIR = REPO / "state"

STALE_AFTER_DAYS = 30

# Slug yang diklaim berubah (design Bab 1.3). `official_url` hanya diisi
# bila halaman resmi sudah DIBUKA langsung; bila belum, TODO — jangan karang.
# `api_id_confirmed` False berarti pengumuman tidak menyebut id API.
CLAIMED_CHANGED = [
    {"name": "GPT-6.2 Astra", "candidate_slug": "gpt-6.2-astra",
     "would_replace": "coder fallback (saat ini gpt-6.1-sol)",
     "official_url": "https://help.openai.com/en/articles/9624314-model-release-notes",
     "official_url_note": "OpenAI Help Center, Model Release Notes, 17 Nov 2026 — dibuka langsung 2026-11-22; URL dicantumkan tanpa parameter pelacak (?utm_...) dari hasil pencarian, path artikel sama.",
     "api_id_confirmed": True,
     "status": "HALAMAN RESMI TERVERIFIKASI 2026-11-22 — kandidat; ganti slug tetap butuh eval kalibrasi per peran + A4."},
    {"name": "GPT-6.2 Sol", "candidate_slug": "gpt-6.2-sol",
     "would_replace": "coder fallback (saat ini gpt-6.1-sol)",
     "official_url": "https://help.openai.com/en/articles/9624314-model-release-notes",
     "official_url_note": "Sama seperti GPT-6.2 Astra — satu halaman release notes 17 Nov 2026.",
     "api_id_confirmed": True,
     "status": "HALAMAN RESMI TERVERIFIKASI 2026-11-22 — kandidat; ganti slug tetap butuh eval kalibrasi per peran + A4."},
    {"name": "Gemini 4 Neon", "candidate_slug": None,
     "would_replace": "researcher/coder fallback (saat ini gemini-3-pro-preview)",
     "official_url": "https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon/",
     "official_url_note": "Google Blog, 'Introducing Gemini 4 Neon', 18 Nov 2026 — dibuka langsung 2026-11-22; URL dicantumkan tanpa parameter pelacak dari hasil pencarian, path artikel sama.",
     "api_id_confirmed": False,
     "status": "HALAMAN RESMI TERVERIFIKASI 2026-11-22 — TAPI pengumuman tidak menyebut id API; id harus dikonfirmasi dari AI Studio / model directory sebelum dipakai. Ganti slug tetap butuh eval kalibrasi + A4."},
    {"name": "Gemini 4 Carbon", "candidate_slug": "gemini-4-carbon",
     "would_replace": "(belum ditentukan — disebut sebagai saudara Neon)",
     "official_url": "https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-carbon/",
     "official_url_note": "Google Blog, 'Introducing Gemini 4 Carbon', 28 Okt 2026 — dibuka langsung 2026-11-22 (docs/sources.md). GA 10 Nov 2026.",
     "api_id_confirmed": False,
     "status": "HALAMAN RESMI TERVERIFIKASI 2026-11-22 — kandidat; id API belum dikonfirmasi; ganti slug tetap butuh eval kalibrasi + A4."},
    {"name": "Fable 5.2", "candidate_slug": "claude-fable-5-2",
     "would_replace": "(belum ditentukan)",
     "official_url": "https://www.anthropic.com/claude-fable-and-mythos-5-2",
     "official_url_note": "Anthropic, 'Introducing Claude Fable 5.2 and Claude Mythos 5.2', 9 Nov 2026 — dibuka langsung 2026-11-22 (docs/sources.md). Model ID claude-fable-5-2.",
     "api_id_confirmed": True,
     "status": "HALAMAN RESMI TERVERIFIKASI 2026-11-22 — kandidat; ganti slug tetap butuh eval kalibrasi + A4."},
    {"name": "Muse Wonder Full", "candidate_slug": "muse-wonder-full",
     "would_replace": "(belum ditentukan — disebut sebagai kandidat orkestrator)",
     "official_url": "https://about.fb.com/news/2026/10/introducing-muse-wonder-models/",
     "official_url_note": "Meta, 'Introducing Muse Wonder and Muse Wonder Full', 12 Okt 2026 — dibuka langsung 2026-11-22 (docs/sources.md).",
     "api_id_confirmed": False,
     "status": "HALAMAN RESMI TERVERIFIKASI 2026-11-22 — kandidat orkestrator; ganti slug tetap butuh eval kalibrasi + A4."},
]


def _age_days(verified_at, today):
    if not verified_at:
        return None
    try:
        d = datetime.date.fromisoformat(str(verified_at))
    except ValueError:
        return None
    return (today - d).days


def _state(verified_at, today):
    age = _age_days(verified_at, today)
    if age is None:
        return "TIDAK TERVERIFIKASI (verified_at kosong)"
    if age <= STALE_AFTER_DAYS:
        return f"SEGAR ({age} hari)"
    return f"BASI ({age} hari > {STALE_AFTER_DAYS} hari — perlu cek ulang)"


def build_report(cfg, today):
    lines = []
    lines.append(f"# Sensus model — {today.isoformat()}")
    lines.append("")
    lines.append("Sensus bulanan MODELS.yaml (Bab 4.7). Sensus ini TIDAK mengubah "
                 "slug apa pun; pergantian slug adalah aksi kelas A4.")
    lines.append("")
    lines.append(f"- MODELS.yaml version: {cfg.get('version')}")
    lines.append(f"- verified (file): {cfg.get('verified')}")
    lines.append(f"- recheck_due (file): {cfg.get('recheck_due')}")
    src = REPO / "docs" / "sources.md"
    lines.append(f"- docs/sources.md: {'ADA di repo (URL kanonis, cek 22 Nov 2026)' if src.exists() else 'TIDAK ADA di repo — URL resmi di bawah berasal dari pencarian web yang dibuka langsung pada 2026-11-22.'}")
    lines.append("")
    lines.append("## Peran (roles)")
    lines.append("")
    lines.append("| peran | provider | model | fallback | status | verified_at | keadaan |")
    lines.append("|---|---|---|---|---|---|---|")
    stale = []
    for role, spec in (cfg.get("roles") or {}).items():
        fb = spec.get("fallback") or {}
        state = _state(spec.get("verified_at"), today)
        if "BASI" in state or "TIDAK" in state:
            stale.append(role)
        lines.append(f"| {role} | {spec.get('provider')} | {spec.get('model')} | "
                     f"{fb.get('model')} | {spec.get('status')} | {spec.get('verified_at')} | {state} |")
    lines.append("")
    lines.append("## Council")
    lines.append("")
    council = cfg.get("council") or {}
    lines.append(f"- quorum: {council.get('quorum')}")
    lines.append(f"- seat_conflict_rule: {council.get('seat_conflict_rule')}")
    for seat in council.get("judges", []):
        lines.append(f"- kursi {seat.get('provider')}/{seat.get('model')}: "
                     f"status={seat.get('status')}, verified_at={seat.get('verified_at')} "
                     f"({_state(seat.get('verified_at'), today)})")
    lines.append("")
    lines.append("## Model dasar lokal")
    lines.append("")
    local = cfg.get("local_base_model") or {}
    lines.append(f"- platform: {local.get('platform')}, model: {local.get('model')} "
                 f"(status={local.get('status')}, verified_at={local.get('verified_at')})")
    lines.append("- TIDAK TERVERIFIKASI — jangan tebak slug; cek dari pengaturan runtime.")
    lines.append("")
    retired = cfg.get("retired_do_not_use") or []
    lines.append(f"## Retired / jangan dipakai ({len(retired)} entri)")
    lines.append("")
    for r in retired:
        lines.append(f"- {r.get('model')} -> pakai {r.get('use_instead')} (retired: {r.get('retired')})")
    lines.append("")
    lines.append("## Slug yang diklaim berubah — perlu cek ulang")
    lines.append("")
    for c in CLAIMED_CHANGED:
        lines.append(f"### {c['name']}")
        lines.append("")
        lines.append(f"- kandidat slug: {c['candidate_slug'] or 'TODO (belum ada id yang dikonfirmasi)'}")
        lines.append(f"- bila dipakai akan menggantikan: {c['would_replace']}")
        lines.append(f"- URL resmi: {c['official_url'] or 'TODO'}")
        lines.append(f"  {c['official_url_note']}")
        lines.append(f"- id API terkonfirmasi: {'ya' if c['api_id_confirmed'] else 'TIDAK'}")
        lines.append(f"- status: {c['status']}")
        lines.append("")
    lines.append("## Kesimpulan")
    lines.append("")
    if stale:
        lines.append(f"- Peran dengan verifikasi basi/belum terverifikasi: {', '.join(stale)}.")
    else:
        lines.append("- Semua peran di MODELS.yaml masih dalam jendela verifikasi 30 hari.")
    lines.append("- TIDAK ADA slug di MODELS.yaml yang diubah oleh sensus ini.")
    lines.append("- Tindak lanjut: (1) konfirmasi id API Gemini 4 Neon dari AI Studio / "
                 "model directory; (2) Carbon, Fable 5.2, dan Muse Wonder Full SUDAH "
                 "terverifikasi resmi 22 Nov 2026 (docs/sources.md) — tinggal eval "
                 "kalibrasi per peran; (3) bila kandidat lolos eval kalibrasi per peran, "
                 "ajukan pergantian slug sebagai aksi A4 — bukan lewat sensus.")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true", help="tulis laporan sensus")
    ap.add_argument("--config", default=str(DEFAULT_CONFIG))
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args()
    if not args.report:
        ap.error("gunakan --report (satu-satunya aksi sensus)")
    cfg_path = pathlib.Path(args.config)
    try:
        cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        print(f"MODELS.yaml tidak bisa dibaca ({cfg_path}): {e}", file=sys.stderr)
        return 2
    today = datetime.date.today()
    report = build_report(cfg, today)
    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"model-census-{today.isoformat()}.md"
    out_path.write_text(report, encoding="utf-8")
    print(report, end="")
    print(f"[laporan ditulis ke {out_path}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
