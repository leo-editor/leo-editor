#@+leo-ver=5-thin
#@+node:ekr.20240321123225.2: * @file ../scripts/upload_leo_to_testpypi.py
#@@language python

import os
import sys

# Make sure leo-editor is on the path.
leo_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
if leo_dir not in sys.path:
    sys.path.insert(0, leo_dir)
from leo.core import leoGlobals as g

print('upload_leo_to_testpypi.py')
os.chdir(leo_dir)

# Upload
if 0:  # Don't do this until we are ready to release.
    command = 'python -m twine upload -r testpypi dist/*.*'
    g.execute_shell_commands(command)
#@-leo
