<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet ekr_test?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5" body_secondary_ratio="0.5">
	<global_window_position top="50" left="50" height="500" width="700"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20050315084904"><vh>Startup</vh>
<v t="ekr.20070325123540"><vh>@chapters</vh></v>
<v t="ekr.20050315084922"><vh>@button Spell</vh></v>
</v>
<v t="EKR.20040519091259"><vh>Annoucements</vh>
<v t="EKR.20040519091259.1"><vh>Download statistics</vh></v>
<v t="EKR.20040519091259.2"><vh>Quotes of the month</vh>
<v t="ekr.20080901114425.2"><vh>Sept 2008</vh></v>
<v t="ekr.20070425092712"><vh>April 2007</vh></v>
<v t="ekr.20070101093904"><vh>January 2007</vh></v>
<v t="ekr.20060823090437"><vh>August 2006</vh></v>
<v t="ekr.20060213160806"><vh>February 2005</vh></v>
<v t="ekr.20040828084148"><vh>August 2004</vh></v>
<v t="ekr.20040630210818"><vh>July 2004</vh></v>
<v t="EKR.20040519091259.3"><vh>November 2003</vh></v>
<v t="EKR.20040519091259.4"><vh>October 2003</vh></v>
</v>
<v t="ekr.20101104090957.1488"><vh>Leo 4.8 b1</vh></v>
</v>
<v t="ekr.20100202061222.1494"><vh>Distribution checklist</vh></v>
<v t="EKR.20040519090846"><vh>Distribution files</vh>
<v t="EKR.20040519090846.2"><vh>@asis ../../INSTALL.TXT</vh>
<v t="EKR.20040519090846.3"><vh>System requirements</vh></v>
<v t="ekr.20080825083632.262"><vh>Leo's HOME directory</vh></v>
<v t="EKR.20040519090846.4"><vh>Linux installation</vh></v>
<v t="EKR.20040519090846.5"><vh>Windows installation</vh></v>
<v t="EKR.20040519090846.6"><vh>MacOS installation</vh></v>
<v t="ekr.20080825083632.263"><vh>Running Leo</vh></v>
</v>
<v t="EKR.20040519090846.1"><vh>@asis ../../LICENSE.TXT</vh></v>
<v t="EKR.20040519090846.8"><vh>@asis ../../PKG-INFO.TXT</vh></v>
<v t="EKR.20040519090846.9"><vh>@asis ../../README.TXT</vh></v>
</v>
<v t="ekr.20090905082405.1486"><vh>@button make leo.zip</vh>
<v t="ekr.20090905082405.1487"><vh>&lt;&lt; includes &gt;&gt;</vh></v>
<v t="ekr.20101104090957.1489"><vh>error</vh></v>
<v t="ekr.20090905082405.1489"><vh>make</vh></v>
<v t="ekr.20090905082405.1490"><vh>unlink</vh></v>
</v>
<v t="ekr.20101027070126.1639"><vh>@button make leo.nsi</vh>
<v t="ekr.20101027070126.1643" a="E"><vh>class nsiWriter</vh>
<v t="ekr.20101027070126.1675"><vh>create_install_files</vh></v>
<v t="ekr.20101027070126.1676"><vh>create_uninstall_files</vh></v>
<v t="ekr.20101027070126.1662" a="E"><vh>run &amp; helpers</vh>
<v t="ekr.20101027070126.1664" a="E"><vh>filterLines &amp; helpers</vh>
<v t="ekr.20101027070126.1665"><vh>delete...</vh></v>
</v>
<v t="ekr.20101027070126.1666"><vh>makeDicts</vh></v>
<v t="ekr.20101027070126.1667"><vh>printMissing</vh></v>
<v t="ekr.20101027070126.1663"><vh>directoryList</vh></v>
</v>
<v t="ekr.20101027070126.1680"><vh>utils...</vh>
<v t="ekr.20101027070126.1679"><vh>openFile</vh></v>
<v t="ekr.20101027070126.1678"><vh>put</vh></v>
</v>
</v>
</v>
<v t="ekr.20101025095431.1517"><vh>Installer/Distribution to do</vh>
<v t="ekr.20101025095431.1518"><vh>Bug 514656 Uninstall operation does not work as expected</vh>
<v t="ekr.20090901092556.1576"><vh>genUninstallData &amp; helpers</vh>
<v t="ekr.20090901121423.1568"><vh>getDeleteDirectories</vh></v>
<v t="ekr.20090901121423.1569"><vh>getDeleteFiles</vh></v>
<v t="ekr.20090901121423.1567"><vh>getUninstallVariableData</vh></v>
</v>
</v>
<v t="ekr.20101026142031.1516"><vh>Registry Keys</vh></v>
</v>
<v t="ekr.20101027131034.1490"><vh>NSIS source files</vh>
<v t="ekr.20101027160251.1500"><vh>Notes</vh>
<v t="ekr.20101027135430.1492"><vh>@url nsi new ui readme</vh></v>
<v t="ekr.20101027135430.1493"><vh>@url about pages</vh></v>
<v t="ekr.20101027160251.1497"><vh>@url nsDialogs</vh></v>
</v>
<v t="ekr.20101027054254.1590"><vh>@edit ../../leo.nsi</vh></v>
<v t="ekr.20101027115225.1494"><vh>@thin nsi-boilerplate.txt</vh></v>
</v>
</vnodes>
<tnodes>
<t tx="EKR.20040519090846">@nocolor

1. Search for ##version

