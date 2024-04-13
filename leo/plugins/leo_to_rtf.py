#@+leo-ver=5-thin
#@+node:danr7.20060902083957: * @file ../plugins/leo_to_rtf.py
#@+<< docstring >>
#@+node:danr7.20060902085340: ** << docstring >> (leo_to_rtf.py)
r""" Outputs a Leo outline as a numbered list to an RTF file. The RTF file
can be loaded into Microsoft Word and formatted as a proper outline.

This plug-in loads installs an "Outline to Microsoft RTF" menu item in your
File > Export... menu in Leo.

Settings such as outputting just the headlines (vs. headlines & body text)
and whether to include or ignore the contents of @file nodes are stored in
the rtf_export.ini file in your Leo\plugins folder.

The default export path is also stored in the INI file. By default, it's
set to c:\ so you may need to modify it depending on your system.

"""
#@-<< docstring >>

# leoToRTF 1.0 plugin by Dan Rahmel
import configparser as ConfigParser
from leo.core import leoGlobals as g

#@+others
#@+node:ekr.20100128073941.5373: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    # Ok for unit testing: creates menu.
    g.registerHandler("create-optional-menus", createExportMenu)
    g.plugin_signon(__name__)
    return True
#@+node:danr7.20060902083957.2: ** createExportMenu (leo_to_rtf)
def createExportMenu(tag, keywords):

    c = keywords.get("c")
    if not c:
        return

    # Insert leoToRTF in #3 position of the File > Export menu.
    c.frame.menu.insert('Export...', 3,
        label='Outline to Microsoft RTF',
        command=lambda c=c: export_rtf(c))
