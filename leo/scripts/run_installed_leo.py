#@+leo-ver=5-thin
#@+node:ekr.20240321123224.1: * @file ../scripts/run_installed_leo.py
#@@language python

"""
run_installed_leo.py: Run leo from Python's `site-packages` folder.

Info item #3837 describes all distribution-related scripts.
https://github.com/leo-editor/leo-editor/issues/3837
"""

import os
import subprocess

print(os.path.basename(__file__))

# Do *not* install from leo-editor!
home_dir = os.path.expanduser("~")
os.chdir(home_dir)

# Run.
command = 'python -m leo.core.runLeo'
print(command)
subprocess.Popen(command, shell=True).communicate()
#@-leo
