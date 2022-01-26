#@+leo-ver=5-thin
#@+node:ekr.20220126054240.1: * @file ../plugins/remove_duplicate_pictures.py
#@+<< docstring (remove_duplicate_pictures.py) >>
#@+node:ekr.20220126054240.2: ** << docstring (remove_duplicate_pictures.py) >>
"""
Remove duplicate 

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
#@-<< docstring (remove_duplicate_pictures.py) >>
#@+<< imports (remove_duplicate_pictures.py) >>
#@+node:ekr.20220126054240.3: ** << imports (remove_duplicate_pictures.py) >>
import argparse
from collections import defaultdict
import os
import pathlib
import sys
import time
# Third party
try:
    from PIL import Image
except Exception:
    print('remove_duplicate_pictures: PIL required')
    print('pip install pillow')
    Image = None
try:
    import imagehash
except Exception:
    imagehash = None
    print('remove_duplicate_pictures: imagehash required')
    print('pip install imagehash')
try:
    import numpy as np
except Exception:
    np = None
    print('remove_duplicate_pictures: numpy required')
    print('pip install numpy')
# Leo
import leo.core.leoGlobals as g
from leo.core.leoQt import isQt5, QtCore, QtGui, QtWidgets
#@-<< imports (remove_duplicate_pictures.py) >>
assert defaultdict and pathlib and time ###
assert QtCore and QtGui

# Globals to retain references to objects.
gApp = None
gWidget = None

#@+others
#@+node:ekr.20220126054240.4: ** init (remove_duplicate_pictures.py)
def init():
    """Return True if the plugin has loaded successfully."""
    return Image and imagehash and np and g.app.gui.guiName().lower().startswith('qt')
#@+node:ekr.20220126054240.5: ** get_args & checkers
def get_args():

    # Automatically implements the --help option.
    description = "usage: python -m remove_duplicate_pictures [options]"
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter)

    # Add args.
    add = parser.add_argument
    add('--background', dest='background', metavar='COLOR', 
        help='Background color')
    # add('--delay', dest='delay', metavar='DELAY',
        # help='Delay (seconds)')
    add('--extensions', dest='extensions', nargs='*', metavar='TYPES',
        help='List of image file extensions.')
        # Default: .jpeg,.jpg,.png  (no spaces allowed)
    add('--full-screen', dest='fullscreen', action='store_true',
        help='Start in full-screen mode')
    add('--height', dest='height', metavar='PIXELS',
        help='Height of window')
    add('--path', dest='path', metavar='DIRECTORY',
        help='Path to root directory')
    # add('--reset-zoom', dest='reset_zoom', action='store_false',
        # help='Reset zoom factor when changing slides')
    # add('--scale', dest='scale', metavar='FLOAT',
        # help='Initial scale (zoom) factor')
    # add('--sort-kind', dest='sort_kind', metavar="KIND",
        # help='Sort kind: (date, name, none, random, or size)')
    # add('--starting-directory', dest='starting_directory', metavar='DIRECTORY',
        # help='Starting directory for file dialogs')
    add('--verbose', dest='verbose', action='store_true',
        help='Enable status messages')
    add('--width', dest='width', metavar='PIXELS',
        help='Width of window')

    # Parse the options, and remove them from sys.argv.
    args = parser.parse_args()

    # Check and return the args.
    return {
         'background_color': args.background or "black",
         # 'delay': get_delay(args.delay),
         'extensions': get_extensions(args.extensions),
         'full_screen': args.fullscreen,
         'height': get_pixels('height', args.height),
         'path': get_path(args.path),
         # 'reset_zoom': args.reset_zoom,
         # 'scale': get_scale(args.scale),
         # 'sort_kind': get_sort_kind(args.sort_kind),
         # 'starting_directory': get_path(args.starting_directory),
         'verbose': args.verbose,
         'width': get_pixels('width', args.width)
    }
#@+node:ekr.20220126054240.7: *3* get_extensions
def get_extensions(aList):
    
    # Ensure extensions start with '.'
    return [
        z if z.startswith('.') else f".{z}"
            for z in aList or []
    ]
#@+node:ekr.20220126054240.8: *3* get_path
def get_path(path):
    
    if path and not os.path.exists(path):
        print(f"--path: not found: {path!r}")
        path = None
    return path
#@+node:ekr.20220126054240.9: *3* get_pixels
def get_pixels(kind, pixels):
    
    if pixels is None:
        return None
    try:
        return int(pixels)
    except ValueError:
        print(f"Bad --{kind} value: {pixels!r}")
        return None
#@+node:ekr.20220126054240.12: ** main
def main():
    global gApp
    gApp = QtWidgets.QApplication(sys.argv)
    args = get_args()
   
    ok = RemoveDuplicates().run(c = None, **args)
    if ok:
        if isQt5:
            sys.exit(gApp.exec_())
        else:
            sys.exit(gApp.exec())
#@+node:ekr.20220126054240.13: ** class RemoveDuplicates
class RemoveDuplicates:
            
    #@+others
    #@+node:ekr.20220126060911.1: *3* Dups.get_files
    def get_files(self, path):
        """Return all files in path, including all subdirectories."""
        return [
            str(z) for z in pathlib.Path(path).rglob('*')
                if z.is_file()
                and os.path.splitext(str(z))[1].lower() in self.extensions
        ]
    #@+node:ekr.20220126060646.1: *3* Dups.run & helper
    def run(self,
        c,  # Required. The commander for this slideshow.
        background_color = None,  # Default background color.
        ### delay = None,  # Delay between slides, in seconds. Default 100.
        extensions = None,  # List of file extensions.
        full_screen = False,  # True: start in full-screen mode.
        height = None,  # Window height (default 1500 pixels) when not in full screen mode.
        path = None,  # Root directory.
        ### scale = None,  # Initial scale factor. Default 1.0
        ### reset_zoom = True,  # True: reset zoom factor when changing slides.
        ### sort_kind = None,  # 'date', 'name', 'none', 'random', or 'size'.  Default is 'random'.
        starting_directory = None,  # Starting directory for file dialogs.
        verbose = False,  # True, print info messages.
        width = None,  # Window width (default 1500 pixels) when not in full screen mode.
    ):
        """
        Create the widgets and run the slideshow.
        Return True if any pictures were found.
        """
        # Keep a reference to this class!
        global gWidget
        gWidget = self
        # Init ivars.
        ### w = self
        self.c = c
        self.background_color = background_color or "black"
        ### self.delay = delay or 100
        self.extensions = extensions or ['.jpeg', '.jpg', '.png']
        self.full_screen = False
        ### self.reset_zoom = reset_zoom
        ### self.scale = scale or 1.0
        ### self.sort_kind = sort_kind or 'random'
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
        ###
            # # Init the widget.
            # w.make_widgets()
            # # Center the widget
            # qtRectangle = w.frameGeometry()
            # centerPoint = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
            # qtRectangle.moveCenter(centerPoint)
            # w.move(qtRectangle.topLeft())
            # # Show the widget.
            # w.showNormal()
            # if full_screen:  # Not self.full_screen.
                # w.toggle_full_screen()
            # # Show the next slide.
            # self.sort(sort_kind)
            # self.next_slide()  # show_slide resets the timer.
        return True
    #@+node:ekr.20220126060646.2: *4* Slides.make_widgets
    def make_widgets(self):

        w = self

        # Init the window's attributes.
        w.setStyleSheet(f"background: {self.background_color}")
        w.setGeometry(0, 0, self._width, self._height)  # The non-full-screen sizes.
        
        # Create the picture area.
        w.picture = QtWidgets.QLabel('picture', self)
        w.picture.keyPressEvent = w.keyPressEvent

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
    #@-others
#@-others

if __name__ == '__main__':
    main()
#@-leo
