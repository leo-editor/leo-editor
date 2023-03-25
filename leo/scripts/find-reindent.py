"""Find reindent.py script.

Writes the path to a file named "reindent-dir.txt" in the user's .leo directory.
"""

import sys, os, os.path

SUFFIX = r'Tools\Scripts\reindent.py'
LEO_HOME_DIR = os.environ['USERPROFILE'] + r'\.leo'
PATH_FILE = LEO_HOME_DIR + r'\reindent-path.txt'

path = None
for p in sys.path:
    candidate = os.path.join(p, SUFFIX)
    if os.path.exists(candidate):
        path = candidate
        break

if path:
     with open(PATH_FILE, 'w', encoding = 'utf-8') as f:
         f.write(path)
