"""Protect the single installable entrypoint and relocatable skill resources."""
import importlib.util
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def test_one_entrypoint_with_resolvable_resources(self):
        self.assertEqual(list(ROOT.rglob('SKILL.md')), [ROOT / 'SKILL.md'],
                         'A second entrypoint can shadow the installed skill')
        documents = [ROOT / 'SKILL.md', *sorted((ROOT / 'references').glob('*.md'))]
        for document in documents:
            for target in re.findall(r'\]\(([^)]+)\)', document.read_text(encoding='utf-8')):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((document.parent / target.split('#')[0]).is_file(),
                                    f'Broken resource in {document.name}: {target}')

    def test_manual_install_works_outside_repository(self):
        with tempfile.TemporaryDirectory(prefix='grill-install-') as temporary:
            installed = Path(temporary) / 'skills' / 'grill-with-docs-ui'
            installed.mkdir(parents=True)
            for name in ('SKILL.md', 'LICENSE'):
                shutil.copy2(ROOT / name, installed / name)
            for name in ('scripts', 'assets', 'references', 'agents'):
                shutil.copytree(ROOT / name, installed / name)
            helper = installed / 'scripts/session.py'
            result = subprocess.run([sys.executable, '-B', str(helper), '--version'],
                                    cwd=temporary, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(result.stdout.strip())
            spec = importlib.util.spec_from_file_location('installed_session', helper)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            session = Path(temporary) / 'interview'
            session.mkdir()
            shutil.copy2(installed / 'assets/round.html', session / 'round-1.html')
            with module.SessionServer(session) as server:
                self.assertEqual(server.latest(), 1)
                self.assertIn('client.js', server.page(1))


if __name__ == '__main__':
    unittest.main()
