#@+leo-ver=5-thin
#@+node:ekr.20250227032644.1: * @file ../scripts/pyflakes_leo.py
"""
pyflakes.py: Run pyflakes on (most) .py files in LeoPyRef.leo.

Info item #3867 describes all of Leo's test scripts:
https://github.com/leo-editor/leo-editor/issues/2867
"""

import glob
import os
import sys

print(os.path.basename(__file__))

try:
    from pyflakes import api, reporter
except Exception:
    print('pyflakes not found')

leo_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
# print('leo_dir', leo_dir)
n_files = 0
directories = (
    'core',
    'scripts',
    'plugins',
)
suppress = (
    'leoflexx.py',  # Can't handle the 'undefined' and 'window' JS vars.
    'qt_main.py',  # Generated automaticlly.
)
if api and reporter:
    for directory in directories:
        directory = os.path.normpath(os.path.join(leo_dir, directory))
        paths = glob.glob(f"{directory}{os.sep}*.py")
        for path in paths:
            if path.endswith(suppress):
                continue
            n_files += 1
            try:
                with open(path, 'rb') as f:
                    contents = f.read().decode()
                report = reporter.Reporter(errorStream=sys.stderr, warningStream=sys.stderr)
                errors = api.check(contents, '', report)
                if errors:
                    print(f"{errors} errors in {path}")
            except Exception as e:
                print(f"Exception in {path}: {e}")
# print('pyflakes_leo: files:', n_files)
#@-leo
