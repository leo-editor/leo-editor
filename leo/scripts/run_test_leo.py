#@+leo-ver=5-thin
#@+node:ekr.20240322162616.1: * @file ../scripts/run_test_leo.py
"""
run_test_leo.py: Run all of Leo's unit tests.

This file's name must *not* start with `test_`.

Info item #3867 describes all of Leo's test scripts:
https://github.com/leo-editor/leo-editor/issues/2867

EKR's test-leo.cmd:
    @echo off
    cd {path to leo-editor}
    python -m leo.scripts.run_test_leo
"""

import os
import subprocess
import sys

print(os.path.basename(__file__))

# cd to leo-editor
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
os.chdir(leo_editor_dir)

args = ' '.join(sys.argv[1:])
isWindows = sys.platform.startswith('win')
python = 'py' if isWindows else 'python'

command = fr'{python} -m unittest'
subprocess.Popen(command, shell=True).communicate()
#@-leo
