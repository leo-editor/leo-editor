import sys
from inspect import isclass
from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import Qt as QtConst
class DemoWidget(QtGui.QWidget):

    count = 0

    def __init__(self, parent=None, color=None):

        QtGui.QWidget.__init__(self, parent)

        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(QtCore.QMargins(0,0,0,0))
        self.layout().setSpacing(0)

        text = QtGui.QTextEdit()
        self.layout().addWidget(text)
        DemoWidget.count += 1
        text.setPlainText("#%d" % DemoWidget.count)

        button_layout = QtGui.QHBoxLayout()
        button_layout.setContentsMargins(QtCore.QMargins(5,5,5,5))
        self.layout().addLayout(button_layout)


        button_layout.addWidget(QtGui.QPushButton("Go"))
        button_layout.addWidget(QtGui.QPushButton("Stop"))

        if color:
            self.setStyleSheet("background-color: %s;"%color)

class NestedSplitterChoice(QtGui.QWidget):

    def __init__(self, parent=None):

        QtGui.QWidget.__init__(self, parent)

        self.setLayout(QtGui.QVBoxLayout())

        button = QtGui.QPushButton("Action", parent=self)
        self.layout().addWidget(button)

        button.setContextMenuPolicy(QtConst.CustomContextMenu)
        button.connect(button,
            Qt.SIGNAL('customContextMenuRequested(QPoint)'),
            lambda pnt: self.parent().choice_menu(self, pnt))
        button.connect(button,
            Qt.SIGNAL('clicked()'),
            lambda: self.parent().choice_menu(self, button.pos()))

class NestedSplitterHandle(QtGui.QSplitterHandle):

    def __init__(self, owner):
        QtGui.QSplitterHandle.__init__(self, owner.orientation(), owner)

        self.setStyleSheet("background-color: green;")

        self.setContextMenuPolicy(QtConst.CustomContextMenu)
        self.connect(self,
            Qt.SIGNAL('customContextMenuRequested(QPoint)'),
            self.splitter_menu)

    def splitter_menu(self, pos):

        splitter = self.splitter()

        if not splitter.enabled:
            return

        splitter = self.splitter()
        index = splitter.indexOf(self)

        widget, neighbour, count = splitter.handle_context(index)

        lr = 'left', 'right'
        ab = 'above', 'below'
        split_dir = 'vertically'
        if self.orientation() == QtConst.Vertical:
            lr, ab = ab, lr
            split_dir = 'horizontally'

        color = '#729fcf', '#f57900'
        sheet = []
        for i in 0,1:
            sheet.append(widget[i].styleSheet())
            widget[i].setStyleSheet(sheet[-1]+"\nborder: 2px solid %s;"%color[i])

        menu = QtGui.QMenu()

        # insert
        act = QtGui.QAction("Insert", self)
        act.setObjectName('insert')
        act.connect(act, Qt.SIGNAL('triggered()'), 
            lambda: splitter.insert(index))
        menu.addAction(act)

        # swap
        act = QtGui.QAction("Swap %d %s %d %s" % (count[0], lr[0], count[1], lr[1]), self)
        act.setObjectName('swap')
        act.connect(act, Qt.SIGNAL('triggered()'), 
            lambda: splitter.swap(index))
        menu.addAction(act)

        # rotate
        act = QtGui.QAction("Rotate all", self)
        act.setObjectName('rotate')
        act.connect(act, Qt.SIGNAL('triggered()'), splitter.rotate)
        menu.addAction(act)

        # remove, +0/-1 reversed, we need to test the one that remains

        # first see if a parent has more than two splits (we could be a sole
        # surviving child)
        max_parent_splits = 0
        up = splitter.parent()
        while isinstance(up, NestedSplitter):
            max_parent_splits = max(max_parent_splits, up.count())
            up = up.parent()
            if max_parent_splits >= 2:
                break  # two is enough

        for i in 0,1:

            keep = splitter.widget(index)
            cull = splitter.widget(index-1)
            if (max_parent_splits >= 2 or  # more splits upstream
                splitter.count() > 2 or    # 3+ splits here, or 2+ downstream
                neighbour[not i] and neighbour[not i].max_count() >= 2):
                act = QtGui.QAction("Remove %d %s"%(count[i], lr[i]), self)
                act.setObjectName('remove %d'%i)
                def wrapper(i=i): splitter.remove(index, i)
                act.connect(act, Qt.SIGNAL('triggered()'), wrapper)
                menu.addAction(act)

        # only offer split if not already split
        for i in 0,1:
            if (not neighbour[i] or neighbour[i].count() == 1):
                act = QtGui.QAction("Split %s %s"%(lr[i], split_dir), self)
                act.setObjectName('split %d'%i)
                def wrapper(i=i): splitter.split(index, i)
                act.connect(act, Qt.SIGNAL('triggered()'), wrapper)
                menu.addAction(act)

        # mark
        for i in 0,1:
            act = QtGui.QAction("Mark %d %s"%(count[i], lr[i]), self)
            act.setObjectName('mark %d'%i)
            def wrapper(i=i): splitter.mark(index, i)
            act.connect(act, Qt.SIGNAL('triggered()'), wrapper)
            menu.addAction(act)

        # swap with mark
        if splitter.root.marked:
            for i in 0,1:
                if not splitter.invalid_swap(widget[i], splitter.root.marked[2]):
                    act = QtGui.QAction("Swap %d %s with marked"%(count[i], lr[i]), self)
                    act.setObjectName('swap mark %d'%i)
                    def wrapper(i=i): splitter.swap_with_marked(index, i)
                    act.connect(act, Qt.SIGNAL('triggered()'), wrapper)
                    menu.addAction(act)

        # add
        for i in 0,1:
            if (not isinstance(splitter.parent(), NestedSplitter) or
                splitter.parent().indexOf(splitter) ==
                    [0,splitter.parent().count()-1][i]):
                act = QtGui.QAction("Add %s"%ab[i], self)
                act.setObjectName('add %d'%i)
                def wrapper(i=i): splitter.add(i)
                act.connect(act, Qt.SIGNAL('triggered()'), wrapper)
                menu.addAction(act)

        for cb in splitter.root.callbacks:
            cb(menu, splitter, index, button_mode=False)

        menu.exec_(self.mapToGlobal(pos))

        for i in 0,1:
            widget[i].setStyleSheet(sheet[i])

