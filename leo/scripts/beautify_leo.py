#@+leo-ver=5-thin
#@+node:ekr.20240322065528.1: * @file ../scripts/beautify_leo.py
#@@language python

"""
beautify_leo.py: beautify Leo's most important files with the leoTokens beautifier.

Works regardless of whether mypyc has compiled leoTokens.py!
"""
import os
import sys

# Make sure leo-editor is on the path.
leo_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
if leo_dir not in sys.path:
    sys.path.insert(0, leo_dir)

from leo.core import leoGlobals as g

print('beautify_leo.py')
os.chdir(leo_dir)

args = '--all --beautified --report --write'
g.execute_shell_commands([
    fr'python -c "import leo.core.leoTokens" {args} leo\commands',
    fr'python -c "import leo.core.leoTokens" {args} leo\commands',
    fr'python -c "import leo.core.leoTokens" {args} --write leo\plugins',
    fr'python -c "import leo.core.leoTokens" {args} leo\modes',
    fr'python -c "import leo.core.leoTokens" {args} leo\unittests\commands',
    fr'python -c "import leo.core.leoTokens" {args} leo\unittests\plugins',
    fr'python -c "import leo.core.leoTokens" {args} leo\unittests\misc_tests',
])
#@-leo
