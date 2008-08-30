#@+leo-ver=4-thin
#@+node:ekr.20080827092958.3:@thin pre-install-script.py
import _winreg as wr
import sys, os

version = '4-5-rc2'

testing = True ; problems = False ; verbose = False
abspath, exists, join = os.path.abspath, os.path.exists, os.path.join

# The path to Leo will be python/Lib/site-packages/leo.
# To get this, we look for entries in sys.path whose first component starts with python.

print '=' * 40 ; found = False
for path in sys.path:
    if found: break
    drive,head = os.path.splitdrive(path)
    if verbose: print 'drive',drive,'head',head
    if not head.lower().startswith(r'\python'):
        continue
    while not found:
        head,tail = os.path.split(head)
        if verbose: print 'head',head,'tail',tail
        head2,tail2 = os.path.split(head)
        if verbose: print 'head2',head2,'tail2',tail2
        if not tail2.strip():
            python = join(drive,'\\',tail) # Don't use abspath here!
            if verbose: print '**found**',python
            found = True

# No error is possible if not found: we simple do nothing later.

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

assert found

if found:
    if not problems and os.path.basename(exe) == 'python.exe': # Avoid showing the console
        exe = pythonw

    # This is the 'pythonw.exe leo.py %1' part
    if testing:
        # Leo hasn't necessarily been installed anywhere: use the trunk.
        s = 'import os; os.chdir(r\'%s\'); import leo.core.runLeo as r; r.run(fileName=r\'%%1\')'
        c_option =  s % top
        if problems: i_option = '-i'
        else:        i_option = ''
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

# That's it!
if testing: print ('done')
#@-node:ekr.20080827092958.3:@thin pre-install-script.py
#@-leo
