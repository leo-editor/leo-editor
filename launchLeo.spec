# -*- mode: python -*-

block_cipher = None

options = [
    ('v', None, 'OPTION'),  # --verbose:
]

if 0:
    added_files = [
        ('c:\\leo.repo\\leo-editor\\leo\\commands', 'leo\\commands'),
        ('c:\\leo.repo\\leo-editor\\leo\\config', 'leo\\config'),
        ('c:\\leo.repo\\leo-editor\\leo\\core', 'leo\\core'),
        ('c:\\leo.repo\\leo-editor\\leo\\dist', 'leo\\dist'),
        ('c:\\leo.repo\\leo-editor\\leo\\doc', 'leo\\doc'),
        ('c:\\leo.repo\\leo-editor\\leo\\extensions', 'leo\\extensions'),
        ('c:\\leo.repo\\leo-editor\\leo\\Icons', 'leo\\Icons'),
        ('c:\\leo.repo\\leo-editor\\leo\\modes', 'leo\\modes'),
        ('c:\\leo.repo\\leo-editor\\leo\\plugins', 'leo\\plugins'),
        ('c:\\leo.repo\\leo-editor\\leo\\themes', 'leo\\themes'),
    ]
else:
    added_files = [ ]

excludes_toc = [
]

a = Analysis(['launchLeo.py'],
             pathex=['c:\\leo.repo\\leo-editor'],
             binaries=None,
             datas=added_files,
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             excludes=excludes_toc,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          options,
          exclude_binaries=True,
          name='launchLeo',
          debug=True,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='launchLeo')