2. Search for this suffix: -b1.

3. Search for copyright

    Latest copyright date: 2010.

    Note: install.txt file embeds a copyright message in the nsi installer.</t>
<t tx="EKR.20040519090846.1">Leo is Open Software and is distributed under the terms of the MIT
License. The gist of the license is that Leo is absolutely free, even
for commercial use (including resale). There is no GNU-like "copyleft"
restriction. The Open Source Initiative board has voted to certify the
MIT license as Open Source. This license is compatible with the GPL.

Copyright (c) 1997-2010 by Edward K. Ream. All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appear in all copies and that
both that copyright notice and this permission notice appear in
supporting documentation, and that the names of Leo or Edward K. Ream
not be used in advertising or publicity pertaining to distribution of
the software without specific, written prior permission.

DISCLAIMER OF WARRANTIES

EDWARD K. REAM (REAM) SPECIFICALLY DISCLAIMS ALL WARRANTIES, EXPRESSED
OR IMPLIED, WITH RESPECT TO THIS COMPUTER SOFTWARE, INCLUDING BUT NOT
LIMITED TO IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE. IN NO EVENT SHALL REAM BE LIABLE FOR ANY LOSS OF
PROFIT OR ANY COMMERCIAL DAMAGE, INCLUDING BUT NOT LIMITED TO SPECIAL,
INCIDENTAL, CONSEQUENTIAL OR OTHER DAMAGES.
</t>
<t tx="EKR.20040519090846.2"></t>
<t tx="EKR.20040519090846.3">System requirements
-------------------

Leo requires Python 2.6 or above (including Python 3.x) and tcl/tk 8.4 or above.
Leo will also work with PyQt instead of tcl/tk.

	Download Python from http://python.org/ 
	Download tcl/Tk from http://tcl.activestate.com/software/tcltk/
    Download PyQt from http://www.riverbankcomputing.co.uk/news

Warning: When building Tcl on Linux, do not specify "--enable-threads" .
Only use Tcl with the default "threads not enabled" case.
</t>
<t tx="EKR.20040519090846.4">
Installing the leo.py on Linux
------------------------------

Download the latest version of Leo (a .zip file) from `Leo's download page`_.

Unzip the downloaded .zip file into the **unpacked folder** in your home directory.
The unpacked folder will be called something like leo-4-5.

You can run Leo from your home directory.
You can add  ~/leo-4-5 to your path, or you can create an alias that executes::

    python ~/leo-4-5/launchLeo.py
</t>
<t tx="EKR.20040519090846.5">
Installing Leo on Windows
--------------------------

There are now two ways to install Leo on Windows:
    
1. Use the single-click executable installer, named something like
   LeoSetup-4.7.1-final.exe

2. Leo is distributed as a .zip file.
   To install Leo from the .zip file:

    1. Download the latest version of Leo (a .zip file) from:    
       http://sourceforge.net/project/showfiles.php?group_id=3458&amp;package_id=29106

    2. Unzip the .zip file and place the unpacked leo folder in 
       the 'Program Files' folder or any convenient location.

    After you have installed Leo, you should add the location of your leo/core folder to your python path.
    One way to do this is adding something like the following to python/Lib/sitecustomize.py:

        import sys
        sys.path.append(r'&lt;path-to-leo&gt;leo\core')

    Another way is to append &lt;path-to-leo&gt; to the Windows PYTHONPATH environment variable.
</t>
<t tx="EKR.20040519090846.6">
Installing leo.py on MacOs
--------------------------

Leo works reliably only on MacOS X 10.3 and above.

For the latest discussion of how to install Leo with PyQt, see
http://groups.google.com/group/leo-editor/browse_thread/thread/2bae897436d3d70e/20d8b94ac3371074?lnk=gst&amp;q=macos#20d8b94ac3371074

To run Leo on Macintosh OS X 10.3 (There will be slight changes for later versions of Mac Os X):

1) Download and install "MacPython 2.3 for Panther addons".

Python is already included in OS X 10.3 so only the addons are necessary

	http://www.cwi.nl/~jack/macpython.html

2) Download and install TclTkAqua.

	http://tcltkaqua.sourceforge.net/

3) Run the PackageManager found in /Applications/MacPython-2.3 and  
install "_tkinter-2.3-binary" by clicking on the package in the list  
and clicking the [Install:] button with "Install dependencies" checked

4)  Install Leo.  There are two ways to do this.

a)  The NEW way: Download Leo-version-number.pkg from

    http://leo.sourceforge.net/

Double-click Leo.pkg to install the Leo folder. I recommend that you install Leo
in your home directory.

b) The OLD way: Download Leo-version-number.zip:

	http://leo.sourceforge.net/

Unzip the contents into the desired directory by double-clicking the downloaded file.

5) Run Leo by control-clicking on /path_to_unzipped_dir/leo/core/leo.py and open
with PythonLauncher.

6) It is a good idea to set PythonLauncher as the default program to  
open python scripts by clicking on "leo.py", choosing Get Info from the  
Finder's File menu, and selecting "PythonLauncher" as the default  
program to "Open With:"

By clicking the "Change All..." button, all python scripts will be  
opened with PythonLauncher.

8) (optional) Download and install Pmw. (Leo now contains Pmw in the extensions folder).

    http://pmw.sourceforge.net/

Pmw must be installed in order to use the Settings panel.

Drag the downloaded gzip file into

/System/Library/Frameworks/Python.framework/Versions/2.3/lib/python2.3/site-packages

