title = 'Blt busy cursor demonstration'

# Import Pmw from this directory tree.
import sys
sys.path[:0] = ['../../..']

import Tkinter
import Pmw

class Demo:
    def __init__(self, parent):
	self.parent = parent

	if Pmw.Blt.havebltbusy(parent):
	    text = 'Click here to show the\nbusy cursor for one second.'
	else:
	    text = 'Sorry\n' \
		'Either the BLT package has not\n' \
		'been installed on this system or\n' \
		'it does not support the busy command.\n' \
		'Clicking on this button will pause\n' \
		'for one second but will not display\n' \
		'the busy cursor.'

	button = Tkinter.Button(parent,
	        text = text,
		command = Pmw.busycallback(self.sleep, parent.update))
	button.pack(padx = 10, pady = 10)

	entry = Tkinter.Entry(parent, width = 30)
	entry.insert('end', 'Try to enter some text while busy.')
	entry.pack(padx = 10, pady = 10)

    def sleep(self):
        self.parent.after(1000)

######################################################################

# Create demo in root window for testing.
if __name__ == '__main__':
    root = Tkinter.Tk()
    Pmw.initialise(root)
    root.title(title)

    exitButton = Tkinter.Button(root, text = 'Exit', command = root.destroy)
    exitButton.pack(side = 'bottom')
    widget = Demo(root)
    root.mainloop()
