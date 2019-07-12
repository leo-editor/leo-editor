<?xml version="1.0" encoding="utf-8"?>
<!-- Created by Leo: http://leoeditor.com/leo_toc.html -->
<leo_file xmlns:leo="http://leoeditor.com/namespaces/leo-python-editor/1.1" >
<leo_header file_format="2"/>
<globals/>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="ekr.20070615131954"><vh>Startup</vh>
<v t="ekr.20150302053516.3"><vh>@settings</vh>
<v t="mhw.20181210131101.1"><vh>@bool put-expansion-bits-in-leo-files = False</vh></v>
</v>
<v t="ekr.20070427110751"><vh>@chapters</vh></v>
</v>
<v t="lkj.20190711235336.1"><vh>Readme</vh></v>
<v t="lkj.20190712001203.1"><vh>scripts</vh>
<v t="mhw-debug-1081.20190310203401.1"><vh>Windows</vh>
<v t="maphew.20130611235500.2658"><vh>@file register-leo.leox</vh></v>
<v t="maphew.20130611235500.2665"><vh>@file unregister-leo.leox</vh></v>
<v t="ekr.20140704052551.17941"><vh>Notes</vh>
<v t="maphew.20130510011223.1646"><vh>sample registry outcome</vh></v>
</v>
</v>
<v t="lkj.20190711232707.1"><vh>Linux</vh></v>
<v t="lkj.20190711232711.1"><vh>Mac</vh></v>
</v>
</vnodes>
<tnodes>
<t tx="ekr.20070427110751"></t>
<t tx="ekr.20070615131954"></t>
<t tx="ekr.20140704052551.17941">@language md

## Test for Leo association
If Leo files are not registered with Windows the following commands will return "not found" errors.

    reg query hkcr\leo.file
    reg query hkcr\.leo
    reg query hkcr\.leox


Example of success:

    C:\&gt; reg query hkcr\leo.file
    
    HKEY_CLASSES_ROOT\leo.file
        (Default)    REG_SZ    Leo Editor File
    
    HKEY_CLASSES_ROOT\leo.file\DefaultIcon
    HKEY_CLASSES_ROOT\leo.file\Shell</t>
<t tx="ekr.20150302053516.3"></t>
<t tx="lkj.20190711232707.1">{placeholder for future functions}</t>
<t tx="lkj.20190711232711.1">{placeholder for future functions}</t>
<t tx="lkj.20190711235336.1">Desktop integration buttons

[Register-leo] - Creates registry keys for Leo file type and .leo file association. Afterwards .leo files will show Leo icon and double-clicking them will open in Leo Editor.

[Unregister-leo] - Removes the above

</t>
<t tx="lkj.20190712001203.1"></t>
<t tx="maphew.20130510011223.1646">This is what the resulting registry key should look like, once exported from
regedit. The translated hex code for Open Command is:
    
    "d:\Python27\python.exe" "C:\Users\Matt\Dropbox\apps\leo-editor\launchLeo.py" "%1" %*


```
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\.leo]
@="Leo.File"

[HKEY_CLASSES_ROOT\.leox]
@="Leo.File"

[HKEY_CLASSES_ROOT\Leo.File]
@="Leo Editor File"

[HKEY_CLASSES_ROOT\Leo.File\DefaultIcon]
@="C:\\Users\\Matt\\Dropbox\\apps\\leo-editor\\leo\\Icons\\LeoDoc.ico"

[HKEY_CLASSES_ROOT\Leo.File\Shell]

[HKEY_CLASSES_ROOT\Leo.File\Shell\Open]

[HKEY_CLASSES_ROOT\Leo.File\Shell\Open\Command]
@=hex(2):22,00,64,00,3a,00,5c,00,50,00,79,00,74,00,68,00,6f,00,6e,00,32,00,37,\
  00,5c,00,70,00,79,00,74,00,68,00,6f,00,6e,00,2e,00,65,00,78,00,65,00,22,00,\
  20,00,22,00,43,00,3a,00,5c,00,55,00,73,00,65,00,72,00,73,00,5c,00,4d,00,61,\
  00,74,00,74,00,5c,00,44,00,72,00,6f,00,70,00,62,00,6f,00,78,00,5c,00,61,00,\
  70,00,70,00,73,00,5c,00,6c,00,65,00,6f,00,2d,00,65,00,64,00,69,00,74,00,6f,\
  00,72,00,5c,00,6c,00,61,00,75,00,6e,00,63,00,68,00,4c,00,65,00,6f,00,2e,00,\
  70,00,79,00,22,00,20,00,22,00,25,00,31,00,22,00,20,00,25,00,2a,00,00,00
```</t>
<t tx="mhw-debug-1081.20190310203401.1">Scripts only of interest when on Microsoft Windows platform.
@path win
</t>
<t tx="mhw.20181210131101.1">True (recommended):
    Write "E" attribute bits in &lt;v&gt; elements.
    Leo outlines will record the expansion state of all nodes.
    
False: (Good for files like unitTest.leo)
    Suppress "E" attribute bits in &lt;v&gt; elements.
    Only the ancestors of the presently selected node will
    be expanded when Leo opens an outline.</t>
</tnodes>
</leo_file>
