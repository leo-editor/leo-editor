#@+leo-ver=5-thin
#@+node:ekr.20170428084208.245: * @file ../external/npyscreen/wgmultiselecttree.py
#@+others
#@+node:ekr.20170428084208.246: ** Declarations
from . import wgmultilinetree as multilinetree
from . import wgcheckbox      as checkbox
import curses
import weakref


#@+node:ekr.20170428084208.247: ** class MultiSelectTree
class MultiSelectTree(multilinetree.SelectOneTree):
    _contained_widgets = checkbox.Checkbox

    #@+others
    #@+node:ekr.20170428084208.248: *3* MultiSelectTree.set_up_handlers
    def set_up_handlers(self):
        '''MultiSelectTree.set_up_handlers.'''
        super(MultiSelectTree, self).set_up_handlers()
        self.handlers.update({
            ord("x"):    self.h_select_toggle,
            curses.ascii.SP: self.h_select_toggle,
            ord("X"):    self.h_select,
            "^U":        self.h_select_none,
        })
    #@+node:ekr.20170428084208.249: *3* MultiSelectTree.h_select_none
    def h_select_none(self, input):
        self.value = []

    #@+node:ekr.20170428084208.250: *3* MultiSelectTree.h_select_toggle
    def h_select_toggle(self, input):
        try:
            working_with = weakref.proxy(self.values[self.cursor_line])
        except TypeError:
            working_with = self.values[self.cursor_line]
        if working_with in self.value:
            self.value.remove(working_with)
        else:
            self.value.append(working_with)

    #@+node:ekr.20170428084208.251: *3* MultiSelectTree.h_set_filtered_to_selected
    def h_set_filtered_to_selected(self, ch):
        self.value = self.get_filtered_values()

    #@+node:ekr.20170428084208.252: *3* MultiSelectTree.h_select_exit
    def h_select_exit(self, ch):
        try:
            working_with = weakref.proxy(self.values[self.cursor_line])
        except TypeError:
            working_with = self.values[self.cursor_line]

        if not working_with in self.value:
            self.value.append(working_with)
        if self.return_exit:
            self.editing = False
            self.how_exited=True
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
