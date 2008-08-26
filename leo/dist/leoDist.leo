<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet ekr_test?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5">
	<global_window_position top="102" left="120" height="810" width="1093"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20050315084904" str_leo_pos="4"><vh>Startup</vh>
<v t="ekr.20070325123540"><vh>@chapters</vh></v>
<v t="ekr.20050315084922"><vh>@button Spell</vh></v>
</v>
<v t="EKR.20040519091259"><vh>Annoucements</vh>
<v t="EKR.20040519091259.1"><vh>Download statistics</vh></v>
<v t="EKR.20040519091259.2"><vh>Quotes of the month</vh>
<v t="ekr.20070425092712"><vh>April 2007</vh></v>
<v t="ekr.20070101093904"><vh>January 2007</vh></v>
<v t="ekr.20060823090437"><vh>August 2006</vh></v>
<v t="ekr.20060213160806"><vh>February 2005</vh></v>
<v t="ekr.20040828084148"><vh>August 2004</vh></v>
<v t="ekr.20040630210818"><vh>July 2004</vh></v>
<v t="EKR.20040519091259.3"><vh>November 2003</vh></v>
<v t="EKR.20040519091259.4"><vh>October 2003</vh></v>
</v>
<v t="ekr.20080825085446.1"><vh>ANN: Leo 4.5 b4</vh></v>
<v t="EKR.20040519091259.30"><vh>Previous announcements</vh>
<v t="ekr.20080807093308.2"><vh>4.5</vh>
<v t="ekr.20080628062747.73"><vh>ANN: Leo 4.5 b1</vh></v>
<v t="ekr.20080807093308.1"><vh>ANN: Leo 4.5 b2</vh></v>
<v t="ekr.20080815093141.108"><vh>ANN: Leo 4.5 b3</vh></v>
</v>
</v>
</v>
<v t="ekr.20080628065201.2"><vh>Distribution checklist</vh></v>
<v t="EKR.20040519090846" a="E"><vh>Distribution files</vh>
<v t="EKR.20040519090846.2"><vh>@asis ../doc/INSTALL.TXT</vh>
<v t="EKR.20040519090846.3"><vh>System requirements</vh></v>
<v t="ekr.20080825083632.262"><vh>Leo's HOME directory</vh></v>
<v t="EKR.20040519090846.4"><vh>Linux installation</vh></v>
<v t="EKR.20040519090846.5"><vh>Windows installation</vh></v>
<v t="EKR.20040519090846.6"><vh>MacOS installation</vh></v>
<v t="ekr.20080825083632.263"><vh>Running Leo</vh></v>
</v>
<v t="EKR.20040519090846.1"><vh>@asis ../doc/LICENSE.TXT</vh></v>
<v t="EKR.20040519090846.8"><vh>@asis ../doc/PKG-INFO.TXT</vh></v>
<v t="EKR.20040519090846.9"><vh>@asis ../doc/README.TXT</vh></v>
<v t="EKR.20040519082027.32"><vh>Linux install/uninstall scripts</vh>
<v t="EKR.20040519082027.33"><vh>@@file-thin ../../install</vh></v>
<v t="EKR.20040519082027.34"><vh>@@file-thin ../../uninstall</vh></v>
</v>
</v>
<v t="ekr.20080826091039.1"><vh>@button make</vh>
<v t="ekr.20080826091039.2"><vh>&lt;&lt; includes &gt;&gt;</vh></v>
<v t="ekr.20080826091039.3"><vh>remove</vh></v>
<v t="ekr.20080826091039.4" a="E"><vh>class createExe</vh>
<v t="ekr.20080826091039.5"><vh>ctor</vh></v>
<v t="ekr.20080826091039.6"><vh>create_exe</vh></v>
<v t="ekr.20080826091039.7"><vh>escape</vh></v>
<v t="ekr.20080826091039.8"><vh>get_exe_bytes</vh></v>
<v t="ekr.20080826091039.9"><vh>get_inidata</vh>
<v t="ekr.20080826091039.10"><vh>get_metaData</vh></v>
<v t="ekr.20080826091039.11"><vh>get_setup</vh></v>
</v>
<v t="ekr.20080826091039.12"><vh>get_python_version</vh></v>
</v>
</v>
</vnodes>
<tnodes>
<t tx="EKR.20040519082027.32">@color
@lineending nl
@language shell</t>
<t tx="EKR.20040519082027.33">@first #!/bin/sh

