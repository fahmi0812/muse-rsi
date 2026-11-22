#!/usr/bin/env python3
"""Tests for scripts/autonomy_gate.py (v3.1 maximum autonomy).

Each test builds a tiny git repo that carries the real policy lists
(config/protected_paths.txt, config/veto_paths.txt, config/limits.yaml),
commits a base, makes one change, and checks the class.

Run: python3 tests/test_autonomy_gate.py
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import autonomy_gate as gate  # noqa: E402

CASES = {'description': 't', 'cases': [
    {'query': 'deploy to kubernetes', 'expected_domains': ['DevOps & Infra']},
    {'query': 'apa kabar', 'expect_no_match': True},
]}


def git(repo, *args):
    subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True, text=True)


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix='gate-test-'))
        r = self.tmp
        git(r, 'init', '-q', '-b', 'main')
        git(r, 'config', 'user.email', 'test@example.invalid')
        git(r, 'config', 'user.name', 'gate-test')
        for rel in ('config/protected_paths.txt', 'config/veto_paths.txt', 'config/limits.yaml',
                    'config/trust.yaml'):
            (r / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / rel, r / rel)
        self.write('scripts/eval_routing.json', json.dumps(CASES, indent=1))
        self.write('scripts/test_canary.py', 'def test_a():\n    pass\n\ndef test_b():\n    pass\n')
        self.write('tests/bad/secret-01.diff', '+token=abc\n')
        self.write('skills/demo/SKILL.md', '---\nname: demo\ndescription: d\n---\nhi\n')
        self.write('docs/note.md', 'note\n')
        self.write('scripts/rsi_cycle.py', 'print(1)\n')
        git(r, 'add', '-A')
        git(r, 'commit', '-q', '-m', 'base')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, rel, text):
        p = self.tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')

    def classify(self):
        git(self.tmp, 'add', '-A')
        git(self.tmp, 'commit', '-q', '-m', 'change')
        return gate.classify_tree(self.tmp, 'HEAD~1', 'HEAD')

    def test_docs_and_skills_are_auto(self):
        self.write('docs/note.md', 'note v2\n')
        self.write('skills/demo/SKILL.md', '---\nname: demo\ndescription: d2\n---\nhi\n')
        self.assertEqual(self.classify()['class'], 'AUTO')

    def test_adding_eval_case_is_veto(self):
        data = json.loads(json.dumps(CASES))
        data['cases'].append({'query': 'tulis email resmi', 'expected_domains': ['Office']})
        self.write('scripts/eval_routing.json', json.dumps(data, indent=1))
        self.assertEqual(self.classify()['class'], 'VETO')

    def test_removing_eval_case_is_hard(self):
        data = json.loads(json.dumps(CASES))
        data['cases'].pop(0)
        self.write('scripts/eval_routing.json', json.dumps(data, indent=1))
        self.assertEqual(self.classify()['class'], 'HARD')

    def test_editing_eval_expectation_is_hard(self):
        data = json.loads(json.dumps(CASES))
        data['cases'][0]['expected_domains'] = ['Other']
        self.write('scripts/eval_routing.json', json.dumps(data, indent=1))
        self.assertEqual(self.classify()['class'], 'HARD')

    def test_removing_canary_is_hard(self):
        self.write('scripts/test_canary.py', 'def test_a():\n    pass\n')
        self.assertEqual(self.classify()['class'], 'HARD')

    def test_adding_canary_is_veto(self):
        self.write('scripts/test_canary.py', 'def test_a():\n    pass\n\ndef test_b():\n    pass\n'
                                             '\ndef test_c():\n    pass\n')
        self.assertEqual(self.classify()['class'], 'VETO')

    def test_editing_known_bad_sample_is_hard(self):
        self.write('tests/bad/secret-01.diff', '+nothing to see\n')
        self.assertEqual(self.classify()['class'], 'HARD')

    def test_engine_fix_is_auto(self):
        self.write('scripts/rsi_cycle.py', 'print(2)\n')
        self.assertEqual(self.classify()['class'], 'AUTO')

    def test_adding_eval_case_with_engine_fix_is_veto(self):
        data = json.loads(json.dumps(CASES))
        data['cases'].append({'query': 'tulis email resmi', 'expected_domains': ['Office']})
        self.write('scripts/eval_routing.json', json.dumps(data, indent=1))
        self.write('scripts/rsi_cycle.py', 'print(2)\n')
        self.assertEqual(self.classify()['class'], 'VETO')

    def test_engine_fix_with_big_diff_is_veto(self):
        self.write('scripts/rsi_cycle.py', 'print(2)\n')
        self.write('docs/big.md', ''.join(f'line {i}\n' for i in range(500)))
        self.assertEqual(self.classify()['class'], 'VETO')

    def test_deleting_engine_is_hard(self):
        (self.tmp / 'scripts/rsi_cycle.py').unlink()
        self.assertEqual(self.classify()['class'], 'HARD')

    def test_trust_config_is_hard(self):
        self.write('config/trust.yaml', 'current: {A5: automatic}\n')
        self.assertEqual(self.classify()['class'], 'HARD')

    def test_shrinking_protected_list_cannot_relax_itself(self):
        # The policy list is read from the BASE side: removing trust.yaml from
        # protected_paths.txt in the same change still classifies it HARD.
        p = self.tmp / 'config/protected_paths.txt'
        p.write_text(p.read_text(encoding='utf-8').replace('config/trust.yaml\n', ''),
                     encoding='utf-8')
        self.write('config/trust.yaml', 'current: {A5: automatic}\n')
        self.assertEqual(self.classify()['class'], 'HARD')

    def test_workflow_is_hard(self):
        self.write('.github/workflows/x.yml', 'on: push\n')
        self.assertEqual(self.classify()['class'], 'HARD')

    def test_big_auto_change_becomes_veto(self):
        self.write('docs/big.md', ''.join(f'line {i}\n' for i in range(500)))
        self.assertEqual(self.classify()['class'], 'VETO')

    def test_patch_mode_matches_tree_mode(self):
        self.write('docs/note.md', 'note v3\n')
        git(self.tmp, 'add', '-A')
        diff = subprocess.run(['git', '-C', str(self.tmp), 'diff', '--cached'],
                              capture_output=True, text=True, check=True).stdout
        git(self.tmp, 'reset', '-q', '--hard', 'HEAD')
        patch = self.tmp.parent / (self.tmp.name + '.patch')
        patch.write_text(diff, encoding='utf-8')
        try:
            self.assertEqual(gate.classify_patch(self.tmp, patch)['class'], 'AUTO')
        finally:
            patch.unlink()


if __name__ == '__main__':
    unittest.main(verbosity=1)
