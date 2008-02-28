title = 'Pmw.Group demonstration'

# Import Pmw from this directory tree.
import sys
sys.path[:0] = ['../../..']

import Tkinter
import Pmw

class Demo:
    def __init__(self, parent):

        # Create and pack the Groups.
	w = Pmw.Group(parent, tag_text='label')
	w.pack(fill = 'both', expand = 1, padx = 6, pady = 6)
	cw = Tkinter.Label(w.interior(),
		text = 'A group with the\ndefault Label tag')
	cw.pack(padx = 2, pady = 2, expand='yes', fill='both')

	w = Pmw.Group(parent, tag_pyclass = None)
	w.pack(fill = 'both', expand = 1, padx = 6, pady = 6)
	cw = Tkinter.Label(w.interior(), text = 'A group\nwithout a tag')
	cw.pack(padx = 2, pady = 2, expand='yes', fill='both')

	radiogroups = []
	self.var = Tkinter.IntVar()
	self.var.set(0)
	radioframe = Tkinter.Frame(parent)
	w = Pmw.Group(radioframe,
		tag_pyclass = Tkinter.Radiobutton,
		tag_text='radiobutton 1',
		tag_value = 0,
		tag_variable = self.var)
	w.pack(fill = 'both', expand = 1, side='left')
	cw = Tkinter.Frame(w.interior(),width=200,height=20)
	cw.pack(padx = 2, pady = 2, expand='yes', fill='both')
	radiogroups.append(w)

	w = Pmw.Group(radioframe,
		tag_pyclass = Tkinter.Radiobutton,
		tag_text='radiobutton 2',
		tag_font = Pmw.logicalfont('Helvetica', 4),
		tag_value = 1,
		tag_variable = self.var)
	w.pack(fill = 'both', expand = 1, side='left')
	cw = Tkinter.Frame(w.interior(),width=200,height=20)
	cw.pack(padx = 2, pady = 2, expand='yes', fill='both')
	radiogroups.append(w)
	radioframe.pack(padx = 6, pady = 6, expand='yes', fill='both')
	Pmw.aligngrouptags(radiogroups)

	w = Pmw.Group(parent,
		tag_pyclass = Tkinter.Checkbutton,
		tag_text='checkbutton',
		tag_foreground='blue')
	w.pack(fill = 'both', expand = 1, padx = 6, pady = 6)
	cw = Tkinter.Frame(w.interior(),width=150,height=20)
	cw.pack(padx = 2, pady = 2, expand='yes', fill='both')

	w = Pmw.Group(parent,
		tag_pyclass = Tkinter.Button,
		tag_text='Tkinter.Button')
        w.configure(tag_command = w.toggle)
	w.pack(fill = 'both', expand = 1, padx = 6, pady = 6)
	cw = Tkinter.Label(w.interior(),
		background = 'aliceblue',
		text = 'A group with\na Button tag!?'
	)
	cw.pack(padx = 2, pady = 2, expand='yes', fill='both')

	w = Pmw.Group(parent,
		tag_pyclass = Tkinter.Button,
		tag_text='Show/Hide')
        w.configure(tag_command = w.toggle)
	w.pack(fill = 'both', expand = 1, padx = 6, pady = 6)
	cw = Tkinter.Label(w.interior(),
		background = 'aliceblue',
		text = 'Now you see me.\nNow you don\'t.'
	)
	cw.pack(padx = 2, pady = 2, expand='yes', fill='both')

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