# This script installs Leo on *nix.
# Initial version by by Frank Merenda (fmerenda@yahoo.com)

# Variables...
LEO_PREFIX=${LEO_PREFIX:-/usr/local}
LEO_RUN_SCRIPT_OUTPUT="${LEO_PREFIX}/bin/leo"

# Bug fix: 2008/4/8: replace /lib/leo by /lib.
LEO_LIB_DIR="${LEO_PREFIX}/lib"

echo ""
echo "Prefix directory set to \"$LEO_PREFIX\""

# Make the directory structure
if [ ! -d $LEO_LIB_DIR ] ; then
    echo ""
    echo Making directory structure $LEO_LIB_DIR

    RESULTS=`mkdir -p -m755 $LEO_LIB_DIR 2&gt;&amp;1`
    if [ $? -ne 0 ]; then
        echo Failure making directory $LEO_LIB_DIR!
        exit 1;
    fi
fi

if [ ! -d $LEO_PREFIX/bin ] ; then
    echo ""
    echo Making directory structure $LEO_PREFIX/bin
    RESULTS=`mkdir -p -m755 $LEO_PREFIX/bin 2&gt;&amp;1`
    if [ $? -ne 0 ]; then
        echo Failure making directory $LEO_PREFIX/bin!
        exit 1;
    fi
fi

# Copy the files
cp -rp leo $LEO_LIB_DIR

echo "python ${LEO_PREFIX}/lib/leo/core/runLeo.py \"$@\"" &gt; $LEO_RUN_SCRIPT_OUTPUT

RESULTS=`chmod 755 $LEO_RUN_SCRIPT_OUTPUT`   

echo ""
echo "Leo installed successfully"
echo "Make sure ${LEO_PREFIX}/bin is in your path then"
echo "type 'leo filename.leo' to use it."   
echo ""

exit 0;
</t>
<t tx="EKR.20040519082027.34">@first #!/bin/sh

# This script uninstalls Leo on Linux.
#
# Initial version by by Frank Merenda (fmerenda@yahoo.com)

# Variables...
LEO_PREFIX=${LEO_PREFIX:-/usr/local}
LEO_RUN_SCRIPT_OUTPUT="${LEO_PREFIX}/bin/leo"
LEO_LIB_DIR="${LEO_PREFIX}/lib/leo"

# Show the commands to remove Leo.
echo ""
echo "Prefix directory set to \"$LEO_PREFIX\""
echo ""
echo "To uninstall leo check the following \"rm\" commands"
echo "if they look ok execute them."
echo "
rm -fr $LEO_LIB_DIR
rm -f  $LEO_RUN_SCRIPT_OUTPUT
"
</t>
<t tx="EKR.20040519090846">@nocolor

Do a search and replace on this suffix.

Latest suffix:  -rc1


</t>
<t tx="EKR.20040519090846.1">Leo is Open Software and is distributed under the terms of the Python License.
The gist of the license is that Leo is absolutely free, even for commercial use
(including resale). There is no GNU-like "copyleft" restriction. The Open Source
Initiative board has voted to certify the Python license as Open Source. This
license is compatible with the GPL.

Copyright (c) 1997-2008 by Edward K. Ream. All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee is hereby granted, provided that
the above copyright notice appear in all copies and that both that copyright
notice and this permission notice appear in supporting documentation, and that
the names of Leo or Edward K. Ream not be used in advertising or publicity
pertaining to distribution of the software without specific, written prior
permission.

