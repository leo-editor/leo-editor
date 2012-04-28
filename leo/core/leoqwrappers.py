from PyQt4 import QtCore
from PyQt4.QtCore import QObject,pyqtSlot

class NodeWrapper(QObject):
    def __init__(self, c,v):
        QObject.__init__(self)
        
        self.c = c
        self.v = v

    @QtCore.pyqtProperty(unicode)
    def h(self):
        return self.v.h

    @QtCore.pyqtProperty(unicode)
    def b(self):
        return self.v.b
    
    
    
    @pyqtSlot()
    def get_b(self):
        return 2
        #return self.v.b
    @pyqtSlot()
    def get_h(self):
        return self.v.h
    @pyqtSlot()
    def children(self):
        #self.all = all = [NodeWrapper(self.c, chi) for chi in self.v.children]
        all = "hello"
        print "Will ret",all
        return all  