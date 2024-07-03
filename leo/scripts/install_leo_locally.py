#@+leo-ver=5-thin
#@+node:ekr.20240321123214.1: * @file ../scripts/install_leo_locally.py
#@@language python
"""
install_leo_locally.py: Install Leo from a wheel file in the `leo-editor/leo/dist` directory.

Run `python -m pip install leo-editor/dist/leo-6.8.0-py3-none-any.whl`
from the *parent* directory of the `leo-editor` directory.

*Note*: sys.path *must not* contain the `leo-editor` directory!

See info item #3837 for full documentation.
https://github.com/leo-editor/leo-editor/issues/3837
"""
import glob
import os
import sys
import subprocess

file_name = os.path.basename(__file__)

if any('leo-editor' in z for z in sys.path):
    print(f"{file_name}: remove leo-editor from sys.path!")
    print('Hint: do *not* run this script from the leo-editor directory!')
else:
    print(file_name)

    # Install from the *parent* of the `leo-editor` directory.
    leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
    parent_dir = os.path.abspath(os.path.join(leo_editor_dir, '..'))
    assert os.path.exists(parent_dir), repr(parent_dir)
    assert os.path.isdir(parent_dir), repr(parent_dir)
    assert not parent_dir.endswith('leo-editor'), repr(parent_dir)
    os.chdir(parent_dir)

    # Install Leo using `pip install leo`
    dist_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..', 'dist'))
    assert os.path.exists(dist_dir), repr(dist_dir)
    assert os.path.isdir(dist_dir), repr(dist_dir)
    wheel_file = 'leo-6.8.0-py3-none-any.whl'
    command = fr"python -m pip install {dist_dir}{os.sep}{wheel_file} --no-cache-dir"  #  --force-reinstall
    print(command)
    subprocess.Popen(command, shell=True).communicate()

    # List site-packages/leo*.
    python_dir = os.path.dirname(sys.executable)
    package_dir = os.path.abspath(os.path.join(python_dir, 'Lib', 'site-packages'))
    print('')
    print('package_dir:', package_dir)
    print('site-packages/leo*...')
    for z in glob.glob(f"{package_dir}{os.sep}leo*"):
        print(' ', z)
#@-leo
