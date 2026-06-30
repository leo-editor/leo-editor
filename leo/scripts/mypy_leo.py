# @+leo-ver=5-thin
# @+node:ekr.20240321122413.8: * @file ../scripts/mypy_leo.py
# @@language python

"""
mypy_leo.py: Run mypy on Leo's files.

Info item #3867 describes all of Leo's test scripts:
https://github.com/leo-editor/leo-editor/issues/2867

EKR's mypy-leo.cmd:
    cd {path-to-leo-editor}
    python -m leo.scripts.mypy_leo
"""

import os
import subprocess
import sys

print(os.path.basename(__file__))

# cd to leo-editor
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
os.chdir(leo_editor_dir)

# args = ' '.join(sys.argv[1:])
python = sys.executable
if 0:  # Test all files.
    files = ['leo/core']  # 1054 errors.
else:  # Test only specific files.
    files = [
        # The six files to be checked.
        'leo/core/leoApp.py',
        'leo/core/leoAtFile.py',
        'leo/core/leoCommands.py',
        'leo/core/leoKeys.py',
        'leo/core/leoGlobals.py',
        'leo/core/leoNodes.py',
        # Additional files containing complaints when following imports.
        'leo/plugins/mod_scripting.py',
        'leo/plugins/qt_commands.py',
        'leo/plugins/qt_frame.py',
        'leo/plugins/qt_gui.py',
        'leo/plugins/qt_idle_time.py',
        'leo/plugins/qt_layout.py',
        'leo/plugins/qt_text.py',
        # 'leo/plugins/qt_tree.py',
        'leo/plugins/viewrendered.py',
        # 'leo/plugins/viewrendered3.py',
    ]
# Apparently 'strict-optional' doesn't work.
incremental = True
follow = False  # False: 436 errors. True: 443 errors.
incremental_arg = '' if incremental else '--no-incremental'
follow_kind = 'normal' if follow else 'skip'
args = f"--follow-imports={follow_kind} {incremental_arg}"
files = ' '.join(files)
command = rf"{python} -m mypy {args} {files}"
subprocess.Popen(command, shell=True).communicate()
# @-leo
