#@+leo-ver=5-thin
#@+node:ekr.20240322162616.1: * @file ../scripts/test_leo.py
"""
test_leo.py: Run all of Leo's unit tests.
"""

import os
import subprocess
import sys

# cd to leo-editor
os.chdir(os.path.abspath(os.path.join(__file__, '..', '..', '..')))

args = ' '.join(sys.argv[1:])
isWindows = sys.platform.startswith('win')
python = 'py' if isWindows else 'python'

command = fr'{python} -m unittest leo'
subprocess.Popen(command, shell=True).communicate()
#@-leo
