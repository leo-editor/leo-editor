# -*- mode: python -*-

# To do:
# - File submenu.
# - Test excluding only _tkinter.
# - Minimal data files for one-file version: .json, icons, themes, plugins, etc.
# - More data files: dist, external, icons, modes, scripts, test, themes, www folders.

# launchLeo.spec: the spec file for pyinstaller.
# Run with pyinstaller launchLeo.spec

generate_folder = False
	# False: generate Leo.exe in dist folder.

import glob, os

def get_modules(name):
	'''return a list of module names in the given subdirector of the leo directory.'''
	abs_dir = os.path.abspath(os.path.join(r'C:\leo.repo\leo-editor\leo', name))
	n = len(abs_dir)+1
	aList = glob.glob(abs_dir + '/*.py')
	return ['leo.%s.%s' % (name, z[n:][:-3]) for z in aList]

# Define all modules in leo.plugins & leo.modes
hiddenimports = get_modules('plugins') + get_modules('modes')

block_cipher = None

datas = [
    # Required for startup...
        ('leo/core/commit_timestamp.json','leo/core'),
        ('leo/plugins/*.ui','leo/plugins'),
    # Required for execute-script.
        ('leo/test/scriptFile.py', 'leo/test'),
    # Required for plugins...
        # Data requifed for startup.
        ('leo/plugins/GraphCanvas/*.*','leo/plugins/GraphCanvas'),
        # These are also hidden imports...
            ('leo/plugins/*.py','leo/plugins'),
            ('leo/plugins/importers/*.py','leo/plugins/importers'),
            ('leo/plugins/writers/*.py','leo/plugins/writers'), 
    # Everything in leo/config...
        ('leo/config/*.leo','leo/config'),
    # Everything in leo/modes...
        ('leo/modes/*.py','leo/modes'),
        ('leo/modes/*.xml','leo/modes'),
    # Everything in leo/Icons...
        ('leo/Icons/*.*','leo/Icons'),
        ('leo/Icons/cleo/*.*','leo/Icons/cleo'),
        ('leo/Icons/cleo/small/*.*','leo/Icons/cleo/small'),
        ('leo/Icons/file_icons/*.*','leo/Icons/file_icons'),
        ('leo/Icons/nodes-dark/plusminus/*.*','leo/Icons/nodes-dark/plusminus'),
        ('leo/Icons/nodes-dark/triangles/*.*','leo/Icons/nodes-dark/triangles'),
        ('leo/Icons/recorder/*.*','leo/Icons/recorder'),
            ### To do: handle inner folders.
        ### ('leo/Icons/Tango/16x16/*.*','leo/Icons/Tango/16x16'),
]

if generate_folder:
    datas.extend([
        # Everything in leo.core...
            ('leo/core/*.leo','leo/core'),
            ('leo/core/*.py','leo/core'),
            ('leo/core/*.txt','leo/core'),
        # Everything in leo/doc...
            ('leo/doc/*.css','leo/doc'),
            ('leo/doc/*.js','leo/doc'),
            ('leo/doc/*.html','leo/doc'),
            ('leo/doc/*.leo','leo/doc'),
            ('leo/doc/*.txt','leo/doc'),
        # Everything in leo/scripts...
            ('leo/scripts/*.bat', 'leo/scripts'),
            ('leo/scripts/*.txt', 'leo/scripts'),
            ('leo/scripts/*.py', 'leo/scripts'),
        # Everything required for unit tests...
            ('leo/test/*.leo','leo/test'),
            ('leo/test/*.py','leo/test'),
            ('leo/test/*.txt','leo/test'),
            ('leo/test/unittest/*.*', 'leo/test/unittest'),
            ('leo/test/unittest/input/*.*', 'leo/test/unittest/input'),
            ('leo/test/unittest/output/*.*', 'leo/test/unittest/output'),
    ])

a = Analysis(['launchLeo.py'],
    pathex=[], # 'c:\\leo.repo\\leo-editor'],
    binaries=None,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=None,
    runtime_hooks=None,
    excludes=['tcl','tk','_tkinter',],
        # List of module or package names to be ignored.
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
