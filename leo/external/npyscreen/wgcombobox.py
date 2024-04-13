#@+leo-ver=5-thin
#@+node:ekr.20170428084207.561: * @file ../external/npyscreen/wgcombobox.py
#!/usr/bin/env python
#@+others
#@+node:ekr.20170428084207.562: ** Declarations
import curses

from . import wgtextbox as textbox
from . import wgmultiline as multiline
# from . import fmForm        as Form
from . import fmPopup as Popup
from . import wgtitlefield as titlefield

#@+node:ekr.20170428084207.563: ** class ComboBox
class ComboBox(textbox.Textfield):
    ENSURE_STRING_VALUE = False
    #@+others
    #@+node:ekr.20170428084207.564: *3* ComboBox.__init__
    def __init__(self, screen, value=None, values=None, **keywords):
        self.values = values or []
        self.value = value or None
        if value == 0:
            self.value = 0
        super(ComboBox, self).__init__(screen, **keywords)

    #@+node:ekr.20170428084207.565: *3* ComboBox.display_value
    def display_value(self, vl):
        """Overload this function to change how values are displayed.
        Should accept one argument (the object to be represented), and return a string."""
        return str(vl)

    #@+node:ekr.20170428084207.566: *3* ComboBox.update
    def update(self, **keywords):
        keywords.update({'cursor': False})
        super(ComboBox, self).update(**keywords)

    #@+node:ekr.20170428084207.567: *3* ComboBox._print
    def _print(self):
        if self.value == None or self.value == '':
            printme = '-unset-'
        else:
            try:
                printme = self.display_value(self.values[self.value])
            except IndexError:
                printme = '-error-'
        if self.do_colors():
            self.parent.curses_pad.addnstr(self.rely, self.relx, printme, self.width, self.parent.theme_manager.findPair(self))
        else:
            self.parent.curses_pad.addnstr(self.rely, self.relx, printme, self.width)


    #@+node:ekr.20170428084207.568: *3* ComboBox.edit
    def edit(self):
        #We'll just use the widget one
        super(textbox.Textfield, self).edit()

    #@+node:ekr.20170428084207.569: *3* ComboBox.set_up_handlers
    def set_up_handlers(self):
        '''ComboBox.set_up_handlers.'''
        super(textbox.Textfield, self).set_up_handlers()
        self.handlers.update({
            curses.ascii.SP: self.h_change_value,
            #curses.ascii.TAB: self.h_change_value,
            curses.ascii.NL: self.h_change_value,
            curses.ascii.CR: self.h_change_value,
            ord('x'): self.h_change_value,
            ord('k'): self.h_exit_up,
            ord('j'): self.h_exit_down,
            ord('h'): self.h_exit_left,
            ord('l'): self.h_exit_right,
        })

    #@+node:ekr.20170428084207.570: *3* ComboBox.h_change_value
    def h_change_value(self, input):
        "Pop up a window in which to select the values for the field"
        F = Popup.Popup(name=self.name)
        l = F.add(multiline.MultiLine,
            values=[self.display_value(x) for x in self.values],
            return_exit=True, select_exit=True,
            value=self.value)
        F.display()
        l.edit()
        self.value = l.value


    #@-others
#@+node:ekr.20170428084207.571: ** class TitleCombo
class TitleCombo(titlefield.TitleText):
    _entry_type = ComboBox

    #@+others
    #@+node:ekr.20170428084207.572: *3* get_values
    def get_values(self):
        try:
            return self.entry_widget.values
        except Exception:
            try:
                return self.__tmp_values
            except Exception:
                return None

    #@+node:ekr.20170428084207.573: *3* set_values
    def set_values(self, values):
        try:
            self.entry_widget.values = values
        except Exception:
            # probably trying to set the value before the textarea is initialized
            self.__tmp_values = values

    #@+node:ekr.20170428084207.574: *3* del_values
    def del_values(self):
        del self.entry_widget.values

    values = property(get_values, set_values, del_values)

    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
