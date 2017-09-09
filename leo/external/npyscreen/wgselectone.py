#@+leo-ver=5-thin
#@+node:ekr.20170428084208.290: * @file ../external/npyscreen/wgselectone.py
#@+others
#@+node:ekr.20170428084208.291: ** Declarations
from . import wgmultiline  as multiline
from . import wgcheckbox   as checkbox

#@+node:ekr.20170428084208.292: ** class SelectOne
class SelectOne(multiline.MultiLine):
    _contained_widgets = checkbox.RoundCheckBox

    #@+others
    #@+node:ekr.20170428084208.293: *3* SelectOne.update
    def update(self, clear=True):
        if self.hidden:
            self.clear()
            return False
        # Make sure that self.value is a list
        if not hasattr(self.value, "append"):
            if self.value is not None:
                self.value = [self.value, ]
            else:
                self.value = []

        super(SelectOne, self).update(clear=clear)

    #@+node:ekr.20170428084208.294: *3* SelectOne.h_select
    def h_select(self, ch):
        self.value = [self.cursor_line,]

    #@+node:ekr.20170428084208.295: *3* SelectOne._print_line
    def _print_line(self, line, value_indexer):
        try:
            display_this = self.display_value(self.values[value_indexer])
            line.value = display_this
            line.hide = False
            if hasattr(line, 'selected'):
                if (value_indexer in self.value and (self.value is not None)):
                    line.selected = True
                else:
                    line.selected = False
            # Most classes in the standard library use this
            else:
                if (value_indexer in self.value and (self.value is not None)):
                    line.show_bold = True
                    line.name = display_this
                    line.value = True
                else:
                    line.show_bold = False
                    line.name = display_this
                    line.value = False

            if value_indexer in self._filtered_values_cache:
                line.important = True
            else:
                line.important = False


        except IndexError:
            line.name = None
            line.hide = True

        line.highlight= False

    #@-others
#@+node:ekr.20170428084208.296: ** class TitleSelectOne
class TitleSelectOne(multiline.TitleMultiLine):
    _entry_type = SelectOne

#@-others
#@@language python
#@@tabwidth -4
#@-leo
