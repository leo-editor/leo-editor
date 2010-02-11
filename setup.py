
# Must be an @nosent file.

print '=' * 30

from distutils.core import setup

long_description = \
"""Leo is an IDE, an outliner, a scripting and unit testing framework based on Python,
a literate programming tool, a data organizer and a project manager.

Leo is written in 100% pure Python and works on any platform that supports
Python 2.2.1 or above and the Tk Tk 8.4 or above.

Download Python from http://python.org/
Download tcl/Tk from http://tcl.activestate.com/software/tcltk/
"""
version='4.4.8-b2' # No spaces and no trailing comma.

setup (
    name='leo',
    version=version, # No spaces and no trailing comma.
    author='Edward K. Ream',
    author_email='edreamleo@gmail.com',
    url='http://webpages.charter.net/edreamleo/front.html',
    download_url='http://sourceforge.net/project/showfiles.php?group_id=3458',
    py_modules=[], # The manifest specifies everything.
    description = "Leo: A Programmer's Editor and More",
    license='Python',
    platforms=['all',],
    long_description = long_description,
)

print ; print 'setup.py done'
