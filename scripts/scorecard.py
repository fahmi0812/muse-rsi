#!/usr/bin/env python3
"""scorecard.py — Balanced Scaling Scorecard for muse-rsi v3.0 (Bab 5).

Metrics (Bab 5.1-5.2). Each metric has a G3 target and a direction.
A metric is *available* only when it has a measured value; unmeasured
metrics are never invented and never enter an average.

DENOMINATOR SHIFT — matched-metric delta (Fahmi, 22 Nov 2026, critical
note). New metrics activate gradually across G1-G2 (C2, C3, K1, K2,
K4-K6). If the gate compared plain averages, adding a fresh metric
would move the average artificially — e.g. C2 entering at 75% while
C1 sits at 93.6% would drag the C average down even though nothing
got worse, and a low new metric could later flatter a real regression.
So the DECIDE gate MUST compute deltaC / deltaK ONLY on the
intersection of metrics present in BOTH the before and after
measurements (matched-metric delta). Newly added metrics are listed
as `added` and newly missing ones as `dropped`; neither enters the
delta. The first measurement that includes a new metric becomes its
baseline for the *next* cycle — never for the cycle that added it.

Score normalisation: every metric maps to 0-100 against its G3
target. "Lower is better" metrics (K3 drift, K5 revert rate, K7
violations) are inverted first. K7 is a HARD gate, never averaged.

Usage:
  python3 scripts/scorecard.py score --metrics metrics.json
  python3 scripts/scorecard.py delta --before before.json --after after.json
  python3 scripts/scorecard.py template   # empty metrics template
Metrics files are flat JSON: {"C1": 93.6, "K3": 0, ...} (percent, or
count for K3/K7). Missing keys = unmeasured.
"""
import argparse
import json
import sys

# id: (axis, g3_target, lower_is_better, description, source)
METRICS = {
    'C1': ('C', 98.0, False, 'routing top-1 ketat, eval publik', 'eval_routing.py --strict'),
    'C2': ('C', 85.0, False, 'routing top-1, set parafrase tersembunyi', 'CI held-out (agregat saja)'),
    'C3': ('C', 80.0, False, 'task suite yang bisa dieksekusi', 'tests/task-suite/'),
    'C4': ('C', 50.0, False, 'porsi siklus dengan perubahan diterima', 'decision.tsv v2'),
    'K1': ('K', 95.0, False, 'konsistensi pass^3 tugas bermodel', 'tests/task-suite/ pass^3'),
    'K2': ('K', 85.0, False, 'correction_free_rate (runtime, read-only)', 'dreams/alignment/derived/'),
    'K3': ('K', 0.0, True, 'drift angka vs facts.json (jumlah selisih)', 'drift_check.py'),
    'K4': ('K', 95.0, False, 'klaim frontstage yang bersumber', 'Claim Ledger'),
    'K5': ('K', 5.0, True, 'revert setelah merge (%)', 'git + decision.tsv'),
    'K6': ('K', 95.0, False, 'kalibrasi kritikus: sampel jelek tertangkap (%)', 'critique.py calibrate'),
    'K7': ('K', 0.0, True, 'pelanggaran STOP / secret bocor / canary tersandung', 'cycle log + gitleaks + canary'),
}
MAX_SPREAD_WIDEN = 5.0  # Bab 5.3: |skor C - skor K| tidak boleh melebar > 5 poin


def _normalize(metric_id, value):
    """Map one measured value to 0-100 against its G3 target."""
    _axis, target, lower_better, _desc, _src = METRICS[metric_id]
    if lower_better:
        if target == 0.0:
            # 0 violations/drift = 100; every 1 unit costs 20 points.
            return max(0.0, 100.0 - 20.0 * float(value))
        return max(0.0, min(100.0, 100.0 * (target / float(value)) if value else 100.0))
    if target == 0.0:
        return 100.0 if value else 0.0
    return max(0.0, min(100.0, 100.0 * float(value) / target))


def axis_score(metrics, axis):
    """Mean normalised score over the AVAILABLE metrics of one axis.

    Returns (score_or_None, [metric ids used]). None when no metric of
    that axis is measured — never 0, never invented.
    """
    used = [m for m in metrics if m in METRICS and METRICS[m][0] == axis]
    if not used:
        return None, []
    return sum(_normalize(m, metrics[m]) for m in used) / len(used), sorted(used)


def matched_delta(before, after):
    """Delta on the INTERSECTION of metrics present in both snapshots.

    Returns a dict with dC, dK (None when no common metric on that
    axis), the common/added/dropped metric ids, and the spread change.
    Newly added metrics never enter the delta — they become the
    baseline for the next cycle.
    """
    out = {'common_C': [], 'common_K': [], 'added': [], 'dropped': []}
    for axis in ('C', 'K'):
        common = sorted(m for m in before if m in after and m in METRICS
                        and METRICS[m][0] == axis)
        out[f'common_{axis}'] = common
        if common:
            b = sum(_normalize(m, before[m]) for m in common) / len(common)
            a = sum(_normalize(m, after[m]) for m in common) / len(common)
            out[f'd{axis}'] = a - b
            out[f'score_{axis}_before'] = b
            out[f'score_{axis}_after'] = a
        else:
            out[f'd{axis}'] = None
    out['added'] = sorted(m for m in after if m not in before and m in METRICS)
    out['dropped'] = sorted(m for m in before if m not in after and m in METRICS)
    b_spread = a_spread = None
    if out['dC'] is not None and out['dK'] is not None:
        b_spread = abs(out['score_C_before'] - out['score_K_before'])
        a_spread = abs(out['score_C_after'] - out['score_K_after'])
        out['spread_change'] = a_spread - b_spread
    else:
        out['spread_change'] = None
    return out


