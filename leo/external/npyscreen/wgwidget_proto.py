#@+leo-ver=5-thin
#@+node:ekr.20170428084208.436: * @file ../external/npyscreen/wgwidget_proto.py
#@+others
#@+node:ekr.20170428084208.437: ** Declarations
import sys

#@+node:ekr.20170428084208.438: ** class _LinePrinter
class _LinePrinter:
    """A base class for printing lines to the screen.
       Do not use directly. For internal use only.
       Experimental.
    """
    #@+others
    #@+node:ekr.20170428084208.439: *3* _LinePrinter.find_width_of_char
    def find_width_of_char(self, ch):
        # will eventually need changing.
        return 1

    #@+node:ekr.20170428084208.440: *3* _print_unicode_char
    def _print_unicode_char(self, ch, force_ascii=None):
        if hasattr(self, '_force_ascii') and force_ascii is None:
            force_ascii = self._force_ascii
        # return the ch to print.  For python 3 this is just ch
        if force_ascii:
            return ch.encode('ascii', 'replace')
        elif sys.version_info[0] >= 3:
            return ch
        else:
            return ch.encode('utf-8', 'replace')

    #@+node:ekr.20170428084208.441: *3* add_line
    def add_line(self, realy, realx,
                unicode_string,
                attributes_list, max_columns,
                force_ascii=False):
        if isinstance(unicode_string, bytes):
            raise ValueError("This class prints unicode strings only.")

        if len(unicode_string) != len(attributes_list):
            raise ValueError("Must supply an attribute for every character.")

        column = 0
        place_in_string = 0

        if hasattr(self, 'curses_pad'):
            # we are a form
            print_on = self.curses_pad
        else:
            # we are a widget
            print_on = self.parent.curses_pad


        while column <= (max_columns - 1):
            try:
                width_of_char_to_print = self.find_width_of_char(unicode_string[place_in_string])
            except IndexError:
                break
            if column - 1 + width_of_char_to_print > max_columns:
                break
            try:
                print_on.addstr(realy, realx + column,
                    self._print_unicode_char(unicode_string[place_in_string]),
                    attributes_list[place_in_string]
                    )
            except IndexError:
                break
            column += width_of_char_to_print
            place_in_string += 1

    #@+node:ekr.20170428084208.442: *3* make_attributes_list
    def make_attributes_list(self, unicode_string, attribute):
        """A convenience function.  Returns a list the length of the unicode_string
        provided, with each entry of the list containing a copy of attribute."""
        if isinstance(unicode_string, bytes):
            raise ValueError("This class is intended for unicode strings only.")

        atb_array = []
        ln = len(unicode_string)
        for x in range(ln):
            atb_array.append(attribute)
        return atb_array
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@nobeautify
#@-leo
