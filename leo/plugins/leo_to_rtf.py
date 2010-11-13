#@+leo-ver=5-thin
#@+node:danr7.20060902083957: * @file leo_to_rtf.py
#@+<< docstring >>
#@+node:danr7.20060902085340: ** << docstring >>
''' Outputs a Leo outline as a numbered list to an RTF file. The RTF file can be
loaded into Microsoft Word and formatted as a proper outline.

If this plug-in loads properly, you should have an "Outline to Microsoft RTF"
option added to your File > Export... menu in Leo.

Settings such as outputting just the headlines (vs. headlines & body text) and whether
to include or ignore the contents of @file nodes are stored in the rtf_export.ini file
in your Leo\plugins folder.

The default export path is also stored in the INI file. By default, it's set to c:\ so
you may need to modify it depending on your system.

'''
#@-<< docstring >>

#@@language python
#@@tabwidth -4

# leoToRTF 1.0 plugin by Dan Rahmel

#@+<< version history >>
#@+node:danr7.20060902085055: ** << version history >>
#@@killcolor
#@+at
# 
# 1.00 - Cleaned up code and commented difficult passages
# 0.92 - Added INI file settings
# 0.91 - Added RTF output code
# 0.90 - Created initial plug-in framework
#@-<< version history >>
#@+<< imports >>
#@+node:danr7.20060902083957.1: ** << imports >>
import leo.core.leoGlobals as g

if g.isPython3:
    import configparser as ConfigParser
else:
    import ConfigParser


#@-<< imports >>

__version__ = "1.0"

#@+others
#@+node:ekr.20100128073941.5373: ** newHeadline
def init():

    # Ok for unit testing: creates menu.
    g.registerHandler("create-optional-menus",createExportMenu)
    g.plugin_signon(__name__)
    return True
#@+node:danr7.20060902083957.2: ** createExportMenu (leo_to_rtf)
def createExportMenu (tag,keywords):

    c = keywords.get("c")

    # Insert leoToRTF in #3 position of the File > Export menu.
    c.frame.menu.insert('Export...',3,
        label = 'Outline to Microsoft RTF',
        command = lambda c = c: export_rtf(c))
