#@+leo-ver=5-thin
#@+node:ekr.20240321123224.1: * @file ../scripts/run_installed_leo.py
#@@language python

"""
run_installed_leo.py: Run leo from Python's `site-packages` directory.

See info item #3837 for full documentation.
https://github.com/leo-editor/leo-editor/issues/3837
"""

import os
import subprocess
import sys

file_name = os.path.basename(__file__)

# cd to the home directory.
home_dir = os.path.expanduser("~")
os.chdir(home_dir)

if any('leo-editor' in z for z in sys.path):
    print(f"{file_name}: remove leo-editor from sys.path!")
    print('Hint: do *not* run this script from the leo-editor directory!')
else:
    # Run.
    print(file_name)
    command = 'python -m leo.core.runLeo'
    print(command)
    print('')
    subprocess.Popen(command, shell=True).communicate()
#@-leo
