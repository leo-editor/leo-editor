"""
Put files into the LeoShadow subfolder.

Usage:

   1. convert.py <filename> LeoShadow x

   This copy file <filename> into the subfolder leoShadow,
   adds the prefix, and creates an empty file at the
   current location.

   After restarting Leo, <filename> will be re-created without
   annotations.

   2. convert -all LeoShadow x

   Apply 'convert.py <filename> LeoShadow x' to all .py files.

   Must be run in the directory with the .py files.

   x is the prefix specified the for mod_shadow plugin.
   
"""
import os, sys, shutil

def convert(filename, leoFolder, prefix):
   if not os.path.exists(leoFolder):
       os.mkdir(leoFolder)
       assert os.path.exists(leoFolder)
   else:
       assert os.path.isdir(leoFolder)
   dir, name = os.path.split(filename)
   newname = os.path.join(dir, leoFolder, prefix + name)
   if os.path.exists(newname):
       return
   print("Putting", filename, "into the shadow folder", leoFolder)
   os.rename(filename, newname)
   f = open(filename, "w")
   f.close()

if __name__ == '__main__':
    scriptname, filename, leoFolder, prefix = sys.argv
    if filename == '-all':
        for filename in os.listdir("."):
            rest, extension = os.path.splitext(filename)
            if extension == '.py':
                if (extension not in ['.leo', '.pyc'] and
                    not filename.startswith("convert")):
                    if os.path.isfile(filename):
                        convert(filename, leoFolder, prefix)
    else:
        convert(filename, leoFolder, prefix)
