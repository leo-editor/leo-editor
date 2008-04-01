
# Must be an @nosent file.

from distutils.core import setup
from pdb import set_trace as pdb # pdb() will drop into the debugger.

pdb()

long_description = \
"""Leo is an IDE, an outliner, a scripting and unit testing framework based on Python,
a literate programming tool, a data organizer and a project manager.

Leo is written in 100% pure Python and works on any platform that supports
Python 2.2.1 or above and the Tk Tk 8.4 or above.

Download Python from http://python.org/
Download tcl/Tk from http://tcl.activestate.com/software/tcltk/
"""

setup (
    name='leo',
    version='4.4.8-beta-3-test', # No spaces and no trailing comma., # No spaces and no trailing comma.
    author='Edward K. Ream',
    author_email='edreamleo@gmail.com',
    url='http://webpages.charter.net/edreamleo/front.html',
    download_url='http://sourceforge.net/project/showfiles.php?group_id=3458',
    packages=['leo'], # The manifest specifies everything.
    description = "Leo: A Programmer's Editor and More",
    license='Python',
    platforms=['all',],
    long_description = long_description,
)

print ; print 'setup.py done'
