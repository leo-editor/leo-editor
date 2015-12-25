# -*- mode: python -*-

# To do: The data folder should be named Leo/leo
# To do: add files so that unit tests can be run.
# To do: add more data files: dist, external, icons, modes, scripts, test, themes, www folders
#            check manifests before adding duplicates (modes are probably already present)

# launchLeo.spec: the spec file for pyinstaller.
# Run with pyinstaller launchLeo.spec

generate_folder = True
	# False: generate Leo.exe in dist folder.
	# The problem with a single Leo.exe file is that there is no leo folder!

import glob, os

def get_modules(name):
	'''return a list of module names in the given subdirector of the leo directory.'''
	abs_dir = os.path.abspath(os.path.join(r'C:\leo.repo\leo-editor\leo', name))
	n = len(abs_dir)+1
	aList = glob.glob(abs_dir + '/*.py')
	return ['leo.%s.%s' % (name, z[n:][:-3]) for z in aList]

# Define all modules in leo.plugins & leo.modes
plugins_list = get_modules('plugins')
modes_list = get_modules('modes')

block_cipher = None

a = Analysis(['launchLeo.py'],
             pathex=['c:\\leo.repo\\leo-editor'],
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
		('leo/modes/*.py','leo/modes'),
		('leo/modes/*.xml','leo/modes'),
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
		hiddenimports=plugins_list + modes_list,
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
          name='Leo',
          debug=False,
          strip=None,
          upx=True,
          console=True )

if generate_folder:
	coll = COLLECT(
	    exe,
	    a.binaries,
	    a.zipfiles,
	    a.datas,
	    strip=None,
	    upx=False,
	    name='Leo')