#@+leo-ver=5-thin
#@+node:ekr.20240323050520.1: * @file ../scripts/beautify_all_leo.py
#@@language python

"""
beautify_all_leo.py: beautify all of Leo's most important files.

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

# args = ' '.join(sys.argv[1:])
args = '--all --beautified --write --report'
isWindows = sys.platform.startswith('win')
python = 'py' if isWindows else 'python'

for command in [
    fr'{python} -c "import leo.core.leoTokens" {args} leo\commands',
    fr'{python} -c "import leo.core.leoTokens" {args} leo\commands',
    fr'{python} -c "import leo.core.leoTokens" {args} leo\plugins',
    fr'{python} -c "import leo.core.leoTokens" {args} leo\modes',
    fr'{python} -c "import leo.core.leoTokens" {args} leo\unittests\commands',
    fr'{python} -c "import leo.core.leoTokens" {args} leo\unittests\plugins',
    fr'{python} -c "import leo.core.leoTokens" {args} leo\unittests\misc_tests',
]:
    subprocess.Popen(command, shell=True).communicate()
#@-leo
