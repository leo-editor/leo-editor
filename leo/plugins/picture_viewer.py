#@+leo-ver=5-thin
#@+node:ekr.20211021200745.1: * @file ../plugins/picture_viewer.py
#@+<< docstring (picture_viewer.py) >>
#@+node:ekr.20211021202710.1: ** << docstring (picture_viewer.py) >>
"""
Display image files in a directory tree as a slide show.

This plugin will display all files in a directory tree that have image
extensions. By default the recognized extensions are '.jpeg', '.jpg', and
'.png'. Other types of image files can be displayed as long as the they are
types known by the Qt PixMap class, including '.gif' and '.bmp'. See, for
example:

https://doc.qt.io/qt-5/qpixmap.html#reading-and-writing-image-files

This plugin should be called from a script (or @command or @button node) as follows:

    from leo.plugins.picture_viewer import Slides
    Slides().run(c)  # See below for defaults.

*Note*: do not enable this plugin. It will be loaded by the calling script.

**Key bindings**

Plain keys control the display of slides:

      space: show the next slide.
  backspace: show the previous slide.
     escape: end the slideshow
          =: zoom in
          -: zoom out
arrows keys: pan the slide
          d: prompt to move the slide to the trash
          h: show the help message
          m: move the file.

**Defaults**

The following keyword arguments may be supplied to the run method:

    background_color = "black",  # Default background color.
    delay = 100,  # Delay between slides, in seconds.
    extensions = ['.jpeg', '.jpg', '.png'],  # List of file extensions.
    full_screen = True,  # True: start in full-screen mode.
    height = 900,  # Window height (pixels) when not in full screen mode.
    path = None,  # If none, display a dialog.
    reset_zoom = True,  # True, reset zoom factor when changing slides.
    sort_kind = 'random',  # 'date', 'name', 'none', 'random', or 'size'
    width = 1500,  # Window width (pixels) when not un full screen mode.

"""
#@-<< docstring (picture_viewer.py) >>
#@+<< imports >>
#@+node:ekr.20211021202633.1: ** << imports >>
import os
import pathlib
import sys
import random
import textwrap
# Third-party imports
try:
    from leo.core.leoQt import isQt5, QtCore, QtGui, QtWidgets
except ImportError:
    QtWidgets = None
# Leo imports
from leo.core import leoGlobals as g
#@-<< imports >>

# Globals to retain references to objects.
gApp = None
gWidget = None

#@+others
#@+node:ekr.20211021202802.1: ** init (picture_viewer.py)
def init():
    """Return True if the plugin has loaded successfully."""
    return g.app.gui.guiName().lower().startswith('qt')
#@+node:ekr.20211023201914.1: ** main
def main():
    args = getargs()
    global gApp
    gApp = QtWidgets.QApplication(sys.argv)
    scale_ = args.get('scale', None)
    Slides.scale = float(scale_ or 1.0)
    if scale_:
        args.pop('scale')

    ok = Slides().run(c = None, **args)
    if ok:
        if isQt5:
            sys.exit(gApp.exec_())
        else:
            sys.exit(gApp.exec())
#@+node:tom.20211023221408.1: *3* getargs
def getargs():
    args = {}
    if len(sys.argv) == 1:
        return args

    argv = sys.argv[1:]
    if '-h' in argv or '--help' in argv:
        print(HELP)
        sys.exit(0)

    argsplits = [arg.replace('--', '').split('=') for arg in argv]
    args = dict(argsplits)

    for key in ('width', 'height'):
        if key in args:
            args[key] = int(args[key])

    if key in ('delay'):
        args['delay'] = float(args['delay'])

    for key in ('full_screen', 'reset_zoom', 'verbose'):
        if key in args:
            args[key] = args[key].lower() == 'true'

    if 'extensions' in args:
        # Must be a comma separated list with no spaces
        args['extensions'] = args['extensions'].split(',')
    return args
