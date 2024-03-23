#@+leo-ver=5-thin
#@+node:ekr.20240321123225.3: * @file ../scripts/install_leo_from_testpypi.py
#@@language python

"""
install_leo_from_testpypi.py: Install leo from https://test.pypi.org/project/leo/.

Info item #3837 describes all distribution-related scripts.
https://github.com/leo-editor/leo-editor/issues/3837
"""

import os
import subprocess

print(os.path.basename(__file__))

# Do *not* install from leo-editor!
home_dir = os.path.expanduser("~")
os.chdir(home_dir)

# Install.
command = 'python -m pip install -i https://test.pypi.org/simple/ leo'
print(command)
subprocess.Popen(command, shell=True).communicate()
#@-leo
