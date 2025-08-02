#@+leo-ver=5-thin
#@+node:ekr.20240321122413.9: * @file ../scripts/pylint_leo.py
#@@language python

"""
pylint_leo.py: Run pylint on Leo's core files.

Info item #3867 describes all of Leo's test scripts:
https://github.com/leo-editor/leo-editor/issues/2867

EKR's pylint-leo.cmd:
    cd {path-to-leo-editor}
    python -m leo.scripts.pylint_leo
"""
import os
import subprocess
import sys
from leo.commands.checkerCommands import PylintCommand

print(os.path.basename(__file__))

# cd to leo-editor
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
os.chdir(leo_editor_dir)

args = ' '.join(sys.argv[1:])
isWindows = sys.platform.startswith('win')
python = 'py' if isWindows else 'python'

rc_file_name = PylintCommand(c=None).get_rc_file()  # #4191.
rc_file = rf"--rcfile {rc_file_name}"
# print(__file__, rc_file)
extensions = 'PyQt6.QtCore,PyQt6.QtGui,PyQt6.QtWidgets,PyQt6.QtWebEngineWidgets'
extension_pkg = f"--extension-pkg-allow-list={extensions}"
command = fr"{python} -m pylint leo {rc_file} {extension_pkg}"

subprocess.Popen(command, shell=True).communicate()
#@-leo
