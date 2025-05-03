#@+leo-ver=5-thin
#@+node:ekr.20240323051724.1: * @file ../scripts/full_test_leo.py
"""
full_test_leo.py: Run all these tests scripts in this order:
    
- beautify_leo.py.
- run_test_leo.py.
- flake8_leo.py.
- pyflakes_leo.py
- mypy_leo.py.
- ruff_leo.py.
- pylint_leo.py.

Devs: *please* run this script before pushing!

Info item #3867 describes all of Leo's test scripts:
https://github.com/leo-editor/leo-editor/issues/2867

EKR's fft.cmd runs all tests:
    @echo off
    cls
    cd {path-to-leo-editor}
    call python -m leo.scripts.full_test_leo
    echo fft.cmd: Done!

EKR's ft.cmd runs all tests except pylint:
    @echo off
    cls
    cd {path-to-leo-editor}
    echo ft.cmd
    call python -m leo.scripts.beautify_leo
    call python -m leo.scripts.run_test_leo
    call python -m leo.scripts.flake8_leo
    call python -m leo.scripts.mypy_leo
    call python -m leo.scripts.ruff_leo
    echo Done!
"""

import os
import subprocess
import sys

print(os.path.basename(__file__))

# cd to leo-editor
os.chdir(os.path.abspath(os.path.join(__file__, '..', '..', '..')))

args = ' '.join(sys.argv[1:])
isWindows = sys.platform.startswith('win')
python = 'py' if isWindows else 'python'

for command in [
    fr'{python} -m leo.scripts.beautify_all_leo',
    fr'{python} -m leo.scripts.flake8_leo',
    fr'{python} -m leo.scripts.pyflakes_leo',
    fr'{python} -m leo.scripts.run_test_leo',
    fr'{python} -m leo.scripts.mypy_leo',
    fr'{python} -m leo.scripts.ruff_leo',
    fr'{python} -m leo.scripts.pylint_leo',
]:
    subprocess.Popen(command, shell=True).communicate()
#@-leo
