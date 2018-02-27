#@+leo-ver=5-thin
#@+node:ekr.20160124165611.1: * @file ../../launchLeo-unified.spec
#@@language python
# -*- mode: python -*-
'''
launchLeo-unified.spec

a pyinstaller .spec file that creates a stand-alone version of Leo.
This is a single .exe file or a folder, depending on generate_folder.

>pyinstaller launchLeo-unified.spec

This may be better, per: https://stackoverflow.com/questions/32457341

>pyinstaller --clean --win-private-assemblies launchLeo-unified.spec
'''

# Requires setuptools 19.2 (19.4 is broken)
#    https://github.com/pyinstaller/pyinstaller/issues/1781

generate_folder = True
    # True is *highly* recommended.

#@+<< imports >>
#@+node:edward.20160313203026.1: ** << imports >> launchLeo-unified.spec
import glob
import os
import sys

is_mac = sys.platform.startswith('darwin')

# Same code as in runLeo.py.
path = os.getcwd()
if path not in sys.path:
    print('launchLeo-unified.spec: appending %s to sys.path' % path)
    sys.path.append(path)

import leo.core.leoGlobals as g
import leo.core.leoApp as leoApp

LM = leoApp.LoadManager()
loadDir = LM.computeLoadDir()
#@-<< imports >>

#@+others
#@+node:edward.20160313203148.2: ** all, ext, icons
# Utilities for creating entries in the "datas" lists...
def all(name):
    '''Return a tuple that causes all files in name to be included.'''
    return ('%s/*.*' % (name), name)

icons = all

def ext(kind, name):
    '''
    Return a tuple that causes all files with the given extension in name
    to be included.
    '''
    if kind.startswith('.'):
        kind = kind[1:]
    return ('%s/*.%s' % (name, kind), name)
#@+node:edward.20160313203912.1: ** define_added_binaries
def define_added_binaries():
    '''Return the added binaries needed for MacOS.'''
    if is_mac and False:
        # This doesn't work, and produces huge folders.
        lib_root = os.path.expanduser(
            '~/anaconda2/pkgs/qt-4.8.7-1/lib')
        assert os.path.exists(lib_root), lib_root
        qt_root = os.path.expanduser(
            '~/anaconda2/lib/python2.7/site-packages/PyQt4')
        assert os.path.exists(qt_root), qt_root
        prefix = 'PyQt4' # None means top-level folder.
        return (
            Tree(
                lib_root,
                prefix=prefix,
                excludes=['pkgconfig','*.a',],
            ) +
            Tree(
                qt_root,
                prefix=prefix,
                excludes=[]
            )
        )
    return []
