#@+leo-ver=5-thin
#@+node:ekr.20070627082044.811: * @thin unittest/batchTest.py
# A file to be executed in batch mode as part of unit testing.
# This file is defined in unitTest.leo

#@@language python
#@@tabwidth -4

trace = False

path = g.os_path_join(g.app.loadDir,"..","test","unittest","createdFile.txt")

if trace: print("batchTest.py: creating: %s" % path)

try:
    try:
        f = open(path,"w")
        f.write("This file was written by unittest/batchTest.py")
    except IOError:
        print("batchTest.py: Can not create", path)
        f = None
finally:
    if f:
        f.close()

assert(g.os_path_exists(path))
#@-leo
