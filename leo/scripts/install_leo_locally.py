#@+leo-ver=5-thin
#@+node:ekr.20240321123214.1: * @file ../scripts/install_leo_locally.py
#@@language python

"""
install_leo_locally.py: Install leo from a wheel file in the `leo/dist` folder.

Info item #3837 describes all distribution-related scripts.
https://github.com/leo-editor/leo-editor/issues/3837
"""

import glob
import os
import sys
import subprocess

print(os.path.basename(__file__))

# Do *not* install from leo-editor!
home_dir = os.path.expanduser("~")
os.chdir(home_dir)

# Install.
dist_dir = os.path.abspath(os.path.join(__file__, '..', '..', 'dist'))
assert os.path.exists(dist_dir), dist_dir
wheel_file = 'leo-6.7.9a1-py3-none-any.whl'
command = fr"python -m pip install {dist_dir}{os.sep}{wheel_file}"
print(command)
subprocess.Popen(command, shell=True).communicate()

# List site-packages/leo*.
python_dir = os.path.dirname(sys.executable)
package_dir = os.path.abspath(os.path.join(python_dir, 'Lib', 'site-packages'))
print('')
print('site-packages/leo*...')
for z in glob.glob(f"{package_dir}{os.sep}leo*"):
    print(z)
#@-leo