Double click on it to unzip and untar the file into a folder to make it
available to Python

Thanks to Randall Voth for these instructions.
</t>
<t tx="EKR.20040519090846.8">Metadata-Version: 1.0
Name: leo
Version: 4.8-b1
Summary: Leo: Literate Editor with Outlines
Home-page: http://webpages.charter.net/edreamleo/front.html
Author: Edward K. Ream
Author-email: edreamleo@charter.net
License: Python
Description:
    Leo is an outline-oriented IDE written in 100% pure Python.
	Leo features a multi-window outlining editor, Python colorizing,
	powerful outline commands and many other things, including 
	unlimited Undo/Redo and an integrated Python shell(IDLE) window.
    Leo requires Python 2.6 or above.  Leo works with Python 3.x.
Platform: Windows, Linux, Macintosh
</t>
<t tx="EKR.20040519090846.9">Leo 4.8 beta 1                               November 8, 2010

Leo 4.8 beta 1 is now available at:
http://sourceforge.net/project/showfiles.php?group_id=3458&amp;package_id=29106

Leo is a text editor, data organizer, project manager and much more. See:
http://webpages.charter.net/edreamleo/intro.html

The highlights of Leo 4.8:
--------------------------

- Leo now uses the simplest possible sentinel lines in external files.
  External files with sentinels now look like Emacs org-mode files.
- Leo Qt gui now supports Drag and Drop.
  This was one of the most frequently requested features.
- Improved abbreviation commands.
  You now define abbreviations in Leo settings nodes, not external files.
- @url nodes may contain url's in body text.
  This allows headlines to contain summaries: very useful.
- Leo now uses PyEnchant to check spelling.
  Much safer than using aspell.
- Leo can now open multiple files from the command line.
- Leo's ancient Tangle and Untangle commands are now deprecated.
  This will help newbies how to learn Leo.
- Leo now shows "Resurrected" and "Recovered" nodes.
  These protect data and show how data have changed.
  These fix several long-standing data-related problems.
- A new "screenshots" plugin for creating slide shows with Leo.
  I used this plugin to create Leo's introductory slide shows.
- A better installer.
- Many bug fixes.

Links:
------
Leo:      http://webpages.charter.net/edreamleo/front.html
Forum:    http://groups.google.com/group/leo-editor
Download: http://sourceforge.net/project/showfiles.php?group_id=3458
Bzr:      http://code.launchpad.net/leo-editor/
Quotes:   http://webpages.charter.net/edreamleo/testimonials.html
</t>
<t tx="EKR.20040519091259">@pagewidth 70
@killcolor

We no longer use a separate announcement.
Just use the readme.</t>
<t tx="EKR.20040519091259.1">4.4.5       setup: 547  zip: 379  2007-12-11
4.4.4       setup: 856  zip: 539  2007-11-02
4.4.3.1     setup: 1092 zip: 743  2007-7-03
4.4.3       setup: 363  zip: 282  2007-6-26
4.4.2.1     setup: 2847 zip: 2044 2006-10-19
4.4.1.1     setup: 1041 zip: 813  2006-9-3
4.4         setup: 1318 zip: 1075 2006-5-11
3.3.3       setup: 1503 zip: 1145 2005-9-19
4.3.2 final setup: 409  zip: 222
4.3.1 final setup: 2168 zip: 1781
4.3 final   setup: 942  zip: 686
4.2.1 final setup: 413  zip: 490
4.2-final   setup: 1828 zip: 1508
4.2b3       setup: 563, zip: 338
4.1rc3      setup: 870  zip: 630
4.1 b5      setup: 195, zip: 128
4.0.4       setup: 340, zip: 385
4.0                     zip: 382
3.12        setup: 953  zip: 592
3.11                    zip: 102
3.10                    zip: 1193</t>
<t tx="EKR.20040519091259.2"></t>
<t tx="EKR.20040519091259.3">I like Leo more the more I use it...It's an unexpected pleasure to
see my (linearly written) code outlined in Leo. I can't wait to use
Leo to start a new project, going from outline to code...Thanks again
for providing the computing community with such a fine piece of
software. -- Jim Shapiro, Ph.D.

If you think you have used all possible programmer's editors, but
have not yet tried Leo, you are wrong...I rate Leo as a "must have"
for Python programmers. The code makes for a good read.
-- John Tobler  http://weblogs.asp.net/Jtobler/
</t>
<t tx="EKR.20040519091259.4">I've written documentation in WordPerfert, Ventura, Word, PageMaker, and
FrameMaker and even though they create wonderfully looking and useful
documents, they've never been able to do what I've been looking for. HTML,
compiled help files, and later PDF came closer, but still not there. I think
I've found it in LEO, a way to make a "living" document. A document built out
of discrete parts that can be re-organized on the fly to meet the needs of a
varying audience...Being a convert for less than a day I've still got a lot to
learn, but just the possibility of keeping system maintenance scripts in the IT
manual is mind boggling.  -- David Nichols dnichols@amci.com</t>
<t tx="ekr.20040630210818">HTML Editing in Leo is soooo much easier then with NoNodeEditors. Ive
had a blast working on a web page. Usually I had to look at a bunch of
gunk all at once. Now I can look at little pieces of gunk! :) 

-Anon (for now)

Before leo, I try to avoid or refactor long functions. With leo, I am
very tempted not to. Being able to view and slice my code at a higher
level in pretty much anyway I want, I feel like a commanding master in
my own mess...Leo lets me be lazy and get away with it. ;)