#@+node:edward.20160313203338.1: ** define_datas
def define_datas():
    '''Return all needed data files.'''
    return [
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
        # This list created by print_icon_directories.
        icons('leo/Icons'),
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
        icons('leo/Icons/cleo'),
        icons('leo/Icons/cleo/small'),
        icons('leo/Icons/file_icons'),
        icons('leo/Icons/nodes-dark/plusminus'),
        icons('leo/Icons/nodes-dark/triangles'),
        icons('leo/Icons/nodes-light/plusminus'),
        icons('leo/Icons/nodes-light/triangles'),
        icons('leo/Icons/recorder'),
        icons('leo/Icons/transparent/boxes/black'),
        icons('leo/Icons/transparent/boxes/solarized'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/base0'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/base00'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/base01'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/base02'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/base03'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/base1'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/base2'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/base3'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/black1'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/black2'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/blue'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/cyan'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/green'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/magenta'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/orange'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/red'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/violet'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/white'),
        icons('leo/Icons/transparent/boxes/solarized-monochromatic/yellow'),
        icons('leo/Icons/transparent/boxes/white'),
        icons('leo/Icons/transparent/icons/declutter/directives/black'),
        icons('leo/Icons/transparent/icons/declutter/directives/solarized'),
        icons('leo/Icons/transparent/icons/declutter/directives/solarized-monochromatic'),
        icons('leo/Icons/transparent/icons/declutter/directives/white'),
        icons('leo/Icons/transparent/icons/declutter/file/black/empty'),
        icons('leo/Icons/transparent/icons/declutter/file/black/text'),
        icons('leo/Icons/transparent/icons/declutter/file/solarized-monochromatic/empty'),
        icons('leo/Icons/transparent/icons/declutter/file/solarized-monochromatic/text'),
        icons('leo/Icons/transparent/icons/declutter/file/solarized/empty/outlined'),
        icons('leo/Icons/transparent/icons/declutter/file/solarized/empty/solid'),
        icons('leo/Icons/transparent/icons/declutter/file/solarized/text/outlined'),
        icons('leo/Icons/transparent/icons/declutter/file/solarized/text/solid'),
        icons('leo/Icons/transparent/icons/declutter/file/white/empty'),
        icons('leo/Icons/transparent/icons/declutter/file/white/text'),
        icons('leo/Icons/transparent/icons/declutter/folder/black'),
        icons('leo/Icons/transparent/icons/declutter/folder/black/horizontal'),
        icons('leo/Icons/transparent/icons/declutter/folder/black/path'),
        icons('leo/Icons/transparent/icons/declutter/folder/black/vertical'),
        icons('leo/Icons/transparent/icons/declutter/folder/solarized'),
        icons('leo/Icons/transparent/icons/declutter/folder/solarized-monochromatic'),
        icons('leo/Icons/transparent/icons/declutter/folder/solarized-monochromatic/horizontal'),
        icons('leo/Icons/transparent/icons/declutter/folder/solarized-monochromatic/path'),
        icons('leo/Icons/transparent/icons/declutter/folder/solarized-monochromatic/vertical'),
        icons('leo/Icons/transparent/icons/declutter/folder/solarized/horizontal/outlined'),
        icons('leo/Icons/transparent/icons/declutter/folder/solarized/horizontal/solid'),
        icons('leo/Icons/transparent/icons/declutter/folder/solarized/path/outlined'),
        icons('leo/Icons/transparent/icons/declutter/folder/solarized/path/solid'),
        icons('leo/Icons/transparent/icons/declutter/folder/solarized/vertical/outlined'),
        icons('leo/Icons/transparent/icons/declutter/folder/solarized/vertical/solid'),
        icons('leo/Icons/transparent/icons/declutter/folder/white'),
        icons('leo/Icons/transparent/icons/declutter/folder/white/horizontal'),
        icons('leo/Icons/transparent/icons/declutter/folder/white/path'),
        icons('leo/Icons/transparent/icons/declutter/folder/white/vertical'),
        icons('leo/Icons/transparent/icons/misc/black'),
        icons('leo/Icons/transparent/icons/misc/solarized'),
        icons('leo/Icons/transparent/icons/misc/solarized-monochromatic'),
        icons('leo/Icons/transparent/icons/misc/white'),
        icons('leo/Icons/transparent/icons/nodes/plusminus/black'),
        icons('leo/Icons/transparent/icons/nodes/plusminus/solarized'),
        icons('leo/Icons/transparent/icons/nodes/plusminus/white'),
        icons('leo/Icons/transparent/icons/nodes/triangles/black'),
        icons('leo/Icons/transparent/icons/nodes/triangles/solarized'),
        icons('leo/Icons/transparent/icons/nodes/triangles/white'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/base0'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/base00'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/base01'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/base02'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/base03'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/base1'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/base2'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/base3'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/black1'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/black2'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/blue'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/cyan'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/green'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/magenta'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/orange'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/red'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/violet'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/white'),
        icons('leo/Icons/transparent/icons/task/solarized/monochromatic/yellow'),
        icons('leo/Icons/transparent/icons/task/solarized/regular'),
        icons('leo/Icons/transparent/icons/task/solarized/small'),
        icons('leo/Icons/transparent/icons/toolbar/black'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/base0'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/base00'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/base01'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/base02'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/base03'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/base1'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/base2'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/base3'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/black1'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/black2'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/blue'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/cyan'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/green'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/magenta'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/orange'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/red'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/violet'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/white'),
        icons('leo/Icons/transparent/icons/toolbar/solarized-monochromatic/yellow'),
        icons('leo/Icons/transparent/icons/toolbar/white'),
    # The following files *are* useful in one-file operation.
    # sys._MEIPASS points to the temp folder.
    # On windows: ~\AppData\Local\Temp\_MEInnnn
    # leo-editor: loaded by LeoPy.leo...
        ('launchLeo-unified.spec', ''),
        ('leo_to_html.xsl', ''),
        ('pylint-leo.py', ''),
         # In LeoPyRef.leo...
        ('flake8-leo.py', ''),
        ('load-leo.html', ''),
        ('pyflakes-leo.py', ''),
        # In leoDist.leo
        ('README.md', ''), # Case important!
        # ('setup.py', ''),
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
        ext('.md', 'leo/doc'),
        ext('.leo', 'leo/doc'),
        ext('.py', 'leo/doc'),
        ext('.txt', 'leo/doc'),
        all('leo/doc/html'),
    # ext('.jif','leo/doc/html'),
    # ext('.py','leo/doc/html'),
    # ext('.txt','leo/doc/html'),
    # leo/extensions...
        ext('.py', 'leo/extensions'),
        all('leo/extensions/hooks'),
    # leo/external...
        # Note: npyscreen is not distributed.
        ext('.cfg', 'leo/external'),
        ext('.md', 'leo/external'),
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
    # execute-script requires the leo/test folder itself.
        ext('.leo', 'leo/test'),
        ext('.py', 'leo/test'),
        ext('.txt', 'leo/test'),
        ext('.css', 'leo/test'),
        all('leo/test/unittest'),
        all('leo/test/unittest/input'),
        all('leo/test/unittest/output'),
        all('leo/test/unittest/perfectImport'),
    # leo/www...
        all('leo/www'),
    ]
