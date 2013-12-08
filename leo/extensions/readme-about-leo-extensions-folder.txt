This folder, the leo/extensions folder, is the place for copies of
python modules that are not defined by Leo.

In contrast, the leo/external folder is the place for code defined by Leo
that is neither a part of Leo's core nor a plugin.

Note: the docstring for  g.importExtension is:

'''Try to import a module.  If that fails, try to import the module
from Leo's extensions directory.'''
