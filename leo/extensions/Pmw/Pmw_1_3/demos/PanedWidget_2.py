title = 'Pmw.PanedWidget demonstration (pane factory)'

# Import Pmw from this directory tree.
import sys
sys.path[:0] = ['../../..']

import Tkinter
import Pmw

class Demo:
    def __init__(self, parent):
	self.paneCount = 0

	# Create a "pane factory".
	label = Tkinter.Label(parent,
		pady = 10,
		text = 'Below is a simple "pane factory".\n' +
			'Drag the handle on the left\nto create new panes.')
	label.pack()
	self.factory = Pmw.PanedWidget(parent,
		orient='horizontal',
		command = self.resize,
		hull_borderwidth = 1,
		hull_relief = 'raised',
		hull_width=300, hull_height=200
                )
	self.factory.add('starter', size = 0.0)
	self.factory.add('main')
	button = Tkinter.Button(self.factory.pane('main'),
		text = 'Pane\n0')
	button.pack(expand = 1)
	self.factory.pack(expand = 1, fill = 'both')

    def resize(self, list):
	# Remove any panes less than 2 pixel wide.
	for i in range(len(list) - 1, 0, -1):
	    if list[i] < 2:
		self.factory.delete(i)

	# If the user has dragged the left hand handle, create a new pane.
	if list[0] > 1:
	    self.paneCount = self.paneCount + 1

	    # Add a button to the new pane.
	    name = self.factory.panes()[0]
	    text = 'Pane\n' + str(self.paneCount)
	    button = Tkinter.Button(self.factory.pane(name), text = text)
	    button.pack(expand = 1)

	    # Create a new starter pane.
	    name = 'Pane ' + str(self.paneCount)
	    self.factory.insert(name, size=0.0)

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
