import sys

from PyQt4.QtCore import QDateTime, QObject, QUrl, pyqtSignal
from PyQt4.QtGui import QApplication
from PyQt4.QtDeclarative import QDeclarativeView


def create_dv():
    # Create the QML user interface.
    view = QDeclarativeView()
    view.setSource(QUrl('qml/leonbmain.qml'))
    view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
    # Display the user interface and allow the user to interact with it.
    view.setGeometry(100, 100, 400, 240)
    view.show()
    
    rootObject = view.rootObject()
    return view

def main():
    

    app = QApplication(sys.argv)
    v = create_dv()
    app.exec_()
    
if __name__ == '__main__':
    main()
    
    

# Get the root object of the user interface.  It defines a
# 'messageRequired' signal and JavaScript 'updateMessage' function.  Both
# can be accessed transparently from Python.

# Provide the current date and time when requested by the user interface.
#rootObject.messageRequired.connect(now.emit_now)

# Update the user interface with the current date and time.
#now.now.connect(rootObject.updateMessage)

# Provide an initial message as a prompt.
#rootObject.updateMessage("Click to get the current date and time")


