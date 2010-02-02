# -*- coding: utf-8 -*-
#@+leo-ver=4-thin
#@+node:ekr.20100202115249.2023:@thin qttexttest.py
#@@first
#@@language python
import sys
from PyQt4 import Qt

isPython3 = sys.version_info >= (3,0,0)
if isPython3:
    def gu(s): return s
else:
    def gu(s): return unicode(s)

s = gu('''Select the following string: वादक.
This string consists of 4 characters, followed by a period.
Hit do, then undo.
Notice that the selection range now includes the period.
''')

n1,n2 = None,None # The selection range.
app = Qt.QApplication(sys.argv) 
f = Qt.QFrame()
f.setLayout(Qt.QVBoxLayout())
w = Qt.QTextEdit()
w.setPlainText(s)

b1 = Qt.QPushButton("Do")
b2 = Qt.QPushButton("Undo")

f.layout().addWidget(w)
f.layout().addWidget(b1)
f.layout().addWidget(b2)
f.show()

def showselect():
    tc = w.textCursor()
    s = w.toPlainText()
    su = gu(s)
    n1,n2 = tc.selectionStart(),tc.selectionEnd()
    print(n1,n2,'length',abs(n2-n1),len(s),len(su),gu(s[n1:n2]).encode('utf-8'))

def do():
    # w.textCursor().removeSelectedText() # works
    global n1,n2,w
    tc = w.textCursor()
    n1,n2 = tc.selectionStart(),tc.selectionEnd()
    tc = w.textCursor()
    tc.removeSelectedText()
    w.setTextCursor(tc) # Has no effect.

def undo():
    global n1,n2,s,w
    w.setPlainText(s)
    tc = w.textCursor()
    if n1 > n2: n1,n2 = n2,n1
    tc.setPosition(n1)
    tc.setPosition(n2,tc.KeepAnchor)
    # tc.movePosition(tc.Right,tc.KeepAnchor,n2-n1)
    w.setTextCursor(tc)

app.connect(w, Qt.SIGNAL("selectionChanged()"), showselect)
app.connect(b1, Qt.SIGNAL("clicked()"), do)
app.connect(b2, Qt.SIGNAL("clicked()"), undo)
app.exec_()
#@-node:ekr.20100202115249.2023:@thin qttexttest.py
#@-leo
