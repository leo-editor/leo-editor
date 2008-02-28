#@+leo-ver=4-thin
#@+node:ekr.20070930183037:@thin jyleo.py
import os, sys

theDir = os.getcwd()

if theDir not in sys.path:
    print 'adding',theDir,'to sys.path'
    sys.path.append(theDir)

import leo
leo.run(jyLeo=True)
#@-node:ekr.20070930183037:@thin jyleo.py
#@-leo
