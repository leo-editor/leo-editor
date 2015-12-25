# -*- mode: python -*-
'''
launchLeo.spec: the spec file for pyinstaller.
Run with pyinstaller launchLeo.spec, **not** with launchLeo.py.
'''

generate_folder = False
    # True: generate only Leo/Leo.exe.
    # False: generate Leo/leo folder as well as Leo/Leo.exe.

import glob, os

def get_modules(name):
	'''return a list of module names in the given subdirector of the leo directory.'''
	abs_dir = os.path.abspath(os.path.join(r'C:\leo.repo\leo-editor\leo', name))
	n = len(abs_dir)+1
	aList = glob.glob(abs_dir + '/*.py')
	return ['leo.%s.%s' % (name, z[n:][:-3]) for z in aList]
    
# Utilities for creating entries in the "datas" lists...
def all(name):
    return ('%s/*.*' % (name), name)
        
def ext(kind,name):
    if kind.startswith('.'):
        kind = kind[1:]
    return ('%s/*.%s' % (name,kind), name)
    
def icons(name):
    return ('%s/*.*' % (name), name)

# Define all modules in leo.plugins & leo.modes
hiddenimports = []
for name in ('external','modes','plugins'):
    hiddenimports.extend(get_modules(name))

block_cipher = None

datas = [
    # Required for startup...
        ('leo/core/commit_timestamp.json','leo/core'),
        ext('.ui','leo/plugins'),
    # Required for execute-script.
        ('leo/test/scriptFile.py', 'leo/test'),
    # Required for plugins...
        # Data requifed for startup.
            all('leo/plugins/GraphCanvas'),
        # These are also hidden imports...
            ext('.py','leo/plugins'),
            ext('.py','leo/plugins/importers'),
            ext('.py','leo/plugins/writers'),
    # leo/config...
        ext('.leo','leo/config'),
    # leo/modes...
        ext('.py','leo/modes'),
        ext('.xml','leo/modes'),
    # All icons in leo/Icons...
        icons('leo/Icons'),
        icons('leo/Icons/cleo'),
        icons('leo/Icons/cleo/small'),
        icons('leo/Icons/file_icons'),
        icons('leo/Icons/nodes-dark/plusminus'),
        icons('leo/Icons/nodes-dark/triangles'),
        icons('leo/Icons/recorder'),
    # All icons in leo/Themes...
        icons('leo/Themes/generic/Icons'),
        icons('leo/Themes/leo_dark_0/Icons'),
        icons('leo/Themes/leo_dark_0/Icons/cleo'),
        icons('leo/Themes/leo_dark_0/Icons/cleo/small'),
        icons('leo/Themes/leo_dark_0/Icons/file_icons'),
        icons('leo/Themes/leo_dark_0/Icons/Tango/16x16/apps'),
]

if generate_folder:
    datas.extend([
        # leo.core...
            ext('.leo','leo/core'),
            ext('.py','leo/core'),
            ext('.txt','leo/core'),
        # leo.dist...
            all('leo/dist'),
        # leo/doc...
            ext('.css','leo/doc'),
            ext('.js','leo/doc'),
            ext('.html','leo/doc'),
            ext('.leo','leo/doc'),
            ext('.txt','leo/doc'),
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
        # leo/external...
            ext('.py','leo/external'),
            ext('.txt','leo/external'),
        # leo/scripts...
            ext('.bat', 'leo/scripts'),
            ext('.txt', 'leo/scripts'),
            ext('.py', 'leo/scripts'),
        # Everything required for unit tests...
            ext('.leo','leo/test'),
            ext('.py','leo/test'),
            ext('.txt','leo/test'),
            all('leo/test/unittest'),
            all('leo/test/unittest/input'),
            all('leo/test/unittest/output'),
        # leo/www
            all('leo/www'),
    ])

a = Analysis(['launchLeo.py'],
    pathex=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    name='leo',
    debug=False,
    strip=None,
    upx=True,
    console=True)

if generate_folder:
	coll = COLLECT(
	    exe,
	    a.binaries,
	    a.zipfiles,
	    a.datas,
	    strip=None,
	    upx=False,
	    name='Leo')
