
#from setuptools import setup,find_packages


#if 'install' in sys.argv:
#    print "WARNING: 'setup.py install' is known to not work."
#    print "Either use 'setup.py develop', or run launchLeo.py directly"
#    sys.exit()

# TODO: sanitize this list, not all needs to be installed

from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES
import os
import sys

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
leo_dir = 'leo'

for dirpath, dirnames, filenames in os.walk(leo_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

# Small hack for working with bdist_wininst.
# See http://mail.python.org/pipermail/distutils-sig/2004-August/004134.html
if len(sys.argv) > 1 and sys.argv[1] == 'bdist_wininst':
    for file_info in data_files:
        file_info[0] = '\\PURELIB\\%s' % file_info[0]


#datapats = ['.tix', '.GIF', '.dbm', '.conf', '.TXT', '.xml', '.gif', '.leo', '.def', '.svg', '.ini', '.six', '.bat', '.cat', '.pro', '.sh', '.xsl', '.bmp', '.js', '.ui', '.rix', '.pmsp',  '.pyd', '.png', '.alg', '.php',  '.css', '.ico', '.txt', '.html',  '.iix',  '.w']
#print data_files

setup(
    name = 'leo-editor',
    version = "0.1",
    author = "Edward Ream",
    author_email = 'edreamleo@gmail.com',
    url = 'http://webpages.charter.net/edreamleo/front.html',
    packages = packages,
    data_files = data_files,
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
    scripts = ['launchLeo.py'],

    #entry_points = {
    #    'console_scripts': [
    #    ],
	
	#'gui_scripts' : [
	# 'leo = leo.core.runLeo:run'
	# ]
    #    }
    
)
