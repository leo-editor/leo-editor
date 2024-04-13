#@+leo-ver=5-thin
#@+node:ekr.20170428084207.618: * @file ../external/npyscreen/wgFormControlCheckbox.py
#!/usr/bin/env python

#@+others
#@+node:ekr.20170428084207.619: ** Declarations
from . import wgcheckbox
import weakref

#@+node:ekr.20170428084207.620: ** class FormControlCheckbox
class FormControlCheckbox(wgcheckbox.Checkbox):
    #@+others
    #@+node:ekr.20170428084207.621: *3* __init__
    def __init__(self, *args, **keywords):
        super(FormControlCheckbox, self).__init__(*args, **keywords)
        self._visibleWhenSelected = []
        self._notVisibleWhenSelected = []

    #@+node:ekr.20170428084207.622: *3* addVisibleWhenSelected
    def addVisibleWhenSelected(self, w):
        """Add a widget to be visible only when this box is selected"""
        self._register(w, vws=True)

    #@+node:ekr.20170428084207.623: *3* addInvisibleWhenSelected
    def addInvisibleWhenSelected(self, w):
        self._register(w, vws=False)

    #@+node:ekr.20170428084207.624: *3* _register
    def _register(self, w, vws=True):
        if vws:
            working_list = self._visibleWhenSelected
        else:
            working_list = self._notVisibleWhenSelected

        if w in working_list:
            pass
        else:
            try:
                working_list.append(weakref.proxy(w))
            except TypeError:
                working_list.append(w)

        self.updateDependents()

    #@+node:ekr.20170428084207.625: *3* updateDependents
    def updateDependents(self):
        # This doesn't yet work.
        if self.value:
            for w in self._visibleWhenSelected:
                w.hidden = False
                w.editable = True
            for w in self._notVisibleWhenSelected:
                w.hidden = True
                w.editable = False
        else:
            for w in self._visibleWhenSelected:
                w.hidden = True
                w.editable = False
            for w in self._notVisibleWhenSelected:
                w.hidden = False
                w.editable = True
        self.parent.display()

    #@+node:ekr.20170428084207.626: *3* h_toggle
    def h_toggle(self, *args):
        super(FormControlCheckbox, self).h_toggle(*args)
        self.updateDependents()



    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
