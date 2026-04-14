# @+leo-ver=5-thin
# @+node:ekr.20260414092941.1: * @file ../scripts/update_leo_tools.py
"""
update_leo_tools.py: Update Leo's checker tools.

EKR's update-leo-tools.cmd:
    cd {path-to-leo-editor}
    python -m leo.scripts.update_leo_tools
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
    f"{python} -m pip install --upgrade flake8",
    f"{python} -m pip install --upgrade mypy",
    f"{python} -m pip install --upgrade pylint",
    f"{python} -m pip install --upgrade ruff",
]:
    print('')
    print(command)
    subprocess.Popen(command, shell=True).communicate()
# @-leo
