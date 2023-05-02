#@+leo-ver=5-thin
#@+node:ekr.20220126054240.1: * @file ../scripts/remove_duplicate_pictures.py
#@+<< docstring (remove_duplicate_pictures.py) >>
#@+node:ekr.20220126054240.2: ** << docstring (remove_duplicate_pictures.py) >>
"""
Remove duplicate files.

This script will display all duplicate files in a tree that have image
extensions. By default the recognized extensions are '.jpeg', '.jpg', and
'.png'. Other types of image files can be displayed as long as the they are
types known by the Qt PixMap class, including '.gif' and '.bmp'.

This script may be run externally as follows::

    python -m leo.script.remove_duplicate_pictures

This script may be called from another script (or @command or @button node) as follows::

    from leo.scripts.remove_duplicate_pictures import RemoveDuplicates
    RemoveDuplicates().run()  # See below for defaults.

**Defaults**

The following keyword arguments may be supplied to the run method:

    extensions = ['.jpeg', '.jpg', '.png'],  # List of file extensions.
    hash_size = 8  # Size of reduced image.
    height = 900,  # Window height in pixels.
    path = None,  # Path to the folder.
    starting_directoy = None  # Starting directory for file dialog if no path given.

**Required packages**

This plugin requires the following third-party packages::

    imagehash:  pip install imagehash
    numpy:      pip install numpy
    PIL:        pip install pillow
    send2trash: pip install send2trash

**Acknowledgment**

The algorithm used is a faster version of the code here:
https://medium.com/@somilshah112/how-to-find-duplicate-or-similar-images-quickly-with-python-2d636af9452f
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
from typing import Any, Dict, List
# Third party
try:
    from PIL import Image
except Exception:
    print('remove_duplicate_pictures.py: PIL required')
    print('pip install pillow')
    Image = None
try:
    import imagehash
except Exception:
    imagehash = None
    print('remove_duplicate_pictures.py: imagehash required')
    print('pip install imagehash')
try:
    import numpy as np
except Exception:
    np = None
    print('remove_duplicate_pictures.py: numpy required')
    print('pip install numpy')
try:
    from send2trash import send2trash
except Exception:
    send2trash = None  # Optional
# Leo: This is not a plugin.
try:
    import leo.core.leoGlobals as g
except Exception:
    print('remove_duplicate_picture.py: can not import leo.core.leoGlobals as g')
try:
    from leo.core.leoQt import isQt5, QtCore, QtGui, QtWidgets
except Exception:
    print('remove_duplicate_pictures.py: Qt required')
    print('pip install pyqt6')
#@-<< imports (remove_duplicate_pictures.py) >>

# Globals to retain references to objects.
gApp = None
gWindow = None

#@+others
#@+node:ekr.20220126054240.5: ** get_args & checkers
def get_args():
    # Automatically implements the --help option.
    description = "usage: python -m remove_duplicate_pictures [options]"
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter)
    # Add args.
    add = parser.add_argument
    add('--extensions', dest='extensions', nargs='*', metavar='TYPES',
        help='List of image file extensions')
        # Default: .jpeg,.jpg,.png  (no spaces allowed)
    add('--hash-size', dest='hash_size', metavar='INT',
        help='hash_size, default 8')
    add('--height', dest='height', metavar='PIXELS',
        help='Height of window')
    add('--path', dest='path', metavar='DIR',
        help='Path to root directory')
    add('--starting-dir', dest='starting_dir', metavar='DIR',
        help='Starting directory of dialog if no path given')
    # Parse the options, and remove them from sys.argv.
    args = parser.parse_args()
    # Check and return the args.
    return {
         'extensions': get_extensions(args.extensions),
         'hash_size': get_int('hash_size', args.hash_size),
         'height': get_int('height', args.height),
         'path': get_path(args.path),
         'starting_directory': get_path(args.starting_dir)
    }
#@+node:ekr.20220126054240.7: *3* get_extensions
def get_extensions(aList):

    # Ensure extensions start with '.'
    return [
        z if z.startswith('.') else f".{z}"
            for z in aList or []
    ]
#@+node:ekr.20220126054240.9: *3* get_int
def get_int(kind, n):

    if n is None:
        return None
    try:
        return int(n)
    except ValueError:
        print(f"Bad --{kind} value: {n!r}")
        return None
#@+node:ekr.20220126054240.8: *3* get_path
def get_path(path):

    if path and not os.path.exists(path):
        print(f"--path: not found: {path!r}")
        path = None
    return path
#@+node:ekr.20220126054240.12: ** main
def main():
    global gApp
    gApp = QtWidgets.QApplication(sys.argv)
    args = get_args()
    ok = RemoveDuplicates().run(**args)
    if ok:
        if isQt5:
            sys.exit(gApp.exec_())
        else:
            sys.exit(gApp.exec())
#@+node:ekr.20220126054240.13: ** class RemoveDuplicates
class RemoveDuplicates:

    dup_list: List[str] = []
    filename_dict: Dict[str, Any] = {}  # Keys are filenames, values are hashes.
    hash_dict: Dict[Any, List[Any]] = defaultdict(list)  # Keys are hashes, values are lists of filenames.
    hash_size = 8
    window_height = 900

    #@+others
    #@+node:ekr.20220126063935.1: *3* Dups.compute_dicts
    def compute_dicts(self, filenames):
        for i, filename in enumerate(filenames):
            try:
                h = imagehash.average_hash(Image.open(filename), self.hash_size)
                self.filename_dict[filename] = h.hash
                self.hash_dict[str(h)].append(filename)
            except Exception:
                print('Bad img:', filename)
                # g.es_exception()
                if filename in filenames:
                    filenames.remove(filename)
    #@+node:ekr.20220126064207.1: *3* Dups.create_frame
    def create_frame(self, filename, filenames, window):

        QLabel = QtWidgets.QLabel
        # Create the frame.
        frame = QtWidgets.QFrame(parent=window)
        # Create the vertical layout.
        layout = QtWidgets.QVBoxLayout()
        frame.setLayout(layout)
        # Set the font.
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(12)
        # Create the labels..
        ctime = time.ctime(os.path.getctime(filename))
        struct_time = time.strptime(ctime)
        creation_time = time.strftime('%Y %m %d', struct_time)
        file_label = QLabel(text=filename, parent=frame)
        file_label.setFont(font)
        layout.addWidget(file_label)
        size = os.path.getsize(filename) / 1000
        info_label = QLabel(text=f"size: {size} KB date: {creation_time}")
        info_label.setFont(font)
        layout.addWidget(info_label)
        # Create the delete button, centered.
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        delete_button = QtWidgets.QPushButton(text='Delete', parent=frame)
        button_layout.addWidget(delete_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        # Set the button action.

        def delete_action(arg):
            self.delete_file(filename)

        delete_button.clicked.connect(delete_action)
        # Create the picture area.
        picture = QtWidgets.QLabel('picture', parent=frame)
        layout.addWidget(picture)
        # Display the picture.
        pixmap = QtGui.QPixmap(filename)
        try:
            TransformationMode = QtCore.Qt if isQt5 else QtCore.Qt.TransformationMode
            image = pixmap.scaledToHeight(self.window_height, TransformationMode.SmoothTransformation)  # pylint: disable=no-member
            picture.setPixmap(image)
            picture.adjustSize()
            return frame
        except Exception:
            g.trace('Bad image')
            g.es_exception()
            return None
    #@+node:ekr.20220126062304.1: *3* Dups.create_window
    def create_window(self, filenames):
        # Create the widget.
        global gWindow
        gWindow = window = QtWidgets.QWidget()
        window.setWindowTitle(f"{len(filenames)} duplicates of {filenames[0]}")
        window.setMinimumHeight(self.window_height)
        # Move the window.
        window.move(50, 50)
        # Init the layouts.
        outer_layout = QtWidgets.QVBoxLayout()
        window.setLayout(outer_layout)
        button_layout = QtWidgets.QHBoxLayout()
        frame_layout = QtWidgets.QHBoxLayout()
        outer_layout.addLayout(button_layout)
        outer_layout.addLayout(frame_layout)
        # Set the font.
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(12)
        # Create the common buttons, left aligned.
        next_button = QtWidgets.QPushButton(text='Next', parent=window)
        quit_button = QtWidgets.QPushButton(text='Quit', parent=window)
        next_button.setFont(font)
        quit_button.setFont(font)
        button_layout.addWidget(next_button)
        button_layout.addWidget(quit_button)
        button_layout.addStretch()
        # Create the actions.
        next_button.clicked.connect(window.close)
        quit_button.clicked.connect(self.quit)
        # Create the subframes and add them to the frame_layout.
        for filename in filenames:
            frame = self.create_frame(filename, filenames[:], window)
            if frame:
                frame_layout.addWidget(frame)
        # Handle close events.
        def closeEvent(*args, **kwargs):
            window.close()
            self.next_window()

        window.closeEvent = closeEvent
        # Show the window.
        window.show()
    #@+node:ekr.20220126064335.1: *3* Dups.delete_file
    send_to_trash_warning_given = False

    def delete_file(self, filename):
        """Issue a prompt and delete the file if the user agrees."""
        global gWindow
        if not send2trash:
            if not self.send_to_trash_warning_given:
                self.send_to_trash_warning_given = True
                print("Deleting files requires send2trash")
                print("pip install Send2Trash")
                return
        if os.path.exists(filename):
            send2trash(filename)
            print('Deleted', filename)
            if filename in self.dup_list:
                self.dup_list.remove(filename)
            if len(self.dup_list) < 2:
                gWindow.close()
        else:
            print('Not found', filename)
    #@+node:ekr.20220126064032.1: *3* Dups.find_duplicates
    def find_duplicates(self):
        """Find duplicates."""
        duplicates = []
        for h in self.hash_dict:
            aList = self.hash_dict.get(h)
            if len(aList) > 1:
                duplicates.append(aList)
        return duplicates

    #@+node:ekr.20220126060911.1: *3* Dups.get_files
    def get_files(self, path):
        """Return all files in path, including all subdirectories."""
        return [
            str(z) for z in pathlib.Path(path).rglob('*')
                if z.is_file()
                and os.path.splitext(str(z))[1].lower() in self.extensions
        ]
    #@+node:ekr.20220126121116.1: *3* Dups.next_window
    def next_window(self):
        """Show the next set of duplicates in a new window."""
        if self.duplicates:
            self.dup_list = self.duplicates.pop()
            self.create_window(self.dup_list)
        else:
            self.quit()
    #@+node:ekr.20220126120555.1: *3* Dups.quit
    def quit(self):
        global gApp, gWindow
        if gApp:  # Running externally.
            gApp.exit()
            gApp = None
        elif gWindow:
            gWindow.destroy()
            gWindow = None
        print('picture_viewer: done')
    #@+node:ekr.20220126060646.1: *3* Dups.run
    def run(self,
        extensions=None,  # List of file extensions.
        hash_size=8,  # Size of compressed image.
        height=None,  # Window height (default 1500 pixels) when not in full screen mode.
        path=None,  # Root directory.
        starting_directory=None,  # Starting directory for file dialog if no path given.
    ):
        """
        Preprecess the files and show the first duplicates.
        Return True if any duplicates were found.
        """
        # Init ivars.
        self.extensions = extensions or ['.jpeg', '.jpg', '.png']
        self.hash_size = hash_size or 8
        self.starting_directory = starting_directory or os.getcwd()
        self.window_height = height or 900
        # Get the directory.
        if not path:
            dialog = QtWidgets.QFileDialog(directory=self.starting_directory)
            path = dialog.getExistingDirectory()
        if not path:
            print("No path given")
            return False
        # Get the files.
        filenames = self.get_files(path)
        if not filenames:
            print(f"No pictures found in {path!r}")
            return False
        print(f"{len(filenames)} file{g.plural(len(filenames))} in {path}")
        print(f"\nPreprocessing with hash size {self.hash_size}. This may take awhile...")
        # Compute the hash dicts.
        self.compute_dicts(filenames)
        # Find the duplicates.
        self.duplicates = self.find_duplicates()
        g.es_print(f"{len(self.duplicates)} duplicate sets")
        ok = bool(self.duplicates)  # Do this before calling next_window.
        if self.duplicates:
            self.next_window()
        return ok
    #@-others
#@-others

if __name__ == '__main__':
    main()
#@-leo
