#@+leo-ver=5-thin
#@+node:ekr.20170428084207.153: * @file ../external/npyscreen/fmFileSelector.py
# type: ignore
#@+others
#@+node:ekr.20170428084207.154: ** Declarations
from . import fmFormMutt
# from . import wgmultiline
from . import wggrid
from . import wgautocomplete
from . import utilNotify

import curses
import os
import os.path
# import operator

#@+node:ekr.20170428084207.155: ** class FileCommand
class FileCommand(wgautocomplete.Filename):
    #@+others
    #@+node:ekr.20170428084207.156: *3* set_up_handlers
    def set_up_handlers(self):
        '''FileCommand.set_up_handlers.'''
        super(FileCommand, self).set_up_handlers()
        self.handlers.update({
            curses.ascii.NL: self.h_select_file,
            curses.ascii.CR: self.h_select_file,
            "^W": self.h_up_level,
        })

    #@+node:ekr.20170428084207.157: *3* h_select_file
    def h_select_file(self, *args, **keywords):
        self.h_exit_down(None)
        self.parent.try_exit()

    #@+node:ekr.20170428084207.158: *3* h_up_level
    def h_up_level(self, *args, **keywords):
        self.value = os.path.split(self.value)[0]
        self.cursor_position = len(self.value)

    #@+node:ekr.20170428084207.159: *3* auto_complete
    def auto_complete(self, input):
        self.value = os.path.expanduser(self.value)

        directory, fname = os.path.split(self.value)
        # Let's have absolute paths.
        directory = os.path.abspath(directory)

        if self.value == '':
            self.value = directory


        try:
            flist = os.listdir(directory)
        except Exception:
            self.show_brief_message("Can't read directory!")
            return False

        flist = [os.path.join(directory, x) for x in flist]
        possibilities = list(filter(
            (lambda x: os.path.split(x)[1].startswith(fname)), flist
            ))

        if len(possibilities) == 0:
            # can't complete
            curses.beep()
            self.cursor_position = len(self.value)

        elif len(possibilities) == 1:
            if self.value != possibilities[0]:
                self.value = possibilities[0]
                if os.path.isdir(self.value) \
                    and not self.value.endswith(os.sep):
                    self.value = self.value + os.sep
            self.cursor_position = len(self.value)

        elif len(possibilities) > 1:
            self.value = os.path.commonprefix(possibilities)
            self.cursor_position = len(self.value)
            curses.beep()

        if os.path.isdir(self.value) and len(possibilities) < 2:
            self.parent.wMain.change_dir(self.value)
            if os.path.isdir(self.value) \
                and not self.value.endswith(os.sep):
                self.value = self.value + os.sep
            self.cursor_position = len(self.value)

            #self.h_exit_up(None)
        else:
            self.parent.value = directory
            self.parent.update_grid()


    #@-others
#@+node:ekr.20170428084207.160: ** class FileGrid
class FileGrid(wggrid.SimpleGrid):
    default_column_number = 3

    #@+others
    #@+node:ekr.20170428084207.161: *3* FileGrid.set_up_handlers
    def set_up_handlers(self):
        '''FileGrid.set_up_handlers.'''
        super(FileGrid, self).set_up_handlers()
        self.handlers.update({
            curses.ascii.NL: self.h_select_file,
            curses.ascii.CR: self.h_select_file,
            curses.ascii.SP: self.h_select_file,
        })

    #@+node:ekr.20170428084207.162: *3* FileGrid.change_dir
    def change_dir(self, select_file):
        try:
            os.listdir(select_file)
        except OSError:
            utilNotify.notify_wait(title="Error", message="Cannot enter directory.")
            return False
        self.parent.value = select_file
        self.parent.wCommand.value = select_file
        self.parent.update_grid()
        self.edit_cell = [0, 0]
        self.begin_row_display_at = 0
        self.begin_col_display_at = 0
        return True



    #@+node:ekr.20170428084207.163: *3* FileGrid.h_select_file
    def h_select_file(self, *args, **keywrods):
        try:
            select_file = os.path.join(self.parent.value, self.values[self.edit_cell[0]][self.edit_cell[1]])
            select_file = os.path.abspath(select_file)
        except(TypeError, IndexError):
            self.edit_cell = [0, 0]
            return False

        if os.path.isdir(select_file):
            self.change_dir(select_file)
        else:
            self.parent.wCommand.value = select_file
            self.h_exit_down(None)

    #@+node:ekr.20170428084207.164: *3* FileGrid.display_value
    def display_value(self, vl):
        p = os.path.split(vl)
        if p[1]:
            return p[1]
        else:
            return os.path.split(p[0])[1] + os.sep

    #@-others
