#@+leo-ver=5-thin
#@+node:ekr.20170805060844.1: * @file ../test/leo-bridge-test.py
"""A simple test bed for the leoBridge module."""
# pylint: disable=invalid-name
import os
import sys
# Adjust the path before importing
# pylint: disable=wrong-import-order,wrong-import-position
dir_ = os.path.abspath('.')
if dir_ not in sys.path:
    # print(f"appending {dir_} to sys.path")
    sys.path.append(dir_)
from leo.core import leoBridge

# Leo files.
files = [
    'c:/leo.repo/leo-editor/leo/test/unitTest.leo',
    'c:/leo.repo/leo-editor/leo/test/test.leo',
    'c:/xyzzy.xxx',
]

# Switches...
kill_leo_output = True  # True: kill all output produced by g.es_print.
silent = True

controller = leoBridge.controller(
    gui='nullGui',  # 'nullGui', 'qt'
    loadPlugins=False,  # True: attempt to load plugins.,
    readSettings = True,  # True: read standard settings files.
    silent=silent,  # True: don't print signon messages.
    verbose=True,
)
g = controller.globals()

# This kills all output from commanders.
if kill_leo_output:

    def do_nothing(*args, **keys):
        pass

    g.es_print = do_nothing

for path in files:
    if os.path.exists(path):
        c = controller.openLeoFile(path)
        if c:
            n = 0
            for p in c.all_positions():
                n += 1
            if not silent:
                print(f"{c.shortFileName()} has {n} nodes")
        else:
            assert False, path  # For unit testing
    elif not silent:
        if path.endswith('xyzzy.xxx'):
            print(f"file not found: {path}")
        else:
            assert False, path  # For unit testing
#@-leo
