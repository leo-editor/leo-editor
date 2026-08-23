# @+leo-ver=5-thin
# @+node:ekr.20260809120840.1: * @file ../scripts/ty_leo.py
"""
ty_leo.py: Run ty on all of Leo.
"""

import importlib
import os
import subprocess
import sys

print(os.path.basename(__file__))

# cd to leo-editor
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
os.chdir(leo_editor_dir)

# @+others
# @+node:ekr.20260823160000.1: ** check_optional_deps
def check_optional_deps() -> bool:
    """Return True if every package that a `# type:ignore` fallback assumes is present is importable. See #4952."""
    # (pip package name, importable module name)
    packages = [
        ('docutils', 'docutils'),
        ('lxml', 'lxml'),
        ('mypy', 'mypy'),
        ('nbformat', 'nbformat'),
        ('Pygments', 'pygments'),
        ('PyQt6', 'PyQt6.QtWidgets'),
        ('PyQt6-QScintilla', 'PyQt6.Qsci'),
        ('pyenchant', 'enchant'),
        ('PyYAML', 'yaml'),
        ('websockets', 'websockets'),
    ]
    missing = []
    for pip_name, module_name in packages:
        try:
            importlib.import_module(module_name)
        except Exception:
            missing.append(pip_name)
    if missing:
        print('ty_leo.py: missing packages that some `# type:ignore` comments assume are installed:')
        for name in missing:
            print(f'  {name}')
        print('Install them with: pip install -r requirements.txt')
        print('Without them, ty reports spurious unused-type-ignore-comment diagnostics.')
        return False
    return True
# @-others

if not check_optional_deps():
    sys.exit(1)

args = ' '.join(sys.argv[1:])
python = sys.executable
command = rf'{python} -m ty check leo {args}'
subprocess.run(command, shell=True, check=False)
# @-leo
