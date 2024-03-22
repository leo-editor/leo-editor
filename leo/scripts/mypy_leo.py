#@+leo-ver=5-thin
#@+node:ekr.20240321122413.8: * @file ../scripts/mypy_leo.py
#@@language python

"""
mypy_leo.py: Run mypy on Leo's files.
"""

import os
import subprocess
import sys

# cd to leo-editor
os.chdir(os.path.abspath(os.path.join(__file__, '..', '..', '..')))

args = ' '.join(sys.argv[1:])
isWindows = sys.platform.startswith('win')
python = 'py' if isWindows else 'python'

# py -m mypy --debug-cache leo %*

command = fr'{python} -m mypy --debug-cache leo'
subprocess.Popen(command, shell=True).communicate()
#@-leo
