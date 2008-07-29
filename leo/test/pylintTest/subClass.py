#@+leo-ver=4-thin
#@+node:ekr.20080702113207.3:@thin pylintTest/subClass.py
import baseClass

class subClass (baseClass.baseClass):

    def __init__ (self,message):

        # init the base class
        baseClass.baseClass.__init__(self,message)

    def run(self):

        g.pr(self.message)
#@-node:ekr.20080702113207.3:@thin pylintTest/subClass.py
#@-leo
