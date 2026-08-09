# @+leo-ver=5-thin
# @+node:ekr.20260809120840.1: * @file ../scripts/ty_leo.py
"""
ty_leo.py: Run ty on all of Leo.
"""

import os
import subprocess
import sys

print(os.path.basename(__file__))

# cd to leo-editor
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
os.chdir(leo_editor_dir)

args = ' '.join(sys.argv[1:])
python = sys.executable
command = rf'{python} -m ty check leo {args}'
subprocess.run(command)
# @-leo