#@+node:danr7.20060902083957.3: ** export_rtf
def export_rtf( c ):

    g.es("Exporting...")

    # Get user preferences from INI file 
    fileName = g.os_path_join(g.app.loadDir,"../","plugins","leo_to_rtf.ini")
    config = ConfigParser.ConfigParser()
    config.read(fileName)
    flagIgnoreFiles =  config.get("Main", "flagIgnoreFiles") == "Yes"
    flagJustHeadlines = config.get("Main", "flagJustHeadlines") == "Yes"
    filePath = config.get("Main", "exportPath").strip() # "c:\\"

    myFileName = c.frame.shortFileName()    # Get current outline filename
    myFileName = myFileName[:-4]            # Remove .leo suffix

    g.es(" Leo -> RTF started...",color="turquoise4")

    # Open file for output
    f=open(filePath + myFileName + ".rtf", 'w')

    # Write RTF header information
    f.write("{\\rtf1\\ansi\\ansicpg1252\\deff0\\deflang1033{\\fonttbl{\\f0\\fswiss\\fcharset0 Arial;}}\n\n")

    # Write RTF list table that provides numbered list formatting
    #@+<< listtable >>
    #@+node:danr7.20060902085826: *3* << listtable >>
    f.write("{\\*\\listtable{\\list\\listtemplateid1723346216\\listhybrid\n")

    f.write("{\\listlevel\\levelnfc0\\levelnfcn0\\leveljc0\\leveljcn0\\levelfollow0\\levelstartat1\\levelspace360\\levelindent0\n")
    f.write("{\\leveltext\\leveltemplateid67698703\\\'02\\\'00.;}\n\n")
    f.write("{\\levelnumbers\\\'01;}\\chbrdr\\brdrnone\\brdrcf1 \\chshdng0\\chcfpat1\\chcbpat1 \\fi-360\\li720\\jclisttab\\tx720 }")

    f.write("{\\listlevel\\levelnfc4\\levelnfcn4\\leveljc0\\leveljcn0\\levelfollow0\\levelstartat1\\levelspace360\\levelindent0")
    f.write("{\\leveltext\\leveltemplateid67698713\\\'02\\\'01.;} {\\levelnumbers\\\'01;}")
    f.write("\\chbrdr\\brdrnone\\brdrcf1 \\chshdng0\\chcfpat1\\chcbpat1 \\fi-360\\li1440\\jclisttab\\tx1440 }")

    f.write("{\\listlevel\\levelnfc2\\levelnfcn2\\leveljc2\\leveljcn2\\levelfollow0\\levelstartat1\\levelspace360\\levelindent0")
    f.write("{\\leveltext\\leveltemplateid67698715\\\'02\\\'02.;} {\\levelnumbers\\\'01;}")
    f.write("\\chbrdr\\brdrnone\\brdrcf1 \\chshdng0\\chcfpat1\\chcbpat1\\fi-180\\li2160\\jclisttab\\tx2160 }")

    f.write("{\\listlevel\\levelnfc0\\levelnfcn0\\leveljc0\\leveljcn0\\levelfollow0\\levelstartat1")
    f.write("\\levelspace360\\levelindent0{\\leveltext\\leveltemplateid67698703\\\'02\\\'03.;}")
    f.write("{\\levelnumbers\\\'01;}\\chbrdr\\brdrnone\\brdrcf1\\chshdng0\\chcfpat1\\chcbpat1 \\fi-360\\li2880\\jclisttab\\tx2880 }")

    f.write("{\\listlevel\\levelnfc4\\levelnfcn4\\leveljc0\\leveljcn0")
    f.write("\\levelfollow0\\levelstartat1\\levelspace360\\levelindent0{\\leveltext\\leveltemplateid67698713\\\'02\\\'04.;}")
    f.write("{\\levelnumbers\\\'01;} \\chbrdr\\brdrnone\\brdrcf1 \\chshdng0\\chcfpat1\\chcbpat1 \\fi-360\\li3600\\jclisttab\\tx3600 }")

    f.write("{\\listlevel\\levelnfc2\\levelnfcn2\\leveljc2")
    f.write("\\leveljcn2\\levelfollow0\\levelstartat1\\levelspace360\\levelindent0{\\leveltext\\leveltemplateid67698715\\\'02\\\'05.;} {\\levelnumbers\\\'01;} \\chbrdr\\brdrnone\\brdrcf1 \\chshdng0\\chcfpat1\\chcbpat1 \\fi-180\\li4320\\jclisttab\\tx4320 }")

    f.write("{\\listlevel\\levelnfc0\\levelnfcn0")
    f.write("\\leveljc0\\leveljcn0\\levelfollow0\\levelstartat1\\levelspace360\\levelindent0{\\leveltext\\leveltemplateid67698703\\\'02\\\'06.;}")
    f.write("{\\levelnumbers\\\'01;}\\chbrdr\\brdrnone\\brdrcf1 \\chshdng0\\chcfpat1\\chcbpat1 \\fi-360\\li5040\\jclisttab\\tx5040 }")

    f.write("{\\listlevel\\levelnfc4\\levelnfcn4\\leveljc0\\leveljcn0\\levelfollow0\\levelstartat1\\levelspace360\\levelindent0")
    f.write("{\\leveltext\\leveltemplateid67698713\\\'02\\\'07.;}")
    f.write("{\\levelnumbers\\\'01;}\\chbrdr\\brdrnone\\brdrcf1 \\chshdng0\\chcfpat1\\chcbpat1 \\fi-360\\li5760\\jclisttab\\tx5760 }")

    f.write("{\\listlevel\\levelnfc2\\levelnfcn2\\leveljc2\\leveljcn2\\levelfollow0\\levelstartat1\\levelspace360\\levelindent0")
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
        curLevel = p.level() + 1    # Store current level so method doesn't have to be called again
        if curLevel != myLevel:
            if myLevel != -1:
                f.write("}")                 # If this is not the 1st level written, close the last before begin
            levelIndent = str(720*curLevel) # Generate the pixel indent for the current level
            f.write(levelHeader)            # Output the generic RTF level info
            f.write("\\li" + levelIndent + "\\tx" + levelIndent + "\\ilvl" + str(curLevel-1) + "\\lin" + levelIndent)        
            f.write("{")

        myLevel = curLevel
        myHeadline = p.h

        # Check if node is an @file and ignore if configured to
        if not (myHeadline[:5] == "@file" and flagIgnoreFiles):
            # Write headline with correct # of tabs for indentation
            myOutput = myHeadline +"\\par "
            myOutput = myOutput.encode( "utf-8" )
            f.write(myOutput)
            # If including outline body text, convert it to RTF usable format
            if not flagJustHeadlines:
                myBody = p.b.encode( "utf-8" ) 
                myBody = myBody.rstrip().rstrip("\n") 
                f.write(myBody + "\\par ")

    # Write final level close
    f.write("}")  

    # Write RTF close
    f.write("}")  

    # Close file
    f.close()
    g.es(" Leo -> RTF completed.",color="turquoise4")
#@-others
#@-leo
