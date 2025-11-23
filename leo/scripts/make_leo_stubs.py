#@+leo-ver=5-thin
#@+node:ekr.20251123134502.1: * @file ../scripts/make_leo_stubs.py
"""
A script to create stub (.pyi) files for Leo's most important files.
"""
#@+<< make_leo_stubs: imports >>
#@+node:ekr.20251123142543.1: ** << make_leo_stubs: imports >>
import glob
import os
import sys

# cd to leo-editor.
leo_editor_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
assert leo_editor_dir.endswith('leo-editor'), repr(leo_editor_dir)
assert os.path.exists(leo_editor_dir), repr(leo_editor_dir)
assert os.path.isdir(leo_editor_dir), repr(leo_editor_dir)
os.chdir(leo_editor_dir)

# Add leo_editor_dir to sys.path.
if leo_editor_dir not in sys.path:
    sys.path.insert(0, leo_editor_dir)

# Do the Leo imports.
import leo.core.leoBridge as leoBridge
from leo.plugins.importers.python import Python_Importer
#@-<< make_leo_stubs: imports >>
#@+<< calculate test files >>
#@+node:ekr.20251123141418.1: ** << calculate test files >>
core_files = glob.glob(f"{leo_editor_dir}{os.sep}leo{os.sep}core{os.sep}*.py")
if 1:
    include = [
        'leoApp',
        'leoAtFile',
        # 'leoCommands'
    ]
    test_files = [os.path.normpath(z) for z in core_files if any(z2 in z for z2 in include)]
else:
    exclude = ['__', 'runLeo',
        'leoclient', 'leoHistory', 'leoJupytext',
        'leoPymacs', 'leoQt', 'leoTips', 'leoVersion',
    ]
    test_files = [os.path.normpath(z) for z in core_files if not any(z2 in z for z2 in exclude)]

# g.printObj(test_files, tag='Test files...')
#@-<< calculate test files >>
controller = leoBridge.controller(
    gui='nullGui',
    loadPlugins=False,  # True: attempt to load plugins.
    readSettings=False,  # True: read standard settings files.
    silent=True,  # True: don't print signon messages.
    verbose=False)  # True: print informational messages.
c = None
g = controller.globals()
for file_name in test_files:
    if not c:
        c = controller.openLeoFile('make_leo_stubs')  ### file_name
        print(c)
    sfn = g.shortFileName(file_name)
    print(f"Processing {sfn}")
    importer = Python_Importer(c)
    # print(importer)
#@-leo
