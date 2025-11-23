#@+leo-ver=5-thin
#@+node:ekr.20251123134502.1: * @file ../scripts/make_leo_stubs.py
"""
A script to create stub (.pyi) files for Leo's most important files.
"""

import glob
import os
from leo.core import leoGlobals as g
from leo.plugins.importers.python import Python_Importer

g.cls()

#@+<< calculate test files >>
#@+node:ekr.20251123141418.1: ** << calculate test files >>
core_dir = g.app.loadDir
core_files = glob.glob(f"{g.app.loadDir}{os.sep}*.py")
if 1:
    include = ['leoApp', 'leoAtFile', 'leoCommands']
    test_files = [os.path.normpath(z) for z in core_files if any(z2 in z for z2 in include)]
else:
    exclude = ['__', 'runLeo', 'leoclient', 'leoHistory', 'leoJupytext',
        'leoPymacs', 'leoQt', 'leoTips', 'leoVersion',
    ]
    test_files = [os.path.normpath(z) for z in core_files if not any(z2 in z for z2 in exclude)]
g.printObj(test_files, tag='Test files...')
#@-<< calculate test files >>
#@-leo
