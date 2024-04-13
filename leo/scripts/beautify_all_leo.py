#@+leo-ver=5-thin
#@+node:ekr.20240323050520.1: * @file ../scripts/beautify_all_leo.py
#@@language python

"""
beautify_all_leo.py: Beautify all of Leo's most important files.

Works regardless of whether mypyc has compiled leoTokens.py!

Info item #3867 describes all of Leo's test scripts:
https://github.com/leo-editor/leo-editor/issues/2867
"""

import os
import subprocess
import sys

print(os.path.basename(__file__))

# cd to leo-editor
os.chdir(os.path.abspath(os.path.join(__file__, '..', '..', '..')))

# Beautify all, and always issue a report.
args = '--all --beautified --write'  #  --report'
isWindows = sys.platform.startswith('win')
python = 'py' if isWindows else 'python'

for command in [
    f'{python} -c "import leo.core.leoTokens" {args} leo/commands',
    f'{python} -c "import leo.core.leoTokens" {args} leo/core',
    f'{python} -c "import leo.core.leoTokens" {args} leo/plugins',
    f'{python} -c "import leo.core.leoTokens" {args} leo/scripts',
    f'{python} -c "import leo.core.leoTokens" {args} leo/modes',
    f'{python} -c "import leo.core.leoTokens" {args} leo/unittests/commands',
    f'{python} -c "import leo.core.leoTokens" {args} leo/unittests/plugins',
    f'{python} -c "import leo.core.leoTokens" {args} leo/unittests/misc_tests',
]:
    subprocess.Popen(command, shell=True).communicate()
#@-leo
