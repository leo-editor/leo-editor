'''A simple test bed for the leoBridge module.'''
import os
import sys
abspath, join = os.path.abspath, os.path.join
dir_ = abspath('.')
if dir_ not in sys.path:
    # print('append to sys.path: %s' % dir_)
    sys.path.append(dir_)
# import leo.core.leoQt as leoQt
    # Required only if we want to use the qt gui.
import leo.core.leoBridge as leoBridge
# print('sys.path:...\n%s' % '\n'.join(sorted(sys.path)))
# print('sys.argv: %s %s' % (len(sys.argv), '\n'.join(sys.argv)))

controller = leoBridge.controller(
    gui='nullGui',
    # gui='qt', # not qttabs
    loadPlugins=False,  # True: attempt to load plugins.
    readSettings=False, # True: read standard settings files.
    silent=True,      # True: don't print signon messages.
    verbose=True)     # True: print informational messages.
g = controller.globals()
# c = controller.openLeoFile(path)
