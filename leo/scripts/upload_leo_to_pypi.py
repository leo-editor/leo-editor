#@+leo-ver=5-thin
#@+node:ekr.20240321123225.4: * @file ../scripts/upload_leo_to_pypi.py
#@@language python

"""
upload_leo_to_pypi.py: Run `python -m twine upload -r pypi dist/*.*`.

See info item #3837 for full documentation.
https://github.com/leo-editor/leo-editor/issues/3837
"""

import os
import subprocess

print(os.path.basename(__file__))

# cd to `leo-editor`.
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
assert leo_editor_dir.endswith('leo-editor'), repr(leo_editor_dir)
assert os.path.exists(leo_editor_dir), repr(leo_editor_dir)
assert os.path.isdir(leo_editor_dir), repr(leo_editor_dir)
os.chdir(leo_editor_dir)

command = 'python -m twine upload -r pypi dist/*.* --verbose'

# Upload.
if 1:  # Don't do this until we are ready to release.
    print(command)
    subprocess.Popen(command, shell=True).communicate()
else:
    print(f"Skipped: {command}")
#@-leo