DISCLAIMER OF WARRANTIES

EDWARD K. REAM (REAM) SPECIFICALLY DISCLAIMS ALL WARRANTIES, EXPRESSED OR
IMPLIED, WITH RESPECT TO THIS COMPUTER SOFTWARE, INCLUDING BUT NOT LIMITED TO
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. IN
NO EVENT SHALL REAM BE LIABLE FOR ANY LOSS OF PROFIT OR ANY COMMERCIAL DAMAGE,
INCLUDING BUT NOT LIMITED TO SPECIAL, INCIDENTAL, CONSEQUENTIAL OR OTHER
DAMAGES.</t>
<t tx="EKR.20040519090846.2"></t>
<t tx="EKR.20040519090846.3">System requirements for leo.py
------------------------------

leo.py requires Python 2.2.1 or above and tcl/tk 8.4 or above.

	Download Python from http://python.org/ 
	Download tcl/Tk from http://tcl.activestate.com/software/tcltk/

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
Installing the leo.py on Windows
--------------------------------

Leo is distributed either as an executable installer (.exe) file or as a .zip file.

To install Leo using the executable installer:

    1. Download the latest version of Leo's installer from:    
       http://sourceforge.net/project/showfiles.php?group_id=3458&amp;package_id=29106
       The installer will be called something like LeoSetup-4-4-3.exe.

    2. Run the installer.
       By default, the install will install Leo in your 'Program Files' directory.

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

5) Run Leo by ontrol-clicking on /path_to_unzipped_dir/leo/core/leo.py and open
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
Version: 4.5-rc1
Summary: Leo: Literate Editor with Outlines
Home-page: http://webpages.charter.net/edreamleo/front.html
Author: Edward K. Ream
Author-email: edreamleo@charter.net
License: Python
Description: Leo is an outline-oriented editor written in 100% pure Python.
		Leo works on any platform that supports Python 2.2.1 and Tk 8.4 or above.
		You may download Python from http://python.org/ and
		tcl/Tk from http://tcl.activestate.com/software/tcltk/
		Leo features a multi-window outlining editor, Python colorizing,
		powerful outline commands and many other things, including 
		Unlimited Undo/Redo and an integrated Python shell(IDLE) window.
		Leo will place its own icon in Leo windows provided that you have
		installed Fredrik Lundh's PIL and tkIcon packages:
		Download PIL from http://www.pythonware.com/downloads/index.htm#pil
		Download tkIcon from http://www.effbot.org/downloads/#tkIcon
Platform: Windows, Linux, Macintosh
</t>
<t tx="EKR.20040519090846.9">Leo 4.5 beta 4                      August 25, 2008

Leo 4.5 beta 4 is now available at:
http://sourceforge.net/project/showfiles.php?group_id=3458&amp;package_id=29106

This beta 4 release will likely be the last release before Leo 4.5 final.

Leo 4.5 contains many important new features.  See below for details.

Leo is a text editor, data organizer, project manager and much more. See:
http://webpages.charter.net/edreamleo/intro.html

The highlights of Leo 4.5:
--------------------------

- Full support for @shadow files in Leo's core.
- Major improvements to Leo's key binding code.
- The beginning of usable vim-like bindings.
- uA's may now be associated with vnodes in @thin and @shadow files.
- Several magor reorganizations of Leo's code:
  including sax-based parsing, support for the Graph world (unified nodes),
  simplified drawing code.
- Leo is now an installable package.
- Prepared code to be ready for Python 3.0.
- Many small improvements and bug fixes.

Links:
------
Leo:      http://webpages.charter.net/edreamleo/front.html
Forum:    http://groups.google.com/group/leo-editor
Download: http://sourceforge.net/project/showfiles.php?group_id=3458
Bzr:      http://code.launchpad.net/leo-editor/
Quotes:   http://webpages.charter.net/edreamleo/testimonials.html</t>
<t tx="EKR.20040519091259">@pagewidth 70
@killcolor</t>
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
<t tx="EKR.20040519091259.30"></t>
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
<t tx="ekr.20080628062747.73">Leo 4.5 beta 1                      June 28, 2008

