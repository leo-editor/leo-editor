#@+leo-ver=4-thin
#@+node:ekr.20070627082044.811:@thin ../test/unittest/batchTest.py
# A file to be executed in batch mode as part of unit testing.

#@@language python
#@@tabwidth -4

trace = False

path = g.os_path_join(g.app.loadDir,"..","test","unittest","createdFile.txt")

if trace:
    print("unittest/batchTest.py: creating: %s" % path)

try:
    try:
        f = open(path,"w")
        f.write("This file was written by unittest/batchTest.py")
    except IOError:
        g.es("Can not create", path)
        f = None
finally:
    if f:
        f.close()
#@nonl
#@-node:ekr.20070627082044.811:@thin ../test/unittest/batchTest.py
#@-leo
