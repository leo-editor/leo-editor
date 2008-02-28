
# Must be an @nosent file.

# print '='*30,'setup.py','='*30

from distutils.core import setup

import leoGlobals as g
long_description = \
"""Leo is an IDE, an outliner, a scripting and unit testing framework based on Python,
a literate programming tool, a data organizer and a project manager.

Leo is written in 100% pure Python and works on any platform that supports
Python 2.2.1 or above and the Tk Tk 8.4 or above.

Download Python from http://python.org/
Download tcl/Tk from http://tcl.activestate.com/software/tcltk/
"""

# long_description = g.adjustTripleString(long_description,c.tab_width)

# print repr(long_description)
version='4.4.7-final' # No spaces and no trailing comma.

if 1:
    setup (
        name='leo',
        version=version,
        author='Edward K. Ream',
        author_email='edreamleo@charter.net',
        url='http://webpages.charter.net/edreamleo/front.html',
        download_url='http://sourceforge.net/project/showfiles.php?group_id=3458',
        py_modules=[], # The manifest specifies everything.
        description = 'Leo: Literate Editor with Outlines',
        license='Python', # licence [sic] changed to license in Python 2.3
        platforms=['all',],
        long_description = long_description,
        # keywords = 'outline, outliner, ide, editor, literate programming',
    )

print ; print 'setup.py done'
