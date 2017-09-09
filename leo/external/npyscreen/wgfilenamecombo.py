#@+leo-ver=5-thin
#@+node:ekr.20170428084207.611: * @file ../external/npyscreen/wgfilenamecombo.py
#@+others
#@+node:ekr.20170428084207.612: ** Declarations
from . import fmFileSelector
from . import wgcombobox

#@+node:ekr.20170428084207.613: ** class FilenameCombo
class FilenameCombo(wgcombobox.ComboBox):
    #@+others
    #@+node:ekr.20170428084207.614: *3* __init__
    def __init__(self, screen,
    # The following are all options taken from the FileSelector
    select_dir=False, #Select a dir, not a file
    must_exist=False, #Selected File must already exist
    confirm_if_exists=False,
    sort_by_extension=True,
    *args, **keywords):
        self.select_dir = select_dir
        self.must_exist = must_exist
        self.confirm_if_exists = confirm_if_exists
        self.sort_by_extension = sort_by_extension

        super(FilenameCombo, self).__init__(screen, *args, **keywords)

    #@+node:ekr.20170428084207.615: *3* _print
    def _print(self):
        if self.value == None:
            printme = '- Unset -'
        else:
            try:
                printme = self.display_value(self.value)
            except IndexError:
                printme = '-error-'
        if self.do_colors():
            self.parent.curses_pad.addnstr(self.rely, self.relx, printme, self.width, self.parent.theme_manager.findPair(self))
        else:
            self.parent.curses_pad.addnstr(self.rely, self.relx, printme, self.width)



    #@+node:ekr.20170428084207.616: *3* h_change_value
    def h_change_value(self, *args, **keywords):
        self.value = fmFileSelector.selectFile(
            starting_value = self.value,
            select_dir = self.select_dir,
            must_exist = self.must_exist,
            confirm_if_exists = self.confirm_if_exists,
            sort_by_extension = self.sort_by_extension
        )
        if self.value == '':
            self.value = None
        self.display()


    #@-others
#@+node:ekr.20170428084207.617: ** class TitleFilenameCombo
class TitleFilenameCombo(wgcombobox.TitleCombo):
    _entry_type = FilenameCombo
#@-others
#@@language python
#@@tabwidth -4
#@-leo
