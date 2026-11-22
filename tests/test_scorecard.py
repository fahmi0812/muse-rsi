#!/usr/bin/env python3
"""Tests for scripts/scorecard.py — matched-metric delta (Fahmi, 22 Nov 2026).

The denominator-shift rule: adding a new metric must never move the
gate delta. A fresh C2 at 75% while C1 sits at 93.6% must NOT drag dC
down, and must NOT flatter a real regression later.
Run: python3 tests/test_scorecard.py  (or python3 -m unittest discover -s tests)
"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'scripts'))
import scorecard  # noqa: E402


class TestMatchedDelta(unittest.TestCase):
    def test_new_metric_excluded_from_delta(self):
        # C2 enters at 75 while C1 is unchanged at 93.6: delta must be 0,
        # not dragged down by the new metric's lower score.
        before = {'C1': 93.6, 'K3': 0}
        after = {'C1': 93.6, 'C2': 75.0, 'K3': 0}
        d = scorecard.matched_delta(before, after)
        self.assertEqual(d['dC'], 0.0)
        self.assertEqual(d['dK'], 0.0)
        self.assertEqual(d['added'], ['C2'])
        accept, _reasons, _d = scorecard.gate(before, after)
        # 0/0 on matched metrics = no progress -> reject (not a false accept).
        self.assertFalse(accept)

    def test_new_metric_does_not_hide_regression(self):
        # C1 falls 93.6 -> 80 while C2 enters at 90: plain averages would
        # look fine (91.8 -> 85 is still a fall, but a higher C2 could mask
        # it); matched delta must see the C1 fall.
        before = {'C1': 93.6}
        after = {'C1': 80.0, 'C2': 95.0}
        d = scorecard.matched_delta(before, after)
        self.assertLess(d['dC'], 0)
        accept, _r, _d = scorecard.gate(before, after)
        self.assertFalse(accept)

    def test_real_improvement_accepted(self):
        before = {'C1': 93.6, 'K3': 1}
        after = {'C1': 97.0, 'K3': 0}
        accept, _r, d = scorecard.gate(before, after)
        self.assertTrue(accept)
        self.assertGreater(d['dC'], 0)
        self.assertGreater(d['dK'], 0)

    def test_k_drop_rejects(self):
        before = {'C1': 93.6, 'K3': 0}
        after = {'C1': 97.0, 'K3': 2}
        accept, _r, _d = scorecard.gate(before, after)
        self.assertFalse(accept)

    def test_k7_hard_gate(self):
        before = {'C1': 93.6, 'K7': 0}
        after = {'C1': 99.0, 'K7': 1}
        accept, reasons, _d = scorecard.gate(before, after)
        self.assertFalse(accept)
        self.assertTrue(any('K7' in r for r in reasons))

    def test_spread_widening_rejects(self):
        # C jumps a lot while K stays: spread widens > 5 -> reject.
        # C1 85->98 (86.7->100), K4 85 (89.5): spread 2.8 -> 10.5.
        before = {'C1': 85.0, 'K4': 85.0}
        after = {'C1': 98.0, 'K4': 85.0}
        d = scorecard.matched_delta(before, after)
        self.assertGreater(d['spread_change'], 5.0)
        accept, _r, _d = scorecard.gate(before, after)
        self.assertFalse(accept)

    def test_no_common_metric_is_not_a_false_pass(self):
        # No overlap at all: both deltas None; gate must not accept
        # on the strength of nothing measurable.
        before = {'C1': 93.6}
        after = {'C2': 75.0}
        accept, reasons, _d = scorecard.gate(before, after)
        self.assertFalse(accept)
        self.assertTrue(any('no common' in r for r in reasons))


if __name__ == '__main__':
    unittest.main(verbosity=2)
