#@+leo-ver=5-thin
#@+node:ekr.20110316093303.14482: * @file nested_splitter.py
#@@language python
#@@tabwidth -4

#@+<< imports >>
#@+node:ekr.20110316093303.14483: ** << imports >>
import leo.core.leoGlobals as g

import sys

from inspect import isclass

from PyQt4 import QtGui, QtCore, Qt

from PyQt4.QtCore import Qt as QtConst
#@-<< imports >>

#@+others
#@+node:ekr.20110316094902.14430: ** init
def init():
    
    # Allow this to be imported as a plugin,
    # but it should never be necessary to do so.
    
    return True
#@+node:ekr.20110316093303.14484: ** class DemoWidget
class DemoWidget(QtGui.QWidget):

    count = 0

    #@+others
    #@+node:ekr.20110316093303.14485: *3* __init__
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
    #@-others
#@+node:ekr.20110316093303.14486: ** class NestedSplitterChoice (QWidget)
class NestedSplitterChoice(QtGui.QWidget):
    #@+others
    #@+node:ekr.20110316093303.14487: *3* __init__
    def __init__(self,parent=None):

        QtGui.QWidget.__init__(self, parent)

        self.setLayout(QtGui.QVBoxLayout())
        
        button = QtGui.QPushButton("Action",self) # EKR: 2011/03/15
        self.layout().addWidget(button)

        button.setContextMenuPolicy(QtConst.CustomContextMenu)
        
        button.connect(button,
            Qt.SIGNAL('customContextMenuRequested(QPoint)'),
            lambda pnt: self.parent().choice_menu(self, pnt))

        button.connect(button,
            Qt.SIGNAL('clicked()'),
            lambda: self.parent().choice_menu(self,button.pos()))
    #@-others
#@+node:ekr.20110316093303.14488: ** class NestedSplitterHandle
class NestedSplitterHandle(QtGui.QSplitterHandle):

    #@+others
    #@+node:ekr.20110316093303.14489: *3* __init__
    def __init__(self, owner):

        QtGui.QSplitterHandle.__init__(self, owner.orientation(), owner)

        self.setStyleSheet("background-color: green;")

        self.setContextMenuPolicy(QtConst.CustomContextMenu)
        self.connect(self,
            Qt.SIGNAL('customContextMenuRequested(QPoint)'),
            self.splitter_menu)
    #@+node:ekr.20110316155727.14373: *3* add_item
    def add_item (self,func,menu,name):
        
        act = QtGui.QAction(name, self)
        act.setObjectName(name.lower().replace(' ','-'))
        act.connect(act, Qt.SIGNAL('triggered()'),func)
        menu.addAction(act)
    #@+node:ekr.20110316093303.14490: *3* splitter_menu
    def splitter_menu(self, pos):

        splitter = self.splitter()

        if not splitter.enabled:
            return

        index = splitter.indexOf(self)

        widget, neighbour, count = splitter.handle_context(index)

        lr = 'Left', 'Right'
        ab = 'Above', 'Below'
        split_dir = 'Vertically'
        if self.orientation() == QtConst.Vertical:
            lr, ab = ab, lr
            split_dir = 'Horizontally'

        color = '#729fcf', '#f57900'
        sheet = []
        for i in 0,1:
            sheet.append(widget[i].styleSheet())
            widget[i].setStyleSheet(sheet[-1]+"\nborder: 2px solid %s;"%color[i])

        menu = QtGui.QMenu()
        
        # Insert.
        def insert_callback(index=index):
            splitter.insert(index)
        self.add_item(insert_callback,menu,'Insert')

        # Swap.
        def swap_callback(index=index):
            splitter.swap(index)
        self.add_item(swap_callback,menu,
            "Swap %d %s %d %s" % (count[0], lr[0], count[1], lr[1]))
        
        # Rotate All.
        self.add_item(splitter.rotate,menu,'Rotate All')

        # Remove, +0/-1 reversed, we need to test the one that remains

        # First see if a parent has more than two splits
        # (we could be a sole surviving child).
        max_parent_splits = 0
        up = splitter.parent()
        while isinstance(up,NestedSplitter):
            max_parent_splits = max(max_parent_splits, up.count())
            up = up.parent()
            if max_parent_splits >= 2:
                break  # two is enough

        for i in 0,1:
            keep = splitter.widget(index)
            cull = splitter.widget(index-1)
            if (max_parent_splits >= 2 or  # more splits upstream
                splitter.count() > 2 or    # 3+ splits here, or 2+ downstream
                neighbour[not i] and neighbour[not i].max_count() >= 2
            ):
                def remove_callback(i=i,index=index):
                    splitter.remove(index,i)
                self.add_item(remove_callback,menu,'Remove %d %s' % (count[i], lr[i]))

        # Split: only if not already split.
        for i in 0,1:
            if not neighbour[i] or neighbour[i].count() == 1:
                def split_callback(i=i,index=index):
                    splitter.split(index,i)
                self.add_item(split_callback,menu,'Split %s %s' % (lr[i], split_dir))

        for i in 0,1:
            def mark_callback(i=i,index=index):
                splitter.mark(index, i)
            self.add_item(mark_callback,menu,'Mark %d %s' % (count[i], lr[i]))
           
        # Swap With Marked.
        if splitter.root.marked:
            for i in 0,1:
                if not splitter.invalid_swap(widget[i],splitter.root.marked[2]):
                    def swap_mark_callback(i=i,index=index):
                        splitter.swap_with_marked(index, i)
                    self.add_item(swap_mark_callback,menu,
                        'Swap %d %s With Marked' % (count[i], lr[i]))
        # Add.
        for i in 0,1:
            if (not isinstance(splitter.parent(), NestedSplitter) or
                splitter.parent().indexOf(splitter) == [0,splitter.parent().count()-1][i]
            ):
                def add_callback(i=i):
                    splitter.add(i)
                self.add_item(add_callback,menu,'Add %s' % (ab[i]))

        for cb in splitter.root.callbacks:
            cb(menu, splitter, index, button_mode=False)

        menu.exec_(self.mapToGlobal(pos))

        for i in 0,1:
            widget[i].setStyleSheet(sheet[i])
    #@-others
