#@+leo-ver=5-thin
#@+node:ekr.20240322084902.1: * @file ../scripts/flake8_leo.py
"""
flake8_leo.py: run flake8 on Leo.

See leo-editor/setup.cfg for defaults
"""

import os
import subprocess
import sys

# cd to leo-editor
os.chdir(os.path.abspath(os.path.join(__file__, '..', '..', '..')))

args = ' '.join(sys.argv[1:])
isWindows = sys.platform.startswith('win')
python = 'py' if isWindows else 'python'

command = fr'{python} -m flake8 {args}'
subprocess.Popen(command, shell=True).communicate()

#@-leo
