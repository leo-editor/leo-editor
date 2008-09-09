#@+leo-ver=4-thin
#@+node:ekr.20080827092958.3:@thin pre-install-script.py
import _winreg as wr
import sys, os

version = '4-5-final'
testing = False

# To uninstall.
# Set edit .leo files to:
#    c:\python25\python.exe c:\leo.repo\trunk\launchLeo.py %1 %2
# Set icon to C:\leo.repo\trunk\leo\Icons\LeoDoc.ico

#@+others
#@+node:ekr.20080909112433.2:findPython
# The path to Leo will be python/Lib/site-packages/leo.
# To get this, we look for entries in sys.path whose first component starts with python.

def findPython(path=None):

    trace = True

    abspath, exists, join = os.path.abspath, os.path.exists, os.path.join

    if path: paths = [path]
    else:    paths = sys.path

    for path in paths:
        drive,tail = os.path.splitdrive(path)
        if trace: print 'drive',drive,'tail',tail
        parts = tail.split('\\') # Hard code os.sep for Windows.
        for part in parts:
            if part.startswith('python'):
                python = join(drive,'\\',part) # Don't use abspath here!
                if trace: print '**found**',python
                return python

    return None
#@-node:ekr.20080909112433.2:findPython
#@+node:ekr.20080909112433.3:def setRegistry
def setRegistry(python,testing):

    use_console = False

    abspath, exists, join = os.path.abspath, os.path.exists, os.path.join

    # Python paths...
    exe     = abspath(join(python,'pythonw.exe'))
    pythonw = abspath(join(os.path.dirname(exe), 'pythonw.exe'))

    # Installed Leo paths...
    top     = abspath(join(python,'Lib','site-packages','Leo-%s' % (version)))
    runLeo  = abspath(join(top,'leo','core','runLeo.py'))
    icon    = abspath(join(top,'leo','icons','LeoDoc.ico'))

    if testing:
        print ('exists %s, python:   %s' % (exists(python),python))
        print ('exists %s, top:      %s' % (exists(top), top))
        print ('exists %s, runLeo:   %s' % (exists(runLeo), runLeo))
        print ('exists %s, icon:     %s' % (exists(icon), icon))

    if use_console and os.path.basename(exe) == 'python.exe': # Avoid showing the console
        exe = pythonw

    # This is the 'pythonw.exe leo.py %1' part
    if testing:
        # Leo hasn't necessarily been installed anywhere: use the trunk.
        s = 'import os; os.chdir(r\'%s\'); import leo.core.runLeo as r; r.run(fileName=r\'%%1\')'
        c_option =  s % top
        if use_console: i_option = '-i'
        else:           i_option = ''
        leo_command = '"%s" %s -c "%s"' % (exe, i_option, c_option) 
    else:
        leo_command = '"%s" "%s" "%%1"' % (exe, runLeo)

    # Magic registry stuff follows...
    # Get the handle.
    h = wr.ConnectRegistry(None, wr.HKEY_CLASSES_ROOT)
    sz = wr.REG_SZ

    # Create the file extension association (assoc .leo on commandline).
    wr.SetValue(h, ".leo", sz, "LeoFile")

    # Creates the 'LeoFile' file type and sets the file type association.
    # (ftype LeoFile at the commandline)
    wr.SetValue(h, r"LeoFile\shell\open\command", sz, leo_command)
    wr.SetValue(h, r"LeoFile\shell", sz, "open") # I don't know if this is needed

    # Point to the icon.
    wr.SetValue(h, r"LeoFile\DefaultIcon", sz, icon)
    wr.SetValue(h, r"LeoFile", sz, "Leo File") # I think this is just for explorer
#@-node:ekr.20080909112433.3:def setRegistry
#@-others

if testing: print '=' * 40

# path = r'c:\xp\python25\python.exe' # Previously failed.
path = None

python = findPython(path=path)

if python:
    setRegistry(python,testing)

if testing: print ('done')
#@-node:ekr.20080827092958.3:@thin pre-install-script.py
#@-leo
