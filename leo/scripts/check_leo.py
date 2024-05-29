#@+leo-ver=5-thin
#@+node:ekr.20240529053756.1: * @file ../scripts/check_leo.py
"""
check_leo.py: Experimental script that checks for undefined methods.
"""
#@+<< imports: check_leo.py >>
#@+node:ekr.20240529055116.1: ** << imports: check_leo.py >>
import os
import sys

# Add the leo/editor folder to sys.path.
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
if leo_editor_dir not in sys.path:
    sys.path.insert(0, leo_editor_dir)
    
leo_dir = os.path.abspath(os.path.join(leo_editor_dir, 'leo'))
    
# No need to change
if 0:
    os.chdir(leo_dir)
    print('cwd:', os.getcwd())

from leo.core import leoGlobals as g

assert g
assert os.path.exists(leo_editor_dir), leo_editor_dir
assert os.path.exists(leo_dir), leo_dir
#@-<< imports: check_leo.py >>

print('check_leo.py: done!')
#@-leo