#@+node:danr7.20060902083957.3: ** export_rtf
def export_rtf(c):
    # pylint: disable=line-too-long
    # Get user preferences from INI file
    fileName = g.os_path_join(g.app.loadDir, "..", "plugins", "leo_to_rtf.ini")
    config = ConfigParser.ConfigParser()
    config.read(fileName)
    flagIgnoreFiles = config.get("Main", "flagIgnoreFiles") == "Yes"
    flagJustHeadlines = config.get("Main", "flagJustHeadlines") == "Yes"
    # Prompt for the file name.
    fileName = g.app.gui.runSaveFileDialog(c,
        title="Export to RTF",
        filetypes=[("RTF files", "*.rtf")],
        defaultextension=".rtf")
    if fileName:
        f = open(fileName, 'w')
    else:
        return
    # Write RTF header information
    f.write("{\\rtf1\\ansi\\ansicpg1252\\deff0\\deflang1033{\\fonttbl{\\f0\\fswiss\\fcharset0 Arial;}}\n\n")
    # Write RTF list table that provides numbered list formatting
    #@+<< listtable >>
    #@+node:danr7.20060902085826: *3* << listtable >>
    #@@wrap

    f.write("{\\*\\listtable{\\list\\listtemplateid1723346216\\listhybrid\n")

    f.write("{\\listlevel\\levelnfc0\\levelnfcn0\\leveljc0\\leveljcn0\\levelfollow0\\levelstartat1\\levelspace360\\levelindent0\n")  # NOQA
    f.write("{\\leveltext\\leveltemplateid67698703\\\'02\\\'00.;}\n\n")
    f.write("{\\levelnumbers\\\'01;}\\chbrdr\\brdrnone\\brdrcf1 \\chshdng0\\chcfpat1\\chcbpat1 \\fi-360\\li720\\jclisttab\\tx720 }")  # NOQA

    f.write("{\\listlevel\\levelnfc4\\levelnfcn4\\leveljc0\\leveljcn0\\levelfollow0\\levelstartat1\\levelspace360\\levelindent0")  # NOQA
    f.write("{\\leveltext\\leveltemplateid67698713\\\'02\\\'01.;} {\\levelnumbers\\\'01;}")
    f.write("\\chbrdr\\brdrnone\\brdrcf1 \\chshdng0\\chcfpat1\\chcbpat1 \\fi-360\\li1440\\jclisttab\\tx1440 }")  # NOQA

    f.write("{\\listlevel\\levelnfc2\\levelnfcn2\\leveljc2\\leveljcn2\\levelfollow0\\levelstartat1\\levelspace360\\levelindent0")  # NOQA
    f.write("{\\leveltext\\leveltemplateid67698715\\\'02\\\'02.;} {\\levelnumbers\\\'01;}")
    f.write("\\chbrdr\\brdrnone\\brdrcf1 \\chshdng0\\chcfpat1\\chcbpat1\\fi-180\\li2160\\jclisttab\\tx2160 }")

    f.write("{\\listlevel\\levelnfc0\\levelnfcn0\\leveljc0\\leveljcn0\\levelfollow0\\levelstartat1")
    f.write("\\levelspace360\\levelindent0{\\leveltext\\leveltemplateid67698703\\\'02\\\'03.;}")
    f.write("{\\levelnumbers\\\'01;}\\chbrdr\\brdrnone\\brdrcf1\\chshdng0\\chcfpat1\\chcbpat1 \\fi-360\\li2880\\jclisttab\\tx2880 }")  # NOQA

    f.write("{\\listlevel\\levelnfc4\\levelnfcn4\\leveljc0\\leveljcn0")
    f.write("\\levelfollow0\\levelstartat1\\levelspace360\\levelindent0{\\leveltext\\leveltemplateid67698713\\\'02\\\'04.;}")  # NOQA
    f.write("{\\levelnumbers\\\'01;} \\chbrdr\\brdrnone\\brdrcf1 \\chshdng0\\chcfpat1\\chcbpat1 \\fi-360\\li3600\\jclisttab\\tx3600 }")  # NOQA

    f.write("{\\listlevel\\levelnfc2\\levelnfcn2\\leveljc2")
    f.write("\\leveljcn2\\levelfollow0\\levelstartat1\\levelspace360\\levelindent0{\\leveltext\\leveltemplateid67698715\\\'02\\\'05.;} {\\levelnumbers\\\'01;} \\chbrdr\\brdrnone\\brdrcf1 \\chshdng0\\chcfpat1\\chcbpat1 \\fi-180\\li4320\\jclisttab\\tx4320 }")  # NOQA

    f.write("{\\listlevel\\levelnfc0\\levelnfcn0")
    f.write("\\leveljc0\\leveljcn0\\levelfollow0\\levelstartat1\\levelspace360\\levelindent0{\\leveltext\\leveltemplateid67698703\\\'02\\\'06.;}")  # NOQA
    f.write("{\\levelnumbers\\\'01;}\\chbrdr\\brdrnone\\brdrcf1 \\chshdng0\\chcfpat1\\chcbpat1 \\fi-360\\li5040\\jclisttab\\tx5040 }")  # NOQA

    f.write("{\\listlevel\\levelnfc4\\levelnfcn4\\leveljc0\\leveljcn0\\levelfollow0\\levelstartat1\\levelspace360\\levelindent0")  # NOQA
    f.write("{\\leveltext\\leveltemplateid67698713\\\'02\\\'07.;}")
    f.write("{\\levelnumbers\\\'01;}\\chbrdr\\brdrnone\\brdrcf1 \\chshdng0\\chcfpat1\\chcbpat1 \\fi-360\\li5760\\jclisttab\\tx5760 }")  # NOQA

    f.write("{\\listlevel\\levelnfc2\\levelnfcn2\\leveljc2\\leveljcn2\\levelfollow0\\levelstartat1\\levelspace360\\levelindent0")  # NOQA
    f.write("{\\leveltext\\leveltemplateid67698715\\\'02\\\'08.;}{\\levelnumbers\\\'01;}")
    f.write("\\chbrdr\\brdrnone\\brdrcf1 \\chshdng0\\chcfpat1\\chcbpat1 \\fi-180\\li6480\\jclisttab\\tx6480 }")

    f.write("{\\listname ;}\\listid127936308}}\n\n")

    f.write("{\\*\\listoverridetable{\\listoverride\\listid127936308\\listoverridecount0\\ls1}}\n\n")
    #@-<< listtable >>
    # Write text formatting foundation
    f.write("\\viewkind4\\uc1\\pard\\f0\\fs20\n\n")
    # Create generic level header
    levelHeader = "\\pard \\ql \\fi-360\\ri0\\widctlpar\\jclisttab\\faauto\\ls1\\adjustright\\rin0\\itap0"
    myLevel = -1
    for p in c.all_positions():
        curLevel = p.level() + 1  # Store current level so method doesn't have to be called again
        if curLevel != myLevel:
            if myLevel != -1:
                # If this is not the 1st level written, close the last before begin
                f.write("}")
            # Generate the pixel indent for the current level
            levelIndent = str(720 * curLevel)
            # Output the generic RTF level info
            f.write(levelHeader)
            f.write("\\li" + levelIndent + "\\tx" + levelIndent + "\\ilvl" + str(curLevel - 1) + "\\lin" + levelIndent)
            f.write("{")
        myLevel = curLevel
        myHeadline = p.h
        # Check if node is an @file and ignore if configured to
        if not (myHeadline[:5] == "@file" and flagIgnoreFiles):
            # Write headline with correct # of tabs for indentation
            myOutput = myHeadline + "\\par "
            myOutput = myOutput.encode("utf-8")
            f.write(myOutput)
            # If including outline body text, convert it to RTF usable format
            if not flagJustHeadlines:
                myBody = p.b.encode("utf-8")
                myBody = myBody.rstrip().rstrip("\n")
                f.write(myBody + "\\par ")
    # Write final level close
    f.write("}")
    # Write RTF close
    f.write("}")
    # Close file
    f.close()
    g.es(" Leo -> RTF completed.", color="turquoise4")
#@-others
#@@language python
#@@tabwidth -4
#@-leo
