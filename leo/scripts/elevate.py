#@+leo-ver=5-thin
#@+node:maphew.20130613230258.2801: * @file elevate.py
''' Open a new python intepreter after asking for elevated UAC permissions, and feed it the python script specified on the command line.

    python elevate.py d:\full\path\to\some-script.py {args for some-script}
'''
import sys
import ctypes
import tempfile

# -i : ask python interpreter to stay open when done, to see messages
params = "-i {} ".format(' '.join(sys.argv[1:]))
print(params)

#@+others
#@+node:maphew.20130613230258.2803: ** UAC Elevation
def elevate(params):
    hwnd = 0                # parent window
    lpOperation = 'runas'   # force elevated UAC prompt
    lpFile = sys.executable # path to python
    lpFile = lpFile.replace('pythonw.exe', 'python.exe') # force console python, only way to see messages
    lpParameters = params   # arguments to pass to python
    lpDirectory = tempfile.gettempdir() # working dir
    nShowCmd = 1            # window visibility, must be 1 for Leo.
    
    print(lpFile, lpParameters)
    #g.es(lpFile, lpParameters)
    retcode = ctypes.windll.shell32.ShellExecuteA(hwnd, lpOperation, lpFile, lpParameters, lpDirectory, nShowCmd)
    msg = 'Exit code: {0} - {1}'.format(retcode, ctypes.FormatError(retcode))
    print(msg)
    #g.es(msg)
    
#@-others

elevate(params)
#@-leo
