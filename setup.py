# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:maphew.20141126130213.2: * @file setup.py
#@@first
'''setup.py for leo'''
simple = False # True: avoid all complications.
trace = False
from setuptools import setup, find_packages # Always prefer setuptools over distutils
from codecs import open # To use a consistent encoding
import leo.core.leoVersion # FIXME: extract from GIT tags instead, ionelmc slide:19
#@+others
#@+node:maphew.20141126230535.3: ** docstring
'''setup.py for leo

    Nov 2014: strip to bare minimum and rebuild using ONLY
    https://python-packaging-user-guide.readthedocs.org/en/latest/index.html
        
    Oct 2017: Excellent guide "﻿Less known packaging features and tricks"
    Ionel Cristian Mărieș, @ionelmc
    https://blog.ionelmc.ro/presentations/packaging/#slide:2
    https://blog.ionelmc.ro/2014/05/25/python-packaging/
'''
#@+node:maphew.20171006124415.1: ** Get description
# Get the long description from the README file
# And also convert to reST
# adapted from https://github.com/BonsaiAI/bonsai-config/blob/0.3.1/setup.py#L7
try:
    from pypandoc import convert
    def read_md(f): return convert(f, 'rst')

except ImportError:
    print("warning: pypandoc module not found, "
          "could not convert Markdown to RST")

#def read_md(f): return open(f, 'r').read()

    
#@+node:maphew.20141126230535.4: ** classifiers
classifiers = [
    'Development Status :: 6 - Mature',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: MacOS',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python',
    'Topic :: Software Development',
    'Topic :: Text Editors',
    'Topic :: Text Processing',
    ]
#@-others

scm_version_options = {
    'write_to_template': '{}+dYYYMMMDD',
    #'write_to_template': 'some random text',
    'write_to' : 'leo/version.py' # feasible for core/leoVersion to use this?
    }

setup(
    name = 'leo',
    #version = leo.core.leoVersion.version,
    # https://github.com/pypa/setuptools_scm
    use_scm_version = scm_version_options,
    setup_requires=['setuptools_scm'],
    version = leo.core.leoVersion.version,
    author = "Edward K. Ream",
    author_email = 'edreamleo@gmail.com',
    url = 'http://leoeditor.com',
    license = 'MIT License',
    description = "An IDE, PIM and Outliner", # becomes "Summary" in pkg-info
    long_description = read_md('README.md'),
    platforms = ['Linux','Windows','MacOS'],
    download_url = 'http://leoeditor.com/download.html',
    classifiers = classifiers,
    packages = find_packages(),
    include_package_data=True, # also include MANIFEST files in wheels
    entry_points = {
       'console_scripts': ['leoc = leo.core.runLeo:run'],
       'gui_scripts' : ['leo = leo.core.runLeo:run']
       }
)

#@@language python
#@@tabwidth -4
#@-leo
