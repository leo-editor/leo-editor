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
    # 112 errors.
    files = [
        'leo/core/leoGlobals.py',
        'leo/core/leoNodes.py',
        'leo/core/leoCommands.py',
        'leo/core/leoAtFile.py',
        'leo/core/leoKeys.py',
        'leo/core/leoApp.py',
    ]
# Apparently 'strict-optional' doesn't work.
incremental = False
incremental_arg = '' if incremental else '--no-incremental'
args = f"--follow-imports=skip {incremental_arg}"
files = ' '.join(files)
command = rf"{python} -m mypy {args} {files}"
subprocess.Popen(command, shell=True).communicate()
# @-leo
