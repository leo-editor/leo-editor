
from setuptools import setup,find_packages

setup(
    name = 'leo-editor',
    version = "0.1",
    author = "Edward Ream",
    author_email = 'edreamleo@gmail.com',
    url = 'http://webpages.charter.net/edreamleo/front.html',
    packages =find_packages(),
    description = "A programmer's editor, and much more",
    long_description = """
Leo is an outline-oriented editor written in 100% pure Python.
Leo works on any platform that supports Python 2.2.1 and Tk 8.4 or above.
You may download Python from http://python.org/ and
tcl/Tk from http://tcl.activestate.com/software/tcltk/
Leo features a multi-window outlining editor, Python colorizing,
powerful outline commands and many other things, including 
Unlimited Undo/Redo and an integrated Python shell(IDLE) window.
Leo will place its own icon in Leo windows provided that you have
installed Fredrik Lundh's PIL and tkIcon packages:
Download PIL from http://www.pythonware.com/downloads/index.htm#pil
Download tkIcon from http://www.effbot.org/downloads/#tkIcon
    """,

    entry_points = {
        'console_scripts': [
        ],
	
	'gui_scripts' : [
	 'leo = leo.core.runLeo:run'
	 ]
        }
    
)
