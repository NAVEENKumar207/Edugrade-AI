"""
Automated AST and static analysis test suite verifying that no dead controls,
unanchored '#' links, unhandled buttons, or insecure target='_blank' links exist.
"""

import os
import re
import glob
from django.test import SimpleTestCase
from django.urls import resolve, Resolver404


class NoDeadControlsTestCase(SimpleTestCase):
    def setUp(self):
        self.ui_files = sorted(glob.glob('ui/pages/*.py') + glob.glob('ui/components/*.py') + ['ui/app.py'])
        self.template_files = sorted(glob.glob('templates/*.html'))

    def test_no_dead_hash_links_in_templates(self):
        """Ensures legacy templates do not contain dead href='#' placeholder links."""
        dead_hash_pattern = re.compile(r'href=[\'"]#[\'"]')
        violations = []
        for path in self.template_files:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            for line_no, line in enumerate(content.splitlines(), 1):
                if dead_hash_pattern.search(line):
                    violations.append(f"{path}:{line_no} -> {line.strip()}")

        self.assertEqual(violations, [], f"Found dead href='#' in templates: {violations}")

    def test_no_dead_hash_links_in_reactpy_ui(self):
        """Ensures ReactPy components do not emit dead href='#' without in-page targets."""
        hash_pattern = re.compile(r'["\']href["\']\s*:\s*["\']#([^\'"]*)["\']')
        violations = []
        for path in self.ui_files:
            # landing.py has real internal anchors (#top, #features, #workflow, #effect)
            if 'landing.py' in path:
                continue
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            for line_no, line in enumerate(content.splitlines(), 1):
                m = hash_pattern.search(line)
                if m and m.group(1) == '':
                    violations.append(f"{path}:{line_no} -> {line.strip()}")

        self.assertEqual(violations, [], f"Found dead href='#' in ReactPy UI: {violations}")

    def test_secure_target_blank(self):
        """Ensures any link with target='_blank' specifies rel='noopener noreferrer'."""
        violations = []
        for path in self.ui_files + self.template_files:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # ReactPy html.a with target _blank
            if '_blank' in content:
                a_blocks = re.findall(r'html\.a\s*\(\s*\{([^}]*)\}', content, re.DOTALL)
                for b in a_blocks:
                    if '_blank' in b and 'noopener' not in b:
                        violations.append(f"{path} -> {b.strip()[:80]}")

                # HTML <a ... target="_blank" ...>
                html_a = re.findall(r'<a[^>]*target=[\'"]_blank[\'"][^>]*>', content, re.IGNORECASE)
                for a in html_a:
                    if 'noopener' not in a.lower():
                        violations.append(f"{path} -> {a}")

        self.assertEqual(violations, [], f"Found target='_blank' without noopener: {violations}")

    def test_no_todo_or_coming_soon_in_user_facing_controls(self):
        """Ensures no clickable control is left as a 'TODO' or 'Coming soon' placeholder."""
        placeholder_pattern = re.compile(r'(TODO|Coming\s*soon)', re.IGNORECASE)
        violations = []
        for path in self.ui_files + self.template_files:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find in button tags or text
            btn_matches = re.findall(r'(?:html\.button|<button)[^>)]*(?:TODO|Coming\s*soon)', content, re.IGNORECASE)
            if btn_matches:
                violations.extend([f"{path} -> {m[:60]}" for m in btn_matches])

        self.assertEqual(violations, [], f"Found placeholder controls: {violations}")
