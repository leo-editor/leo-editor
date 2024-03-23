#@+leo-ver=5-thin
#@+node:ekr.20240321122413.8: * @file ../scripts/mypy_leo.py
#@@language python

"""
mypy_leo.py: Run mypy on Leo's files.

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

command = fr'{python} -m mypy --debug-cache leo'
subprocess.Popen(command, shell=True).communicate()
#@-leo
