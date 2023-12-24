#@+leo-ver=5-thin
#@+node:ekr.20170428084208.354: * @file ../external/npyscreen/wgtextboxunicode.py
#@+others
#@+node:ekr.20170428084208.355: ** Declarations
from . import wgtextbox

import unicodedata
# import curses



#@+node:ekr.20170428084208.356: ** class TextfieldUnicode
class TextfieldUnicode(wgtextbox.Textfield):
    width_mapping = {'F': 2, 'H': 1, 'W': 2, 'Na': 1, 'N': 1}
    #@+others
    #@+node:ekr.20170428084208.357: *3* find_apparent_cursor_position
    def find_apparent_cursor_position(self,):
        string_to_print = self.display_value(self.value)[self.begin_at : self.maximum_string_length + self.begin_at - self.left_margin]
        cursor_place_in_visible_string = self.cursor_position - self.begin_at
        counter = 0
        columns = 0
        while counter < cursor_place_in_visible_string:
            columns += self.find_width_of_char(string_to_print[counter])
            counter += 1
        return columns

    #@+node:ekr.20170428084208.358: *3* TextfieldUnicode.find_width_of_char
    def find_width_of_char(self, char):
        return 1
        w = unicodedata.east_asian_width(char)
        if w == 'A':
            # Ambiguous - allow 1, but be aware that this could well be wrong
            return 1
        else:
            return self.__class__.width_mapping[w]





    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@-leo
