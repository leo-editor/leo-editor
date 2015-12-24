# -*- mode: python -*-

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
        ('leo/plugins/*.ui','leo/plugins'),
        ('leo/plugins/GraphCanvas/*.*','leo/plugins/GraphCanvas'),
            # Data.
        # These are also hidden imports...
        ('leo/plugins/*.py','leo/plugins'),
        ('leo/plugins/importers/*.py','leo/plugins/importers'),
        ('leo/plugins/writers/*.py','leo/plugins/writers'),
    ],
    hiddenimports=[
        # To do: generate this list automatically.
        # First, required plugins...
        'leo.plugins.free_layout',
        'leo.plugins.mod_scripting',
        'leo.plugins.plugins_menu',
        # Next, optional plugins...
        'leo.plugins.backlink.',
        'leo.plugins.bookmarks',
        'leo.plugins.bzr_qcommands',
        'leo.plugins.contextmenu',
        'leo.plugins.ctagscompleter',
        'leo.plugins.graphcanvas',
            # conflicts with valuespace.py?
            # Requires backlink.py
        'leo.plugins.leoremote',
        'leo.plugins.mod_http',
        'leo.plugins.nav_qt',
        'leo.plugins.nodeActions',
        'leo.plugins.projectwizard',
        'leo.plugins.quickMove',
        'leo.plugins.quicksearch',
        'leo.plugins.spydershell',
        'leo.plugins.stickynotes',
        'leo.plugins.systray',
        'leo.plugins.todo',
            # Used by todo.py...
            'leo.plugins.QNCalendarWidget',
        'leo.plugins.valuespace',
        'leo.plugins.viewrendered',
    ],
    hookspath=None,
    runtime_hooks=None,
    excludes=['tcl','tk','_tkinter',],
        # List of module or package names to be ignored.
    win_no_prefer_redirects=None,
    win_private_assemblies=None,
    cipher=None)

if 0:
    print('sorted(a.pure)...')
    for z in sorted(a.pure):
        print(z)
        

# PYZ, EXE, COLLECT and MERGE defined in api.py.
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    options=[
        # ('v', None, 'OPTION'),  # --verbose:
    ],
    exclude_binaries=True,
    name='Leo',
    debug=False,
    strip=None,
    upx=False,
    console=True)

# Required, even when building to a folder.
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=None,
    upx=False,
    name='Leo')
