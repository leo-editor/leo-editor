#@+leo-ver=5-thin
#@+node:ekr.20240322065528.1: * @file ../scripts/beautify_leo.py
#@@language python

"""
beautify_leo.py: Beautify only *changed* files.

Works regardless of whether mypyc has compiled leoTokens.py!

Info item #3867 describes all of Leo's test scripts:
https://github.com/leo-editor/leo-editor/issues/2867

EKR's beautify-leo.cmd:
    cd {path-to-leo-editor}
    python -m leo.scripts.beautify_leo
"""

import os
import subprocess
import sys

print(os.path.basename(__file__))

# cd to leo-editor
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
os.chdir(leo_editor_dir)

# Beautify only changed files. Issue a report only if files have changed.
args = '--beautified --write'
isWindows = sys.platform.startswith('win')
python = 'py' if isWindows else 'python'

for command in [
    f'{python} -c "import leo.core.leoTokens" {args} leo/commands',
    f'{python} -c "import leo.core.leoTokens" {args} leo/core',
    f'{python} -c "import leo.core.leoTokens" {args} leo/scripts',
    f'{python} -c "import leo.core.leoTokens" {args} leo/plugins',
    f'{python} -c "import leo.core.leoTokens" {args} leo/modes',
    f'{python} -c "import leo.core.leoTokens" {args} leo/unittests/commands',
    f'{python} -c "import leo.core.leoTokens" {args} leo/unittests/plugins',
    f'{python} -c "import leo.core.leoTokens" {args} leo/unittests/misc_tests',
]:
    subprocess.Popen(command, shell=True).communicate()
#@-leo
