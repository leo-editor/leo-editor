# @+leo-ver=5-thin
# @+node:ekr.20240321122413.8: * @file ../scripts/mypy_leo.py
"""
mypy_leo.py: Run mypy on Leo's files.

Info item #3867 describes all of Leo's test scripts:
https://github.com/leo-editor/leo-editor/issues/2867

EKR's mypy-leo.cmd:
    cd {path-to-leo-editor}
    python -m leo.scripts.mypy_leo
"""

# @+<< mypy_leo.py: imports & startup >>
# @+node:ekr.20260703122126.1: ** << mypy_leo.py: imports & startup >>
import os
import subprocess
import sys

print(os.path.basename(__file__))

# cd to leo-editor
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
os.chdir(leo_editor_dir)
# @-<< mypy_leo.py: imports & startup >>
incremental = True
follow = False
if 1:  # Test all files.
    files = [
        'leo',
    ]
else:
    files = [
        # Files to check with strict_optional in .mypy.ini.
        'leo/core/leoApp.py',
        'leo/core/leoGlobals.py',
        'leo/core/leoCommands.py',
        'leo/core/leoNodes.py',

        # Follow-on files, with errors uncovered by checking leoCommands.py.
        'leo/commands/abbrevCommands.py',
        'leo/core/leoExternalFiles.py',
        'leo/core/leoserver.py',

        # To be checked in other PRs...
        #   'leo/core/leoApp.py',
        #   'leo/core/leoAtFile.py',
        #   'leo/core/leoKeys.py',
        #   'leo/plugins/mod_scripting.py',
        #   'leo/plugins/qt_commands.py',
        #   'leo/plugins/qt_frame.py',
        #   'leo/plugins/qt_gui.py',
        #   'leo/plugins/qt_idle_time.py',
        #   'leo/plugins/qt_layout.py',
        #   'leo/plugins/qt_text.py',
        #   'leo/plugins/qt_tree.py',
        # 'leo/plugins/viewrendered.py',
        #   'leo/plugins/viewrendered3.py',
    ]  # fmt: skip

python = sys.executable
incremental_arg = '' if incremental else '--no-incremental'
follow_kind = 'normal' if follow else 'skip'
# args = ' '.join(sys.argv[1:])
args = f"--follow-imports={follow_kind} {incremental_arg}"
files = ' '.join(files)
command = rf"{python} -m mypy {args} {files}"
# print(f"{command=}")
subprocess.Popen(command, shell=True).communicate()

# @@language python
# @-leo