Mark Ng

[Quote] I have just finished a little embedded system for someone, written in
C using leo as the editor. I told the customer he _had_ to use leo for
ongoing maintenance, after I looked at one of the main state machines:
600 lines in the derived file, but trivialy easy to get your head
around in Leo...

The good news is that having been forced to meet leo he thinks it'll
solve many other problems that his company has with code maintenance.
Another step to world domination!

Leo allows you to do things that you'd never consider with another editor. 

BTW: in a real-time embedded system like I was working on, not having
the overhead of a function call (which you'd have had if you'd split
the case statement as you would with a normal editor) saves time, and
makes the system more flexible...
[End Quote]</t>
<t tx="ekr.20040828084148">Leo is the best IDE that I have had the pleasure to use. I have been using it
now for about 2 -- 3 months. It has totally changed not only the way that I
program, but also the way that I store and organise all of the information that
I need for the job that I do. -- Ian Mulvany</t>
<t tx="ekr.20050315084904"></t>
<t tx="ekr.20050315084922">c.spellCommands.openSpellTab()</t>
<t tx="ekr.20060213160806">"Thanks for a wonderful program – everybody should be using it! It blows the
socks off that Java Mind mapping software that won project of the month a while
back on sourceforge!" -- Derick van Niekerk.
</t>
<t tx="ekr.20060823090437">Thanks for creating the most useful and amazing application that
I've come across in years. I use Leo every day.</t>
<t tx="ekr.20070101093904">Leo is THE BEST THING to ever had happened to me. I've done in two
weeks what would have taken me years (not exaggerating!). Thanks Ed
for a terrific tool!!!!
 
Julian S. Fecteau 
</t>
<t tx="ekr.20070325123540"></t>
<t tx="ekr.20070425092712">Leo--especially with its feature of user-controllable outlining and
overview __has for the last 4-5 years had the greatest positive effect
on my overall programming quality of life than anything else out there
in the software world (apart maybe from the Python language itself,
and those who contribute Python modules to the world). -- David McNab
</t>
<t tx="ekr.20080825083632.262">Python's HOME environment variable specifies Leo's HOME directory.
See http://docs.python.org/lib/os-procinfo.html for details.

Leo puts several files in your HOME/.leo directory:
.leoID.txt, .leoRecentFiles.txt, and myLeoSettings.leo.
There are various fallback directories if there is no home directory.
</t>
<t tx="ekr.20080825083632.263">
Running Leo
-----------

You can run Leo from a Python interpreter as follows::

    import leo
    leo.run() # runs Leo, opening a new outline or,
    leo.run(fileName=aFileName) # runs Leo, opening the given file name.

Another way to run Leo is as follows::

    cd &lt;path-to-launchLeo.py&gt;
    python launchLeo.py

Here are some tips that may make running Leo easier:

**Linux**
    The following shell script will allow you to open foo.leo files by typing leo foo::

        #!/bin/sh 
        python &lt;leopath&gt;launchLeo.py $1

    where &lt;leopath&gt; is the path to the directory *containing* the leo directory. 

**Windows**
    If you have `associated .leo files with Leo`_ you may run Leo by double-clicking any .leo file.
    You can also use a batch file.
    Put the following .bat file in c:\\Windows::

        cd &lt;path-to-leo&gt;
        c:\python25\python &lt;path-to-leo&gt;launchLeo.py %1

    where &lt;path-to-leo&gt; is the path to the directory *containing* the leo directory.

    This opens the file specified by the first argument (%1).

The first time you start Leo, a dialog will ask you for a unique identifier. If
you are using cvs, use your cvs login name. Otherwise your initials will do. Leo
stores this identifier in the file ``.leoID.txt``. Leo attempts to create
``leoID.txt`` in the .leo sub-directory of your home directory, then in Leo's config directory, and
finally in Leo's core directory. You can change this identifier at any time by
editing ``.leoID.txt``.</t>
<t tx="ekr.20080901114425.2">For me Squeak and Leo have been two of the most significant technologies to
redefine my personal computer experience and the ideas behind computing.</t>
<t tx="ekr.20090901092556.1576">def genUninstallData(self,dirs,dirDict,filesDict):

    '''Generate the manifest-specific uninstall data.'''

    trace = True

    s = r'''
Section Uninstall

    DeleteRegKey HKEY_LOCAL_MACHINE "${hkey_local_machine}"

    ; Delete files &amp; directories only if we own them!
    ReadRegStr $$1 HKCR "${ext}" ""
    StrCmp $$1 "${name}File" 0 FinishUninstall

    ; Delete files &amp; directories only if there is no backup_val key.
    ReadRegStr $$1 HKCR "${ext}" "backup_val"
    StrCmp $$1 "" 0 DeleteLeoKeysAndFiles
      DeleteRegKey HKCR "${ext}"
    Goto FinishUninstall

DeleteLeoKeysAndFiles:
    WriteRegStr HKCR "${ext}" "" $$1
    DeleteRegValue HKCR "${ext}" "backup_val"

    ; ---- Start of manifest-related data...
'''

    self.put(s,substitute=True)

    # Does all the hard work.
    s = self.getUninstallVariableData(dirs,dirDict,filesDict)
    if trace: g.trace('\n',s)
    self.put(s,adjust = False)

    s = r'''
    ; ---- End of manifest related data.

FinishUninstall:
    ; MessageBox MB_YESNO|MB_ICONQUESTION \
    ;    "Delete all files in ${INSTDIR}?" IDNO NoDelete
; NoDelete:

  Delete "${SMPROGRAMS}\${name}\Uninstall.lnk"
  RMDir "${SMPROGRAMS}\${name}-${version}"
  Delete "${DESKTOP}\${name}.lnk"

  DeleteRegKey ${uninst_root_key} "${uninst_key}"
  SetAutoClose false

; end Uninstall section
SectionEnd
'''

    self.put(s,substitute=True)
