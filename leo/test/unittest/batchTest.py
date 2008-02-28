#@+leo-ver=4-thin
#@+node:ekr.20070627082044.811:@thin ../test/unittest/batchTest.py
# A file to be executed in batch mode as part of unit testing.

#@@language python
#@@tabwidth -4

path = g.os_path_join(g.app.loadDir,"..","test","unittest","createdFile.txt")

if 0:
    print "creating", path

f = None
try:
    try:
        f = open(path,"w")
        f.write("This is a test")
    except IOError:
        g.es("Can not create", path)
finally:
    if f:
        f.close()
#@nonl
#@-node:ekr.20070627082044.811:@thin ../test/unittest/batchTest.py
#@-leo
