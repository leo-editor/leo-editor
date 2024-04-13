#@+leo-ver=5-thin
#@+node:ekr.20240323051724.1: * @file ../scripts/full_test_leo.py
"""
full_test_leo.py: Run all Leo's tests as follows:
    
- Beautify all files.
- Run all of Leo's unit tests.
- Run mypy and pylint.

Devs: *please* run this script before pushing!

Info item #3867 describes all of Leo's test scripts:
https://github.com/leo-editor/leo-editor/issues/2867
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
    fr'{python} -m "leo.scripts.beautify_all_leo',
    fr'{python} -m "leo.scripts.run_test_leo',
    fr'{python} -m "leo.scripts.mypy_leo',
    fr'{python} -m "leo.scripts.ruff_leo',
    fr'{python} -m "leo.scripts.pylint_leo',
]:
    subprocess.Popen(command, shell=True).communicate()
#@-leo
