#@+leo-ver=4-thin
#@+node:ekr.20080913110741.1:@thin leo-post-install-script.py
# Leo's post-install script

#@<< imports >>
#@+node:ekr.20080913110741.3:<< imports >>
import _winreg as wr
import os
import shutil
import sys
#@-node:ekr.20080913110741.3:<< imports >>
#@nl

version = '4-5-1-final'
testing = True

# To uninstall.
# Set edit .leo files to:
#    c:\python25\python.exe c:\leo.repo\trunk\launchLeo.py %1 %2
# Set icon to C:\leo.repo\trunk\leo\Icons\LeoDoc.ico

abspath, exists, join = os.path.abspath, os.path.exists, os.path.join

#@+others
#@+node:ekr.20080913110741.4:install & helpers
def install():

    python = findPython()

    if python:
        copyPostInstallScript(python)
        setRegistry(python)
#@+node:ekr.20080913110741.5:copyPostInstallScript
def copyPostInstallScript(python):

    path = sys.argv[0]
    assert path,'leo-post-install-script: no sys.argv[0]'
    path = os.path.normpath(os.path.abspath(path))
    # print ('path: %s' % path)
    scripts = os.path.join(python,'Scripts')
    shutil.copy(path,scripts)
#@-node:ekr.20080913110741.5:copyPostInstallScript
#@+node:ekr.20080909112433.2:findPython
# The path to Leo will be python/Lib/site-packages/leo.
# To get this, we look for entries in sys.path whose first component starts with python.

def findPython(path=None):

    trace = False

    if path: paths = [path]
    else:    paths = sys.path

    for path in paths:
        drive,tail = os.path.splitdrive(path)
        result = [drive,'\\']
        # if trace: print 'drive',drive,'tail',tail
        parts = tail.split('\\') # Hard code os.sep for Windows.
        for part in parts:
            result.append(part)
            if part.startswith('python'):
                python = join(*result) # Don't use abspath here!
                if trace: print '**found**',python
                return python

    return None
#@-node:ekr.20080909112433.2:findPython
#@+node:ekr.20080909112433.3:setRegistry
def setRegistry(python):

    use_console = False ; trace = False

    abspath, exists, join = os.path.abspath, os.path.exists, os.path.join

    # Python paths...
    exe     = abspath(join(python,'pythonw.exe'))
    pythonw = abspath(join(os.path.dirname(exe), 'pythonw.exe'))

    # Installed Leo paths...
    top     = abspath(join(python,'Lib','site-packages','Leo-%s' % (version)))
    runLeo  = abspath(join(top,'leo','core','runLeo.py'))
    icon    = abspath(join(top,'leo','icons','LeoDoc.ico'))

    if trace:
        print ('exists %s, python:   %s' % (exists(python),python))
        print ('exists %s, top:      %s' % (exists(top), top))
        print ('exists %s, runLeo:   %s' % (exists(runLeo), runLeo))
        print ('exists %s, icon:     %s' % (exists(icon), icon))

    if use_console and os.path.basename(exe) == 'python.exe': # Avoid showing the console
        exe = pythonw

    # This is the 'pythonw.exe leo.py %1' part
    if trace:
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
#@-node:ekr.20080909112433.3:setRegistry
#@-node:ekr.20080913110741.4:install & helpers
#@+node:ekr.20080913110741.6:uninstall & helper
def uninstall():

    unsetRegistery()
#@+node:ekr.20080913110741.7:unsetRegistery
def unsetRegistery():

    '''Uninstall Leo entries from the Windows registry.'''

    h = wr.ConnectRegistry(None,wr.HKEY_CLASSES_ROOT)

    table = (
        '.leo',
        r'LeoFile\shell\open\command',
        r'LeoFile\shell\open',
        r'LeoFile\shell',
        r'LeoFile\DefaultIcon',
        r'LeoFile',
    )

    for key in table:
        try:
            wr.DeleteKey(h,key)
        except WindowsError:
            print 'Failed to delete %s key' % key
#@-node:ekr.20080913110741.7:unsetRegistery
#@-node:ekr.20080913110741.6:uninstall & helper
#@-others

path = None
# path = r'c:\xp\python25\python.exe' # Previously failed.

arg = sys.argv[1]
assert arg in ('-install','-remove'),'leo-post-install-script: bad sys.argv[1]: %s' % arg

if arg == '-install':
    install()
else:
    uninstall()

print ('leo-post-install-script(%s): done' % (arg))
#@-node:ekr.20080913110741.1:@thin leo-post-install-script.py
#@-leo
