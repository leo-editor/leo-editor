#@+leo-ver=5-thin
#@+node:ekr.20240322065528.1: * @file ../scripts/beautify_leo.py
#@@language python

"""
beautify_leo.py: beautify Leo's most important files with the leoTokens beautifier.

Works regardless of whether mypyc has compiled leoTokens.py!
"""

import os
import subprocess
import sys

# cd to leo-editor
os.chdir(os.path.abspath(os.path.join(__file__, '..', '..', '..')))

args = ' '.join(sys.argv[1:])
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
