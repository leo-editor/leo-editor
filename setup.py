# -*- coding: utf-8 -*-
#@+leo-ver=5-thin
#@+node:maphew.20180224170853.1: * @file ../../setup.py
#@@first
'''setup.py for leo'''
#@+others
#@+node:maphew.20180305124637.1: ** imports
from codecs import open # To use a consistent encoding
import os
import platform
from shutil import rmtree
from setuptools import setup, find_packages # Always prefer setuptools over distutils
import leo.core.leoGlobals as g
import leo.core.leoVersion as leoVersion
#@+node:maphew.20141126230535.3: ** docstring
'''setup.py for leo

    Nov 2014: strip to bare minimum and rebuild using ONLY
    https://python-packaging-user-guide.readthedocs.org/en/latest/index.html
    
    Oct 2017: Excellent guide "﻿Less known packaging features and tricks"
    Ionel Cristian Mărieș, @ionelmc
    https://blog.ionelmc.ro/presentations/packaging/#slide:2
    https://blog.ionelmc.ro/2014/05/25/python-packaging/
'''

#@+node:maphew.20181010203342.385: ** get_version
def get_version(file, version=None):
    '''Determine current Leo version. Use git if in checkout, else internal Leo'''
    root = os.path.dirname(os.path.realpath(file))
    if os.path.exists(os.path.join(root,'.git')):
        version = git_version(file)
    if not version:
        version = get_semver(leoVersion.version)
    return version
#@+node:maphew.20181010203342.386: *3* git_version
def git_version(file):
    '''Fetch from Git: {tag} {distance-from-tag} {current commit hash}
       Return as semantic version string compliant with PEP440'''
    root = os.path.dirname(os.path.realpath(file))
    try:
        tag, distance, commit = g.gitDescribe(root)
            # 5.6b2, 55, e1129da
        ctag = clean_git_tag(tag)
        #version = get_semver(ctag)
        version = ctag
        if int(distance) > 0:
            version = '{}-dev{}'.format(version, distance)
    except IndexError:
        version = None
    return version

#@+node:maphew.20180224170257.1: *4* clean_git_tag
def clean_git_tag(tag):
    '''Return only version number from tag name. Ignore unkown formats.
       Is specific to tags in Leo's repository.
            5.7b1          -->	5.7b1
            Leo-4-4-8-b1   -->	4-4-8-b1
            v5.3           -->	5.3
            Fixed-bug-149  -->  Fixed-bug-149
    '''
    if tag.lower().startswith('leo-'): tag = tag[4:]
    if tag.lower().startswith('v'): tag = tag[1:]
    return tag
#@+node:maphew.20180224170149.1: *3* get_semver
def get_semver(tag):
    '''Return 'Semantic Version' from tag string'''
    try:
        import semantic_version
        version = str(semantic_version.Version.coerce(tag, partial=True))
            # tuple of major, minor, build, pre-release, patch
            # 5.6b2 --> 5.6-b2
    except ImportError or ValueError as err:
        print('\n', err)
        print('''*** Failed to parse Semantic Version from git tag '{0}'.
        Expecting tag name like '5.7b2', 'leo-4.9.12', 'v4.3' for releases.
        This version can't be uploaded to PyPi.org.'''.format(tag))
        version = tag
    return version
#@+node:maphew.20171006124415.1: ** Get description

with open('README.md') as f:
    long_description = f.read()

# Get the long description from the README file and convert to reST
# adapted from https://github.com/BonsaiAI/bonsai-config/blob/0.3.1/setup.py#L7
# bugfix #773 courtesy @Overdrivr, https://stackoverflow.com/a/35521100/14420
# try:
    # print('\n--- Getting long description ---')
    # from pypandoc import convert_file, convert_text
    # convert_text('#some title', 'rst', format='md') 
        # # fix #847, will raise OSError if pandoc binary not found
    # def read_md(f):
        # rst = convert_file(f, 'rst')
        # rst = rst.replace('\r', '') # fix #773
        # return rst
# except (ImportError, OSError) as err:
    # print('\n', err)
    # print('*** Warning: could not convert Readme.md to .rst (harmless for users)')
    # def read_md(f): return open(f, 'r').read()
        # # disable to obviously fail if markdown conversion fails

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
#@+node:maphew.20180415195922.1: ** Setup requirements
setup_requires = []
    # setup_requires no longer needed with PEP-518 and pip >v10
#@+node:maphew.20171120133429.1: ** User requirements
user_requires = [
    'PyQt5; python_version >= "3.0"',
    #'python-qt5; python_version < "3.0" and platform_system=="Windows"',
        # disabled, pending "pip install from .whl fails conditional dependency check" https://github.com/pypa/pip/issues/4886
    ## missing: pyqt for Linux python 2.x (doesn't exist on PyPi)
    'docutils', # used by Sphinx, rST plugin
    'nbformat', # for Jupyter notebook integration
    'pylint','pyflakes', # coding syntax standards
    #'pypandoc', # doc format conversion
    'sphinx', # rST plugin
    #'semantic_version', # Pip packaging    
    #'twine','wheel','keyring' # Pip packaging, uploading to PyPi
    #'pyenchant', # spell check support ## no wheels for some platforms, e.g. amd64
    #'pyxml', # xml importing ## no pip package
    ]
#@+node:maphew.20171122231442.1: ** clean
def clean():
    print('\nRemoving build, dist and egg directories')
    root = os.path.dirname(os.path.realpath(__file__))
    for d in ['build', 'dist', 'leo.egg-info', '.eggs']:
        dpath = os.path.join(root, d)
        if os.path.isdir(dpath):
            rmtree(dpath)
clean()
#@-others

def define_entry_points(entry_points=None):
    print('Creating entry_points for [OS name - system]: {} - {}'.format(platform.os.name, platform.system()))
    entry_points={
       'console_scripts': [
            'leo-c = leo.core.runLeo:run_console',
            'leo-console = leo.core.runLeo:run_console'],
        'gui_scripts': ['leo = leo.core.runLeo:run']
       }                
    if platform.system() == 'Windows':
        entry_points.update({
            'console_scripts': [
                'leo-m = leo.core.runLeo:run',
                'leo-messages = leo.core.runLeo:run']})
    return entry_points
        
setup(
    name='leo',
    # version = leo.core.leoVersion.version,
    version=get_version(__file__),
    author='Edward K. Ream',
    author_email='edreamleo@gmail.com',
    url='http://leoeditor.com',
    license='MIT License',
    description='An IDE, PIM and Outliner', # becomes 'Summary' in pkg-info
    #long_description=read_md('README.md'),
    long_description=long_description,
    long_description_content_type="text/markdown", # PEP566
    platforms=['Linux', 'Windows', 'MacOS'],
    download_url='http://leoeditor.com/download.html',
    classifiers=classifiers,
    packages=find_packages(),
    include_package_data=True, # also include MANIFEST files in wheels
    setup_requires=setup_requires,
    install_requires=user_requires,
    #scripts=['leo/dist/leo-install.py'],
        # no longer needed. `entry_points` is the preferred method now
        # delete the script too, after testing
    entry_points=define_entry_points()
)

#@@language python
#@@tabwidth -4
#@-leo