#@+node:ekr.20110316093303.14491: ** class NestedSplitter (QSplitter)
class NestedSplitter(QtGui.QSplitter): 

    enabled = True
        # allow special behavior to be turned of at import stage
        # useful if other code must run to set up callbacks, that
        # other code can re-enable

    other_orientation = {
        QtConst.Vertical: QtConst.Horizontal,
        QtConst.Horizontal: QtConst.Vertical
    }

    #@+others
    #@+node:ekr.20110316093303.14492: *3* __init__
    def __init__(self,parent=None,orientation=QtConst.Horizontal,root=None):

        QtGui.QSplitter.__init__(self,orientation,parent)
        
        name = parent and parent.objectName() or '<no parent>'
        g.trace(self)

        if not root:
            root = self.top()
            if root == self:
                root.marked = None # Tuple: self,index,side-1,widget
                root.callbacks = []
                root.holders = {}

        self.root = root
    #@+node:ekr.20110318080425.14395: *3* __repr__
    def __repr__ (self):
        
        parent = self.parent()

        return '(NestedSplitter): parent: %s at %s' % (
            parent and parent.objectName() or '<no parent>',
            id(self))

    __str__ = __repr__
    #@+node:ekr.20110316093303.14493: *3* add
    def add(self,side,button=True,w=None):

        orientation = self.other_orientation[self.orientation()]
        
        layout = self.parent().layout()
        g.trace(layout)

        if isinstance(self.parent(),NestedSplitter):
            # don't add new splitter if not needed, i.e. we're the
            # only child of a previosly more populated splitter
            self.parent().insertWidget(
                self.parent().indexOf(self) + side,
                NestedSplitterChoice(self))

        elif layout:
            new = NestedSplitter(None,orientation=orientation,
                root=self.root)
            # parent set by insertWidget() below
            old = self
            pos = layout.indexOf(old)
            ### layout.insertWidget(pos,new)
            new.addWidget(old)
            if button:
                new.insertWidget(side,NestedSplitterChoice(new))
            elif w:
                new.insertWidget(side,w)
            else:
                g.trace('can not happen: no w')
        else:
            # fail - parent is not NestedSplitter and has no layout
            g.trace('fail',self)
            pass
    #@+node:ekr.20110316093303.14494: *3* choice_menu
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
    #@+node:ekr.20110316093303.14496: *3* contains
    def contains(self, widget):

        """check if widget is a descendent of self"""

        for i in range(self.count()):
            if widget == self.widget(i):
                return True
            if isinstance(self.widget(i), NestedSplitter):
                if self.widget(i).contains(widget):
                    return True

        return False
    #@+node:ekr.20110316093303.14497: *3* createHandle
    def createHandle(self, *args, **kargs):

        return NestedSplitterHandle(self)
    #@+node:ekr.20110316093303.14498: *3* handle_context
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
    #@+node:ekr.20110316093303.14499: *3* insert (changed)
    def insert(self,index,button=True,w=None):
        
        if button:
            w = NestedSplitterChoice(self)
            # A QWidget, with self as parent.
            # This creates the menu.
        elif not w:
            w = QtGui.QWidget(self) # Should never happen.

        self.insertWidget(index,w)
        
        return w
    #@+node:ekr.20110316093303.14500: *3* invalid_swap
    def invalid_swap(self,w0,w1):
        
        return (
            w0 == w1 or
            isinstance(w0,NestedSplitter) and w0.contains(w1) or
            isinstance(w1,NestedSplitter) and w1.contains(w0))
    #@+node:ekr.20110316093303.14501: *3* mark
    def mark(self, index, side):

        self.root.marked = (self, index, side-1,
            self.widget(index+side-1))
    #@+node:ekr.20110316093303.14502: *3* max_count
    def max_count(self):

        """find max widgets in this and child splitters"""

        return max([i.count() for i in self.self_and_descendants()])

    #@+node:ekr.20110316093303.14503: *3* register
    def register(self, cb):
        
        # g.trace(cb)

        self.root.callbacks.append(cb)
    #@+node:ekr.20110316093303.14504: *3* remove & helper
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

    #@+node:ekr.20110316093303.14495: *4* close_or_keep
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
    #@+node:ekr.20110316093303.14505: *3* replace_widget
    def replace_widget(self, old, new):

        self.insertWidget(self.indexOf(old), new)
        old.deleteLater()

    #@+node:ekr.20110316093303.14506: *3* rotate
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
    #@+node:ekr.20110316093303.14507: *3* self_and_descendants
    def self_and_descendants(self):

        """Yield self and all **NestedSplitter** descendants"""

        for i in range(self.count()):
            if isinstance(self.widget(i), NestedSplitter):
                for w in self.widget(i).self_and_descendants():
                    yield w
        yield self
    #@+node:ekr.20110316093303.14508: *3* split
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
    #@+node:ekr.20110316093303.14509: *3* swap
    def swap(self, index):

        self.insertWidget(index-1, self.widget(index))
    #@+node:ekr.20110316093303.14510: *3* swap_with_marked
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
    #@+node:ekr.20110316093303.14511: *3* top
    def top(self):

        """find top widget, which is not necessarily root"""

        top = self
        while isinstance(top.parent(), NestedSplitter):
            top = top.parent()

        return top
    #@-others
#@+node:ekr.20110316093303.14513: ** main & helpers
def main():
    
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
#@+node:ekr.20110316093303.14514: *3* demo_nest
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

#@+node:ekr.20110316093303.14515: *3* callback
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

#@+node:ekr.20110316093303.14516: *3* callback2
# example - remove "Remove" commands from handle context menu
def callback2(menu, splitter, index, button_mode):

    if button_mode:
        return

    for i in [i for i in menu.actions()
              if str(i.objectName()).startswith('remove')]:
        menu.removeAction(i)

#@+node:ekr.20110316093303.14517: *3* dont_close_special
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
#@-others

if __name__ == "__main__":
    main()
#@-leo