Leo 4.5 beta 1 is now available at:
http://sourceforge.net/project/showfiles.php?group_id=3458&amp;package_id=29106

Leo is a text editor, data organizer, project manager and much more. See:
http://webpages.charter.net/edreamleo/intro.html

The highlights of Leo 4.5:
--------------------------
- A major revision of Leo's node structures, compatible with so-called unified nodes.
- A major revision of Leo's key-handling code.  Most per-pane key bindings have been eliminated.
- A major revision of Leo's outline drawing and focus handling code.
  Calls to c.beginUpdate and c.endUpdate simply request later redrawing in c.outerUpdate.
- The beginning of usable vim-like bindings.  More support is coming.
- Many small improvements and bug fixes.

Links:
------
Leo:      http://webpages.charter.net/edreamleo/front.html
Forum:    http://groups.google.com/group/leo-editor
Download: http://sourceforge.net/project/showfiles.php?group_id=3458
Bzr:      http://code.launchpad.net/leo-editor/
Quotes:   http://webpages.charter.net/edreamleo/testimonials.html</t>
<t tx="ekr.20080628065201.2">Testing:
    - Run all unit tests.
    - Run pylint-leo.bat.
LeoDocs.leo:
    - Remove top-level clones.
    - Select the readme node.
LeoPlugins.leo:
    - Remove top-level clones.
LeoPy.leo:
    - Update version numbers.
LeoDist.leo:
    - Update version numbers.
    - Update announcement.
    - Update readme.txt
Create a cvs tag:
    - bzr tag leo-x-y
    - bzr commit --unchanged -m "added tag"
    - bzr push
Create distribution files using @button make in leoDist.leo
Test files
	- Test created leosetup.exe file.
	- test the files created in c:\Python\Lib\site-packages\leo-x-y folder
    ** Open unitTest.leo: does it open without errors?
    ** Open leoPlugins.leo: does it open without errors?

@color
# **** Scan all folders &amp; files before uploading.
@nocolor

Create Release on SourceForge

*** FTP no longer supported.
*** Use: https://frs.sourceforge.net/webupload

Announcements
- Update version number on Leo's wikipedia site: http://en.wikipedia.org/wiki/Leo_(editor)
    - Edit with the 'Edit this page' *tab* (not a link)
- Update version number on web site.
- Announce to SourceForge itself.
- Announce to leo-editor.
- Announce to comp.lang.python
- Register Leo at http://www.python.org/pypi?:action=submit_form</t>
<t tx="ekr.20080807093308.1">Leo 4.5 beta 2                      August 7, 2008

Leo 4.5 beta 2 is now available at:
http://sourceforge.net/project/showfiles.php?group_id=3458&amp;package_id=29106

Leo 4.5 contains many important new features.  See below for details.

Leo is a text editor, data organizer, project manager and much more. See:
http://webpages.charter.net/edreamleo/intro.html

The highlights of Leo 4.5:
--------------------------

- Full support for @shadow files in Leo's core.
- Major improvements to Leo's key binding code.
- The beginning of usable vim-like bindings.
- uA's may now be associated with vnodes in @thin and @shadow files.
- Several magor reorganizations of Leo's code:
  including sax-based parsing, support for the Graph world (unified nodes),
  simplified drawing code.
- Leo is now an installable package.
- Prepared code to be ready for Python 3.0.
- Many small improvements and bug fixes.