#@+node:edward.20160313203420.1: ** define_hidden_imports
def define_hidden_imports():
    '''Define all modules in leo.plugins & leo.modes.'''
    hidden_imports = []
    for name in ('external', 'modes', 'plugins',
                 'plugins/importers', 'plugins/writers',
    ):
        hidden_imports.extend(get_modules(name))

    hidden_imports = [z.replace('/','.') for z in hidden_imports]
    if 0:
        print('hidden imports...')
        for z in sorted(hidden_imports):
            print(z)
        sys.exit()
    return hidden_imports
#@+node:edward.20160313203148.1: ** get_modules
def get_modules(name):
    '''
    Return a list of module names (separated by dots) in the leo/x directory.
    This could be replaced by PyInstaller.utils.hooks.collect_submodules.
    '''
    abs_dir = g.os_path_finalize_join(loadDir, '..', name)
    n = len(abs_dir) + 1
    aList = glob.glob(abs_dir + '/*.py')
    return ['leo.%s.%s' % (name, z[n:][: -3]) for z in aList]
#@+node:edward.20160313203251.1: ** main
def main():
    '''Main line of launchLeo-unified.spec.'''
    added_binaries = define_added_binaries()
    datas = define_datas()
    hidden_imports = define_hidden_imports()
    exclude_modules = ['_tkinter',]
    a = Analysis(['launchLeo.py'],
        pathex=[],
        binaries=None,
        datas=datas,
        hiddenimports=hidden_imports,
        hookspath=None,
        runtime_hooks=None,
        excludes=exclude_modules,
        win_no_prefer_redirects=None,
        win_private_assemblies=None,
        cipher=None)
    pyz = PYZ(a.pure, a.zipped_data, cipher=None)
    if generate_folder:
        if is_mac:
            # Does not work at present.
            exe = EXE(pyz,
                a.scripts,
                a.binaries + added_binaries,
                exclude_binaries=False,
                name='LeoApp', # 'leo' doesn't work on Linux.
                debug=False,
                strip=None,
                upx=True,
                console=True )
        else:
            exe = EXE(pyz,
                a.scripts,
                exclude_binaries=True,
                name='LeoApp', # 'leo' doesn't work on Linux.
                debug=False,
                strip=None,
                upx=True,
                console=True )
    else:
        exe = EXE(pyz,
            a.scripts,
            a.binaries + added_binaries,
            a.zipfiles,
            a.datas,
            name='LeoApp', # 'leo' doesn't work on Linux.
            debug=False,
            strip=None,
            upx=True,
            console=True)
    if generate_folder:
        coll = COLLECT(
            exe,
            a.binaries + added_binaries,
            a.zipfiles,
            a.datas,
            strip=None,
            upx=False,
            name='LeoAppFolder')
#@+node:ekr.20170316215354.1: ** print_icon_directories
def print_icon_directories():
    '''Print list of all Icon directories containing icons.'''
    g.cls()
    import os
    rootDir = g.os_path_finalize_join(g.app.loadDir, '..', 'Icons')
    result = []
    for dirName, subdirList, fileList in os.walk(rootDir):
        if fileList:
            s = dirName.replace('\\','/')
            s = s.replace('C:/leo.repo/leo-editor/','')
            result.append("icons('%s')," % (s))
    for path in sorted(result):
        print(path)
#@-others
main()
#@-leo
