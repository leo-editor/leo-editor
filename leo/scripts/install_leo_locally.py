#@+leo-ver=5-thin
#@+node:ekr.20240321123214.1: * @file ../scripts/install_leo_locally.py
#@@language python

import glob
import os
import sys

# Make sure leo-editor is on the path.
leo_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
if leo_dir not in sys.path:
    sys.path.insert(0, leo_dir)
from leo.core import leoGlobals as g

g.cls()
print('install_leo_locally.py')

# Do *not* install from leo-editor!
home_dir = os.path.expanduser("~")
os.chdir(home_dir)

# Install.
wheel_file = 'leo-6.7.9a1-py3-none-any.whl'
command = fr"python -m pip install {leo_dir}{os.sep}dist{os.sep}{wheel_file}"
g.execute_shell_commands(command)

# List site-packages/leo*.
python_dir = os.path.dirname(sys.executable)
package_dir = os.path.abspath(os.path.join(python_dir, 'Lib', 'site-packages'))
print('')
print('site-packages/leo*...')
for z in glob.glob(f"{package_dir}{os.sep}leo*"):
    print(z)
#@-leo
