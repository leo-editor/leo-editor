import sys

from PyQt4.QtCore import QDateTime, QObject, QUrl, pyqtSignal
from PyQt4.QtGui import QApplication
from PyQt4.QtDeclarative import QDeclarativeView


# This class will emit the current date and time as a signal when
# requested.
class Now(QObject):

    now = pyqtSignal(str)

    def emit_now(self):
        formatted_date = QDateTime.currentDateTime().toString()
        self.now.emit(formatted_date)


app = QApplication(sys.argv)

now = Now()

# Create the QML user interface.
view = QDeclarativeView()
view.setSource(QUrl('message.qml'))
view.setResizeMode(QDeclarativeView.SizeRootObjectToView)

# Get the root object of the user interface.  It defines a
# 'messageRequired' signal and JavaScript 'updateMessage' function.  Both
# can be accessed transparently from Python.
rootObject = view.rootObject()

# Provide the current date and time when requested by the user interface.
rootObject.messageRequired.connect(now.emit_now)

# Update the user interface with the current date and time.
now.now.connect(rootObject.updateMessage)

# Provide an initial message as a prompt.
rootObject.updateMessage("Click to get the current date and time")

# Display the user interface and allow the user to interact with it.
view.setGeometry(100, 100, 400, 240)
view.show()

app.exec_()