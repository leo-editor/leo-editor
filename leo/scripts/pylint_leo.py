#@+leo-ver=5-thin
#@+node:ekr.20240321122413.9: * @file ../scripts/pylint_leo.py
#@@language python

"""
pylint_leo.py: Run pylint on Leo's core files.

Info item #3867 describes all of Leo's test scripts:
https://github.com/leo-editor/leo-editor/issues/2867
"""

# No longer used by Leo's official test scripts.
# pylint is not part of requirements.txt.

import os
import subprocess
import sys

# cd to leo-editor
os.chdir(os.path.abspath(os.path.join(__file__, '..', '..', '..')))

# Print a signon.
args_s = ' '.join(sys.argv[1:])
print(os.path.basename(__file__), args_s)

isWindows = sys.platform.startswith('win')
python = 'py' if isWindows else 'python'

command = fr'{python} -m pylint leo {args_s} --extension-pkg-allow-list=PyQt6.QtCore,PyQt6.QtGui,PyQt6.QtWidgets'
subprocess.Popen(command, shell=True).communicate()
#@-leo