</t>
<t tx="ekr.20090901121423.1567">def getUninstallVariableData(self,dirs,dirDict,filesDict):

    s1 = self.getDeleteFiles(dirs,dirDict,filesDict)
    s2 = self.getDeleteDirectories(dirs,dirDict)
    return '%s\n%s' % (s1,s2)
</t>
<t tx="ekr.20090901121423.1568">def getDeleteDirectories (self,dirs,dirDict):

    reverseDirs = dirs[:]
    reverseDirs.reverse()

    result = []

    if 1:
        result.append('; Recursively delete the leo directory and everything in it.\n')
        result.append('RMDir /r "$INSTDIR\\leo"\n\n')
    else:
        result.append('; Uninstall directories in reverse order\n')
        for theDir in reverseDirs:
            # Delete the directory even if it has files.
            if theDir and theDir != '**top':
                if not theDir.startswith('.bzr'):
                    result.append('RMDir "$INSTDIR\\%s"\n' % (
                        theDir.replace('/','\\')))

    # top-level folder.
    result.append('; Delete the top-level directory.\n')
    result.append('RMDir "$INSTDIR"\n')

    result = [self.indent(z) for z in result]
    return ''.join(result)
</t>
<t tx="ekr.20090901121423.1569">def getDeleteFiles (self,dirs,dirDict,filesDict):

    result = []
    result.append('\n')
    result.append('; Uninstall files...\n\n')

    # top-level files.
    result.append('; Delete top-level files...\n')
    aList = dirDict.get('**top',[])
    # Add *.py, *.pyo, *.pyc and *.leo, the most common added files.
    if 0: # This seems way too drastic, and not needed.
        for fn in ('*.py','*.pyo','*.pyc','*.leo',):
            aList.append(fn)
    # special case.
    aList.append('uninst.exe')
    # Warning: **never** delete all files in the top-level directory.
    for fn in aList:
        result.append('Delete "$INSTDIR\\%s"\n' % fn)

    if 0:
        wildcard_delete = True
        if wildcard_delete:
            result.append('\n')
        # Use the \r option to recursively delete everything in the leo directory.

        for theDir in dirs:
            if theDir:
                dir2 = theDir.replace('/','\\')
                if wildcard_delete:
                    result.append('Delete "$INSTDIR\\%s\\*.*"\n' % (dir2))
                else:
                    aList = dirDict.get(theDir,[])
                    if aList:
                        result.append('\n')
                        result.append('Delete "$INSTDIR\\%s\\*.pyc"\n' % (dir2))
                        result.append('Delete "$INSTDIR\\%s\\*.pyo"\n' % (dir2))
                    for fn in aList:
                        result.append('Delete "$INSTDIR\\%s\\%s"\n' % (
                            dir2,fn))

    result = [self.indent(z) for z in result]
    return ''.join(result)
</t>
<t tx="ekr.20090905082405.1486">'''Create leo.zip using bzr export'''

# To do: Leo bitmap.

&lt;&lt; includes &gt;&gt;

version = '4.8-b1' ##version

@others

abspath,exists,join = g.os_path_abspath,g.os_path_exists,g.os_path_join

root = join('Lib','site-packages','Leo-%s' % (version)) # Don't use abspath!
docDir  = abspath(join(g.app.loadDir,'..','doc'))
top     = abspath(join(g.app.loadDir,'..','..'))
zipFile = abspath(join(top,'Leo-%s.zip' % (version)))
zipFile2= abspath(join(top,'Leo-%s-temp.zip' % (version)))

make()

g.es_print('@button make-leo-zip: done')
</t>
<t tx="ekr.20090905082405.1487">import os
import shutil
import struct
import sys
import time</t>
<t tx="ekr.20090905082405.1489">def make():

    # Make the manifest.
    commands = (
        r'cd %s' % (top),
        r'bzr ls -R &gt;bzr-manifest.txt'
    )

    for z in commands:
        print ('command: %s' % z)
        os.system(z)

    # Copy files from the doc directory to the top directory.
    if 0: # No longer needed: these are in the root directory.
        for theFile in ('PKG-INFO.TXT','INSTALL.TXT','README.TXT',):
            src_path= abspath(join(docDir,theFile))
            dst_path= abspath(join(top,theFile))
            if g.os_path_exists(src_path):
                shutil.copyfile(src_path,dst_path)
                assert g.os_path_exists(dst_path)
                g.es_print('created in %s: %s' % (top,theFile))
            else:
                error('not found: %s' % src_path)
                return

    for z in (zipFile,zipFile2):
        if exists(z): unlink(z)

    commands = (
        r'cd %s' % (top),
        r'bzr status',
        # This commit ensures the proper files are included in the distribution.
        # r'bzr commit -m "commit doc files during make"',
        r'bzr status',
        r'bzr export "%s"' % (zipFile),
        r'bzr export --root="%s" "%s"' % (root,zipFile2),
    )

    for z in commands:
        print ('command: %s' % z)
        os.system(z)

    # Unlink temp files.
    unlink(zipFile2)
    if 0: # Don't unlink these!
        for z in ('PKG-INFO.TXT','INSTALL.TXT','README.TXT',):
            path= abspath(join(top,z))
            if exists(z): unlink(z)

    os.system('dir %s' % (top))
