#@+leo-ver=5-thin
#@+node:ekr.20211021200745.1: * @file ../scripts/picture_viewer.py
#@+<< docstring (picture_viewer.py) >>
#@+node:ekr.20211021202710.1: ** << docstring (picture_viewer.py) >>
"""
Display image files in a directory tree as a slide show.

This script will display all files in a directory tree that have image
extensions. By default the recognized extensions are '.jpeg', '.jpg', and
'.png'. Other types of image files can be displayed as long as the they are
types known by the Qt PixMap class, including '.gif' and '.bmp'. See, for
example:

https://doc.qt.io/qt-5/qpixmap.html#reading-and-writing-image-files

This file may be run externally as follows::

    python -m leo.scripts.picture_viewer

This script may be called from another script (or @command or @button node) as follows:

    from leo.scripts.picture_viewer import Slides
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
import json
import os
import pathlib
import shutil
import sys
import random
import textwrap
# Leo imports: This is not a plugin.
try:
    import leo.core.leoGlobals as g
except Exception:
    print('picture_viewer.py: can not import leo.core.leoGlobals as g')
try:
    from leo.core.leoQt import QtCore, QtGui, QtWidgets
    from leo.core.leoQt import AlignmentFlag, ButtonRole, Information
except Exception:
    print('picture_viewer.py: Qt required')
    print('pip install pyqt6')
#@-<< imports (picture_viewer.py) >>

# Globals to retain references to objects.
gApp = None
gWidget = None

#@+others
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
    add('--use-db', dest='use_db', action='store_true',
        help='Save slide data in ~/.leo/picture_viewer.json')
    add('--verbose', dest='verbose', action='store_true',
        help='Enable status messages')
    add('--width', dest='width', metavar='PIXELS',
        help='Width of window')
    add('--wrap', dest='wrap_flag', action='store_true',
        help='Wrap around')

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
         'use_db': args.use_db,
         'verbose': args.verbose,
         'width': get_pixels('width', args.width),
         'wrap_flag': args.wrap_flag,
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
        sys.exit(gApp.exec())
#@+node:ekr.20211021202356.1: ** class Slides(QWidget)
class Slides(QtWidgets.QWidget):  # type:ignore

    # Command-line arguments...
    scale: float = 1.0
    starting_directory: str = None
    use_db: bool = False
    trace: bool = False
    verbose: bool = False
    wrap_flag: bool = True

    # Internal...
    db: dict[str, list] = None
    debug: bool = False
    dx: int = 0  # x-scroll value.
    dy: int = 0  # y-scroll value.
    files_list: list[str]
    slide_number = -1
    timer = QtCore.QBasicTimer()

    #@+others
    #@+node:ekr.20211021200821.14: *3* Slides.show_slide
    def show_slide(self):
        # Reset the timer.
        self.timer.stop()
        self.timer.start(int(self.delay * 1000.0), self)
        if not self.files_list:
            self.quit()
        # Get the file name.
        file_name = self.files_list[self.slide_number]
        # Change the window's title.
        self.setWindowTitle(file_name)
        # Set self.scale, self.dx and self.dy.
        if self.trace:
            print('')  # For trace in load_data.
        if self.reset_zoom:
            self.load_data()
        else:
            self.dx = self.dy = 0
            self.scale = 1.0
        try:
            # Try to return drawing to a pristine state.
            if 1:  # Clear the pixmap cache.
                QtGui.QPixmapCache.clear()
            if 0:  # Doesn't work.
                self.reset_scroll()
            # Create the pixmap.
            pixmap = QtGui.QPixmap(file_name)
            TransformationMode = QtCore.Qt.TransformationMode
            transform = TransformationMode.SmoothTransformation
            # Scale appropriately. Do *not* change this!
            image1 = pixmap.scaledToHeight(int(self.height() * self.scale), transform)
            image2 = pixmap.scaledToWidth(int(self.width() * self.scale), transform)
            image = image1 if image1.height() <= image2.height() else image2
            # Scroll the pixmap.
            self.do_scroll()
            # Insert the pixmap in the picture.
            self.picture.setPixmap(image)
            self.picture.adjustSize()
        except Exception:
            g.es_exception()
    #@+node:ekr.20230219044810.1: *3* Slides: commands
    #@+node:ekr.20230116092517.1: *4* Slides.copy
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
    #@+node:ekr.20211021200821.4: *4* Slides.delete
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
        result = dialog.exec()
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
    #@+node:ekr.20211021200821.7: *4* Slides.move_to
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
    #@+node:ekr.20211021200821.8: *4* Slides.next_slide
    def next_slide(self):
        # Save the previous data, if any.
        self.save_data()
        # Find the next slide or quit.
        if not self.files_list:
            print('No more slides')
            self.quit()
        elif self.slide_number + 1 < len(self.files_list):
            self.slide_number += 1  # No need to wrap.
        elif self.wrap_flag:
            self.slide_number = 0  # Wrap.
        else:
            return  # Don't quit in this direction.
        # Show the next slide.
        self.show_slide()
    #@+node:ekr.20211021200821.9: *4* Slides.prev_slide
    def prev_slide(self):
        # Save the previous data.
        self.save_data()
        # Find the previous slide or do nothing.
        if not self.files_list:
            self.quit()
        elif self.slide_number > 0:  # No need to wrap.
            self.slide_number -= 1
        elif self.wrap_flag:  # Wrap.
            self.slide_number = len(self.files_list) - 1
        else:
            return  # Don't quit in this direction.
        # Show the previous slide.
        self.show_slide()
    #@+node:ekr.20211029020533.1: *4* Slides.restart
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
        # print(f"Found {len(self.files_list)} files")
        self.slide_number = -1
        self.sort(self.sort_kind)
        self.next_slide()  # show_slide resets the timer.
    #@+node:ekr.20211021200821.13: *4* Slides.show_help
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
    #@+node:ekr.20211021200821.17: *4* Slides.toggle_full_screen
    def toggle_full_screen(self):
        w = self
        if w.full_screen:
            w.full_screen = False
            w.picture.adjustSize()
            w.showNormal()
        else:
            w.full_screen = True
            WindowState = QtCore.Qt.WindowState
            w.setWindowState(WindowState.WindowFullScreen)
            w.picture.setGeometry(0, 0, w.width(), w.height())
            w.picture.adjustSize()
    #@+node:ekr.20211021200821.18: *4* Slides.zoom_in & zoom_out
    def zoom_in(self):
        self.scale = self.scale * 1.05
        self.save_data()
        self.show_slide()

    def zoom_out(self):
        self.scale = self.scale * (1.0 / 1.05)
        self.save_data()
        self.show_slide()
    #@+node:ekr.20230220041302.1: *3* Slides: db
    #@+node:ekr.20230220063749.1: *4* Slides.init_db
    def init_db(self):

        if not self.use_db:
            self.db = {}
            return
        self.db_path = os.path.join(os.path.expanduser("~"), '.leo', 'picture_viewer.json')
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r') as f:
                    self.db = json.load(f)
                if self.verbose:
                    n = len(self.db.keys())
                    print(f"{n} entries in {self.db_path}")
            else:
                self.db = {}
        except Exception:
            g.es_exception()
    #@+node:ekr.20230220041332.1: *4* Slides.dump_data
    def dump_data(self):
        d = self.db
        # print(f"{self.db_path}...")
        for key in sorted(d.keys()):
            sfn = g.truncate(g.shortFileName(key), 20)
            print(f"{sfn:20} {d [key]}")
    #@+node:ekr.20230219054034.1: *4* Slides.load_data
    def load_data(self) -> None:

        file_name = self.files_list[self.slide_number]
        if file_name in self.db:
            try:
                self.scale, self.dx, self.dy = self.db[file_name]
                self.dx = int(self.dx)
                self.dy = int(self.dy)
            except TypeError:
                g.trace('TypeError', file_name)
                self.scale = self.db[file_name]  # type:ignore
                self.dx = self.dy = 0
        else:
            self.scale = 1.0
            self.dx = self.dy = 0
        if self.trace:  # Don't remove.
            print(
                f"load_data: {g.caller():<20} {self.slide_number} scale: {self.scale:9.8} x: "
                f"{self.dx} y: {self.dy}")
    #@+node:ekr.20230218180340.1: *4* Slides.save_data
    def save_data(self):

        if 0 <= self.slide_number < len(self.files_list):
            # Don't remove this trace.
            if self.trace and g.caller() != 'scrollContentsBy':
                print(
                    f"save_data: {g.caller():<20} {self.slide_number} scale: {self.scale:9.8} "
                    f"x: {self.dx} y: {self.dy}")
            file_name = self.files_list[self.slide_number]
            self.db[file_name] = [self.scale, int(self.dx), int(self.dy)]
    #@+node:ekr.20230219044202.1: *3* Slides: event handlers
    def closeEvent(self, event):
        """Override QWidget.closeEvent."""
        self.quit()

    # def moveEvent(self, event=None):
        # g.trace(event.oldPos())
        # super().moveEvent(event)

    def timerEvent(self, e=None):
        self.next_slide()  # show_slide resets the timer.
    #@+node:ekr.20211021200821.5: *4* Slides.keyPressEvent
    def keyPressEvent(self, event):

        s = event.text()
        if not s:
            return
        d = {
            '\x1b': self.quit,  # ESC.
            '\b': self.prev_slide,
            '\r': self.next_slide,
            '\n': self.next_slide,
            ' ': self.next_slide,
            '+': self.zoom_in,
            '-': self.zoom_out,
            '=': self.zoom_in,
            '_': self.zoom_out,
            'c': self.copy,
            'd': self.delete,
            'f': self.toggle_full_screen,
            'h': self.show_help,
            'm': self.move_to,
            'n': self.next_slide,
            'p': self.prev_slide,
            'q': self.quit,
            'r': self.restart,
        }
        f = d.get(s.lower())
        if f:
            f()
        # print(f"picture_viewer.py: ignoring key: {s!r} {event.key()}")
    #@+node:ekr.20230224054924.1: *3* Slides: scrolling
    #@+node:ekr.20230223054727.1: *4* Slides.do_scroll
    scroll_lockout = False

    def do_scroll(self):
        """Call  QScrollBar::setValue()."""
        w = self
        dx, dy = self.dx, self.dy
        area = w.scroll_area
        hbar, vbar = area.horizontalScrollBar(), area.verticalScrollBar()
        assert hbar.isEnabled()
        assert vbar.isEnabled()
        try:
            w.scroll_lockout = True  # Lock out scrollContentsBy.
            if 1:  # The scale won't make much difference.
                hbar.setValue(dx)
                vbar.setValue(-dy)  # tbpassin: use -dy
            else:
                hbar.setValue(int(self.scale * dx))
                vbar.setValue(-int(self.scale * dy))  # tbpassin: use -dy
        finally:
            w.scroll_lockout = False
    #@+node:ekr.20230224054937.1: *4* Slides.reset_scroll (not used)
    def reset_scroll(self):
        """Reset the scrollbars."""
        w = self
        try:
            w.scroll_lockout = True  # Lock out scrollContentsBy.
            w.scroll_area.horizontalScrollBar().setValue(0)
            w.scroll_area.verticalScrollBar().setValue(0)
        finally:
            w.scroll_lockout = False
    #@+node:ekr.20230219053658.1: *4* Slides.scrollContentsBy
    def scrollContentsBy(self, dx: int, dy: int):
        """
        Override QtWidgets.QScrollArea.scrollContentsBy.

        Called *after* the scrolling has already happened!

        Calling this function in order to scroll programmatically is an error.
        """
        if self.scroll_lockout:
            return
        try:
            # Prefer the trace in save_data.
            QtWidgets.QScrollArea.scrollContentsBy(self.scroll_area, dx, dy)
            self.dx += dx
            self.dy += dy
            self.save_data()
        except OverflowError:
            g.trace('scroll overflow', dx, dy)
    #@+node:ekr.20230219045030.1: *3* Slides: startup & shutdown
    #@+node:ekr.20211021200821.2: *4* Slides.get_files
    def get_files(self, path):
        """Return all files in path, including all subdirectories."""
        return [
            str(z) for z in pathlib.Path(path).rglob('*')
                if z.is_file()
                and os.path.splitext(str(z))[1].lower() in self.extensions
        ]
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
        w.scroll_area.scrollContentsBy = self.scrollContentsBy
        area.setWidget(self.picture)
        area.setAlignment(AlignmentFlag.AlignHCenter | AlignmentFlag.AlignVCenter)
        # Remember the viewport:
        w.view_port = area.viewport()

        # Disable scrollbars.
        ScrollBarPolicy = QtCore.Qt.ScrollBarPolicy
        area.setHorizontalScrollBarPolicy(ScrollBarPolicy.ScrollBarAlwaysOff)
        area.setVerticalScrollBarPolicy(ScrollBarPolicy.ScrollBarAlwaysOff)

        # Init the layout.
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.scroll_area)
        w.setLayout(layout)
    #@+node:ekr.20211021200821.10: *4* Slides.quit
    def quit(self):
        global gApp
        self.timer.stop()
        # Not necessary, but good for traces.
        self.save_data()
        # Update the db.
        if self.use_db:
            if self.debug:
                self.dump_data()
            with open(self.db_path, 'w') as f:
                json.dump(self.db, f, indent=2)
            if self.verbose:
                print(f"wrote {len(self.db.keys())} entries to {g.shortFileName(self.db_path)}")
        self.destroy()
        if gApp:  # Running externally.
            gApp.exit()
            gApp = None
        if self.verbose:
            print('picture_viewer: done')
    #@+node:ekr.20211021200821.11: *4* Slides.run
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
        use_db=False,  # True: Save picture_viewer.json.
        verbose=False,  # True, print info messages.
        width=None,  # Window width (default 1500 pixels) when not in full screen mode.
        wrap_flag=False,  # Wrap around.
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
        self.use_db = use_db
        self.verbose = verbose
        self.wrap_flag = wrap_flag
        # Init the db.
        self.init_db()
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
    #@+node:ekr.20211021200821.15: *4* Slides.sort
    def sort(self, sort_kind):
        """sort files_list based on sort_kind."""
        if sort_kind == 'date':
            self.files_list.sort(key=os.path.getmtime)
        elif sort_kind == 'name':
            self.files_list.sort()
        elif sort_kind in (None, 'none'):
            pass
        elif sort_kind == 'random':
            random.shuffle(self.files_list)
        elif sort_kind == 'size':
            self.files_list.sort(key=os.path.getsize)
        else:
            g.trace(f"unknown sort kind: {sort_kind!r}")
    #@-others
#@-others

if __name__ == '__main__':
    main()
#@-leo
