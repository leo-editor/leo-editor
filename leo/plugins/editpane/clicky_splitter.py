#@+leo-ver=5-thin
#@+node:tbrown.20171029210211.1: * @file ../plugins/editpane/clicky_splitter.py
#@@language python
"""
clicky_splitter.py - a QSplitter which allows flipping / rotating of
content by clicking on the splitter handle

Terry Brown, TerryNBrown@gmail.com, Sun Oct 29 21:02:25 2017
"""

from leo.core.leoQt import QtWidgets
from leo.core.leoQt import MouseButton, Orientation


class ClickySplitterHandle(QtWidgets.QSplitterHandle):
    """Handle which notifies splitter when it's clicked"""

    def mouseReleaseEvent(self, event):
        """mouse event - mouse released on splitter handle,

        Args:
            event (QMouseEvent): mouse event
        """
        if event.button() == MouseButton.LeftButton:
            return  # might have been resizing panes
        self.splitter().flip_spin()


class ClickySplitter(QtWidgets.QSplitter):
    """Splitter that rotates / flips when its handle's clicked"""

    def __init__(self, *args, **kwargs):
        """set initial state"""
        super().__init__(*args, **kwargs)
        self._click_state = 'spin'

    def createHandle(self):
        """use custom handle"""
        return ClickySplitterHandle(self.orientation(), self)

    def flip_spin(self):
        """swap or rotate"""
        if self._click_state == 'flip':
            self.insertWidget(0, self.widget(1))
            self._click_state = 'spin'
        else:
            vertical, horizontal = Orientation.Vertical, Orientation.Horizontal
            self.setOrientation(vertical if self.orientation() == horizontal else vertical)
            self._click_state = 'flip'
#@-leo
