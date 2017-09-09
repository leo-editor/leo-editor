#@+leo-ver=5-thin
#@+node:ekr.20170428084208.285: * @file ../external/npyscreen/wgpassword.py
#!/usr/bin/python
#@+others
#@+node:ekr.20170428084208.286: ** Declarations
# import curses
from .wgtextbox import Textfield
from . import wgtitlefield as titlefield


#@+node:ekr.20170428084208.287: ** class PasswordEntry
class PasswordEntry(Textfield):
    #@+others
    #@+node:ekr.20170428084208.288: *3* _print
    def _print(self):
        strlen = len(self.value)
        if self.maximum_string_length < strlen:
            tmp_x = self.relx
            for i in range(self.maximum_string_length):
                self.parent.curses_pad.addch(self.rely, tmp_x, '-')
                tmp_x += 1

        else:
            tmp_x = self.relx
            for i in range(strlen):
                self.parent.curses_pad.addstr(self.rely, tmp_x, '-')
                tmp_x += 1

    #@-others
#@+node:ekr.20170428084208.289: ** class TitlePassword
class TitlePassword(titlefield.TitleText):
    _entry_type = PasswordEntry

#@-others
#@@language python
#@@tabwidth -4
#@-leo
