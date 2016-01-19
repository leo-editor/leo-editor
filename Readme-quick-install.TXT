Readme-quick-install.TXT

This document describes two ways of running Leo without having to install *anything* else.

Method 1. (Folder-based, Recommended)

Download the Leo folder, unpack it *anywhere* you like, and run leo.exe from within the unpacked folder.

Method 2. (Single-file, Easiest):

Download leo.exe and execute it *anywhere* by double-clicking on it.

There are two disadvantages to using the single-file method:

1. Before Leo starts, PyInstaller unpacks all libraries and data files to a temp folder:
       ~\AppData\Local\Temp\_MEInnn.
   As a result, starting leo.exe is slower than usual.

2. *Warning*: You can open Leo files from the "Files:Open Leo File" menu,
   but these files exist *only* in the temp folder. They will be *destroyed*
   when you exit leo.exe. If you want to do real work with Leo you must
   create .leo files in a permanent folder on your machine.
   
Both the folder-based and single-file version were created by PyInstaller: http://pythonhosted.org/PyInstaller.