</t>
<t tx="ekr.20090905082405.1490">def unlink (fileName):

    print ('removing: %s' % fileName)
    os.remove(fileName)
</t>
<t tx="ekr.20100202061222.1494">@nocolor-node

Testing:
    - Run all unit tests.
    - Run pylint-leo.bat.
LeoDocs.leo:
    **Update version on home page.
    - Remove top-level clones.
    - Select the readme node.
LeoPlugins.leo:
    - Remove top-level clones.
LeoPy.leo:
    - Update version numbers.
LeoDist.leo:
    - Make sure copyright dates are correct.
        (trunk/license.txt **and** leo/doc/license.txt.)
    - Update version numbers: search this file for ##version.
    - Update readme.txt
    - Check 'INSTALL.TXT'
    - Check 'PKG-INFO.TXT'
Create the manifest:
    - Delete old distribution (.exe,.zip) files.
    - Create the manifest: bzr ls -R &gt;bzr-manifest.txt
    - review bzr-manifest file: remove .~?~ files.
Create a bzr tag:
    - bzr tag leo-x-y
    - bzr commit --unchanged -m "added tag"
    - bzr push
Create distribution files using to @button make scripts in leoDist.leo
    - 1: Make leo.nsi
    - 2: Create the installer:
        - Choose leo.nsi in Windows Explorer and select "Compile NSI Script"
        - or just double-click leo.nsi.
    - 3: Make leo.zip (use the button)
Test files
	- test the files created in c:\Python\Lib\site-packages\leo-x-y folder
    ** Open unitTest.leo: does it open without errors?
    ** Open leoPlugins.leo: does it open without errors?
    - Run all unit tests in the installed folder, with the installed Leo.

@color
# **** Scan all folders &amp; files before uploading.
@nocolor

Create Release on SourceForge:
    https://sourceforge.net/project/admin/explorer.php?group_id=3458

Announcements
- Update version number on Leo's wikipedia site:
    http://en.wikipedia.org/wiki/Leo_(editor)
    - Edit with the 'Edit this page' *tab* (not a link)
- Update version number on web site.
- Announce to SourceForge itself.
- Announce to leo-editor.
- Announce to comp.lang.python (use Forte Agent)
- Register Leo at http://www.python.org/pypi?:action=submit_form</t>
<t tx="ekr.20101025095431.1517">@nocolor-node

To do:
    There is a problem with the desktop shortcut.
    Make the License look better.  It can be an .rtf file.
    Add description sections.

Done:
** Switched to new interface: it is *much* better.
- Test desktop shortcut.  It opens Python 2.6 as expected.
- Make sure the uninstaller gets deleted.
</t>
<t tx="ekr.20101025095431.1518">@nocolor-node

On Sun, Oct 17, 2010 at 12:04 PM, David Szent-Györgyi
&lt;514656@bugs.launchpad.net&gt; wrote:

Perhaps changing the current working directory away from the installation
directory before applying the NSIS RMDir command to the installation directory
would work.

If not, use the /REBOOTOK option of the RmDir command to force
deletion of the installation folder on the next reboot.

Both these techniques are described at
http://nsis.sourceforge.net/Docs/Chapter4.html#4.9.1.8
</t>
<t tx="ekr.20101026142031.1516">@nocolor-node

HKEY_CURRENT_USER\Software\Classes\Applications\python.exe
HKEY_CURRENT_USER\Software\Classes\Applications\python.exe\shell\open\command
    val = c:\Python26\python.exe %1
HKCU
HKEY_CURRENT_USER\Software\Classes\Applications\pythonw.exe
HKEY_CURRENT_USER\Software\Classes\Applications\pythonw.exe\shell\open\command
    val = c:\Python26\pythonw.exe %1

HKEY_CURRENT_USER\Software\Classes\Applications\py_auto_file\shell\open\command
    val = c:\Python26\python.exe %1
    
HKEY_CURRENT_USER\Software\Classes\Installer\Products\nnnnnn

HKLM
HKEY_LOCAL_MACHINE\SOFTWARE\Python
HKEY_LOCAL_MACHINE\SOFTWARE\Python\PythonCore
HKEY_LOCAL_MACHINE\SOFTWARE\Python\PythonCore\2.7\InstallPath
    val = c:\python27\
HKEY_LOCAL_MACHINE\SOFTWARE\Python\PythonPath
    val = c:\Python27\Lib;\Python27\DLLs;C:\Python27\Lib\lib-tk
</t>
<t tx="ekr.20101027070126.1639">'''Use bzr-manifest.txt to two "helper" files for leo.nsi:

        leo\dist\nsi-install-files.txt
        leo\dist\nsi-uninstall-files.txt
'''

# **Important**: create bzr-manifest **before** running this script::
#       cd to trunk
#       bzr ls -R &gt;bzr-manifest.txt


import os,string,sys

# Globals...
join = g.os_path_finalize_join
rootDir  = join(g.app.loadDir,'..','..')
distDir =  join(g.app.loadDir,'..','dist')
manifest = join(rootDir,'bzr-manifest.txt')
install_fn   = join(distDir,'nsi-install-files.txt')
uninstall_fn = join(distDir,'nsi-uninstall-files.txt')

assert g.os_path_exists(manifest)

@others

