#@+leo-ver=5-thin
#@+node:maphew.20131101000129.2139: * @file setup.py
#@@language python
#@@tabwidth -4
#@+others
#@+node:ville.20090213231648.2: ** setup declarations
#if 'install' in sys.argv:
#    print "WARNING: 'setup.py install' is known to not work."
#    print "Either use 'setup.py develop', or run launchLeo.py directly"
#    sys.exit()

# TODO: sanitize this list, not all needs to be installed

# from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES
import os,fnmatch
from setuptools import setup, find_packages

#@+node:maphew.20130503222911.1635: ** Get description
try:
    long_description = open('README.TXT', 'rt').read()
except IOError:
    long_description = """
Leo is an outline-oriented IDE written in 100% pure Python.
Leo features a multi-window outlining editor, Python colorizing,
powerful outline commands and many other things, including 
unlimited Undo/Redo and an integrated Python shell(IDLE) window.
Leo requires Python 2.6 or above.  Leo works with Python 3.x.
Requires PyQt and SIP preinstalled.
    """
#@+node:maphew.20130508020338.1645: ** Get version
import leo.core.leoVersion
# for development snapshots
#version = '{0}-build-{1}'.format(leo.core.leoVersion.version, leo.core.leoVersion.build)

# for stable builds / full release
version = leo.core.leoVersion.version
version = '4.11-final'
#@+node:ville.20090213231648.3: ** fullsplit
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

#@+node:ville.20090213231648.4: ** purelib hack
# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in list(INSTALL_SCHEMES.values()):
    scheme['data'] = scheme['purelib']
#@+node:ville.20090213233714.2: *3* @url http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
#@+node:ville.20090213231648.5: ** collect (and filter) files
# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
leo_dir = 'leo'

# stuff that breaks package (or is redundant)
scrub_datafiles = ['leo/extensions', '_build', 'leo/test', 'leo/plugins/test', 'leo/doc/html', '__pycache__']

for dirpath, dirnames, filenames in os.walk(leo_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    # if '__init__.py' in filenames:
        # fsplit = fullsplit(dirpath)
        # packages.append('.'.join(fsplit))
    if filenames:
        if not any(pat in dirpath for pat in scrub_datafiles):
            data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

packages = find_packages()

if '--debug' in sys.argv[1:]:
    import pprint
    print("data files")
    pprint.pprint(data_files)
    print("packages (pre-cleanup)")
    pprint.pprint(packages)
    
#cleanup unwanted packages

# extensions should be provided through repos (packaging)
packages = [pa for pa in packages if not pa.startswith('leo.extensions')]

if '--debug' in sys.argv[1:]:
    print("packages (post-cleanup)")
    pprint.pprint(packages)
    
#cleanup unwanted data files
#@+node:ville.20090213231648.6: ** bdist_wininst hack
# Small hack for working with bdist_wininst.
# See http://mail.python.org/pipermail/distutils-sig/2004-August/004134.html
if len(sys.argv) > 1 and sys.argv[1] == 'bdist_wininst':
    for file_info in data_files:
        file_info[0] = '\\PURELIB\\%s' % file_info[0]
#@-others

# Note than only *.ui matches now - add asterisks as needed/valid
datapats = ['.tix', '.GIF', '.dbm', '.conf', '.TXT', '.xml', '.gif', '*.leo', '.def', '.svg', '*.ini', '.six', '.bat', '.cat', '.pro', '.sh', '.xsl', '.bmp', '.js', '*.ui', '.rix', '.pmsp',  '.pyd', '.png', '.alg', '.php',  '.css', '.ico', '*.txt', '.html',  '.iix',  '.w']
#print data_files

# variable order matches order on pkg info page, but that's just a niceity
# https://testpypi.python.org/pypi?name=leo-editor&version=4.10-final&:action=submit_form
setup(
    name = 'leo',
    version = version,
    author = "Edward K. Ream",
    author_email = 'edreamleo@gmail.com',
# don't use maintainer, else it overwrites author in PKG-INFO
# c.f. note 3 @url http://docs.python.org/3/distutils/setupscript.html#additional-meta-data
#    maintainer = 'Matt Wilkie',
#    maintainer_email = 'maphew@gmail.com',
    url = 'http://leoeditor.com',
    license = 'MIT License',
    description = "Leonine Editor with Outlines",
    long_description = long_description,
    #keywords = [],
    platforms = ['linux','windows'],
    download_url = 'http://sourceforge.net/projects/leo/files/Leo/',
    #bugtrack_url = 'https://bugs.launchpad.net/leo-editor',    #only py3?

    # only include dependencies which can be installed by pip (so not PyQt or SIP)
    requires = ['docutils'],

    #provides = [],
    #obsoletes= [],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Text Editors',
        'Topic :: Text Processing',
        ],

    packages = packages,
    data_files = data_files,
    #package_data = {'leo.plugins' : datapats },
    package_data = {'' : datapats }, #no need to restrict to just plugins(?)
    scripts = ['leo-install.py'],

    entry_points = {
        'console_scripts': [
        'leoc = leo.core.runLeo:run'
        ],
        'gui_scripts' : [
        'leo = leo.core.runLeo:run'
        ]
       }
)
#@-leo
