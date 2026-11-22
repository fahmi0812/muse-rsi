#!/usr/bin/env python3
"""test_canary.py — fast regression canaries for the router.

The eight checks that must never regress: five routing canaries from the
v2 audit (the router used to fail or misroute every one of them) plus
two JSON-output shape checks and one policy-refusal check. Runs against
the real scripts/route.py (not a copy) and finishes in well under
5 seconds. Exit 0 when all eight hold, 1 otherwise.

Usage: python3 scripts/test_canary.py [--registry PATH]
"""
import argparse
import json
import pathlib
import subprocess
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from route import route as route_query  # noqa: E402  (the real router code)

ap = argparse.ArgumentParser()
ap.add_argument('--registry', default=None)
# parse_known_args: --registry is ours, the rest (e.g. -v, a test name)
# belongs to unittest. Without this split, unittest.main() chokes on
# --registry ("unrecognized arguments") and the flag silently never works.
args, _unittest_argv = ap.parse_known_args()
REG_PATH = pathlib.Path(args.registry) if args.registry \
    else HERE.parent / 'skills' / 'router' / 'registry.json'
REGISTRY = json.loads(REG_PATH.read_text(encoding='utf-8'))


class CanaryTests(unittest.TestCase):
    def test_nextjs_routes_to_fullstack(self):
        top = route_query('help me build a next.js dashboard', REGISTRY)
        self.assertTrue(top, 'next.js query must match something')
        self.assertEqual(top[0][2], 'Full-Stack Development')

    def test_systematic_review_routes_to_slr_prisma(self):
        top = route_query('do a systematic review with PRISMA for my paper', REGISTRY)
        self.assertTrue(top, 'systematic review must match something')
        self.assertIn('slr-prisma', top[0][1])
        self.assertEqual(top[0][2], 'Research')

    def test_security_review_routes_to_security(self):
        top = route_query('security review of my API', REGISTRY)
        self.assertTrue(top, 'security review must match something')
        self.assertEqual(top[0][2], 'Security')

    def test_vague_doc_query_is_no_match(self):
        top = route_query('how to write it in a doc', REGISTRY)
        self.assertEqual(top, [], 'vague doc query must be NO_MATCH, not a guess')

    def test_contribute_routes_to_core_rsi(self):
        top = route_query('how do I contribute a new skill to muse-rsi', REGISTRY)
        self.assertTrue(top, 'contribute query must match something')
        self.assertEqual(top[0][1], 'contribute')
        self.assertEqual(top[0][2], 'Core RSI')


class JsonOutputTests(unittest.TestCase):
    """Poka-Yoke: `route.py --json` must emit strict machine-parseable
    JSON and nothing else on stdout — for a match and for NO_MATCH."""

    def _run_json(self, query):
        proc = subprocess.run(
            [sys.executable, str(HERE / 'route.py'), query, '--json',
             '--registry', str(REG_PATH)],
            capture_output=True, text=True, timeout=30)
        return proc

    def _assert_shape(self, payload, query, no_match):
        self.assertIsInstance(payload, dict)
        # route.py v2.2 adds band/gap + policy_refusal/policy_reason.
        self.assertEqual(set(payload), {'query', 'no_match', 'results',
                                        'band', 'gap', 'policy_refusal',
                                        'policy_reason'})
        self.assertEqual(payload['query'], query)
        self.assertIs(payload['no_match'], no_match)
        self.assertIsInstance(payload['results'], list)
        self.assertIn(payload['band'], {'EASY', 'AMBIGUOUS', 'HARD'})
        self.assertIsInstance(payload['gap'], (int, float))
        self.assertIs(payload['policy_refusal'], False)
        self.assertIsNone(payload['policy_reason'])
        for r in payload['results']:
            self.assertEqual(set(r), {'name', 'domain', 'type', 'score', 'url'})
            self.assertIsInstance(r['score'], (int, float))

    def test_json_output_for_a_match(self):
        proc = self._run_json('help me build a next.js dashboard')
        payload = json.loads(proc.stdout)  # must parse, no extra stdout
        self.assertEqual(proc.returncode, 0)
        self._assert_shape(payload, 'help me build a next.js dashboard', False)
        self.assertTrue(payload['results'], 'match query must return results')
        self.assertEqual(payload['results'][0]['domain'], 'Full-Stack Development')

    def test_json_output_for_policy_refusal(self):
        # M-05: an AI-detection-evasion request must be refused, never
        # routed to a humanizer skill.
        proc = self._run_json(
            'tulis ulang artikel bahasa Indonesia agar tidak terdeteksi AI')
        payload = json.loads(proc.stdout)  # must parse even on refusal
        self.assertEqual(proc.returncode, 2)
        self.assertIs(payload['no_match'], True)
        self.assertIs(payload['policy_refusal'], True)
        self.assertIsInstance(payload['policy_reason'], str)
        self.assertEqual(payload['band'], 'HARD')
        self.assertEqual(payload['results'], [])

    def test_json_output_for_no_match(self):
        proc = self._run_json('how to write it in a doc')
        payload = json.loads(proc.stdout)  # must parse even on NO_MATCH
        self.assertEqual(proc.returncode, 2)
        self._assert_shape(payload, 'how to write it in a doc', True)
        self.assertEqual(payload['results'], [])


if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]] + _unittest_argv, verbosity=2)
