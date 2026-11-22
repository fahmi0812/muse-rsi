#!/usr/bin/env python3
"""Tests for scripts/gen_facts.py — head compared by ANCESTRY (22 Nov 2026).

The CI failure on commit f2ca3c9: gen_facts.py --check demanded the stored
head equal the current head exactly, so ANY later commit (even the
workflow-only commit f2ca3c9 itself) made the check fail with
"head: stored '11a045a' != current 'f2ca3c9'". The fix: a stored head
passes when it is an ancestor of HEAD; every other field (registry,
eval, canary, manifest) is still compared exactly, so a real content
change still fails.

PR #11 follow-up (22 Nov 2026): the ancestry check itself failed in
CI because actions/checkout@v5 defaults to a depth-1 shallow clone,
which does not contain the stored head at all — merge-base then
reports a true ancestor as "not an ancestor" ("stored 'f2ca3c9' is
not an ancestor of HEAD '1e0e538'"). The fix unshallows the repo
once before concluding. Tests below cover the shallow-clone case.
Run: python3 tests/test_gen_facts.py  (or python3 -m unittest discover -s tests)
"""
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'scripts'))
import gen_facts  # noqa: E402


def _make_repo(n_commits, seed=''):
    """A throwaway git repo with n commits; returns (path, [short shas]).

    The seed makes two repos' commits differ — without it, two repos
    built in the same second with identical content/author/message
    would hash to the SAME commit sha.
    """
    tmp = tempfile.mkdtemp(prefix='genfacts-test-')
    repo = pathlib.Path(tmp)
    subprocess.run(['git', 'init', '-q'], cwd=repo, check=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.local'],
                   cwd=repo, check=True)
    subprocess.run(['git', 'config', 'user.name', 'gen_facts test'],
                   cwd=repo, check=True)
    shas = []
    for i in range(n_commits):
        (repo / 'file.txt').write_text(f'line {i} {seed}\n', encoding='utf-8')
        subprocess.run(['git', 'add', '.'], cwd=repo, check=True)
        subprocess.run(['git', 'commit', '-qm', f'commit {i}'],
                       cwd=repo, check=True)
        shas.append(subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'], cwd=repo,
            capture_output=True, text=True, check=True).stdout.strip())
    return repo, shas


def _facts(head, registry_total=248):
    return {'head': head, 'registry_total': registry_total,
            'eval_top3': '130/130', 'canary': '8/8',
            'manifest_ok': True}


class TestHeadAncestry(unittest.TestCase):
    def test_stored_head_ancestor_passes(self):
        # The f2ca3c9 case: stored head is the parent commit, HEAD moved
        # on by a later (workflow-only) commit — numbers unchanged.
        repo, shas = _make_repo(2)
        problems = gen_facts.compare_facts(_facts(shas[0]),
                                           _facts(shas[1]), repo)
        self.assertEqual(problems, [])

    def test_equal_head_passes(self):
        repo, shas = _make_repo(1)
        problems = gen_facts.compare_facts(_facts(shas[0]),
                                           _facts(shas[0]), repo)
        self.assertEqual(problems, [])

    def test_non_ancestor_head_fails(self):
        # A head from an unrelated history (or a diverged rewrite) is
        # not an ancestor of HEAD — must fail, not silently pass.
        repo, shas = _make_repo(1)
        other, other_shas = _make_repo(1, seed='unrelated-history')
        problems = gen_facts.compare_facts(_facts(other_shas[0]),
                                           _facts(shas[0]), repo)
        self.assertEqual(len(problems), 1)
        self.assertIn('head', problems[0])
        self.assertIn('not an ancestor', problems[0])

    def test_unknown_head_fails(self):
        # The stale '088fd7d' case: a sha that does not exist in this
        # history at all must fail, never be treated as an ancestor.
        repo, shas = _make_repo(1)
        self.assertFalse(gen_facts.is_ancestor(repo, '088fd7d'))
        problems = gen_facts.compare_facts(_facts('088fd7d'),
                                           _facts(shas[0]), repo)
        self.assertEqual(len(problems), 1)
        self.assertIn('head', problems[0])

    def test_number_change_still_fails(self):
        # Ancestry must NOT excuse a real content change: registry
        # 247 -> 248 with an ancestor head still fails on the number.
        repo, shas = _make_repo(2)
        problems = gen_facts.compare_facts(_facts(shas[0], 247),
                                           _facts(shas[1], 248), repo)
        self.assertEqual(len(problems), 1)
        self.assertIn('registry_total', problems[0])

    def test_missing_head_fails(self):
        repo, shas = _make_repo(1)
        stored = _facts(shas[0])
        del stored['head']
        problems = gen_facts.compare_facts(stored, _facts(shas[0]), repo)
        self.assertEqual(len(problems), 1)
        self.assertIn('head', problems[0])

    def test_shallow_clone_ancestor_passes(self):
        # The PR #11 CI case: a depth-1 checkout contains only HEAD,
        # so the stored parent head is missing locally — the check
        # must unshallow once and then see it IS an ancestor.
        src, shas = _make_repo(2)
        dst = pathlib.Path(tempfile.mkdtemp(prefix='genfacts-shallow-'))
        subprocess.run(['git', 'clone', '-q', '--depth', '1',
                        f'file://{src}', str(dst)], check=True)
        self.assertEqual(
            subprocess.run(['git', 'rev-parse',
                            '--is-shallow-repository'], cwd=dst,
                           capture_output=True, text=True,
                           check=True).stdout.strip(), 'true')
        problems = gen_facts.compare_facts(_facts(shas[0]),
                                           _facts(shas[1]), dst)
        self.assertEqual(problems, [])

    def test_shallow_clone_unknown_head_still_fails(self):
        # Unshallowing must not turn an unknown sha into a pass.
        src, shas = _make_repo(2)
        dst = pathlib.Path(tempfile.mkdtemp(prefix='genfacts-shallow-'))
        subprocess.run(['git', 'clone', '-q', '--depth', '1',
                        f'file://{src}', str(dst)], check=True)
        self.assertFalse(gen_facts.is_ancestor(dst, '088fd7d'))
        problems = gen_facts.compare_facts(_facts('088fd7d'),
                                           _facts(shas[1]), dst)
        self.assertEqual(len(problems), 1)
        self.assertIn('head', problems[0])


if __name__ == '__main__':
    unittest.main(verbosity=2)
