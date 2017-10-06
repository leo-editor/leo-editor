#@+leo-ver=5-thin
#@+node:maphew.20141126130213.2: * @file setup.py
'''setup.py for leo'''
simple = False # True: avoid all complications.
trace = False
from setuptools import setup, find_packages # Always prefer setuptools over distutils
from codecs import open # To use a consistent encoding
import leo.core.leoVersion
#@+node:maphew.20141126230535.3: ** docstring
'''setup.py for leo

    Nov 2014: strip to bare minimum and rebuild using ONLY
    https://python-packaging-user-guide.readthedocs.org/en/latest/index.html
    
    See if we can get all the way to end (painless `python setup.py install` and
    `pip install .` on all platforms) without having to leave standard library
    or leverage hacks.
'''
#@+node:maphew.20141126230535.4: ** classifiers
classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Win32 (MS Windows)',
    'Environment :: X11 Applications :: Qt',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: MacOS',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development',
    'Topic :: Text Editors',
    'Topic :: Text Processing',
    ]
#@-others

setup(
    name = 'leo',
    version = leo.core.leoVersion.version,
    author = "Edward K. Ream",
    author_email = 'edreamleo@gmail.com',
    url = 'http://leoeditor.com',
    license = 'MIT License',
    description = "Leo: Leonine Editor with Outlines", # becomes "Summary" in pkg-info
    platforms = ['Linux','Windows','MacOS'],
    download_url = 'http://sourceforge.net/projects/leo/files/Leo/',
    classifiers = classifiers,
    packages = find_packages(),
    #packages = ['', 'core'], 
    #package_dir = {'': 'leo'},
    entry_points = {
       'console_scripts': ['leoc = leo.core.runLeo:run'],
        # 'gui_scripts' : ['leow = leo.core.runLeo.run']
       }
)

#@@language python
#@@tabwidth -4
#@-leo
