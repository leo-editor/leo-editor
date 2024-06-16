#@+leo-ver=5-thin
#@+node:ekr.20240322173731.1: * @file ../scripts/pip_uninstall_all.py
"""
pip_uninstall_all.py: Use pip to uninstall *all* python packages.

Don't use this script unless you know what you are doing!

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
    f"{python} -m pip freeze > temp_requirements.txt",
    f"{python} -m pip uninstall -r temp_requirements.txt -y --verbose",
    f"{python} -m pip list",

]:
    print('')
    print(command)
    print('')
    subprocess.Popen(command, shell=True).communicate()

if os.path.exists('temp_requirements.txt'):
    print('')
    print('remove temp_requirements.txt')
    os.remove('temp_requirements.txt')

# cd to the leo-editor directory.
os.chdir(leo_editor_dir)
#@-leo
