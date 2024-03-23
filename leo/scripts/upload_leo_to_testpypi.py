#@+leo-ver=5-thin
#@+node:ekr.20240321123225.2: * @file ../scripts/upload_leo_to_testpypi.py
#@@language python

"""
upload_leo_to_testpypi.py: Run `python -m twine upload -r testpypi dist/*.*`.

Info item #3837 describes all distribution-related scripts.
https://github.com/leo-editor/leo-editor/issues/3837
"""

import os
import subprocess

print(os.path.basename(__file__))

# cd to leo-editor
os.chdir(os.path.abspath(os.path.join(__file__, '..', '..', '..')))

# Upload
if 0:  # Don't do this until we are ready to release.
    command = 'python -m twine upload -r testpypi dist/*.*'
    print(command)
    subprocess.Popen(command, shell=True).communicate()
#@-leo
