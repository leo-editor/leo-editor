#@+leo-ver=5-thin
#@+node:ekr.20070627082044.808: * @thin unittest/errorTest.py
# A file that contains functions with errors in them.
# This is used to test error reporting in scripts

#@@language python
#@@tabwidth -4

def testIndexError():

    a = []
    b = a[2]

# The next line is used by @test c.checkFileTimeStamp.   
# timestamp: 1231502468.77
#@-leo
