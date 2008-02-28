title = 'Pmw.NoteBook demonstration (with no tabs)'

# Import Pmw from this directory tree.
import sys
sys.path[:0] = ['../../..']

import Tkinter
import Pmw

# Reuse the NoteBook with tabs demo.
import NoteBook_2

class Demo(NoteBook_2.Demo):
    def __init__(self, parent):
        NoteBook_2.Demo.__init__(self, parent, withTabs = 0)

# Create demo in root window for testing.
if __name__ == '__main__':
    root = Tkinter.Tk()
    Pmw.initialise(root)
    root.title(title)

    widget = Demo(root)
    exitButton = Tkinter.Button(root, text = 'Exit', command = root.destroy)
    exitButton.pack()
    root.mainloop()
