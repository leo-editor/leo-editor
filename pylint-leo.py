import os
import sys
from pylint import lint

core_table = (
    # ('leoGlobals.py',''),
    # ('leoApp.py',''),
    # ('leoAtFile.py',''),
    #  ('leoChapters.py',''),
    # ('leoCommands.py',''),
    # ('leoEditCommands.py','W0511'),
    # ('leoFileCommands.py',''),
    # ('leoFind.py',''),
    # ('leoFrame.py',''),
    # ('leoGlobals.py',''), # E0602:4528:isBytes: Undefined variable 'bytes'
    # ('leoGui.py','W0511'), # W0511: to do
    # ('leoImport.py',''),
    # ('leoMenu.py',''),
    # ('leoNodes.py',''),
    # ('leoPlugins.py',''),
    # ('leoShadow.py',''),
    # ('leoTangle.py',''),
    # ('leoUndo.py',''),
)

plugins_table = (
    # ('qtGui.py','W0221'),
    # ('mod_scripting.py','E0611'),
        # Harmless: E0611:489:scriptingController.runDebugScriptCommand:
        # No name 'leoScriptModule' in module 'leo.core'
    # ('open_with.py',''),
    # ('toolbar.py','E1101,W0221,W0511'),
        # Dangerous: many erroneous E1101 errors
        # Harmless: W0221: Arguments number differs from overridden method
        # Harmless: W0511: Fixme and to-do.
    # ('UNL.py',''),
    # ('vim.py',''),
    # ('xemacs.py',''),
)

def run(fn,suppress):
    args = ['--rcfile=leo/test/pylint-leo-rc.txt']
    if suppress: args.append('--disable-msg=%s' % (suppress))
    args.append(fn)
    if os.path.exists(fn):
        print('*****',fn,suppress)
        lint.Run(args)
    else:
        print('file not found:',fn)

for fn,suppress in core_table:
    fn = os.path.join('c:\leo.repo','trunk','leo','core',fn)
    run(fn,suppress)
    
for fn,suppress in plugins_table:
    fn = os.path.join('c:\leo.repo','trunk','leo','plugins',fn)
    run(fn,suppress)
