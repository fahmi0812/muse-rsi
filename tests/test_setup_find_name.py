#!/usr/bin/env python3
"""Regression tests for setup.py find_name — escaped asterisks (issue #8).

An IDENTITY.md whose Role line is written with Markdown-escaped
asterisks (`- \\*\\*Role:\\*\\* ...`) made find_name return None, so
setup fell back to the generic Role line. Unescaping `\\*` before
matching fixes it; these tests pin both the escaped and the plain
shapes. Run: python3 tests/test_setup_find_name.py
"""
import importlib.util
import pathlib
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    'muse_setup_under_test', REPO / 'setup' / 'setup.py')
_setup = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_setup)
find_name = _setup.find_name

ROLE = 'Full-Autonomous High-Speed Orchestrator & Friendly Practical Tutor.'


class FindNameEscapedTests(unittest.TestCase):
    def test_escaped_role(self):
        text = '- \\*\\*Role:\\*\\* ' + ROLE
        self.assertEqual(find_name(text, 'Role'), ROLE)

    def test_plain_role(self):
        text = '- **Role:** ' + ROLE
        self.assertEqual(find_name(text, 'Role'), ROLE)

    def test_escaped_name(self):
        self.assertEqual(
            find_name('- \\*\\*Name:\\*\\* ClaudiaAra', 'Name'),
            'ClaudiaAra')

    def test_plain_name(self):
        self.assertEqual(
            find_name('- **Name:** ClaudiaAra', 'Name'), 'ClaudiaAra')

    def test_no_match_still_none(self):
        self.assertIsNone(find_name('- **User:** somebody', 'Role'))
        self.assertIsNone(find_name('', 'Name'))


if __name__ == '__main__':
    unittest.main()
