# -*- mode: python ; coding: utf-8 -*-

# c:\code\leo-editor\leo\dist
# c:\code\leo-editor\launchLeo.py
leo_root = os.path.join(os.path.abspath(SPECPATH), '../../')
launcher = os.path.join(leo_root, 'launchLeo.py')


block_cipher = None

a = Analysis([launcher],
			 pathex=[leo_root],
             binaries=[],
             datas=[(leo_root + 'leo', 'leo')],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='leo',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='leo')

# Guide: https://blog.aaronhktan.com/posts/2018/05/14/pyqt5-pyinstaller-executable
#
# fix ModuleNotFoundError: No module named 'pkg_resources.py2_warn'
# https://github.com/pypa/setuptools/issues/1963#issuecomment-574265532