class NestedSplitter(QtGui.QSplitter): 

    enabled = True
    # allow special behavior to be turned of at import stage
    # useful if other code must run to set up callbacks, that
    # other code can re-enable

    other_orientation = {
        QtConst.Vertical: QtConst.Horizontal,
        QtConst.Horizontal: QtConst.Vertical
    }


    def __init__(self, parent=None, orientation=QtConst.Horizontal, root=None):

        QtGui.QSplitter.__init__(self, orientation, parent)

        if not root:
            root = self.top()
            if root == self:
                root.marked = None
                root.callbacks = []
                root.holders = {}
        self.root = root
        
    def add(self, side):

        orientation = self.other_orientation[self.orientation()]

        if isinstance(self.parent(), NestedSplitter):
            # don't add new splitter if not needed, i.e. we're the
            # only child of a previosly more populated splitter

            self.parent().insertWidget(
                self.parent().indexOf(self) + side - 1 + 1,
                NestedSplitterChoice(self))

        elif self.parent().layout():

            new = NestedSplitter(None, orientation=orientation,
                root=self.root)
            # parent set by insertWidget() below

            old = self

            pos = self.parent().layout().indexOf(old)

            self.parent().layout().insertWidget(pos, new)

            new.addWidget(old)
            new.insertWidget(side, NestedSplitterChoice(new))

        else:
            # fail - parent is not NestedSplitter and has no layout
            pass
    def choice_menu(self, button, pos):

        menu = QtGui.QMenu()

        if self.root.marked and not self.invalid_swap(button, self.root.marked[3]):
            an_item = True
            act = QtGui.QAction("Move marked here", self)
            act.connect(act, Qt.SIGNAL('triggered()'), 
                lambda: self.replace_widget(button, self.root.marked[3]))
            menu.addAction(act)        

        for cb in self.root.callbacks:
            cb(menu, self, self.indexOf(button), button_mode=True)

        if menu.isEmpty():
            act = QtGui.QAction("Nothing marked, and no options", self)
            menu.addAction(act)

        menu.exec_(button.mapToGlobal(pos))
    def close_or_keep(self, widget):

        if widget is None:
            return

        for k in self.root.holders:
            if hasattr(widget, k):
                holder = self.root.holders[k]
                if hasattr(holder, "addTab"):
                    holder.addTab(widget, getattr(widget,k))
                else:
                    holder.addWidget(widget)
                break
        else:
            widget.close()
            widget.deleteLater()
    def contains(self, widget):
        """check if widget is a descendent of self"""

        for i in range(self.count()):
            if widget == self.widget(i):
                return True
            if isinstance(self.widget(i), NestedSplitter):
                if self.widget(i).contains(widget):
                    return True

        return False

    def createHandle(self, *args, **kargs):

        return NestedSplitterHandle(self)

    def handle_context(self, index):

        widget = [
            self.widget(index-1),
            self.widget(index),
        ]

        neighbour = [ (i if isinstance(i, NestedSplitter) else None)
            for i in widget ]

        count = []
        for i in 0,1:
            if neighbour[i]:
                l = [ii.count() for ii in neighbour[i].self_and_descendants()]
                n = sum(l) - len(l) + 1  # count leaves, not splitters
                count.append(n)
            else:
                count.append(1)

        return widget, neighbour, count
    def insert(self, index):

        self.insertWidget(index, NestedSplitterChoice(self))

    def invalid_swap(self, w0, w1):
        if w0 == w1:
            return True
        if (isinstance(w0, NestedSplitter) and w0.contains(w1) or
            isinstance(w1, NestedSplitter) and w1.contains(w0)):
            return True     
        return False

    def mark(self, index, side):       
        self.root.marked = (self, index, side-1,
            self.widget(index+side-1))
    def max_count(self):
        """find max widgets in this and child splitters"""

        return max([i.count() for i in self.self_and_descendants()])

    def register(self, cb):

        self.root.callbacks.append(cb)
    def remove(self, index, side):

        widget = self.widget(index+side-1)

        # clear marked if it's going to be deleted
        if (self.root.marked and (self.root.marked[3] == widget or
            isinstance(self.root.marked[3], NestedSplitter) and
            self.root.marked[3].contains(widget))):
            self.root.marked = None

        # send close signal to all children
        if isinstance(widget, NestedSplitter):

            count = widget.count()

            for splitter in widget.self_and_descendants():
                for i in range(splitter.count()):
                    self.close_or_keep(splitter.widget(i))

            if count <= 0:
                widget.deleteLater()

        else:
            self.close_or_keep(widget)

    def replace_widget(self, old, new):

        self.insertWidget(self.indexOf(old), new)
        old.deleteLater()

    def rotate(self, descending=False):
        """Change orientation - current rotates entire hierachy, doing less
        is visually confusing because you end up with nested splitters with
        the same orientation - avoiding that would mean doing rotation by
        inserting out widgets into our ancestors, etc.
        """

        for i in self.top().self_and_descendants():
            if i.orientation() == QtConst.Vertical:
                i.setOrientation(QtConst.Horizontal)
            else:
                i.setOrientation(QtConst.Vertical)
    def self_and_descendants(self):
        """Yield self and all **NestedSplitter** descendants"""

        for i in range(self.count()):
            if isinstance(self.widget(i), NestedSplitter):
                for w in self.widget(i).self_and_descendants():
                    yield w
        yield self
    def split(self, index, side):

        old = self.widget(index+side-1)

        if isinstance(old, NestedSplitter):
            old.addWidget(NestedSplitterChoice(self))
            return

        orientation = self.other_orientation[self.orientation()]

        new = NestedSplitter(self, orientation=orientation, root=self.root)
        self.insertWidget(index+side-1, new)
        new.addWidget(old)
        new.addWidget(NestedSplitterChoice(self))
    def swap(self, index):

        self.insertWidget(index-1, self.widget(index))

    def swap_with_marked(self, index, side):

        osplitter, oidx, oside, ow = self.root.marked

        idx = index+side-1
        # convert from handle index to widget index
        # 1 already subtracted from oside in mark()
        w = self.widget(idx)

        if self.invalid_swap(w, ow):
            # print 'Invalid swap'
            return

        self.insertWidget(idx, ow)
        osplitter.insertWidget(oidx, w)

        self.root.marked = self, self.indexOf(ow), 0, ow
    def top(self):
        """find top widget, which is not necessarily root"""

        top = self
        while isinstance(top.parent(), NestedSplitter):
            top = top.parent()

        return top
