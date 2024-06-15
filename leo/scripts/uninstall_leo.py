#@+leo-ver=5-thin
#@+node:ekr.20240321123225.1: * @file ../scripts/uninstall_leo.py
#@@language python

"""
uninstall_leo.py: Run `pip uninstall leo`.

*Note*: The leo-editor folder must *not* be in sys.path!

Info item #3837 describes all distribution-related scripts.
https://github.com/leo-editor/leo-editor/issues/3837
"""
import os
import sys
import subprocess

file_name = os.path.basename(__file__)

if any('leo-editor' in z for z in sys.path):
    print(f"{file_name}: remove leo-editor from sys.path!")
    print('Hint: do *not* run this script from the leo-editor directory!')
else:
    print(os.path.basename(__file__))

    # Do *not* install from leo-editor!
    home_dir = os.path.expanduser("~")
    os.chdir(home_dir)

    # Uninstall.
    # --yes: Don’t ask for confirmation of uninstall deletions.
    command = 'python -m pip uninstall leo'
    print(command)
    subprocess.Popen(command, shell=True).communicate()
#@-leo
