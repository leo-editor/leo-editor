# -*- mode: python -*-
'''
launchLeo-folder.spec: a spec file for pyinstaller that creates a folder-based install of Leo.
Run with pyinstaller launchLeo-folder.spec, **not** with launchLeo.py.
'''

block_cipher = None

import glob, os, sys

# Same code as in runLeo.py.
path = os.getcwd()
if path not in sys.path:
    print('launchLeo.spec: appending %s to sys.path' % path)
    sys.path.append(path)

import leo.core.leoGlobals as g
import leo.core.leoApp as leoApp

LM = leoApp.LoadManager()
loadDir = LM.computeLoadDir()

def get_modules(name):
    '''return a list of module names in the leo/name directory.'''
    # abs_dir = os.path.abspath(os.path.join(r'C:\leo.repo\leo-editor\leo', name))
    abs_dir = g.os_path_finalize_join(loadDir, '..', name)
    n = len(abs_dir) + 1
    aList = glob.glob(abs_dir + '/*.py')
    return ['leo.%s.%s' % (name, z[n:][: -3]) for z in aList]

hiddenimports = []
for name in ('external', 'modes', 'plugins'):
    hiddenimports.extend(get_modules(name))

# Utilities for creating entries in the "datas" lists...
def all(name):
    '''Return a tuple that causes all files in name to be included.'''
    return ('%s/*.*' % (name), name)

icons = all

def ext(kind, name):
    '''Return a tuple that causes all files with the given extension in name to be included.'''
    if kind.startswith('.'):
        kind = kind[1:]
    return ('%s/*.%s' % (name, kind), name)

datas = [
    # Required for startup...
        ('leo/core/commit_timestamp.json', 'leo/core'),
        ext('.ui', 'leo/plugins'),
    # Required for plugins...
        # Data requifed for startup.
            all('leo/plugins/GraphCanvas'),
        # These are also hidden imports...
            ext('.py', 'leo/plugins'),
            ext('.py', 'leo/plugins/importers'),
            ext('.py', 'leo/plugins/writers'),
    # leo/config...
        ext('.leo', 'leo/config'),
    # leo/modes...
        ext('.py', 'leo/modes'),
        ext('.xml', 'leo/modes'),
    # All icons...
        icons('leo/Icons'),
        icons('leo/Icons/cleo'),
        icons('leo/Icons/cleo/small'),
        icons('leo/Icons/file_icons'),
        icons('leo/Icons/nodes-dark/plusminus'),
        icons('leo/Icons/nodes-dark/triangles'),
        icons('leo/Icons/recorder'),
        icons('leo/themes/generic/Icons'),
        icons('leo/themes/leo_dark_0/Icons'),
        icons('leo/themes/leo_dark_0/Icons/cleo'),
        icons('leo/themes/leo_dark_0/Icons/cleo/small'),
        icons('leo/themes/leo_dark_0/Icons/file_icons'),
        icons('leo/themes/leo_dark_0/Icons/Tango/16x16/apps'),
    # Additional Leo data fles...
    # leo-editor: loaded by LeoPy.leo...
        ('launchLeo-folder.spec', ''),
        ('launchLeo-single.spec', ''),
        ('leo_to_html.xsl', ''),
        ('pylint-leo.py', ''),
        ('setup.py', ''),
        # leo.commands...
            ext('.py', 'leo/commands'),
        # leo.core...
            # Only include reference files.
                # ext('.leo', 'leo/core'),
                ('leo/core/LeoPyRef.leo', 'leo/core'),
            ext('.py', 'leo/core'),
            ext('.txt', 'leo/core'),
        # leo.dist...
            all('leo/dist'),
        # leo/doc & leo/doc/html
            ext('.css', 'leo/doc'),
            ext('.js', 'leo/doc'),
            ext('.html', 'leo/doc'),
            ext('.leo', 'leo/doc'),
        ext('.py', 'leo/doc'),
            ext('.txt', 'leo/doc'),
        all('leo/doc/html'),
        # ext('.jif','leo/doc/html'),
        # ext('.py','leo/doc/html'),
        # ext('.txt','leo/doc/html'),
        # User-selectable icons.
            icons('leo/Icons/Tango/16x16/actions'),
            icons('leo/Icons/Tango/16x16/animations'),
            icons('leo/Icons/Tango/16x16/apps'),
            icons('leo/Icons/Tango/16x16/categories'),
            icons('leo/Icons/Tango/16x16/devices'),
            icons('leo/Icons/Tango/16x16/emblems'),
            icons('leo/Icons/Tango/16x16/emotes'),
            icons('leo/Icons/Tango/16x16/mimetypes'),
            icons('leo/Icons/Tango/16x16/places'),
            icons('leo/Icons/Tango/16x16/status'),
        # leo/extensions...
            ext('.py', 'leo/extensions'),
            all('leo/extensions/hooks'),
        # leo/external...
            ext('.leo', 'leo/external'),
            ext('.py', 'leo/external'),
            ext('.txt', 'leo/external'),
            ext('.css', 'leo/external/ckeditor'),
            ext('.js', 'leo/external/ckeditor'),
            ext('.json', 'leo/external/ckeditor'),
            ext('.md', 'leo/external/ckeditor'),
        # leo/plugins...
            # Only include reference files.
            # ext('.leo', 'leo/plugins'),
                ('leo/plugins/leoPluginsRef.leo', 'leo/plugins'),
                ('leo/plugins/leoGuiPluginsRef.leo', 'leo/plugins'),
            ext('.txt', 'leo/plugins'),
            ext('.py', 'leo/plugins/examples'),
            ext('.py', 'leo/plugins/test'),
        # leo/scripts...
            ext('.bat', 'leo/scripts'),
            ext('.leo', 'leo/scripts'),
            ext('.txt', 'leo/scripts'),
            ext('.py', 'leo/scripts'),
        # Everything required for unit tests...
        # The leo/test folder itself is required for
        # the execute-script command.
            ext('.leo', 'leo/test'),
            ext('.py', 'leo/test'),
            ext('.txt', 'leo/test'),
            all('leo/test/unittest'),
            all('leo/test/unittest/input'),
            all('leo/test/unittest/output'),
        # leo/www...
            all('leo/www'),
]

a = Analysis(
    ['launchLeo.py'],
    pathex=[], ###'c:\\leo.repo\\leo-editor'],
    binaries=None,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=None,
    runtime_hooks=None,
    excludes=['_tkinter',],
    win_no_prefer_redirects=None,
    win_private_assemblies=None,
    cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
    a.scripts,
    exclude_binaries=True,
    name='leo',
    debug=False,
    strip=None,
    upx=True,
    console=True )

coll = COLLECT(exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=None,
    upx=True,
    name='Leo')