if __name__ == "__main__":

    def demo_nest(splitter):
        orientation = splitter.other_orientation[splitter.orientation()]
        x = NestedSplitter(splitter, root=splitter.root,
            orientation=orientation)
        s = [x]
        for i in range(4):
            orientation = splitter.other_orientation[orientation]
            ns = []
            for j in s:
                j.addWidget(DemoWidget())
                ns.append(NestedSplitter(splitter, orientation=orientation,
                    root=splitter.root))
                j.addWidget(ns[-1])
            s = ns

        for i in s:
            i.addWidget(DemoWidget())

        return x

    def callback(menu, splitter, index, button_mode):

        if not button_mode:
            return

        act = QtGui.QAction("Add DemoWidget", splitter)
        def wrapper():
            splitter.replace_widget(splitter.widget(index),
               DemoWidget(splitter))
        act.connect(act, Qt.SIGNAL('triggered()'), wrapper)
        menu.addAction(act)

        act = QtGui.QAction("Add DemoWidget Nest", splitter)
        def wrapper():
            splitter.replace_widget(splitter.widget(index),
                demo_nest(splitter))
        act.connect(act, Qt.SIGNAL('triggered()'), wrapper)
        menu.addAction(act)

    # example - remove "Remove" commands from handle context menu
    def callback2(menu, splitter, index, button_mode):

        if button_mode:
            return

        for i in [i for i in menu.actions()
                  if str(i.objectName()).startswith('remove')]:
            menu.removeAction(i)

    # more complex example only removing remove action for particular target
    def dont_close_special(menu, splitter, index, button_mode):

        if button_mode:
            return

        widget, neighbour, count = splitter.handle_context(index)

        for i in 0,1:
            if (widget[i] == special or
                neighbour[i] and neighbour[i].contains(special)):

                for a in [a for a in menu.actions()
                          if a.objectName() == "remove %d"%i]:
                    menu.removeAction(i)


    app = Qt.QApplication(sys.argv)

    wdg = DemoWidget()
    wdg2 = DemoWidget()

    splitter = NestedSplitter()
    splitter.addWidget(wdg)
    splitter.addWidget(wdg2)

    splitter.register(callback)
    # splitter.register(callback2)

    holder = QtGui.QWidget()
    holder.setLayout(QtGui.QVBoxLayout())
    holder.layout().setContentsMargins(QtCore.QMargins(0,0,0,0))
    holder.layout().addWidget(splitter)
    holder.show()

    app.exec_()