nsi = nsiWriter()
nsi.run(manifest)
g.es_print('@button make-leo-nsi done')
</t>
<t tx="ekr.20101027070126.1643">class nsiWriter:

    '''
    A class to write two "helper" files for leo.nsi:

        leo\dist\nsi-install-files.txt
        leo\dist\nsi-uninstall-files.txt

    These are the only files that depend on the bzr manifest.
    '''

    @others
</t>
<t tx="ekr.20101027070126.1662">def run (self,mainifest_fn):

    '''The top-level logic.'''

    # Create and filter the list of files from the manifest.
    s = open(mainifest_fn).read()
    lines = g.splitLines(s)
    files = self.filterLines(lines)

    # Compute the list of all the directories.
    dirs = self.directoryList(rootDir)

    # Compute dictionaries of directories and files.
    dirDict,filesDict = self.makeDicts(dirs,files)

    # Print manifest lines not in either dict.
    # This is a crucial check.
    errors = self.printMissing(files,dirDict,filesDict)
    if not errors:
        self.create_install_files(dirs,dirDict,filesDict)
        self.create_uninstall_files(dirs,dirDict,filesDict)
</t>
<t tx="ekr.20101027070126.1663">def directoryList (self,rootDir):

    '''Compute a top-down list of all directories.
       These directories start at the top-level directory.'''

    trace = False
    ignoreDirs = ('.bzr',)
    # Important: this adds all directories on EKR's machine,
    # regardless of whether they appear in the manifest!
    result = [] ; n = len(rootDir)
    for z in os.walk(rootDir): # top-down traversal.
        dirpath, dirnames, filenames = z
        assert dirpath.startswith(rootDir),z
        if len(dirpath) &gt; n:
            path = dirpath[n+1:].replace('\\','/')
            result.append(path)
    for z2 in ignoreDirs:
        result = [ z for z in result if not z.startswith(z2)]
    if trace:
        g.trace('-' * 40)
        g.trace(g.listToString(result))
    return result
</t>
<t tx="ekr.20101027070126.1664">def filterLines (self,lines):

    '''Filter lines from the input manifest file.'''

    trace = False

    # Remove blank lines, comments, and .pyc and .pyo files.
    lines = self.deleteBlankLines(lines)
    lines = self.deleteComments(lines)
    lines = self.deleteExt(lines,'.pyc')
    lines = self.deleteExt(lines,'.pyo')
    lines = self.deleteExt(lines,'.zip') # Don't include the zip file.
    lines = self.deleteExt(lines,'.exe') # Don't include the installer.

    # Remove specific files.
    deleteList = (
        '.bzrignore',
        'bzr-manifest.txt',
        'bzr-small-manifest.txt',
        'setup.py',
        'leo/test/unittest/.leo_shadow/',
        'nsi.log.txt', # Can't write log while we are creating it.
        'leo/core/leoPy.leo',
        'leo/core/ekrLeoPy.leo',
    )
    lines = self.deleteFiles(lines,deleteList)
    if lines and lines[0].endswith('bzr ls -R'):
        lines = lines[1:]

    if trace:
        g.trace('=' * 40)
        g.trace(g.listToString(lines))

    return lines
</t>
<t tx="ekr.20101027070126.1665">def deleteBlankLines (self,lines):

    return [z.strip() for z in lines if z.strip()]

def deleteComments (self,lines):

    return [z for z in lines if not z.startswith('#')]

def deleteExt (self,lines,ext):

    return [z for z in lines if not z.endswith(ext)]

def deleteFiles (self,lines,deleteList):

    return [z for z in lines if not z in deleteList]
</t>
<t tx="ekr.20101027070126.1666">def makeDicts (self,dirs,lines):

    trace = False ; verbose = False

    # Create the dirDict.
    # Keys are directories.
    # Values are files contained in each directory.
    dirDict = {}
    dirDict['**top'] = [] # Create an entry for the root directory.
    for z in dirs:
        dirDict[z] = []

    # Assign files to dirDict.
    for line in lines:
        line = line.strip().replace('\\','/')
        if line in dirDict.keys():
            path,fn = None,None
        elif line.startswith('leo/'):
            path,fn = g.os_path_split(line)
        else:
            path,fn = '**top',line.strip()

        # Don't include top-level leo directory,
        # Do include leo/scripts/leo file.
        if fn and (path != '**top**' or fn != 'leo'):
            aList = dirDict.get(path,[])
            assert line not in aList,repr(line)
            aList.append(fn)
            dirDict[path]=aList

    for theDir in sorted(dirDict):
        aList = dirDict.get(theDir)
        if aList and trace:
            if verbose:
                print() ; print(theDir)
                print(g.listToString(aList))
            else:
                print(theDir)

    # Create the inverse dict.
    filesDict = {}
    for theDir in sorted(dirDict):
        aList = dirDict.get(theDir)
        for fn in aList:
            path = g.choose(theDir=='**top',
                fn,'%s/%s' % (theDir,fn))
            filesDict[path] = theDir

    return dirDict,filesDict
</t>
<t tx="ekr.20101027070126.1667">def printMissing (self,files,dirDict,filesDict):

    errors = 0

    for fn in files:
        fn = fn.rstrip('/')
        if fn and fn not in dirDict and fn not in filesDict:
            g.es_print('missing',fn,color='red')
            errors += 1

    if errors:
        g.es_print('%s errors' % (errors),color='red')

    return errors
