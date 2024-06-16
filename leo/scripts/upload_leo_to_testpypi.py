#@+leo-ver=5-thin
#@+node:ekr.20240321123225.2: * @file ../scripts/upload_leo_to_testpypi.py
#@@language python

"""
upload_leo_to_testpypi.py: Run `python -m twine upload -r testpypi dist/*.*`.

See info item #3837 for full documentation.
https://github.com/leo-editor/leo-editor/issues/3837
"""

import os
import subprocess

print(os.path.basename(__file__))

# cd to the `leo-editor` directory.
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
assert leo_editor_dir.endswith('leo-editor')
os.chdir(leo_editor_dir)

# Upload
if 0:  # Don't do this until we are ready to release.
    command = 'python -m twine upload -r testpypi dist/*.*'
    print(command)
    subprocess.Popen(command, shell=True).communicate()
#@-leo
