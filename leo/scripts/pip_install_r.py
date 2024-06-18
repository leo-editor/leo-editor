#@+leo-ver=5-thin
#@+node:ekr.20240322173704.1: * @file ../scripts/pip_install_r.py
"""
pip_install_r.py: Install all of Leo's requirements from requirements.txt.

This script does *not* install Leo itself.

See info item #3837 for full documentation.
https://github.com/leo-editor/leo-editor/issues/3837
"""

import os
import subprocess
import sys

print(os.path.basename(__file__))

# cd to `leo-editor`.
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
assert leo_editor_dir.endswith('leo-editor'), repr(leo_editor_dir)
assert os.path.exists(leo_editor_dir), repr(leo_editor_dir)
assert os.path.isdir(leo_editor_dir), repr(leo_editor_dir)
os.chdir(leo_editor_dir)

isWindows = sys.platform.startswith('win')
python = 'py' if isWindows else 'python'

for command in [
   f"{python} -m pip install -r requirements.txt --no-warn-script-location",
   f"{python} -m pip list",
]:
    print(command)
    subprocess.Popen(command, shell=True).communicate()
#@-leo
