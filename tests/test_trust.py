#!/usr/bin/env python3
"""Tests for scripts/trust.py with the v3.1 config (maximum autonomy).

Run: python3 tests/test_trust.py
"""
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
TRUST = ROOT / 'scripts' / 'trust.py'
CONFIG = ROOT / 'config' / 'trust.yaml'


def trust(ledger, *args):
    r = subprocess.run([sys.executable, str(TRUST), '--config', str(CONFIG), '--ledger',
                        str(ledger), *args], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


class TrustTests(unittest.TestCase):
    def setUp(self):
        self.ledger = pathlib.Path(tempfile.mkdtemp(prefix='trust-test-')) / 'ledger.json'

    def test_default_levels(self):
        expect = {'A0': 0, 'A1': 0, 'A2': 0, 'A3': 0, 'A4': 4, 'A5': 1}
        for cls, code in expect.items():
            rc, out = trust(self.ledger, 'check', cls)
            self.assertEqual(rc, code, f'{cls}: {out}')

    def test_a2_demotion_delays_but_never_asks(self):
        rc, out = trust(self.ledger, 'record', '--class', 'A2', '--event', 'revert_after_merge')
        self.assertEqual(rc, 0, out)
        self.assertIn('veto_window', out)
        rc, out = trust(self.ledger, 'check', 'A2')
        self.assertEqual(rc, 4, out)  # allowed after the veto window, no approval

    def test_a4_demotion_goes_to_fahmi_merge(self):
        trust(self.ledger, 'record', '--class', 'A4', '--event', 'veto')
        rc, out = trust(self.ledger, 'check', 'A4')
        self.assertEqual(rc, 1, out)

    def test_first_accepted_at_is_recorded(self):
        trust(self.ledger, 'record', '--class', 'A2', '--event', 'accepted_pr')
        self.assertIn('first_accepted_at', self.ledger.read_text(encoding='utf-8'))
        self.assertNotIn('"first_accepted_at": null', self.ledger.read_text(encoding='utf-8'))

    def test_unknown_class_is_usage_error(self):
        rc, _ = trust(self.ledger, 'check', 'A9')
        self.assertEqual(rc, 2)


if __name__ == '__main__':
    unittest.main(verbosity=1)