</t>
<t tx="ekr.20101027070126.1675">def create_install_files(self,dirs,dirDict,filesDict):

    global install_fn,rootDir
    put = self.put

    self.f = self.openFile(install_fn)
    if not self.f: return

    # Top level
    theDir = '**top'
    put('\n')
    put('; top-level\n')
    put('SetOutPath "$INSTDIR"\n')
    put('SetOverwrite ifnewer\n')
    aList = dirDict.get(theDir,[])
    for fn in aList:
        put('File "%s"\n' % fn)

    for theDir in dirs:
        if theDir != '**top':
            aList = dirDict.get(theDir,[])
            if aList:
                theDir2 = theDir.replace('/','\\').rstrip('\\')
                put('\n')
                put('SetOutPath $INSTDIR\\%s\n' % theDir2)
                for fn in aList:
                    # Fix bug 425369: quote file names.
                    put('File "%s\\%s\\%s"\n' % (
                        rootDir,theDir2,fn))

    self.f.close()
</t>
<t tx="ekr.20101027070126.1676">def create_uninstall_files(self,dirs,dirDict,filesDict):

    def clean(s):
        return s.replace('/','\\')
    put = self.put

    self.f = self.openFile(uninstall_fn)
    if not self.f: return

    # Part 1: Delete top-level files.
    put('\n')
    put('; Uninstall files...\n\n')

    put('SetOutPath $Temp\n')

    # Get the list of top-level files.
    aList = dirDict.get('**top',[])

    # Add some special cases:
    for fn in ('*.pyo','*.pyc',
        'uninst.exe','setup.py','bzr-manifest.txt',
    ):
        if fn not in aList:
            aList.append(fn)

    for fn in aList:
        # Always delete individual files.
        put('Delete "$INSTDIR\\%s"\n' % fn)

    # Part 2: Delete files in lower directories.
    for theDir in dirs:
        if theDir:
            dir2 = clean(theDir)
            aList = dirDict.get(theDir,[])
            if aList:
                put('\n')
                put('Delete "$INSTDIR\\%s\\*.pyc"\n' % (dir2))
                put('Delete "$INSTDIR\\%s\\*.pyo"\n' % (dir2))
            for fn in aList:
                put('Delete "$INSTDIR\\%s\\%s"\n' % (dir2,fn))

    # Part 3: Delete directories.
    reverseDirs = dirs[:]
    reverseDirs.reverse()
    put('\n')
    put('; Uninstall directories in reverse order\n')
    for theDir in reverseDirs:
        # Delete the directory even if it has files.
        if theDir and theDir != '**top':
            if not theDir.startswith('.bzr'):
                put('RMDir "$INSTDIR\\%s"\n' % (clean(theDir)))

    # Delete the op-level folder.
    put('\n')
    put('; Delete the top-level directory.\n')
    put('RMDir "$INSTDIR"\n')

    self.f.close()
</t>
<t tx="ekr.20101027070126.1678">def put (self,s):

    self.f.write(s)
</t>
<t tx="ekr.20101027070126.1679">def openFile (self,fn):

    try:
        f = open(fn,'w')
        return f
    except IOError:
        g.error('can not open',fn)
        return None
</t>
<t tx="ekr.20101027070126.1680"></t>
<t tx="ekr.20101027131034.1490">@color</t>
<t tx="ekr.20101027135430.1492">http://nsis.sourceforge.net/Docs/Modern%20UI%202/Readme.html</t>
<t tx="ekr.20101027135430.1493">http://nsis.sourceforge.net/Docs/Chapter4.html#4.5</t>
<t tx="ekr.20101027160251.1497">http://nsis.sourceforge.net/Docs/nsDialogs/Readme.html</t>
<t tx="ekr.20101027160251.1500"></t>
<t tx="ekr.20101104090957.1488">Leo 4.8 beta 1                               November 8, 2010

Leo 4.8 beta 1 is now available at:
http://sourceforge.net/project/showfiles.php?group_id=3458&amp;package_id=29106

Leo is a text editor, data organizer, project manager and much more. See:
http://webpages.charter.net/edreamleo/intro.html

The highlights of Leo 4.8:
--------------------------

- Leo now uses the simplest possible sentinel lines in external files.
  External files with sentinels now look like Emacs org-mode files.
- Leo Qt gui now supports Drag and Drop.
  This was one of the most frequently requested features.
- Improved abbreviation commands.
  You now define abbreviations in Leo settings nodes, not external files.
- @url nodes may contain url's in body text.
  This allows headlines to contain summaries: very useful.
- Leo now uses PyEnchant to check spelling.
  Much safer than using aspell.
- Leo can now open multiple files from the command line.
- Leo's ancient Tangle and Untangle commands are now deprecated.
  This will help newbies how to learn Leo.
- Leo now shows "Resurrected" and "Recovered" nodes.
  These protect data and show how data have changed.
  These fix several long-standing data-related problems.
- A new "screenshots" plugin for creating slide shows with Leo.
  I used this plugin to create Leo's introductory slide shows.
- A better installer.
- Many bug fixes.

Links:
------
Leo:      http://webpages.charter.net/edreamleo/front.html
Forum:    http://groups.google.com/group/leo-editor
Download: http://sourceforge.net/project/showfiles.php?group_id=3458
Bzr:      http://code.launchpad.net/leo-editor/
Quotes:   http://webpages.charter.net/edreamleo/testimonials.html
</t>
<t tx="ekr.20101104090957.1489">def error (s):

    g.es_print('error: %s' % s,color='red')
</t>
</tnodes>
</leo_file>
