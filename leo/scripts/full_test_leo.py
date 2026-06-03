# @+leo-ver=5-thin
# @+node:ekr.20240323051724.1: * @file ../scripts/full_test_leo.py
"""
full_test_leo.py: Run all these tests scripts in this order:

- beautify_all_leo.py.
- run_test_leo.py.
- flake8_leo.py.
- pyflakes_leo.py
- mypy_leo.py.
- ruff_leo.py.
- check_leo.py.
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
"""

import os
import subprocess
import sys

print(os.path.basename(__file__))

# cd to leo-editor
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
os.chdir(leo_editor_dir)

args = ' '.join(sys.argv[1:])
python = sys.executable
for command in [
    rf'{python} -m leo.scripts.beautify_all_leo',
    rf'{python} -m leo.scripts.flake8_leo',
    rf'{python} -m leo.scripts.pyflakes_leo',
    rf'{python} -m leo.scripts.run_test_leo',
    rf'{python} -m leo.scripts.mypy_leo',
    rf'{python} -m leo.scripts.ruff_leo',
    rf'{python} -m leo.scripts.check_leo',
    rf'{python} -m leo.scripts.pylint_leo',
]:
    subprocess.Popen(command, shell=True).communicate()
# @-leo
