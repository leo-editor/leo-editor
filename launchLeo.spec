# -*- mode: python -*-

# To do: generate single-file version.
# To do: run unit tests from single-file version.

import glob, os

# Define all modules in leo.plugins.
# plugins = g.os_path_finalize_join(g.app.loadDir,'..','plugins')
plugins = os.path.abspath(os.path.join(r'C:\leo.repo\leo-editor\leo\plugins'))
n = len(plugins)+1
aList = glob.glob(plugins+'/*.py')
plugins_list = ['leo.plugins.%s' % z[n:][:-3] for z in aList]

# Analysis defined in build_main.py:
a = Analysis(['launchLeo.py'],
    pathex=[],
        # List of paths to be searched before sys.path
    binaries=None,
    datas=[
        ('leo/config/*.leo','leo/config'),
        ('leo/core/commit_timestamp.json','leo/core'),
        ('leo/doc/*.css','leo/doc'),
        ('leo/doc/*.js','leo/doc'),
        ('leo/doc/*.html','leo/doc'),
        ('leo/doc/*.leo','leo/doc'),
        ('leo/doc/*.txt','leo/doc'),
        ('leo/Icons/*.*','leo/Icons'),
        ('leo/Icons/cleo/*.*','leo/Icons/cleo'),
        ('leo/plugins/*.ui','leo/plugins'),
        ('leo/plugins/GraphCanvas/*.*','leo/plugins/GraphCanvas'),
            # Data.
        # These are also hidden imports...
        ('leo/plugins/*.py','leo/plugins'),
        ('leo/plugins/importers/*.py','leo/plugins/importers'),
        ('leo/plugins/writers/*.py','leo/plugins/writers'),
        # Required for execute-script.
        ('leo/test/scriptFile.py','leo/test'),
        ('leo/test/test.leo','leo/test'),
        ('leo/test/unittest.leo','leo/test'),
    ],
    hiddenimports=plugins_list,
    hookspath=None,
    runtime_hooks=None,
    excludes=['tcl','tk','_tkinter',],
        # List of module or package names to be ignored.
    win_no_prefer_redirects=None,
    win_private_assemblies=None,
    cipher=None)

# PYZ, EXE, COLLECT and MERGE are defined in api.py.
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    options=[
        # ('v', None, 'OPTION'),  # --verbose
    ],
    exclude_binaries=True,
    name='Leo',
    debug=False,
    strip=None,
    upx=False,
    console=True)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=None,
    upx=False,
    name='Leo')