Links:
------
Leo:      http://webpages.charter.net/edreamleo/front.html
Forum:    http://groups.google.com/group/leo-editor
Download: http://sourceforge.net/project/showfiles.php?group_id=3458
Bzr:      http://code.launchpad.net/leo-editor/
Quotes:   http://webpages.charter.net/edreamleo/testimonials.html</t>
<t tx="ekr.20080807093308.2"></t>
<t tx="ekr.20080815093141.108">Leo 4.5 beta 3                      August 15, 2008

Leo 4.5 beta 3 is now available at:
http://sourceforge.net/project/showfiles.php?group_id=3458&amp;package_id=29106

Leo 4.5 contains many important new features.  See below for details.

Leo is a text editor, data organizer, project manager and much more. See:
http://webpages.charter.net/edreamleo/intro.html

The highlights of Leo 4.5:
--------------------------

- Full support for @shadow files in Leo's core.
- Major improvements to Leo's key binding code.
- The beginning of usable vim-like bindings.
- uA's may now be associated with vnodes in @thin and @shadow files.
- Several magor reorganizations of Leo's code:
  including sax-based parsing, support for the Graph world (unified nodes),
  simplified drawing code.
- Leo is now an installable package.
- Prepared code to be ready for Python 3.0.
- Many small improvements and bug fixes.

Links:
------
Leo:      http://webpages.charter.net/edreamleo/front.html
Forum:    http://groups.google.com/group/leo-editor
Download: http://sourceforge.net/project/showfiles.php?group_id=3458
Bzr:      http://code.launchpad.net/leo-editor/
Quotes:   http://webpages.charter.net/edreamleo/testimonials.html</t>
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
        python &lt;leopath&gt;/leo/core/runLeo.py $1

    where &lt;leopath&gt; is the path to the directory containing the leo directory. 

**Windows**
    If you have `associated .leo files with Leo`_ you may run Leo by double-clicking any .leo file.
    You can also use a batch file.
    Put the following .bat file in c:\\Windows::

        cd &lt;path-to-leo&gt;
        c:\python25\python &lt;path-to-leo&gt;leo\core\runLeo.py %1

    where &lt;path-to-leo&gt; is the path to the directory containing the leo directory.

    This opens the file specified by the first argument (%1).

The first time you start Leo, a dialog will ask you for a unique identifier. If
you are using cvs, use your cvs login name. Otherwise your initials will do. Leo
stores this identifier in the file ``.leoID.txt``. Leo attempts to create
``leoID.txt`` in the .leo sub-directory of your home directory, then in Leo's config directory, and
finally in Leo's core directory. You can change this identifier at any time by
editing ``.leoID.txt``.</t>
<t tx="ekr.20080825085446.1">Leo 4.5 beta 4                      August 25, 2008

Leo 4.5 beta 4 is now available at:
http://sourceforge.net/project/showfiles.php?group_id=3458&amp;package_id=29106

This beta 4 release will likely be the last release before Leo 4.5 final.

Leo 4.5 contains many important new features.  See below for details.

Leo is a text editor, data organizer, project manager and much more. See:
http://webpages.charter.net/edreamleo/intro.html

The highlights of Leo 4.5:
--------------------------

- Full support for @shadow files in Leo's core.
- Major improvements to Leo's key binding code.
- The beginning of usable vim-like bindings.
- uA's may now be associated with vnodes in @thin and @shadow files.
- Several magor reorganizations of Leo's code:
  including sax-based parsing, support for the Graph world (unified nodes),
  simplified drawing code.
- Leo is now an installable package.
- Prepared code to be ready for Python 3.0.
- Many small improvements and bug fixes.

Links:
------
Leo:      http://webpages.charter.net/edreamleo/front.html
Forum:    http://groups.google.com/group/leo-editor
Download: http://sourceforge.net/project/showfiles.php?group_id=3458
Bzr:      http://code.launchpad.net/leo-editor/
Quotes:   http://webpages.charter.net/edreamleo/testimonials.html</t>
<t tx="ekr.20080826091039.1">'''Create a Windows .exe installer directly from a .zip file.
This code is based on create_exe in distutils/command/bdist_windinst.py.'''

