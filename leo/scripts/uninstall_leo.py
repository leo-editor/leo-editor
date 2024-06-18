#@+leo-ver=5-thin
#@+node:ekr.20240321123225.1: * @file ../scripts/uninstall_leo.py
#@@language python

"""
uninstall_leo.py: Run `pip uninstall leo` from the *parent* directory of the `leo-editor` directory.

*Note*: sys.path *must not* contain the `leo-editor` directory!

See info item #3837 for full documentation.
https://github.com/leo-editor/leo-editor/issues/3837
"""
import os
import shutil
import sys
import subprocess

file_name = os.path.basename(__file__)

if any('leo-editor' in z for z in sys.path):
    print(f"{file_name}: remove leo-editor from sys.path!")
    print('Hint: do *not* run this script from the leo-editor directory!')
else:
    print(os.path.basename(__file__))

    # Uninstall from the *parent* of the `leo-editor` directory.
    leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
    parent_dir = os.path.abspath(os.path.join(leo_editor_dir, '..'))
    assert os.path.exists(parent_dir), repr(parent_dir)
    assert os.path.isdir(parent_dir), repr(parent_dir)
    assert not parent_dir.endswith('leo-editor'), repr(parent_dir)
    os.chdir(parent_dir)

    # Remove Leo from Python's site-packages directory.
    # --yes: Don’t ask for confirmation of uninstall deletions.
    command = 'python -m pip uninstall leo'
    print(command)
    subprocess.Popen(command, shell=True).communicate()

    if 0:  # This hack should no longer be necessary.
        # Delete the leo/leo.egg-info directory.
        egg_dir = os.path.abspath(os.path.join(leo_editor_dir, 'leo.egg-info'))
        print('')
        if os.path.exists(egg_dir):
            print(f"removed: {egg_dir}")
            shutil.rmtree(egg_dir)
#@-leo