#@+node:ekr.20170428084207.165: ** class FileSelector
class FileSelector(fmFormMutt.FormMutt):
    MAIN_WIDGET_CLASS = FileGrid
    COMMAND_WIDGET_CLASS = FileCommand
    BLANK_LINES_BASE = 0
    #@+others
    #@+node:ekr.20170428084207.166: *3* __init__
    def __init__(self,
    select_dir=False,  #Select a dir, not a file
    must_exist=False,  #Selected File must already exist
    confirm_if_exists=True,
    sort_by_extension=True,
    *args, **keywords):

        self.select_dir = select_dir
        self.must_exist = must_exist
        self.confirm_if_exists = confirm_if_exists
        self.sort_by_extension = sort_by_extension

        super(FileSelector, self).__init__(*args, **keywords)
        try:
            if not self.value:
                self.value = os.getcwd()
        except Exception:
            self.value = os.getcwd()

    #@+node:ekr.20170428084207.167: *3* try_exit
    def try_exit(self):
        if not self.wCommand.value:
            self.value = ''
            self.exit_editing()
            return None

        # There is a bug in the next three lines
        self.wCommand.value = os.path.join(self.value, self.wCommand.value)
        self.wCommand.value = os.path.expanduser(self.wCommand.value)
        self.wCommand.value = os.path.abspath(self.wCommand.value)


        self.value = self.wCommand.value

        if self.confirm_if_exists and os.path.exists(self.value):
            if not utilNotify.notify_yes_no(title="Confirm", message="Select Existing File?"):
                return False
        if self.must_exist and not os.path.exists(self.value):
            utilNotify.notify_confirm(title="Error", message="Selected filename does not exist.")
            return False
        if self.select_dir and not os.path.isdir(self.value):
            utilNotify.notify_confirm(title="Error", message="Selected filename is not a directory.")
            return False
        self.exit_editing()
        return True

    #@+node:ekr.20170428084207.168: *3* set_colors
    def set_colors(self):
        self.wCommand.color = 'IMPORTANT'
        self.wCommand.color = 'STANDOUT'


    #@+node:ekr.20170428084207.169: *3* beforeEditing
    def beforeEditing(self,):
        self.adjust_widgets()
        self.set_colors()

    #@+node:ekr.20170428084207.170: *3* update_grid
    def update_grid(self,):
        if self.value:
            self.value = os.path.expanduser(self.value)

        if not os.path.exists(self.value):
            self.value = os.getcwd()

        if os.path.isdir(self.value):
            working_dir = self.value
        else:
            working_dir = os.path.dirname(self.value)

        self.wStatus1.value = working_dir

        file_list = []
        if os.path.abspath(os.path.join(working_dir, '..')) != os.path.abspath(working_dir):
            file_list.append('..')
        try:
            file_list.extend([os.path.join(working_dir, fn) for fn in os.listdir(working_dir)])
        except OSError:
            utilNotify.notify_wait(title="Error", message="Could not read specified directory.")
        # DOES NOT CURRENTLY WORK - EXCEPT FOR THE WORKING DIRECTORY.  REFACTOR.
        new_file_list = []
        for f in file_list:
            f = os.path.normpath(f)
            if os.path.isdir(f):
                new_file_list.append(f + os.sep)
            else:
                new_file_list.append(f)  # + "*")
        file_list = new_file_list
        del new_file_list

        # sort Filelist
        file_list.sort()
        if self.sort_by_extension:
            file_list.sort(key=self.get_extension)
        file_list.sort(key=os.path.isdir, reverse=True)

        self.wMain.set_grid_values_from_flat_list(file_list, reset_cursor=False)

        self.display()

    #@+node:ekr.20170428084207.171: *3* get_extension
    def get_extension(self, fn):
        return os.path.splitext(fn)[1]

    #@+node:ekr.20170428084207.172: *3* adjust_widgets
    def adjust_widgets(self):
        self.update_grid()

    #@-others
#@+node:ekr.20170428084207.173: ** selectFile
def selectFile(starting_value=None, *args, **keywords):
    F = FileSelector(*args, **keywords)
    F.set_colors()
    F.wCommand.show_bold = True
    if starting_value:
        if not os.path.exists(os.path.abspath(os.path.expanduser(starting_value))):
            F.value = os.getcwd()
        else:
            F.value = starting_value
            F.wCommand.value = starting_value
    else:
        F.value = os.getcwd()
    F.update_grid()
    F.display()
    F.edit()
    return F.wCommand.value

#@-others
#@@language python
#@@tabwidth -4
#@@nobeautify
#@-leo