#@+node:tom.20211023234125.1: *3* HELP
HELP = """Display images in a directory tree as a slide show.
USAGE: python3 -m leo.plugins.picture_viewer [options]

Options must have the form "--<name>=<value>".  For example:
    
    --delay=20

AVAILABLE OPTIONS with defaults:
    background_color -- a CSS color name. Default: black.
    delay -- Delay between slides, in seconds. Default: 100 
    extensions -- a comma-separated list of image file extensions.
                  Default: .jpeg,.jpg,.png  (no spaces allowed)
    full_screen -- start in full-screen mode. Any other value than true 
                   or True will be treated as False.  Default: False.
    height -- window height (pixels) when not in full screen mode.
              Default: 900.
    path -- path to image top directory. If not present, display a dialog.
    reset_zoom -- reset zoom factor when changing slides. Any other 
                  value than true or True will be treated as False.
                  Default: True
    scale -- relative size of the image frame.  Default: 1.0.
    sort_kind -- one of random, date, name, none, random, or size
    verbose -- whether to print info messages.  Any other value than true 
               or True will be treated as False. Default: False
    width -- window width (pixels) when not in full screen mode.
             Default: 1500
"""
#@+node:ekr.20211021202356.1: ** class Slides
if QtWidgets:

    class Slides(QtWidgets.QWidget):

        scale = 1.0
        slide_number = -1
        timer = QtCore.QBasicTimer()

        #@+others
        #@+node:ekr.20211024030844.1: *3* Slides.closeEvent
        def closeEvent(self, event):
            """Override QWidget.closeEvent."""
            self.quit()
        #@+node:ekr.20211021200821.4: *3* Slides.delete
        send_to_trash_warning_given = False

        def delete(self):
            """Issue a prompt and delete the file if the user agrees."""
            try:
                from send2trash import send2trash
            except Exception:
                if not self.send_to_trash_warning_given:
                    self.send_to_trash_warning_given = True
                    print("Deleting files requires send2trash")
                    print("pip install Send2Trash")
                return
            file_name = self.files_list[self.slide_number]
            result = g.app.gui.runAskYesNoDialog(
                c = self.c,
                title = "Delete File?",
                message = f"Delete file {g.shortFileName(file_name)}?"
            )
            if result == 'yes':
                # Move the file to the trash.
                send2trash(file_name)
                del self.files_list[self.slide_number]
                print(f"Deleted {file_name}")
                self.slide_number = max(0, self.slide_number - 1)
                self.next_slide()
                self.raise_()
        #@+node:ekr.20211021200821.2: *3* Slides.get_files
        def get_files(self, path):
            """Return all files in path, including all subdirectories."""
            return [
                str(z) for z in pathlib.Path(path).rglob('*')
                    if z.is_file()
                    and os.path.splitext(str(z))[1].lower() in self.extensions
            ]
        #@+node:ekr.20211021200821.5: *3* Slides.keyPressEvent
        def keyPressEvent (self, event):

            i = event.key()
            s = event.text()
            mods = event.modifiers()
            if s == 'd':
                self.delete()
            elif s == 'f':
                self.toggle_full_screen()
            elif s == 'h':
                self.show_help()
            elif s == 'm':
                self.move_to()
            elif s == 'n' or i == 32:  # ' '
                self.next_slide()
            elif s == 'p' or s == '\b':
                self.prev_slide()
            elif s == 'q' or s == '\x1b':  # ESC.
                self.quit()
            elif s in '=+':
                self.zoom_in()
            elif s == '-_':
                self.zoom_out()
            elif i == 16777235:
                self.move_up()
            elif i == 16777237:
                self.move_down()
            elif i == 16777234:
                self.move_left()
            elif i == 16777236:
                self.move_right()
            else:
                print(f"picture_viewer.py: ignoring {s!r} {i}, {mods!r}")

        #@+node:ekr.20211021200821.6: *3* Slides.move_up/down/left/right
        def move_down(self):
            self.scroll_area.scrollContentsBy(0, -400 * self.scale)

        def move_left(self):
            self.scroll_area.scrollContentsBy(400 * self.scale, 0)

        def move_right(self):
            self.scroll_area.scrollContentsBy(-400 * self.scale, 0)

        def move_up(self):
            self.scroll_area.scrollContentsBy(0, 400 * self.scale)
        #@+node:ekr.20211021200821.7: *3* Slides.move_to
        def move_to(self):
            """Issue a prompt and move the file if the user agrees."""
            file_name = self.files_list[self.slide_number]
            path = QtWidgets.QFileDialog().getExistingDirectory()
            if path:
                new_path = os.path.join(path, os.path.basename(file_name))
                if os.path.exists(new_path):
                    print("File exists:", new_path)
                else:
                    pathlib.Path(file_name).rename(new_path)
                    del self.files_list[self.slide_number]
                    self.slide_number = max(0, self.slide_number - 1)
                    self.next_slide()
                    self.raise_()
        #@+node:ekr.20211021200821.8: *3* Slides.next_slide
        def next_slide(self):

            if self.slide_number + 1 < len(self.files_list):
                self.slide_number += 1  # Don't wrap.
            if self.reset_zoom:
                self.scale = 1.0
            self.show_slide()
        #@+node:ekr.20211021200821.9: *3* Slides.prev_slide
        def prev_slide(self):

            if self.slide_number > 0: # Don't wrap.
                self.slide_number -= 1
            if self.reset_zoom:
                self.scale = 1.0
            self.show_slide()
        #@+node:ekr.20211021200821.10: *3* Slides.quit
        def quit(self):
            global gApp
            self.timer.stop()
            self.destroy()
            if gApp:  # Running externally.
                gApp.exit()
                gApp = None
            else:
                print('done')
        #@+node:ekr.20211021200821.11: *3* Slides.run & helper
        def run(self,
            c,  # Required. The commander for this slideshow.
            background_color = "black",  # Default background color.
            delay = 100,  # Delay between slides, in seconds.
            extensions = None,  # List of file extensions.
            full_screen = False,  # True: start in full-screen mode.
            height = 900,  # Window height (pixels) when not in full screen mode.
            path = None,  # Root directory.
            reset_zoom = True,  # True: reset zoom factor when changing slides.
            sort_kind = 'random',  # 'date', 'name', 'none', 'random', or 'size'
            verbose = False,  # True, print info messages.
            width = 1500,  # Window width (pixels) when not un full screen mode.
        ):
            """
            Create the widgets and run the slideshow.
            Return True if any pictures were found.
            """
            # Keep a reference to this class!
            global gWidget
            gWidget = self
            # Init ivars.
            w = self
            self.c = c
            self.background_color = background_color or "black"
            self.delay = delay
            self.extensions = extensions or ['.jpeg', '.jpg', '.png']
            self.full_screen = False
            self.reset_zoom = reset_zoom
            self.verbose = verbose
            # Careful: width and height are QWidget methods.
            self._height = height
            self._width = width
            # Compute the files list.
            if not path:
                path = QtWidgets.QFileDialog().getExistingDirectory()
            if not path:
                print("No path given")
                return False
            self.files_list = self.get_files(path)
            if not self.files_list:
                print(f"No slides found in {path!r}")
                return False
            n = len(self.files_list)
            if self.verbose:
                print(f"Found {n} picture{g.plural(n)} in {path}")
            # Init the widget.
            w.make_widgets()
            # Center the widget
            qtRectangle = w.frameGeometry()
            centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
            qtRectangle.moveCenter(centerPoint)
            w.move(qtRectangle.topLeft())
            # Show the widget.
            w.showNormal()
            if full_screen:  # Not self.full_screen.
                w.toggle_full_screen()
            # Show the next slide.
            self.sort(sort_kind)
            w.next_slide()  # show_slide resets the timer.
            return True
        #@+node:ekr.20211021200821.12: *4* Slides.make_widgets
        def make_widgets(self):

            w = self
            # Init the window's attributes.
            w.setStyleSheet(f"background: {self.background_color}")
            w.setGeometry(0, 0, self._width, self._height)  # The non-full-screen sizes.

            # Create the picture area.
            w.picture = QtWidgets.QLabel('picture', self)

            # Create the scroll area.
            w.scroll_area = area =QtWidgets.QScrollArea()
            area.setWidget(self.picture)
            AlignmentFlag = QtCore.Qt if isQt5 else QtCore.Qt.AlignmentFlag
            area.setAlignment(AlignmentFlag.AlignHCenter | AlignmentFlag.AlignVCenter)

            # Disable scrollbars.
            ScrollBarPolicy = QtCore.Qt if isQt5 else QtCore.Qt.ScrollBarPolicy
            area.setHorizontalScrollBarPolicy(ScrollBarPolicy.ScrollBarAlwaysOff)
            area.setVerticalScrollBarPolicy(ScrollBarPolicy.ScrollBarAlwaysOff)

            # Init the layout.
            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(self.scroll_area)
            w.setLayout(layout)
        #@+node:ekr.20211021200821.13: *3* Slides.show_help
        def show_help(self):
            """Show the help message."""
            print(textwrap.dedent('''\
                            d delete slide
                            f toggle full screen
                            h show help
                 n or <space> show next slide
             p or <backspace> show previous slide
                   q or <esc> end slideshow
                            + zoom in
                            - zoom out
                     up arrow scroll up
                   down arrow scroll down
                   left arrow scroll left
                  right arrow scroll right
            '''))
        #@+node:ekr.20211021200821.14: *3* Slides.show_slide
        def show_slide(self):
            # Reset the timer.
            self.timer.stop()
            self.timer.start(int(self.delay * 1000.0), self)
            # Get the file name.
            file_name = self.files_list[self.slide_number]
            # Change the title.
            self.setWindowTitle(file_name)
            # Display the picture.
            pixmap = QtGui.QPixmap(file_name)
            try:
                TransformationMode = QtCore.Qt if isQt5 else QtCore.Qt.TransformationMode
                image = pixmap.scaledToHeight(
                    int(self.height() * self.scale),
                    TransformationMode.SmoothTransformation,
                )
                self.picture.setPixmap(image)
                self.picture.adjustSize()
            except Exception:
                self.next_slide()
        #@+node:ekr.20211021200821.15: *3* Slides.sort
        def sort(self, sort_kind):
            """sort files_list based on sort_kind."""
            if sort_kind == 'date':
                if self.verbose:
                    print('Sorting by date...')
                self.files_list.sort(key = os.path.getmtime)
            elif sort_kind == 'name':
                if self.verbose:
                    print('Sorting by name...')
                self.files_list.sort()
            elif sort_kind in (None, 'none'):
                pass
            elif sort_kind == 'random':
                if self.verbose:
                    print('Randomizing...')
                random.shuffle(self.files_list)
            elif sort_kind == 'size':
                if self.verbose:
                    print('Sorting by size...')
                self.files_list.sort(key = os.path.getsize)
            else:
                g.trace(f"unknown sort kind: {sort_kind!r}")
        #@+node:ekr.20211021200821.16: *3* Slides.timerEvent
        def timerEvent(self, e=None):
            self.next_slide()  # show_slide resets the timer.
        #@+node:ekr.20211021200821.17: *3* Slides.toggle_full_screen
        def toggle_full_screen(self):
            w = self
            if w.full_screen:
                w.full_screen = False
                w.picture.adjustSize()
                w.showNormal()
            else:
                w.full_screen = True
                WindowState = QtCore.Qt if isQt5 else QtCore.Qt.WindowState
                w.setWindowState(WindowState.WindowFullScreen)
                w.picture.setGeometry(0, 0, w.width(), w.height())
                w.picture.adjustSize()
        #@+node:ekr.20211021200821.18: *3* Slides.zoom_in & zoom_out
        def zoom_in(self):
            self.scale = self.scale * 1.05
            self.show_slide()

        def zoom_out(self):
            self.scale = self.scale * (1.0 / 1.05)
            self.show_slide()
        #@-others
#@-others

if __name__ == '__main__':
    main()
#@-leo
