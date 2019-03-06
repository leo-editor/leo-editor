import os
import sys
print(sys.executable)   # python.exe, pythonw.exe
print(sys.exec_prefix)  # python.exe's directory

# Leo's library path (ie: ./leo-editor/leo or PYTHONHOME/Lib/site-packages/leo)
import leo
leolibpath = leo.__path__
print(leolibpath)

## We don't use leoGlobals.computeLoadDir() because it doesn't work 
## without instantiating g.app first, and that's too much for just this
# import leo.core.runLeo
# import leo.core.leoGlobals as g
# g.es_print(g.computeLeoDir())


# Leo's launch exe, if in PATH. Py3 only, cross platform
import shutil
print(shutil.which('leo'))

