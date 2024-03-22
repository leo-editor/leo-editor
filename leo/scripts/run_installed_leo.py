#@+leo-ver=5-thin
#@+node:ekr.20240321123224.1: * @file ../scripts/run_installed_leo.py
#@@language python

"""
run_installed_leo.py: run leo from Python's `site-packages` folder.

Info item #3837 describes all distribution-related scripts.
https://github.com/leo-editor/leo-editor/issues/3837
"""

import os
import sys

# Make sure leo-editor is on the path.
leo_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
if leo_dir not in sys.path:
    sys.path.insert(0, leo_dir)
from leo.core import leoGlobals as g

print('run_installed_leo.py')

# Do *not* install from leo-editor!
home_dir = os.path.expanduser("~")
os.chdir(home_dir)

# Run. 
command = 'python -m leo.core.runLeo'
g.execute_shell_commands(command)
#@-leo