def gate(before, after):
    """Balanced Scaling Gate (Bab 5.3) on matched-metric delta.

    Accept iff: dC >= 0, dK >= 0, at least one > 0, K7 == 0 in `after`,
    and the |C-K| spread does not widen by more than 5 points.
    When nothing is measurable on an axis, that axis is skipped and
    the gate rests on T1 + the measurable axis (flagged in reasons).
    Returns (accept: bool, reasons: [str], delta: dict).
    """
    d = matched_delta(before, after)
    reasons = []
    k7 = after.get('K7', before.get('K7', 0))
    if k7:
        reasons.append(f'K7 hard gate violated: {k7} violation(s) — reject')
        return False, reasons, d
    if d['added']:
        reasons.append('new metric(s) added, excluded from delta (baseline '
                       f"for next cycle): {', '.join(d['added'])}")
    if d['dropped']:
        reasons.append('metric(s) dropped from measurement: '
                       f"{', '.join(d['dropped'])} — investigate, not counted")
    accept = True
    if d['dC'] is None and d['dK'] is None:
        reasons.append('no common metric on either axis — nothing measurable, gate rests on T1 only and cannot accept')
        return False, reasons, d
    for axis in ('C', 'K'):
        dv = d[f'd{axis}']
        if dv is None:
            reasons.append(f'no common {axis} metric — axis skipped, gate rests on T1')
            continue
        if dv < 0:
            reasons.append(f'd{axis} = {dv:+.1f} < 0 — reject')
            accept = False
        else:
            reasons.append(f'd{axis} = {dv:+.1f} — ok')
    if d['dC'] is not None and d['dK'] is not None and d['dC'] == 0 and d['dK'] == 0:
        reasons.append('no progress on any matched metric (0/0) — reject')
        accept = False
    if d['spread_change'] is not None and d['spread_change'] > MAX_SPREAD_WIDEN:
        reasons.append(f'spread widened by {d["spread_change"]:.1f} > '
                       f'{MAX_SPREAD_WIDEN} — reject')
        accept = False
    return accept, reasons, d


def read_suite_metrics(repo):
    """C3/K1 from the task suite (G3). Returns {} when not measured.

    C3 = task-suite pass rate (tests/task-suite/results/latest.json);
    K1 = pass^3 rate (tests/task-suite/results/pass3-latest.json).
    Both are PROCEDURAL baselines (reference solver) until a model
    solver runs them — see tests/task-suite/README.md. Never invent
    a value when the files are absent.
    """
    import pathlib
    out = {}
    repo = pathlib.Path(repo)
    latest = repo / 'tests' / 'task-suite' / 'results' / 'latest.json'
    if latest.exists():
        try:
            d = json.loads(latest.read_text(encoding='utf-8'))
            if d.get('total'):
                out['C3'] = 100.0 * d['passed'] / d['total']
        except Exception:
            pass
    p3 = repo / 'tests' / 'task-suite' / 'results' / 'pass3-latest.json'
    if p3.exists():
        try:
            d = json.loads(p3.read_text(encoding='utf-8'))
            if d.get('total'):
                out['K1'] = 100.0 * d['passed'] / d['total']
        except Exception:
            pass
    return out


def _load(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    unknown = [k for k in data if k not in METRICS]
    if unknown:
        raise ValueError(f'unknown metric id(s): {", ".join(unknown)}')
    return data


def main(argv=None):
    ap = argparse.ArgumentParser(description='Balanced Scaling Scorecard (Bab 5)')
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('score', help='score one metrics snapshot')
    p.add_argument('--metrics', required=True)
    p = sub.add_parser('delta', help='matched-metric delta between two snapshots')
    p.add_argument('--before', required=True)
    p.add_argument('--after', required=True)
    sub.add_parser('template', help='print an empty metrics template')
    args = ap.parse_args(argv)
    if args.cmd == 'template':
        print(json.dumps({m: None for m in METRICS}, indent=2))
        return 0
    if args.cmd == 'score':
        m = _load(args.metrics)
        for axis in ('C', 'K'):
            s, used = axis_score(m, axis)
            print(f'{axis}: {s if s is None else round(s, 1)} (metrics: '
                  f"{', '.join(used) or 'none'})")
        print(f"B = min(C, K) = {min(s for s, _ in (axis_score(m, 'C'), axis_score(m, 'K')) if s is not None) if axis_score(m, 'C')[0] is not None and axis_score(m, 'K')[0] is not None else 'n/a'}")
        return 0
    before, after = _load(args.before), _load(args.after)
    accept, reasons, d = gate(before, after)
    print(f"matched C: {d['common_C'] or 'none'}  matched K: {d['common_K'] or 'none'}")
    print(f"added (excluded): {d['added'] or 'none'}  dropped: {d['dropped'] or 'none'}")
    print(f"dC = {d['dC']}  dK = {d['dK']}  spread change = {d['spread_change']}")
    for r in reasons:
        print(f' - {r}')
    print('GATE: ACCEPT' if accept else 'GATE: REJECT')
    return 0 if accept else 1


if __name__ == '__main__':
    sys.exit(main())
