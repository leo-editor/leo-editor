#@+leo-ver=5-thin
#@+node:ekr.20240321122822.1: * @file ../scripts/build_leo.py
#@@language python
import glob
import os
import sys

# Make sure leo-editor is on the path.
leo_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
if leo_dir not in sys.path:
    # print(f"add {leo_dir!r} to sys.path")
    sys.path.insert(0, leo_dir)
from leo.core import leoGlobals as g

g.cls()
print('build_leo.py')
os.chdir(leo_dir)

# delete leo/dist/*.*
for z in glob.glob(f"{leo_dir}{os.sep}dist{os.sep}*.*"):
    os.remove(z)

# build *both* sdist and wheel.
command = 'python -m build > build_log.txt'
g.execute_shell_commands(command)

# print('build_leo.py: done')
#@-leo