# To do: require Python 2.5 when running this script.
# To do: post-install script to associate Leo with .leo files.
# To do: Leo bitmap.

&lt;&lt; includes &gt;&gt;
@others

version = '4-5-rc1'
abspath,exists,join = g.os_path_abspath,g.os_path_exists,g.os_path_join

docDir = abspath(join(g.app.loadDir,'..','doc'))
top = abspath(join(g.app.loadDir,'..','..'))
zipFile =  abspath(join(top,'Leo-%s.zip' % (version)))
zipFile2 = abspath(join(top,'Leo-%s-temp.zip' % (version)))
exeFile =  abspath(join(top,'Leo-%s.exe' % (version)))
root = join('Lib','site-packages','Leo-%s' % (version)) # Do not use abspath here!

# Copy files from the doc directory to the top directory.
for theFile in ('PKG-INFO.TXT','INSTALL.TXT','README.TXT',):
    path= abspath(join(docDir,theFile))
    shutil.copy(path,top)
    print('created in %s: %s' % (top,theFile))

if 1:
    for z in (zipFile,zipFile2,exeFile):
        if exists(z): remove(z)

    commands = (
        r'cd %s' % (top),
        r'bzr export "%s"' % (zipFile),
        r'bzr export --root="%s" "%s"' % (root,zipFile2),
    )

    for z in commands:
        print ('command: %s' % z)
        os.system(z)

    x = createExe(exeFile,zipFile2,version=version)
    x.create_exe()
    remove(zipFile2)
    os.system('dir %s' % (top))

print('done')
</t>
<t tx="ekr.20080826091039.2">import os
import shutil
import struct
import sys
import time</t>
<t tx="ekr.20080826091039.3">def remove (fileName):

    g.es_print('removing',fileName)
    os.remove(fileName)
</t>
<t tx="ekr.20080826091039.4">class createExe:

    @others
</t>
<t tx="ekr.20080826091039.5">def __init__ (self,exeFile,zipFile,version):

    self.exeFile = exeFile
    self.zipFile = zipFile
    self.theDir = g.os_path_dirname(zipFile)

    # The path to distutils.command
    self.distutils_command_path = r'C:\Python25\Lib\distutils\command'

    # Hard-code the meta-data.
    self.author = 'Edward K. Ream'
    self.author_email = 'edreamleo@gmail.com'
    self.description = "Leo: a programmer's editor, and more"
    self.long_description = ''
    self.maintainer = ''
    self.maintainer_email = ''
    self.name = 'Leo'
    self.url = 'http://webpages.charter.net/edreamleo/front.html'
    self.version = version

    # Hard-coded options from initialize options.
    self.no_target_compile = True
    self.no_target_optimize = True
    self.target_version = None # Require specific python version.
    self.bitmap = None # bitmap to use for the installer instead of python-powered logo
    self.title = 'Install Leo...' # title to display on the installer background instead of default
    self.install_script = None
        # basename of installation script to be run after installation or before deinstallation
    self.pre_install_script = None
        # Fully qualified filename of a script to be run before any files are installed.
        # This script need not be in the distribution
</t>
<t tx="ekr.20080826091039.6">def create_exe (self, bitmap=None): ### arcname, fullname, bitmap=None):

    cfgdata = self.get_inidata()

    g.es_print("creating %s" % self.exeFile)

    f = open(self.exeFile,"wb")
    f.write(self.get_exe_bytes())

    if bitmap:
        bitmapdata = open(bitmap, "rb").read()
        bitmaplen = len(bitmapdata)
        f.write(bitmapdata)
    else:
        bitmaplen = 0

    # Convert cfgdata from unicode to ascii, mbcs encoded
    if isinstance(cfgdata, unicode):
        cfgdata = cfgdata.encode("mbcs")

    # Append the pre-install script
    cfgdata = cfgdata + "\0"

    if self.pre_install_script:
        script_data = open(self.pre_install_script, "r").read()
        cfgdata = cfgdata + script_data + "\n\0"
    else:
        cfgdata = cfgdata + "\0"

    f.write(cfgdata)

    # The 'magic number' is used to make sure that the binary
    # layout of 'cfgdata' is what the wininst.exe binary expects.
    # If the layout changes, increment that number here and in
    # the wininst.exe sources, and recompile.
    header = struct.pack("&lt;iii",
        0x1234567B,       # Magic number.
        len(cfgdata),     # length
        bitmaplen,        # number of bytes in bitmap
    )
    f.write(header)

    # Now append the zip file(!!)
    f.write(open(self.zipFile, "rb").read())</t>
