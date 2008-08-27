#@+leo-ver=4-thin
#@+node:ekr.20080827092958.1:@thin post-install-script.py
import _winreg as wr
import sys, os

testing = True ; problems = False
abspath, exists, join = os.path.abspath, os.path.exists, os.path.join

# Leo path needs to come from the installer!
if testing:             leo_path = abspath(join(g.app.loadDir,'..'))
elif len(sys.argv) > 1: leo_path = abspath(sys.argv[1])
else:                   leo_path = r"c:\Program Files\leo"

# Compute paths.
exe     = sys.executable
top     = abspath(join(leo_path,'..'))
pythonw = abspath(join(os.path.dirname(exe), 'pythonw.exe'))
runLeo  = abspath(join(leo_path,'core','runLeo.py'))
icon    = abspath(join(leo_path,'icons','LeoDoc.ico'))

if testing:
    print ('exists %s, top:      %s' % (exists(top), top))
    print ('exists %s, leo_path: %s' % (exists(leo_path),leo_path))
    print ('exists %s, runLeo:   %s' % (exists(runLeo), runLeo))
    print ('exists %s, icon:     %s' % (exists(icon), icon))

if 1:
    if not problems and os.path.basename(exe) == 'python.exe': # Avoid showing the console
        exe = pythonw

    # This is the 'pythonw.exe leo.py %1' part
    if testing:
        # Leo hasn't necessarily been installed anywhere: use the trunk.
        s = 'import os; os.chdir(r\'%s\'); import leo.core.runLeo as r; r.run(fileName=r\'%%1\')'
        c_option =  s % top
        i_option = g.choose(problems,'-i','')
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
#@-node:ekr.20080827092958.1:@thin post-install-script.py
#@-leo
