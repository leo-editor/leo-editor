#@+leo-ver=5-thin
#@+node:ekr.20170428084207.536: * @file ../external/npyscreen/wgcheckbox.py
#!/usr/bin/python

#@+others
#@+node:ekr.20170428084207.537: ** Declarations
from .wgtextbox   import Textfield
from .wgwidget    import Widget
#from .wgmultiline import MultiLine
from . import wgwidget as widget
import curses

#@+node:ekr.20170428084207.538: ** class _ToggleControl
class _ToggleControl(Widget):
    #@+others
    #@+node:ekr.20170428084207.539: *3* set_up_handlers
    def set_up_handlers(self):
        '''ToggleControl.set_up_handlers.'''
        super(_ToggleControl, self).set_up_handlers()
        self.handlers.update({
            curses.ascii.SP: self.h_toggle,
            ord('x'):        self.h_toggle,
            curses.ascii.NL: self.h_select_exit,
            curses.ascii.CR: self.h_select_exit,
            ord('j'):        self.h_exit_down,
            ord('k'):        self.h_exit_up,
            ord('h'):        self.h_exit_left,
            ord('l'):        self.h_exit_right,
        })

    #@+node:ekr.20170428084207.540: *3* h_toggle
    def h_toggle(self, ch):
        if self.value is False or self.value is None or self.value == 0:
            self.value = True
        else:
            self.value = False
        self.whenToggled()

    #@+node:ekr.20170428084207.541: *3* whenToggled
    def whenToggled(self):
        pass

    #@+node:ekr.20170428084207.542: *3* _ToggleControl.h_select_exit
    def h_select_exit(self, ch):
        if not self.value:
            self.h_toggle(ch)
        self.editing = False
        self.how_exited = widget.EXITED_DOWN


    #@-others
#@+node:ekr.20170428084207.543: ** class CheckboxBare
class CheckboxBare(_ToggleControl):
    False_box = '[ ]'
    True_box  = '[X]'

    #@+others
    #@+node:ekr.20170428084207.544: *3* __init__
    def __init__(self, screen, value = False, **keywords):
        super(CheckboxBare, self).__init__(screen, **keywords)
        self.value = value
        self.hide  = False

    #@+node:ekr.20170428084207.545: *3* calculate_area_needed
    def calculate_area_needed(self):
        return 1, 4

    #@+node:ekr.20170428084207.546: *3* CheckboxBare.update
    def update(self, clear=True):
        if clear: self.clear()
        if self.hidden:
            self.clear()
            return False
        if self.hide: return True

        if self.value:
            cb_display = self.__class__.True_box
        else:
            cb_display = self.__class__.False_box

        if self.do_colors():
            self.parent.curses_pad.addstr(self.rely, self.relx, cb_display, self.parent.theme_manager.findPair(self, 'CONTROL'))
        else:
            self.parent.curses_pad.addstr(self.rely, self.relx, cb_display)

        if self.editing:
            if self.value:
                char_under_cur = 'X'
            else:
                char_under_cur = ' '
            if self.do_colors():
                self.parent.curses_pad.addstr(self.rely, self.relx + 1, char_under_cur, self.parent.theme_manager.findPair(self) | curses.A_STANDOUT)
            else:
                self.parent.curses_pad.addstr(self.rely,  self.relx + 1, curses.A_STANDOUT)






    #@-others
#@+node:ekr.20170428084207.547: ** class Checkbox
class Checkbox(_ToggleControl):
    False_box = '[ ]'
    True_box  = '[X]'

    #@+others
    #@+node:ekr.20170428084207.548: *3* __init__
    def __init__(self, screen, value = False, **keywords):
        self.value = value
        super(Checkbox, self).__init__(screen, **keywords)

        self._create_label_area(screen)


        self.show_bold = False
        self.highlight = False
        self.important = False
        self.hide      = False

    #@+node:ekr.20170428084207.549: *3* _create_label_area
    def _create_label_area(self, screen):
        l_a_width = self.width - 5

        if l_a_width < 1:
             raise ValueError("Width of checkbox + label must be at least 6")

        self.label_area = Textfield(screen, rely=self.rely, relx=self.relx+5,
                      width=self.width-5, value=self.name)


    #@+node:ekr.20170428084207.550: *3* CheckBox.update
    def update(self, clear=True):
        if clear: self.clear()
        if self.hidden:
            self.clear()
            return False
        if self.hide: return True

        if self.value:
            cb_display = self.__class__.True_box
        else:
            cb_display = self.__class__.False_box

        if self.do_colors():
            self.parent.curses_pad.addstr(self.rely, self.relx, cb_display, self.parent.theme_manager.findPair(self, 'CONTROL'))
        else:
            self.parent.curses_pad.addstr(self.rely, self.relx, cb_display)

        self._update_label_area()

    #@+node:ekr.20170428084207.551: *3* _update_label_area
    def _update_label_area(self, clear=True):
        self.label_area.value = self.name
        self._update_label_row_attributes(self.label_area, clear=clear)

    #@+node:ekr.20170428084207.552: *3* _update_label_row_attributes
    def _update_label_row_attributes(self, row, clear=True):
        if self.editing:
            row.highlight = True
        else:
            row.highlight = False

        if self.show_bold:
            row.show_bold = True
        else:
            row.show_bold = False

        if self.important:
            row.important = True
        else:
            row.important = False

        if self.highlight:
            row.highlight = True
        else:
            row.highlight = False

        row.update(clear=clear)

    #@+node:ekr.20170428084207.553: *3* calculate_area_needed
    def calculate_area_needed(self):
        return 1,0

    #@-others
#@+node:ekr.20170428084207.554: ** class CheckBox
class CheckBox(Checkbox):
    pass


#@+node:ekr.20170428084207.555: ** class RoundCheckBox
class RoundCheckBox(Checkbox):
    False_box = '( )'
    True_box  = '(X)'

#@+node:ekr.20170428084207.556: ** class CheckBoxMultiline
class CheckBoxMultiline(Checkbox):
    #@+others
    #@+node:ekr.20170428084207.557: *3* _create_label_area
    def _create_label_area(self, screen):
        self.label_area = []
        for y in range(self.height):
            self.label_area.append(
               Textfield(screen, rely=self.rely+y,
                           relx=self.relx+5,
                           width=self.width-5,
                           value=None)
            )

    #@+node:ekr.20170428084207.558: *3* _update_label_area
    def _update_label_area(self, clear=True):
        for x in range(len(self.label_area)):
            if x >= len(self.name):
                self.label_area[x].value = ''
                self.label_area[x].hidden = True
            else:
                self.label_area[x].value = self.name[x]
                self.label_area[x].hidden = False
                self._update_label_row_attributes(self.label_area[x], clear=clear)

    #@+node:ekr.20170428084207.559: *3* calculate_area_needed
    def calculate_area_needed(self):
        return 0,0

    #@-others
#@+node:ekr.20170428084207.560: ** class RoundCheckBoxMultiline
class RoundCheckBoxMultiline(CheckBoxMultiline):
    False_box = '( )'
    True_box  = '(X)'


#@-others
#@@language python
#@@tabwidth -4
#@-leo
