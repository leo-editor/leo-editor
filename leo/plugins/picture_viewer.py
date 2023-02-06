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

This file may be run externally as follows::

    python -m leo.plugins.picture_viewer

This plugin may be called from a script (or @command or @button node) as follows:

    from leo.plugins.picture_viewer import Slides
    Slides().run()  # See below for defaults.

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
          r: restart: choose another folder

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
#@+<< imports (picture_viewer.py) >>
#@+node:ekr.20211021202633.1: ** << imports (picture_viewer.py) >>
import argparse
import os
import pathlib
import shutil
import sys
import random
import textwrap
from typing import List
# Leo imports
from leo.core import leoGlobals as g
try:
    from leo.core.leoQt import isQt5, isQt6, QtCore, QtGui, QtWidgets
    from leo.core.leoQt import ButtonRole, Information
except ImportError:
    QtWidgets = None
#@-<< imports (picture_viewer.py) >>

# Globals to retain references to objects.
gApp = None
gWidget = None

#@+others
#@+node:ekr.20211021202802.1: ** init (picture_viewer.py)
def init():
    """Return True if the plugin has loaded successfully."""
    return g.app.gui.guiName().lower().startswith('qt')
#@+node:tom.20211023221408.1: ** get_args & checkers
def get_args():

    # Automatically implements the --help option.
    description = "usage: python -m picture_viewer [options]"
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter)

    # Add args.
    add = parser.add_argument
    add('--background', dest='background', metavar='COLOR',
        help='Background color')
    add('--delay', dest='delay', metavar='DELAY',
        help='Delay (seconds)')
    add('--extensions', dest='extensions', nargs='*', metavar='TYPES',
        help='List of image file extensions.')
        # Default: .jpeg,.jpg,.png  (no spaces allowed)
    add('--full-screen', dest='fullscreen', action='store_true',
        help='Start in full-screen mode')
    add('--height', dest='height', metavar='PIXELS',
        help='Height of window')
    add('--path', dest='path', metavar='DIRECTORY',
        help='Path to root directory')
    add('--reset-zoom', dest='reset_zoom', action='store_false',
        help='Reset zoom factor when changing slides')
    add('--scale', dest='scale', metavar='FLOAT',
        help='Initial scale (zoom) factor')
    add('--sort-kind', dest='sort_kind', metavar="KIND",
        help='Sort kind: (date, name, none, random, or size)')
    add('--starting-directory', dest='starting_directory', metavar='DIRECTORY',
        help='Starting directory for file dialogs')
    add('--verbose', dest='verbose', action='store_true',
        help='Enable status messages')
    add('--width', dest='width', metavar='PIXELS',
        help='Width of window')

    # Parse the options, and remove them from sys.argv.
    args = parser.parse_args()

    # Check and return the args.
    return {
         'background_color': args.background or "black",
         'delay': get_delay(args.delay),
         'extensions': get_extensions(args.extensions),
         'full_screen': args.fullscreen,
         'height': get_pixels('height', args.height),
         'path': get_path(args.path),
         'reset_zoom': args.reset_zoom,
         'scale': get_scale(args.scale),
         'sort_kind': get_sort_kind(args.sort_kind),
         'starting_directory': get_path(args.starting_directory),
         'verbose': args.verbose,
         'width': get_pixels('width', args.width)
    }
#@+node:ekr.20211101064157.1: *3* get_delay
def get_delay(delay):
    if delay is None:
        return None
    try:
        return float(delay)
    except ValueError:
        print(f"Bad delay value: {delay!r}")
        return None
#@+node:ekr.20211024034921.1: *3* get_extensions
def get_extensions(aList):

    # Ensure extensions start with '.'
    return [
        z if z.startswith('.') else f".{z}"
            for z in aList or []
    ]
#@+node:ekr.20211024041658.1: *3* get_path
def get_path(path):

    if path and not os.path.exists(path):
        print(f"--path: not found: {path!r}")
        path = None
    return path
#@+node:ekr.20211024035501.1: *3* get_pixels
def get_pixels(kind, pixels):

    if pixels is None:
        return None
    try:
        return int(pixels)
    except ValueError:
        print(f"Bad --{kind} value: {pixels!r}")
        return None
#@+node:ekr.20211024041359.1: *3* get_scale
def get_scale(scale):

    try:
        return float(scale or 1.0)
    except ValueError:
        print(f"Bad --scale: {scale!r}")
        return 1.0
#@+node:ekr.20211024040842.1: *3* get_sort_kind
def get_sort_kind(kind):

    if not kind:
        return None
    kind = kind.lower()
    if kind not in ('date', 'name', 'none', 'random', 'size'):
        print(f"bad --sort-kind: {kind!r}")
        kind = 'none'
    return kind
#@+node:ekr.20211023201914.1: ** main
def main():
    global gApp
    gApp = QtWidgets.QApplication(sys.argv)
    args = get_args()

    ok = Slides().run(**args)
    if ok:
        if isQt5:
            sys.exit(gApp.exec_())
        else:
            sys.exit(gApp.exec())
