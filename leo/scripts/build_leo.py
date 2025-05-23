#@+leo-ver=5-thin
#@+node:ekr.20240321122822.1: * @file ../scripts/build_leo.py
#@@language python

"""
build_leo.py: Build Leo as follows:

- Delete all files in the `leo-editor/leo/dist` directory.
- Run `python -m build > build_log.txt`.

See info item #3837 for full documentation.
https://github.com/leo-editor/leo-editor/issues/3837
"""
import glob
import os
import subprocess

print(os.path.basename(__file__))

# cd to leo-editor.
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
assert leo_editor_dir.endswith('leo-editor'), repr(leo_editor_dir)
assert os.path.exists(leo_editor_dir), repr(leo_editor_dir)
assert os.path.isdir(leo_editor_dir), repr(leo_editor_dir)
os.chdir(leo_editor_dir)

# delete leo/dist/*.*
dist_dir = os.path.abspath(os.path.join(leo_editor_dir, 'dist'))
assert os.path.exists(dist_dir), dist_dir
for z in glob.glob(f"{dist_dir}{os.sep}*.*"):
    os.remove(z)

# build *both* sdist and wheel.
command = 'python -m build > build_log.txt'
print('')
print(command)
print('')
subprocess.Popen(command, shell=True).communicate()

print('See build_log.txt')
#@-leo
