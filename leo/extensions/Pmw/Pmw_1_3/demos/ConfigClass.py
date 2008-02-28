title = 'Component python class configuration demonstration'

# Import Pmw from this directory tree.
import sys
sys.path[:0] = ['../../..']

import Tkinter
import Pmw

class MyButton(Tkinter.Button):
    # This is just an ordinary button with special colors.

    def __init__(self, master=None, cnf={}, **kw):
	self.__toggle = 0
	kw['background'] = 'green'
	kw['activebackground'] = 'red'
	apply(Tkinter.Button.__init__, (self, master, cnf), kw)

class Demo:
    def __init__(self, parent):

	# Create a title label:
	label = Tkinter.Label(parent,
		text = 'EntryFields with label components of specified type:')
	label.pack(fill='x', expand=1, padx=10, pady=5)

	# Create and pack some EntryFields.
	entries = []
	entry = Pmw.EntryField(parent,
		labelpos = 'w',
		label_text = 'Label'
	)
	entry.pack(fill='x', expand=1, padx=10, pady=5)
	entries.append(entry)

	entry = Pmw.EntryField(parent,
		labelpos = 'w',
		label_pyclass = Tkinter.Button,
		label_text = 'Button'
	)
	entry.pack(fill='x', expand=1, padx=10, pady=5)
	entries.append(entry)

	entry = Pmw.EntryField(parent,
		labelpos = 'w',
		label_pyclass = MyButton,
		label_text = 'Special button'
	)
	entry.pack(fill='x', expand=1, padx=10, pady=5)
	entries.append(entry)

	Pmw.alignlabels(entries)

	# Create and pack a ButtonBox.
	buttonBox = Pmw.ButtonBox(parent,
		labelpos = 'nw',
		label_text = 'ButtonBox:')
	buttonBox.pack(fill = 'both', expand = 1, padx=10, pady=5)

	# Add some buttons to the ButtonBox.
	buttonBox.add('with a')
	buttonBox.add('special', pyclass = MyButton)
	buttonBox.add('button')

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