<t tx="ekr.20080826091039.7">def escape(self,s):

    return s.replace("\n", "\\n")
</t>
<t tx="ekr.20080826091039.8">def get_exe_bytes (self):

    from distutils.msvccompiler import get_build_version
    # If a target-version other than the current version has been
    # specified, then using the MSVC version from *this* build is no good.
    # Without actually finding and executing the target version and parsing
    # its sys.version, we just hard-code our knowledge of old versions.
    cur_version = self.get_python_version()

    if self.target_version and self.target_version != cur_version:
        # If the target version is *later* than us, then we assume they
        # use what we use.
        # string compares seem wrong, but are what sysconfig.py itself uses
        if self.target_version &gt; cur_version:
            bv = get_build_version()
        else:
            if self.target_version &lt; "2.4":
                bv = "6"
            else:
                bv = "7.1"
    else:
        # for current version - use authoritative check.
        bv = get_build_version()

    # wininst-x.y.exe is in the same directory as this file
    directory = self.distutils_command_path ## os.path.dirname(__file__)

    # we must use a wininst-x.y.exe built with the same C compiler
    # used for python.  XXX What about mingw, borland, and so on?
    filename = os.path.join(directory, "wininst-%s.exe" % bv)

    # g.es_print('reading %s' % filename)
    return open(filename, "rb").read()</t>
<t tx="ekr.20080826091039.9">def get_inidata (self):
    # Return data describing the installation.

    lines = []
    lines,info = self.get_metaData(lines)
    lines = self.get_setup(lines,info)

    result = '\n'.join(lines)
    # g.trace(result)

    return result
</t>
<t tx="ekr.20080826091039.10">def get_metaData(self,lines):

    '''Create the lines of the metadata section.'''

    lines.append("[metadata]")

    # 'info' will be displayed in the installer's dialog box.
    info = (self.long_description or '') + '\n'

    table = (
        "author", "author_email","description",
        "maintainer","maintainer_email",
        "name", "url", "version",)

    for ivar in table:
        data = self.escape(getattr(self,ivar))
        if data:
            info = info + ("\n    %s: %s" % (ivar.capitalize(), data))
            lines.append("%s=%s" % (ivar, data))

    return lines, info
</t>
<t tx="ekr.20080826091039.11">def get_setup (self,lines,info):

    '''Append the lines of the setup section.'''

    lines.append("\n[Setup]")

    if self.install_script:
        lines.append("install_script=%s" % self.install_script)

    lines.append("info=%s" % self.escape(info))
    lines.append("target_compile=%d" % (not self.no_target_compile))
    lines.append("target_optimize=%d" % (not self.no_target_optimize))

    if self.target_version:
        lines.append("target_version=%s" % self.target_version)

    lines.append("title=%s" % self.escape(self.title))

    build_info = "Built %s with ekr-script" % (time.ctime(time.time()))
    lines.append("build_info=%s" % build_info)

    return lines
</t>
<t tx="ekr.20080826091039.12">def get_python_version(self):

    """Return a string containing the major and minor Python version,
    leaving off the patchlevel.  Sample return values could be '1.5'
    or '2.2'.
    """
    return sys.version[:3]</t>
</tnodes>
</leo_file>
