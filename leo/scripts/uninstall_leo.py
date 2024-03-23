#@+leo-ver=5-thin
#@+node:ekr.20240321123225.1: * @file ../scripts/uninstall_leo.py
#@@language python

"""
uninstall_leo.py: Run `pip uninstall leo`.

Info item #3837 describes all distribution-related scripts.
https://github.com/leo-editor/leo-editor/issues/3837
"""

import os
import subprocess

print(os.path.basename(__file__))

# Do *not* install from leo-editor!
home_dir = os.path.expanduser("~")
os.chdir(home_dir)

# Uninstall.
command = 'python -m pip uninstall leo'
print(command)
subprocess.Popen(command, shell=True).communicate()
#@-leo
