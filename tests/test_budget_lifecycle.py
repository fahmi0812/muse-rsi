#!/usr/bin/env python3
"""Regression test: the Loop Engine must close the run_budget.py budget
at the end of every cycle (2026-11-27).

Bug: rsi_cycle.py started a budget in PRECHECK but never called
`run_budget.py close`. run_budget.py start refuses to overwrite an
active budget (exit 3), so every cycle after the first fell back to
the internal counter — the externally enforced 40-step / 45-min / $0
budget silently stopped working. decision.tsv 2026-11-23..26 shows
"budget via internal counter (run_budget.py start failed)" and
~/.muse-rsi/budget.json still held the 23 Nov cycle's active budget.

Run: python3 tests/test_budget_lifecycle.py
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr


class BudgetLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix='budget-lifecycle-'))
        # Sandbox repo: git + the scripts/config the engine needs.
        self.repo = self.tmp / 'repo'
        (self.repo / 'scripts').mkdir(parents=True)
        (self.repo / 'config').mkdir()
        for name in ('rsi_cycle.py', 'run_budget.py', 'decision_log.py',
                     'scorecard.py'):
            shutil.copy(ROOT / 'scripts' / name, self.repo / 'scripts' / name)
        shutil.copy(ROOT / 'config' / 'limits.yaml',
                    self.repo / 'config' / 'limits.yaml')
        _run(['git', 'init', '-q', str(self.repo)])
        _run(['git', '-C', str(self.repo), 'config', 'user.name', 'test'])
        _run(['git', '-C', str(self.repo), 'config', 'user.email',
              'test@example.com'])
        (self.repo / 'README.md').write_text('sandbox\n', encoding='utf-8')
        _run(['git', '-C', str(self.repo), 'add', '-A'])
        _run(['git', '-C', str(self.repo), 'commit', '-qm', 'sandbox'])
        self.home = self.tmp / 'home'  # no STOP / directives.yaml
        self.home.mkdir()
        self.state_home = self.tmp / 'state'
        self.state_home.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run_empty_cycle(self):
        code = (
            "import sys; sys.path.insert(0, %r); "
            "from rsi_cycle import Cycle; "
            "import pathlib; "
            "c = Cycle(repo=pathlib.Path(%r), home=pathlib.Path(%r), "
            "state_home=pathlib.Path(%r)); "
            "raise SystemExit(c.run())"
        ) % (str(self.repo / 'scripts'), str(self.repo), str(self.home),
             str(self.state_home))
        return _run([sys.executable, '-c', code])

    def test_budget_closed_at_end_of_empty_cycle(self):
        rc, out = self._run_empty_cycle()
        self.assertEqual(rc, 0, out)
        budget = json.loads(
            (self.state_home / 'budget.json').read_text(encoding='utf-8'))
        self.assertEqual(budget['status'], 'done',
                         f"budget left {budget['status']}: {out}")
        # The next cycle's start must succeed (no stale active budget).
        rc2, out2 = _run([sys.executable,
                          str(self.repo / 'scripts' / 'run_budget.py'),
                          'start', '--task', 'rsi-cycle-next',
                          '--budget', '40', '--file',
                          str(self.state_home / 'budget.json')])
        self.assertEqual(rc2, 0, out2)


if __name__ == '__main__':
    unittest.main(verbosity=1)
