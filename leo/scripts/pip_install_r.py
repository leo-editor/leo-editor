#@+leo-ver=5-thin
#@+node:ekr.20240322173704.1: * @file ../scripts/pip_install_r.py
"""
pip_install_r.py: Install all of Leo's requirements from requirements.txt.

Info item #3837 describes all distribution-related scripts.
https://github.com/leo-editor/leo-editor/issues/3837
"""

import os
import subprocess
import sys

print(os.path.basename(__file__))

# cd to leo-editor
os.chdir(os.path.abspath(os.path.join(__file__, '..', '..', '..')))

isWindows = sys.platform.startswith('win')
python = 'py' if isWindows else 'python'

for command in [
   f"{python} -m pip install -r requirements.txt --no-warn-script-location",
   f"{python} -m pip list",
]:
    print(command)
    subprocess.Popen(command, shell=True).communicate()
#@-leo
