#@+leo-ver=5-thin
#@+node:ekr.20240322162616.1: * @file ../scripts/run_test_leo.py
"""
run_test_leo.py: Run all of Leo's unit tests.

This file's name must *not* start with `test_`!
"""

import os
import subprocess
import sys

# cd to leo-editor
os.chdir(os.path.abspath(os.path.join(__file__, '..', '..', '..')))

args = ' '.join(sys.argv[1:])
isWindows = sys.platform.startswith('win')
python = 'py' if isWindows else 'python'

command = fr'{python} -m unittest'
subprocess.Popen(command, shell=True).communicate()
#@-leo