#@+node:ekr.20211021202356.1: ** class Slides
if QtWidgets:

    class Slides(QtWidgets.QWidget):  # type:ignore

        files_list: List[str]
        scale: float = 1.0
        slide_number = -1
        starting_directory: str = None
        timer = QtCore.QBasicTimer()
        verbose: bool = False

        #@+others
        #@+node:ekr.20211024030844.1: *3* Slides.closeEvent
        def closeEvent(self, event):
            """Override QWidget.closeEvent."""
            self.quit()
        #@+node:ekr.20230116092517.1: *3* Slides.copy
        def copy(self):
            """Issue a prompt and copy the file if the user agrees."""
            file_name = self.files_list[self.slide_number]
            path: str = QtWidgets.QFileDialog().getExistingDirectory()
            if not path:
                print('No path')
                return
            new_path = os.path.join(path, os.path.basename(file_name))
            if os.path.exists(new_path):
                print("File exists:", new_path)
            else:
                shutil.copy(file_name, new_path)
                print('Copied to', new_path)
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
            # Create the dialog without relying on g.app.gui.
            dialog = QtWidgets.QMessageBox(self)
            dialog.setStyleSheet("background: white;")
            yes = dialog.addButton('Yes', ButtonRole.YesRole)
            dialog.addButton('No', ButtonRole.NoRole)
            dialog.setWindowTitle("Delete File?")
            dialog.setText(f"Delete file {g.shortFileName(file_name)}?")
            dialog.setIcon(Information.Warning)
            dialog.setDefaultButton(yes)

            def dialog_keypress_event(event):
                s = event.text()
                if s == 'y':
                    dialog.done(0)
                elif s == 'n' or s == '\x1b':  # ESC.
                    dialog.done(1)

            dialog.keyPressEvent = dialog_keypress_event
            dialog.raise_()
            result = dialog.exec() if isQt6 else dialog.exec_()
            if result == 0:
                # Move the file to the trash.
                send2trash(file_name)
                del self.files_list[self.slide_number]
                print(f"Deleted {file_name}")
                if self.files_list:
                    self.slide_number = max(0, self.slide_number - 1)
                    self.next_slide()
                    self.raise_()
                else:
                    print('No more slides')
                    self.quit()
        #@+node:ekr.20211021200821.2: *3* Slides.get_files
        def get_files(self, path):
            """Return all files in path, including all subdirectories."""
            return [
                str(z) for z in pathlib.Path(path).rglob('*')
                    if z.is_file()
                    and os.path.splitext(str(z))[1].lower() in self.extensions
            ]
        #@+node:ekr.20211021200821.5: *3* Slides.keyPressEvent
        def keyPressEvent(self, event):

            i = event.key()
            s = event.text()
            mods = event.modifiers()
            if mods and 'ShiftModifier' not in repr(mods):
                print(f"picture_viewer.py: ignoring modified key: {s!r} {i}")
                return
            if s == 'c':
                self.copy()
            elif s == 'd':
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
            elif s == 'r':
                self.restart()
            elif s in '=+':
                self.zoom_in()
            elif s in '-_':
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
                print(f"picture_viewer.py: ignoring key: {s!r} {i}")

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
            path: str = QtWidgets.QFileDialog().getExistingDirectory()
            if not path:
                return
            new_path = os.path.join(path, os.path.basename(file_name))
            if os.path.exists(new_path):
                print("File exists:", new_path)
                pathlib.Path(file_name).unlink(new_path)  # type:ignore
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
            else:
                print('No more slides')
                self.quit()
            if self.reset_zoom:
                self.scale = 1.0
            self.show_slide()
        #@+node:ekr.20211021200821.9: *3* Slides.prev_slide
        def prev_slide(self):

            if self.slide_number > 0:  # Don't wrap.
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
            if self.verbose:
                print('picture_viewer: done')
        #@+node:ekr.20211029020533.1: *3* Slides.restart
        def restart(self):
            dialog = QtWidgets.QFileDialog(directory=self.starting_directory)
            path = dialog.getExistingDirectory()
            if not path:
                if self.verbose:
                    print("No path given")
                self.quit()
                return
            self.starting_directory = path
            os.chdir(path)
            self.files_list = self.get_files(path)
            print(f"Found {len(self.files_list)} files")
            self.slide_number = -1
            self.sort(self.sort_kind)
            self.next_slide()  # show_slide resets the timer.
        #@+node:ekr.20211021200821.11: *3* Slides.run & helper
        def run(self,
            background_color=None,  # Default background color.
            delay=None,  # Delay between slides, in seconds. Default 100.
            extensions=None,  # List of file extensions.
            full_screen=False,  # True: start in full-screen mode.
            height=None,  # Window height (default 1500 pixels) when not in full screen mode.
            path=None,  # Root directory.
            scale=None,  # Initial scale factor. Default 1.0
            reset_zoom=True,  # True: reset zoom factor when changing slides.
            sort_kind=None,  # 'date', 'name', 'none', 'random', or 'size'.  Default is 'random'.
            starting_directory=None,  # Starting directory for file dialogs.
            verbose=False,  # True, print info messages.
            width=None,  # Window width (default 1500 pixels) when not in full screen mode.
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
            self.background_color = background_color or "black"
            self.delay = delay or 100
            self.extensions = extensions or ['.jpeg', '.jpg', '.png']
            self.full_screen = False
            self.reset_zoom = reset_zoom
            self.scale = scale or 1.0
            self.sort_kind = sort_kind or 'random'
            self.starting_directory = starting_directory or os.getcwd()
            self.verbose = verbose
            # Careful: width and height are QWidget methods.
            self._height = height or 900
            self._width = width or 1500
            # Compute the files list.
            if not path:
                dialog = QtWidgets.QFileDialog(directory=self.starting_directory)
                path = dialog.getExistingDirectory()
            if not path:
                if self.verbose:
                    print("No path given")
                return False
            self.files_list = self.get_files(path)
            if not self.files_list:
                print(f"No slides found in {path!r}")
                return False
            print(f"Found {len(self.files_list)} files")
            self.starting_directory = path
            os.chdir(path)
            n = len(self.files_list)
            if self.verbose:
                print(f"Found {n} picture{g.plural(n)} in {path}")
            # Init the widget.
            w.make_widgets()
            # Center the widget
            qtRectangle = w.frameGeometry()
            centerPoint = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
            qtRectangle.moveCenter(centerPoint)
            w.move(qtRectangle.topLeft())
            # Show the widget.
            w.showNormal()
            if full_screen:  # Not self.full_screen.
                w.toggle_full_screen()
            # Show the next slide.
            self.sort(sort_kind)
            self.next_slide()  # show_slide resets the timer.
            return True
        #@+node:ekr.20211021200821.12: *4* Slides.make_widgets
        def make_widgets(self):

            w = self

            # Init the window's attributes.
            w.setStyleSheet(f"background: {self.background_color}")
            w.setGeometry(0, 0, self._width, self._height)  # The non-full-screen sizes.

            # Create the picture area.
            w.picture = QtWidgets.QLabel('picture', self)
            w.picture.keyPressEvent = w.keyPressEvent

            # Create the scroll area.
            w.scroll_area = area = QtWidgets.QScrollArea()
            area.setWidget(self.picture)
            AlignmentFlag = QtCore.Qt if isQt5 else QtCore.Qt.AlignmentFlag
            area.setAlignment(AlignmentFlag.AlignHCenter | AlignmentFlag.AlignVCenter)  # pylint: disable=no-member

            # Disable scrollbars.
            ScrollBarPolicy = QtCore.Qt if isQt5 else QtCore.Qt.ScrollBarPolicy
            area.setHorizontalScrollBarPolicy(ScrollBarPolicy.ScrollBarAlwaysOff)  # pylint: disable=no-member
            area.setVerticalScrollBarPolicy(ScrollBarPolicy.ScrollBarAlwaysOff)  # pylint: disable=no-member

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
                    n show next slide
                    p show previous slide
                    q end slideshow
                    r restart slideshow in new folder
                    + zoom in
                    - zoom out
                <esc> end slidshow
              <space> show next slide
          <backspace> show previous slide
           arrow keys scroll picture
        '''))
        #@+node:ekr.20211021200821.14: *3* Slides.show_slide
        def show_slide(self):
            # Reset the timer.
            self.timer.stop()
            self.timer.start(int(self.delay * 1000.0), self)
            if not self.files_list:
                self.quit()
            # Get the file name.
            file_name = self.files_list[self.slide_number]
            if self.verbose:
                print(file_name)
            # Change the title.
            self.setWindowTitle(file_name)
            # Display the picture.
            pixmap = QtGui.QPixmap(file_name)
            try:
                TransformationMode = QtCore.Qt if isQt5 else QtCore.Qt.TransformationMode
                transform = TransformationMode.SmoothTransformation  # pylint: disable=no-member
                if 1:  # Take the smaller immage.
                    image1 = pixmap.scaledToHeight(int(self.height() * self.scale), transform)
                    image2 = pixmap.scaledToWidth(int(self.width() * self.scale), transform)
                    image = image1 if image1.height() <= image2.height() else image2
                else:  # Legacy
                    image = pixmap.scaledToHeight(int(self.height() * self.scale), transform)
                self.picture.setPixmap(image)
                self.picture.adjustSize()
            except Exception:
                g.es_exception()
        #@+node:ekr.20211021200821.15: *3* Slides.sort
        def sort(self, sort_kind):
            """sort files_list based on sort_kind."""
            if sort_kind == 'date':
                if self.verbose:
                    print('Sorting by date...')
                self.files_list.sort(key=os.path.getmtime)
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
                self.files_list.sort(key=os.path.getsize)
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
                w.setWindowState(WindowState.WindowFullScreen)  # pylint: disable=no-member
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
