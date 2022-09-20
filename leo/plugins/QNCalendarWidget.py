#@+leo-ver=5-thin
#@+node:ekr.20160519123329.1: * @file ../plugins/QNCalendarWidget.py
#@@language python
"""
QNCalendarWidget.py - a QCalendarWidget which shows N months at a time.

Not a full QCalendarWidget implementation, just enough to work
with a QDateEdit (QNDateEdit) in a particular context.

Terry_N_Brown@yahoo.com, Tue Oct 15 09:53:38 2013
"""

import sys
import datetime
from leo.core import leoGlobals as g
from leo.core.leoQt import QtCore, QtWidgets
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.

def init():
    return True  # For unit tests.

class QNCalendarWidget(QtWidgets.QCalendarWidget):  # type:ignore
    def __init__(self, n=3, columns=3, year=None, month=None):
        """set up

        :Parameters:
        - `self`: the widget
        - `n`: number of months to display
        - `columns`: months to display before start a new row
        - `year`: year of first calendar
        - `month`: month of first calendar
        """

        super().__init__()

        self.build(n, columns, year=year, month=month)

    def build(self, n=3, columns=3, year=None, month=None):

        self.calendars = []

        if year is None:
            year = datetime.date.today().year
        if month is None:
            month = datetime.date.today().month

        layout = QtWidgets.QGridLayout()
        while self.layout().count():
            self.layout().removeItem(self.layout().itemAt(0))
        self.layout().addLayout(layout)
        size = self.minimumSizeHint()
        x, y = size.width(), size.height()
        x *= min(n, columns)
        y *= 1 + ((n - 1) // columns)
        self.setMinimumSize(QtCore.QSize(x, y))

        for i in range(n):
            calendar = QtWidgets.QCalendarWidget()
            calendar.i = i
            calendar.setCurrentPage(year, month)
            month += 1
            if month == 13:
                year += 1
                month = 1
            calendar.currentPageChanged.connect(
                lambda year, month, cal=calendar:
                    self.currentPageChanged(year, month, cal))
            calendar.clicked.connect(self.return_result)
            calendar.activated.connect(self.return_result)
            self.calendars.append(calendar)
            layout.addWidget(calendar, i // columns, i % columns)

    def currentPageChanged(self, year, month, cal):
        """currentPageChanged - Handle change of view

        :Parameters:
        - `self`: self
        - `year`: new year
        - `month`: new month
        - `cal`: which calendar
        """

        for i in range(cal.i):
            month -= 1
            if month == 0:
                year -= 1
                month = 12
        for calendar in self.calendars:
            calendar.setCurrentPage(year, month)
            month += 1
            if month == 13:
                year += 1
                month = 1

    activated = QtCore.pyqtSignal(QtCore.QDate)

    def return_result(self, date):
        """return_result - Return result

        :Parameters:
        - `self`: self
        - `cal`: the calendar that was activated
        """

        for i in self.calendars:
            old = i.blockSignals(True)  # stop currentPageChanged firing
            y, m = i.yearShown(), i.monthShown()
            i.setSelectedDate(date)
            i.setCurrentPage(y, m)
            i.blockSignals(old)
        self.activated.emit(date)

class QNDateEdit(QtWidgets.QDateEdit):  # type:ignore
    def __init__(self, parent=None, n=3, columns=3):
        """set up

        :Parameters:
        - `self`: the widget
        - `n`: number of months to display
        - `columns`: months to display before start a new row
        """

        super().__init__(parent)
        self.setCalendarPopup(True)
        self.cw = QNCalendarWidget(n=n, columns=columns)
        self.setCalendarWidget(self.cw)

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = QtWidgets.QWidget()
    l = QtWidgets.QVBoxLayout()
    win.setLayout(l)

    w = QtWidgets.QDateEdit()
    w.setCalendarPopup(True)
    l.addWidget(w)
    l.addWidget(QNDateEdit())
    l.addWidget(QNDateEdit(n=6))
    l.addWidget(QNDateEdit(n=1))
    l.addWidget(QNDateEdit(n=2))
    l.addWidget(QNDateEdit(n=6, columns=2))
    l.addWidget(QNDateEdit(n=6, columns=4))
    l.addWidget(QNDateEdit(n=12, columns=4))
    l.addWidget(QNDateEdit(columns=1))
    last = QNDateEdit()
    l.addWidget(last)
    last.calendarWidget().build(5, 4)

    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
#@-leo
