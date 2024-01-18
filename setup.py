#@+leo-ver=5-thin
#@+node:maphew.20180224170853.1: * @file ../../setup.py
"""
setup.py for leo.

Run with `python -m build` from the leo-editor directory.
"""
#@+<< imports >>
#@+node:maphew.20180305124637.1: ** << imports >>
import platform
import re
import sys
import traceback
# Third-part tools.
import setuptools  # Prefer setuptools over distutils.
#@-<< imports >>
#@+<< define classifiers >>
#@+node:maphew.20141126230535.4: ** << define classifiers >>
classifiers = [
    'Development Status :: 6 - Mature',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: MacOS',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Software Development',
    'Topic :: Text Editors',
    'Topic :: Text Processing',
]
#@-<< define classifiers >>
#@+<< define install_requires >>
#@+node:maphew.20171120133429.1: ** << define install_requires >>
install_requires = [
    
    'PyQt5 >= 5.15',  # #2884: require v5.15. #1217: require v5.12+.
    'PyQtWebEngine',
    'build >= 0.6.0',  # simple PEP 517 package builder
    'docutils',  # used by Sphinx, rST plugin
    'flexx',  # for LeoWapp browser gui
    'meta',  # for livecode.py plugin, which is enabled by default
    'nbformat',  # for Jupyter notebook integration
    'pylint', 'pyflakes',
    'pyenchant',  # The spell tab.
    'pyshortcuts >= 1.7',  # desktop integration (#1243)
    'sphinx',  # rST plugin
    'tk',  # tkinter.

    # For leoAst.py and leoTokens.py.
    'asttokens',  # abstract syntax tree text parsing
    'black',  # coding syntax standards

    # #3603: windows-curses doesn't work with Python 3.12.
    # This issue has now been fixed.
    'windows-curses; platform_system=="Windows"',  # for console mode on Windows
]
#@-<< define install_requires >>
#@+others  # Define helpers
#@+node:maphew.20190207205714.1: ** define_entry_points
def define_entry_points(entry_points=None):
    """
    Return a dict defining scripts that get installed to PYTHONHOME/Scripts.
    """
    entry_points = {
        'console_scripts': [
            'leo-c = leo.core.runLeo:run_console',
            'leo-console = leo.core.runLeo:run_console',
        ],
        'gui_scripts': ['leo = leo.core.runLeo:run'],
    }
    # Add leo-messages wrapper for windows platform
    if platform.system() == 'Windows':
        x = entry_points['console_scripts']
        x.append('leo-m = leo.core.runLeo:run')
        x.append('leo-messages = leo.core.runLeo:run')
        entry_points.update({'console_scripts': x})
    return entry_points
#@+node:ekr.20210813135632.1: ** dump_entry_points
def dump_entry_points():
    """Dump the entry_points list."""
    global entry_points
    print(f"setup.py: entry_points. OS = {platform.os.name}, system = {platform.system()}")
    for key in entry_points:
        aList = entry_points.get(key)
        list_s = '\n    '.join(aList)
        print(f"  {key}: [\n    {list_s}\n  ]")
#@+node:ekr.20210813100609.1: ** get_readme_contents
def get_readme_contents():
    """Return the contents of README.md."""
    with open('README.md') as f:
        return f.read()
#@+node:ekr.20210814041052.1: ** is_valid_version
pattern = re.compile(r'[0-9]+\.[0-9]+(\.[0-9]+)?((b|rc)[0-9]+)?')

def is_valid_version(version):
    """"
    Return True if version has the form '5.7b2', 'v4.3', etc.

    See PEP 440: https://www.python.org/dev/peps/pep-0440/

    For Leo, valid versions shall have the form: `N1.N2(.N3)?(bN|rcN)?`
    where N is any integer.

    In particular, neither alternative spellings nor alpha releases are valid.
    """
    m = pattern.match(version)
    return bool(m and len(m.group(0)) == len(version))
#@+node:ekr.20210813103317.1: ** print_exception
def print_exception():
    """Like g.es_exception."""
    typ, val, tb = sys.exc_info()
    # val is the second argument to the raise statement.
    lines = traceback.format_exception(typ, val, tb)
    for line in lines:
        print(line)
#@+node:ekr.20210814043248.1: ** test is_valid_version
def test_is_valid_version():
    """
    A unit test for is_valid_version.

    However, `python -m setup` won't work :-)
    """
    table = (
        '1.2', '3.4.5', '6.7b1', '8.9rc3',  # good.
        'v1.2', '3.4a1', '5.6-b1',  # bad
    )
    for s in table:
        ok = is_valid_version(s)
        print(f"{ok!s:5} {s}")
#@-others
production = True
testing = False
# Dashes are not allowed.
version = '6.7.7'  ##version Should match version in leoVersion.py
entry_points = define_entry_points()
long_description = get_readme_contents()
assert is_valid_version(version), version
if testing:
    dump_entry_points()
    test_is_valid_version()
if production:
    setuptools.setup(
        name='leo',  # Add username?.
        version=version,
        author='Edward K. Ream',
        author_email='edreamleo@gmail.com',
        url='https://leo-editor.github.io/leo-editor',
        license='MIT License',
        description='An IDE, PIM and Outliner',  # becomes 'Summary' in pkg-info
        long_description=long_description,
        long_description_content_type="text/markdown",  # PEP566
        platforms=['Linux', 'Windows', 'MacOS'],
        download_url='https://leo-editor.github.io/leo-editor/download.html',
        classifiers=classifiers,
        packages=setuptools.find_packages(),
        include_package_data=True,  # also include MANIFEST files in wheels
        setup_requires=[],  # No longer needed with PEP-518 and pip >v10.
        install_requires=install_requires,
        entry_points=entry_points,
        python_requires='>=3.9',
    )
print('setup.py: done')
#@@language python
#@@tabwidth -4
#@-leo
