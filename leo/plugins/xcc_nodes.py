#@+leo-ver=5-thin
#@+node:ekr.20060513122450: * @file xcc_nodes.py

"""Integrates C/C++ compiler and debugger in a node."""

#@+<< About this plugin >>
#@+middle:ekr.20060513153648: ** Documentation
#@+node:ekr.20060513122450.1: *3* << About this plugin >>
#@@nocolor
#@+at 			X C++ Compiler nodes----
# PLEASE SEE http://xccnode.sourceforge.net/
#  The xcc_nodes.py plugins simplify c++ syntax and integrate compiling and debuging tools.
# 
# To start debugging, create a node whose headline is::
# 
#     @xcc projectname
# 
# or::
# 
#     @xcc projectname.ext
# 
# The optional extension (*.ext) set the kind of project the node will build.
# An empty extension is equivalent to the '.exe' extension.
# 
# As soon as "@xcc" is written in the headline the plugin creates an empty configuration.
# 
#     if ext == cpp,
#         inflate name.cpp
#         the node will attempt to build an executable
#     if ext == h,
#         inflate name.h
#         the node will attempt to check the syntax of the header
#     if ext == exe,
#         this is equivalent to no ext at all
#         inflate name.h and name.cpp
#         the node will attempt to build an executable
#     if ext == dll,
#         inflate name.h and name.cpp
#         the node will attempt to build a dynamic link library
#     if ext == lib,
#         inflate name.h and name.cpp
#  			the node will attempt to build a static link library
# 
# Creating programs
# 
# The "@xcc" node support Leo's @others syntax but **not**  section references.
#  	The actual code is written in the children of the main node and the code generation is
#  	affected by headlines.
# 
#  	Here are the rules: (see examples for good understanding)
# - The '@' rule: If a headline starts with "@", the node and its children are ignored.
# 
# - The semicolon rule: If a headline ends with ";" and another compatible rule is trigered in the
#  same headline, the rule will be written in the source if there is one.
# 
# **//**: If a headline start with "//", all its body and children are commented out as follows::
#     /*headline
#         body text
#         and
#         childs
#         */
# 
# This rule is compatible with the ';' rule.
# 
# - The function rule: If a headline ends with ")", the headline is used as funtion prototype.
#   The body and children are encased automatically in the opening and closing curly brace.
# 
#   The class and function rules are disabled while in a function rule.
#   The function rule is compatible with the semicolon rule, except that if there is a
#   header in the project the function will always be declared in the header and
#   defined in the	source, appending "!" prevents declaration in header for global functions.
# 
# - The class rule: If a headline starts with "class", a class is declared and opening and
#   closing curly brace are automatically written, all the children of this node are class members,
#   the functions are correctly dispatched between header and source (access specifier is
#    appended if needed).
# 
# - The "Default" rule: If a headline doesn't match any of the preceeding rules,
#   its headline is written as a comment and the body and childs written "as is" as follows::
# 
#     //headline
#         body text
#         and all children.
# 
# This rule is compatible with the semicolon rule.
# 
# -> Config Panel reference:
# 	-> options : generally the most used options.
# 		-> Create files : Request that files should be inflated.
# 		-> Compile : Request that the project should be built using the configured compiler.
# 			-> Seek first error : Attempt to locate the first error encountered.
# 		-> Execute : Request to run the built exe.
# 			-> Connect to pipe : Interface the built exe pipe to the node interface, exe is simply spwned if unchecked.
# 		-> Debug : Request to run the built exe with the configured debugger (overide the "Execute" option).
# 			-> Seek breapoints : Detect and "Goto" encountered breakpoints.
# 		-> Xcc verbose : Special verbose mode usefull to config the debugger and widely used when coding the plugin
#  		-> Filter output : Filter compiler and debugger ouput, showing only error and warning
# 		-> Colorize log : Colorize the output if checked, allowing easyer browsing.
# 
# - by Alexis Gendron Paquette
#@-<< About this plugin >>
#@+<< version history >>
#@+middle:ekr.20060513153648: ** Documentation
#@+node:ekr.20060513183934: *3* << version history >>
#@@nocolor
#@+at
# 
# v 0.1: Pierre Bidon, et. al.
# 
# v 0.2 EKR:
# - Add per-node controller class.  This required many changes.
# - Many stylistic changes.  More are coming.
# 
# v 0.3 EKR:
# - Fixed a large number of crashers due to the reorganized code.
# - The major panels now appear to work.
# 
# v 0.4 EKR:
# - Added a ``what I did`` section.
# - Made UpdateProcess a cc method.
# - It appears that cc.OPTS is not set properly in PageClass.LoadObjects.
#   This prevents the compiler from working.
#@-<< version history >>
#@+<< what I did >>
#@+middle:ekr.20060513153648: ** Documentation
#@+node:ekr.20060514121335: *3* << what I did >>
#@@nocolor
#@+at
# 
# **Important**: I have spent 8 or more hours making the following changes.
# Without doubt I have introduced some bugs while doing so. However, it was
# important to make these changes, for the following reasons:
# 
# 1. This is very important code, and deserves the best packaging.
# 
# 2. This code may form the basis of a Python-oriented debugger, so I wanted
#    to make the code base as solid as possible.
# 
# 3. Working and debugging code is the best way for me to really understand it.
# 
# Here is what I have done in detail:
# 
# - Eliminated * imports:
# 
# - Created the module-level init function that registers all hooks.
#   This is the recommended style: it shows in one place where all the hooks are.
# 
# - Removed most try/except handling.
#     - Such handling is *usually* unnecessary, especially since Leo does a good job
#       of recovering from crashes. However, try/except blocks might be important
#       when executing user code, so perhaps it will be necessary to put some back in.
#     - Replaced ``x = aDict[key]`` by ``x = aDict.get(key)`` to avoid exceptions.
# 
# *** Eliminated *all* global variables (except commanders) as follows:
# 
# - Created per-commander controller class instances.
#     - The controllers dictionary is the only global variable.
#     - The new OnCreate event handler creates controller instances.
#     - Replaced all global variables by ivars of the controller class.
#     - Global constants still exist.
#     - Most former global functions now are methods of the controller class.
#     - By convention, cc refers to the proper controller, i.e., the controller for the proper commander c.
#     - cc gets passed to the constructor of almost all classes.
#     - Replaced init logic (start2 hook) by logic in the ctor for the controller class.
# 
# - Simplified module-level event handlers.
#     - They simply call the corresponding event handler in the proper controller instance.
# 
# - Renamed most classes from XXX to XxxClass.
# 
# - Eliminated the Parser global.
#     - All Rule classes now get a Parser argument and define self.Parser.
# 
# - Disabled some weird code in OnIdle.  I'm not sure what this is supposed to do.
# 
# - Create a new pause module-level function that calls winPause or linPause as appropriate.
# 
# - Used more Pythonic or Leonic ideoms in many places:
#     - Replaced ``if x == True:`` by ``if x:``.
#     - Replaced ``if x == False:`` by ``if not x:``.
#     - Replaced ``if x != '':`` by ``if not x:``
#     etc.
#     *** Warning: these simplifications might cause problems.
#         For example, the re module uses None as a sentinal, and can also return 0,
#         so tests like ``if result:`` are not correct in such cases.  I have tried
#         not to simplify the code "too much" but I may have made mistakes.
#     *** if p is a node, ``if p == None:`` *must* be replaced by ``if not p:``.
#     - cc.VERBOSE and cc.FILTER_OUTPUT now have values True/False instead of 'true'/'false'.
#     - Defined TraceBack as g.es_exception.
#     - Changed ``Error(x) ; return`` to ``return Error(x)``, and similarly for Warning, etc.
# 
# - Simplified the code wherever possible.
#     - Sometimes the change can be dramatic, as in cc.cGetDict.
# 
# * There does not seem to be any definition of ExtractLines.
#@-<< what I did >>
#@+<< imports >>
#@+node:ekr.20060513122450.4: ** << imports >>
import leo.core.leoGlobals as g

import Tkinter as Tk

from winsound import Beep as beep
import traceback
import os,sys,thread,threading,time,string,re
import tkFileDialog,tkMessageBox,tkSimpleDialog
import pickle,base64,zlib
#@-<< imports >>

controllers = {}

if 1: # To be replaced by ivars
    #@+<< globals >>
    #@+node:ekr.20060513122450.5: ** << globals >>
    #@+others
    #@+node:ekr.20060513122450.9: *3* Write Info
    FILE_HDR = ""
    FILE_FTR = ""

    CLASS_HDR = "//"+5*"------------------"+"\n"
    CLASS_OPN = ""
    CLASS_END = ""
    CLASS_FTR = ""

    FUNC_HDR = "//"+5*"------------------"+"\n"
    FUNC_OPN = ""
    FUNC_END = ""
    FUNC_FTR = ""
    #@+node:ekr.20060513122450.6: *3* Process
    if os.name == "dos" or os.name == "nt":
        Encoding = "mbcs"
    else:
    	Encoding = "ascii"

    #--------------------------
    ProcessList = []
    #@+node:ekr.20060513122450.16: *3* Icons
    #@+node:ekr.20060513122450.17: *4* Go
    Go_e = "S\'x\\xdam\\x8e\\xcbn\\x830\\x14D\\xf7\\xfcLk \\xb2\\xbc\\xe8\\xe2\\xda@\\xc4\\xd32\\xe0\\x90.!J\\xa1\\x04\\x02\\x04K\\x80\\xbf\\xbeV\\xd6\\x1d\\xe9\\xe8\\x8cf5\\xf9\\xe7p\\xe6\\xde\\xd0\\xf9\\x00\\x02R\\x01\\xc0\\x9b\\xbb\\xa3\\xf0\\xfdd@\\nWH5\\x95\\xe9\\x956\\xd6+\\xe6\\x844\\xdcl|\\xbf]\\x03\\xfd\\xb2\\t\\xc16r\\x96j \\xa7\\xe3f\\xe9\\xb9\\x90\\xea\\xfbH\\xb1[\\xf8\\xfa\\xa90v2\\xadG\\xf5\\xc2v\\xd6\\x7f\\x18\\x88\\x01\\x8d\\xaa\\xef\\x83\\xb9v\\x1es\\xdc\\xc1?a\\xdb[\\xd6\\xfb\\x11@X\\t(\\x19\\xdd\\xc35\\xa6\\xd4\\x83)\\x8d\\x1fG\\xeb\\x8a\\x98uB\\xa2K\\xd2\\xb5\\xc0#\\xf8\\xcd\\xe5xI\\x8ap\\x95\\xb1\\xdf\\x8b\\x15_\\x9eT\\xf8\\xac\\xf4X\\\'\\xd7\\xf9,\\xc0\\x92u\\x11\\xc0\\x81\\xf2i\\xd8\\xdbtIR\\xdaJw\\x9aD\\xbb\\xf1(b%\"\\xf5\\x02b\\x8b\\x7f\\x80n\\xa2E]\\xe1f~\\x00\\xe0\\xad_\\xd6\\x1f\\x96\\x88[)\'\np0\n."
    #@+node:ekr.20060513122450.18: *4* StepIn
    StepIn_e = "S\'x\\xda\\x95\\xd0Ms\\x820\\x10\\x06\\xe0;\\x7f\\xa5\\x17\\x15\\xa6\\x0e\\x87\\x1e6\\x100|\\x9a\\xa4\\x0c\\xda\\x9bP\\x0b\\x02\\x82\"\\x18\\xf0\\xd77\\xe1\\xdaS3\\xf3dg\\x92\\xec\\xbb3a\\xab\\xc6\\x8d\\xed\\xa6\\xc4\\x00\\x14\\xa2\\x04 \\xce\\xae\\xfa\\x98\\x9d\\xf5a{^\\x0f\\xdbTy\\r\\x99\\x12+S\\xbe\\x95R\\xf3)\\r\\xd9\\xc6|J\\xb2\\xae\\xe5\\x93\\xb5\\xa6\\xb6\\xfe\\xb4\\x19n\\xa7\\xb4QZo\\xce\\x95\\xc6\\xe3\\x89Ry<\\xac\\xc8\\xac\\xe0\\x92\\xf0\\xc52I\\xca\\xf5\\xe1\\x95\\xeb\\xd1\\xe2\\xa4G\\xbd&sTV\\x7f\\xdcD\\x95\\x92\\xaa\\x84\\xfa\\xe6\\xf3\\xfaf\\xd1\\xda\\xb3h\\x85\\xa7\\x90\\xab\\x03\\x99\\xc3\\xea/\\x97\\x01\\xc5P\\x10\\x0b\\xfe.\\r\\xfe\\xb3,\\xb1\\x94\\xe5K\\x00H\\x05\\xb0\\xb7\\xd0D\\x1e>\\x02{\\xee\\xb8v\\x7f \\x01\\xc4A\\x05\\x159\\x8f^\\xd4\\xe8\\xb8+\\xef\\xcfQ5O\\x06\\xd0\\x10\\x17yq\\xddU\\xc4H(B(\\x19-\\x87N\\x82\\xcb\\x8e\\x82\\xf8c\\x8f\\x8aU\\xe8\\x072\\x9b\\x89\\x1d\\x08m\\x15\\xbb\\xc8f\\xc2\\xb7\\xf6\\xcc\\xeb.\\x07\\x84\\xcb\\x90\\xec\\x03Q\\xd0\\xb1\\xa4\\x989\\xf7\\x9f\\x16\\xdek,\\x1b>\\x9b\\xef\\xc0\\xb6\\x8f\\x1d=\\xc4\\xed\\xe5M\\x0e\\xe1\\x8c^Z\\xe4|\\xd2 j\\x10\\x1a\\xf8.\\xd3J\\xd1\\xcd\\x1e\\xb2\\rJb\\xd4\\x82i:\\x85 `?>\\xb4_\\xa4j\\x9b\\xc9\'\np0\n."
    #@+node:ekr.20060513122450.19: *4* StepOver
    StepOver_e = "S\'x\\xda\\x95\\xd0Mo\\x830\\x0c\\x06\\xe0;\\xbf\\xa6|hh\\x87\\x1e\\x9c\\x10h`@\\x03\\xed(\\xbbA\\x86\\xc2\\x97J\\x05l\\x01~\\xfdHw\\x9f\\xb4Wz\\xec\\x8b-YN\\x0e\\xbd\\x17;}M\\x00\\x18DW\\x80\\xc8\\xae\\xf4\\xd9\\xce\\x94m.\\x95XY\\xb8\\xad\\xb8\\xca7\\xbf\\xed\\xb2We.\\rE\\xdfGuM\\x95\\xb1\\xccf\\xe5Q\\x18\\xf3\\xb8{\\x14Y\\xaf\\xdc\\x83\\x8c\\xdf\\xfd\\x95\\xf7\\xfez\\xed\\xe9\\x1a\\xb6t%5M\\x9f*s\\xb6+3\\xda\\xf8\\xae0#\\xb56j\\xb9\\xfe\\xbbz\\xed\\xfdTI\\xbbG\\x90v>f\\xed\\xf0\\x12\\xb7d\\t\\x93\\xee\\xc3K\\x80\\x11\\x10\\x14\\xc3\\xdf\\xd1\\xe0?\\xc1\\xf2\\xd9\\x9e/\\x01\\xa0\\x8d\\x847\\x8c\\x16:\\x05\\x08\\xe1uJ\\xb5\\xb1\\xc3IN]$\\x98\\x90\\\'\\x1f\\xa4\\xcc\\xc3\\xc0\\x850\\x8c\\x9a\\xba\\xa6A\\xec\\x92U\\xcf\\xc0At\\x10\\x11r\\x93\\xeb\\x019\\xc8bS\\x02\\x08\\x1f\\x863\\x96\\xcc\\xea.\\x1e\\x08\\xbd8a4hy\\x00\\x143\\xdf\\xee\\xef\\xb5\\xe0\\xd4\\xa3h\\xab\\x9c\\xf2\\xaba\\xef\\x1e\\xc6\\x84I\\xcag!\\xac\\x98\\x9cH\\xcbo\\x13\\x069Y\\xa9?b\\x03\\xce\\xedV[\\xc5%\\xac\\x97O\\xc2\\xb1!)\\xb9]4Q\\x87\\xab\\xe77\\xc2\\xca\\xf4\\xb30\\xf9\\xdb~\"\\xc4\\xf2x\\xd4~\\x00\\\'\\xed\\x9a\\xd0\'\np0\n."
    #@+node:ekr.20060513122450.20: *4* StepOut
    StepOut_e = "S\"x\\xda\\x95\\xd0\\xddn\\x820\\x14\\xc0\\xf1{\\x9eF\\xc5\\x8c\\xedb\\x17\\xa7\\xa5`a\\x80\\x05;\\xd4;As\\xca\\x87\\x9bQ\\x94\\x8f\\xa7_\\xcb\\x1b\\xac\\xc9/\'9i\\xfeM\\x9a.Z?q[\\xc5\\x00\\x04\\xc4\\x12 )\\xae\\xf6\\xb3\\xb8\\xd8\\x9dsYvNnL]a$\\xc6P:\\xda\\xde{\\x95\\xf9\\x87\\xd1\\x15\\xab\\x8f\\x97\\xa6\\xe7\\xd2\\xd2\\xf7\\x96\\xc6\\xbd\\xc8;\\xe3vZiy\\xab\\x95?\\xc18k\\x83L\\xd6A\\x16\\xd5|\\x8c\\x14\\x1f\\x99\\xe2\\xd9\\xec\\xb2N\\x9d\\xf9U\\xad\\xb4\\xbb\\xc9*\\xedx2Nv|\\xd7\\x9d\\xd9a\\x15\\xd7F~\\x8duV\\x97\\x9a[\\x985\\x01\\x15\\xf5\\xef[R\\xb3!\\xca\\xccB\\xf7\\xd2\\xe6\\xe8\\xa7 \\x18 \\xa7\\x00`\\xc1\\x7f\\x0e\\xed\\xe71\\x7f\\t\\x00o\\x01\\xb6\\x94\\x0c\\\\\\xfa\\xd4E\\xc4\\xad\\xa5\\xb7\\x04\\x9b\\xfc\\x8b\\x02\\xde7A\\x8f\\xb8\\x90\\xa17E\\xef\\x8ce=6\\x8c\\xd0\\x1d[\\xec<\\xa2\\xb8\\xdc\\x10w|\\x84\\x02\\xf0\\xb6\\xe0\\xd2S4F\\xeaUp8\\xd1\\xe8\\x8ar\\x98\\xa0\\xea\\xad\\xa6<\\xb9(\\x90\\x9d_J\\x08\\xdf\\x150\\x9e/\\xacI\\x15J\\x97\\xba4\\x0f\\xfdjI c>\\xfb\\xe6\\x9b\\xfd/\\x0e\\x870\\x8a\\x08*2$\\x10\\x9c\\xf91\\xc3*>$t\\xbf\\x86\\xeaL,2\\xae\\xc6M\\xa3{O\\x07H\\xfa\\x90\\x94\\xef\\xa0/]_\\xb1\\xf2\\x8b\\xa0\\x80\\xa4\\xff\\xfc\\xb4\\xfe\\x00\\xd4\\xc7\\xa1 \"\np0\n."
    #@+node:ekr.20060513122450.21: *4* Pause
    Pause_e = "S\'x\\xda\\x95\\xceKn\\x830\\x18\\x04\\xe0=\\x97i\\xf3t\\xba\\xc8\\xe2\\xb7\\t\\xc6N\\xb0e\\x08\\x02\\x96\\x85\\x02\\x86:\\x84\\x14Wn9}Q{\\x82\\x8e\\xf4I\\xb3\\x19i\\xe2gC\\xa5o\\xf4\\t@A\\xa4\\x00\\x04\\xaa7\\x16e+[f\\xbb\\xc5f1\\xdbR.]\\xce\\x13Z\\xe4\\xc1\\xcb!\\x0f\\xd0>3\\x03OR\\xc3\\x92\\x93\\t-\\xeaC1{\\x9a\\x8a\\xfeim?\\xea\\xb5\\xedM\\xc0\\x93\\xda\\xc1\\xffC\\xfeF\\xde\\xef#\\x00V(\\x10\\x04\\x7f\\xb1\\xe9\\xec\\xe3\\xd6U\\xb9\\x0c}\\xd82B\\xb4\\xdaJ\\xca\\xaf\\xeeN\\x19&8m8\\xef\\x8aT\\xf9\\xb4\\xd3\\xd3%}\\xcc\\xf7(\\x13\\xac\\xed\\xa2\\xc6\\x80\\xday\\xef\\xcc\\x07\\x03\\xac\\xba\\xc9\\x98\\x1d\\x1e\\x82\\xde\\xba\\xd1\\x0e\\xda\\xb1\\xf4\\xbb\\x91\\xe6Z]\\xe2\\xcf\\xbe(h\\x89\\xc1\\x9d\\x13\\xdc\\xb7N\\x91\\x81\\x8c\\x8e\\xbf\\xd11~\\x8d\\x08\\x80t\\xc7\\xa3\\xf7\\x03\\xce\\xc7^\\x95\'\np0\n."
    #@+node:ekr.20060513122450.22: *4* Stop
    Stop_e = "S\'x\\xda-\\x8c\\xc1\\x8e\\x820\\x14E\\xf7\\xfc\\x8c\\xa2\\x18\\xdc\\xb8x\\x14h\\x0b%\\x0e4LSv`\\xb4O@t\\xa4\\x19\\x18\\xbe~&d\\xee\\xe2\\x9c\\xe4,n\\xb1\\xed\\xe99\\xec1\\x02\\xc8Ad\\x00\\xe7\\xe6\\xb1\\xb7\\xfe\\xd5\\xb5\\xbeZl\\xa3\\x96\\xaf\\x9d}\\xd5\\xaal\\xd9_\\xdc\\xdb\\xb7>\\x1eR~\\xf9$\\xb4q\\t\\xbdx3\\x88\\xed\\x0b\\xfe\\xe7\\xac$\\xd3\\xaa\\xf5\\x10\\x80\\xab\\x1c\\x18\\tf>\\xa6a`&\\x9d\\xb0\\xb8\\xe5\\x1d\\xa5\\x811Z\\x8b\\x04y\\xa78\\x18\\x8c\\xde\\xb5\\x91P\\xd6\\t\\xbd\\xe3\\xc4\\xaa\\xef\\xc9s\\xb2Z\\x02\\xc8l\\xb8\\xde\\x97\\xaa\\x93\\x85\\xe8\\xe4\\xb8A\\x94\\xba|T\\xa2_2\\x16\\xc5$\\x7f\\xa6\\xb7\\x8f\\xc1\\xe0\\x0f13X\\x8a\\x05F&\\x1eZ\\xe9Y\\x1a\\x00\\x84\\xe3\\xc9\\xf9\\x05\\x1a\\x01HO\'\np0\n."
    #@+node:ekr.20060513122450.23: *4* Watch
    WatchData = "S\"x\\xda\\x95\\x90\\xdbr\\x820\\x10@\\xdf\\xf9\\x1a\\xc1Z\\xea\\xe3&\\x86\\x8b\\x96\\x8bf\\x18\\x8coBk \\xa4B!\\x8a\\xc9\\xd77\\xfa\\x07\\xdd\\x99\\xb3g\\xf7ewg\\x0f\\x0b\\x19f\\x1b\\xd9\\x10\\x80=\\xa4\\x05@Z\\x95\\xae\\xaaJ\\xa3\\xaa\\xec\\xc9\\xa3\\xf633\\xf9\\xd6\\xc7\\xcc\\x9d\\xfc\\xc0:p\\xa7c`,\\xf7\\xca\\xd6\\xa3\\xb7\\xbeW\\xdeZ\\x9d\\xbd\\xb5\\xb3\\xfc-\\xd7\\x16w5h\\x0bu\\xfdwO\\x8d\'\\xad\\xcco)\\x07F\\xe5\\xaa\\xd7\\xd2\\xf4T.\\x07Z\\x8fL\\xd7\\x8a\\xd1\\xfa~\\xd2\\x85\\xdc\\xd2\\xe2j\\x11\\xb1NDL\\x9f\\x10\\xe7\\x99\\x9a\\xe8Fd\\x94\\x91\\xe1x#\\xc2\\xfaj\\xfb&R~\\x13\\xa5\\xbe\\xb0X\\x9b\\xefejjO\\x99&T\\xe3\\xd9\\x1d\\x04\\xf3\\xd2\\xb3]g\\xb1\\x13\\xbbaG9\\x80\\x03\\xff\\t<\\xbf\\xf4z\\t@\\xdc\\x00D\\x18=\\x18\\xdbm\\x10\\x9f\\x07\\xe2\\xf4\\xb8El\\xda\\xda\\xe6\\xab,\\x82\\x16b\\x12F\\x98\\x7f\\x04|\\x143#\\x04\\x03\\x97\\x19N\\xda>\\xee>\\xa3\\x96s\\x9d$-\\xdbw1A\\xb3j\\xcfR\\xac\\x12\\xa0!\\xc6\\xec\\x92#~p\\xdeB\\x84\\x10]L\\xb7X\\xf3\\xbe\\xc8s\\x01\\x8f\\xe2\\x07o\\x0eo\\xfdq#`\\x9f\\x07!\\x1cz\\x8d\\n>\\xbb\\xdd\\xe5\\xb3y\\xef\\x92,Ar\\xde\\xdez\\xd4\\xa4\\xa5)\\xc7\\x92\\x04\\xdfWx\\xd4\\x1d:9\\xdcey\\x84\\x16{{\\xba\\xef\\xfc\\x01\\xdb\\xb2\\x9a\\xfc\"\np0\n."
    #@+node:ekr.20060513122450.24: *4* Config
    ConfigData = "S\'x\\xdaU\\xce\\xc1r\\x820\\x14\\x85\\xe1=O\\x03\\xd6\\x11\\xbb\\xbc\\t\\x84\\x06\\x0c\\x99@-\\xda\\x1d\\xa4N\\x10(j\\xc9\\x10\\xe0\\xe9k\\xd8yg\\xbe\\xb9\\x9b\\x7fq2\\xb7\\x8bx\\xd0\\xd5!\\x80\\x00&\\x00R\\xff\\xe2i\\xbf\\xf0tU,\\xba\\xe2\\xd6$}\\x8b\\x8c\\xf2D\\xa6\\xa7Q\\x16\\xefc\\xb5\\xb1l\\xe6\\xfd\\x95\\x1bm9\\xf7\\xb2\\xe8\\xfa\\xa4\\x90}<\\xaf::\\xb3\\x86\\xcea\\xfd\\xa1\\xfd\\xcb[\\xba\\xc8\\xb5K\\x9b\\xb3g\\xcb8?\\xb6\\xf7$W\\xf0z\\xd8\\xac\\xcfY\\x17\\x01\\xd0\\n \\xc68S7\\x16\\x802\\x8a\\xd0\\x01\\x1b\\x8a\\tF\\x8aR\\xce@\\x18N\\x00+\\x97\\x8a\\x14\\xc0$1\\xa0\\xba\\x1d\\xcaC-\\xdc\\x9c#\\x04\\xfbG\\x19\\xd57\\xe7\\xf8\\x0b(@\\xed\\x105\\x0b=3\\x1ev\\x8a\\xf5\\x15\\xc1\\xd0\\xee\\xd1!\\x80t\\xc74R\\xe2Hq\\x8f\\x94\\xfb\\xc5\\xae`\"\\x81\\x82O\\xd3d\\xd1\\xf5[\\xe5\\x12=\\xa6\\xed\\xcf)\\x84m\\xbb\\x1b\\x03\\xe7\\xb9\\xd8w\\xfe\\x01*\\x83e%\'\np0\n."
    #@+node:ekr.20060513122450.25: *4* Prompt
    Prompt_e = "S\'x\\xda\\xad\\x90\\xcdn\\xab0\\x14\\x84\\xf7\\xbcJ\\x16\\xb9I\\xdbp\\xbb\\xe8\\xe2p\\xb0\\x8d\\xe1\\xf2\\xe3:\\xb4%;\\x12r\\r\\x86\\x14Zh\\x0cy\\xfa\\x92\\xf6\\t*\\xf5\\x93F\\xa3\\x91F\\xb3\\x98\\xc7?\\r\\x8b\\xdd\\xa6d\\x02\\x04D)@\\xb2\\x9c\\xf9\\x7fs\\xbfX\\x9e\\xed\\xc5\\xfet7\\xd8\\xc7\\x9ba\\xff\\xbc\\x9au\\xe9\\xed\\xf8\\xd2\\xbf\\xd0\\xf1\\x1a\\xf3\\xe7\\xa6\\xdbM\\x87W\\x7f:4|\\n5\\x97\\xc4*\\xbdk;\\xba\\x1c\\xd6\\xc3{>+[\\x0f:[G:[us\\xdd\\x97i\\xdd\\x05\\xb2\\xf6Q\\xe8v\\x13W\\xd7@J.\\x00\\x96c\\xbdc\\x8f \\x08(\\x8e\\xf0\\x8d\\x05\\xbf\\xc8\\xcf\\xc6\\xd0|\\xd9\\xd7%\\x00\\xfcm>\\x86\\xc5\\x0e\\xf4\\x81\\xeb(\\xa3\\xa8\\x85\\xf5\\x96\\xf7\\x01E\\x18y%\\xbb\\x91\\xf7G\\xdfE\\tSq\\xaeD\\x9f\\\'\\x9e\\x1e\\xf9G\\xd1\\x18q\\x9b\\\'\\xbe\\xae\\xc8S\\xd6Om\\x9b\\xba\\x1e:w\\xf1\\xae6\\x1da\\xa1\\x87\\x08\\xe2%\\xacn-\\x11\"\\xbaXli\\x0b\\xdc\\xb4\\x1c\\xdc1\\x13E\"D{@\\x07+\\x88\\\\L\\x03\\xf5\\x11zP\\xf6\\x9b\\xfd+(Ch\\xdaH\\xf8k\\xc3vl\\x81q45\\x8bC\\xbd\\x19d\\xce-TNU\\x94\\xda@J\\xa8\\xae)U\\\'\\xf8\\x97)BOR\\xaf\\xa0\\xdb\\xf9\\xf5\\xe2]\\x9d\\x19$|\\xb4\\x03\\xc5\\x02R\\x95\\xfc\\xb8]\\x0b\\x15I\\x80\\xd8<<X\\x9fJ\\x0f\\xa2\\xed\'\np0\n."
    #@+node:ekr.20060513122450.26: *3* Colors
    ErrorColor = "#%02x%02x%02x" % (255,200,200)
    BreakColor = "#%02x%02x%02x" % (200,200,255)
    LineNumColor = "#%02x%02x%02x" % (200,200,255)
    RegExpFgColor = "#%02x%02x%02x" % (0,0,255)
    VarSupBgColor = "#%02x%02x%02x" % (255,230,230)
    #@-others
    #@-<< globals >>

#@@language python
#@@tabwidth -4

__version__ = "0.5" # EKR: use c.frame.body.bodyCtrl.leo_bodyBar and .leo_bodyXBar.

#@+others
#@+node:ekr.20060513153648: ** Documentation
#@+node:ekr.20060513122450.2: *3* Known Flaws
#@@nocolor
#@+at 
# 
# *** Most flaw can be worked around by using "default" node(or rule) and writing all	code inside it.
#  (default rule -> comment out headline & write body "as is")
# - the currently selected node Info is refreshed in a leasy way when editing headline or body.
# - line number refresh isnt 100% accurate when editing text in the body.
# - Breakpoints can only be Added/deleted, Enabling/Disabling isnt supported yet.
# - code auto dispath feature wont work as expected with template class and function.
# - class is the only structural keyword supported in the tree to date, union, struct and enum dont trigger any rule.
# - DLL debugging is untested to date, it surely dont work.
# - Untested on Linux, see linPause and aPause functions.
#@+node:ekr.20060513122450.3: *3* Future Features
#@@nocolor
#@+at
# 
# - C/C++ code/project importer/merger
# - "Document" rule -> auto inflating/compiling html(possibly .chm) documentation for the project.
# - Display external files if needed.(external error or similar)
# - "Browse Info" management allowing declaration/references to be searched and displayed.
# - Automation of precompiled headers, possibly using a "#PCH" node.
# - in the debugger regular expression/task list:
#     reg exp:
#         if a group named "FOO" is returned by the regular
#         expression, then the "_FOO_" variable is supported
#         by the corresponding "Task" line.
#     Task:
#         Apart from those defined by the corresponding regular	expression,
#@+node:ekr.20060513142641: ** Module level
#@+node:ekr.20060513123144: *3* init
def init ():

    ok = g.app.gui.guiName() == "tkinter" and not g.app.unitTesting

    if ok:
        data = (
            (("new","open2"), OnCreate),
            # ("start2",      OnStart2),
            ("select2",     OnSelect2),
            ("idle",        OnIdle),
            ("command2",    OnCommand2),
            ("bodydclick2", OnBodyDoubleClick),
            ("bodykey2",    OnBodyKey2),
            ("headkey2",    OnHeadKey2),
            ("end1",        OnQuit),
        )

        for hook,f in data:
            g.registerHandler(hook,f)
            g.plugin_signon(__name__)

    return ok
#@+node:ekr.20060513122450.395: *4* Module-level event handlers
#@+node:ekr.20060513122450.397: *5* OnCreate
def OnCreate(tag,keywords):

    c = keywords.get("c")
    if c:
        controllers [c] = controllerClass(c)
#@+node:ekr.20060513122450.396: *5* OnStart2 (No longer used)
if 0:
    def OnStart2(tag,keywords):
        try:
            if XCC_INITED == False:
                c = keywords.get("c")
                InitXcc(c)
                n = c.p
                h = n.h	

        except Exception as e:
            TraceBack()
#@+node:ekr.20060513122450.398: *5* OnSelect2
def OnSelect2(tag,keywords):

    global controllers
    c = keywords.get("c")
    cc = controllers.get(c)
    cc and cc.onSelect()
#@+node:ekr.20060513122450.399: *5* OnIdle
def OnIdle(tag,keywords):

    global controllers
    c = keywords.get("c")
    cc = controllers.get(c)
    cc and cc.onIdle()
#@+node:ekr.20060513122450.400: *5* OnCommand2
def OnCommand2(tag,keywords):

    global controllers
    c = keywords.get("c")
    cc = controllers.get(c)
    cc and cc.onCommand2(keywords)
#@+node:ekr.20060513122450.401: *5* OnBodyDoubleClick
def OnBodyDoubleClick(tag,keywords):

    global controllers
    c = keywords.get("c")
    cc = controllers.get(c)
    cc and cc.onBodyDoubleClick()
#@+node:ekr.20060513122450.402: *5* OnBodyKey2
def OnBodyKey2(tag,keywords):

    global controllers
    c = keywords.get("c")
    cc = controllers.get(c)
    cc and cc.onBodyKey2(keywords)
#@+node:ekr.20060513122450.403: *5* OnHeadKey2
def OnHeadKey2(tag,keywords):

    global controllers
    c = keywords.get("c")
    cc = controllers.get(c)
    cc and cc.onHeadKey2(keywords)
#@+node:ekr.20060513122450.404: *5* OnQuit
def OnQuit(tag,keywords):

    global controllers
    for key in controllers.keys():
        cc = controllers.get(key)
        cc.onQuit()
#@+node:ekr.20060513160819: *4* pause & helpers
def pause (self,pid):

    if os.name == "nt":
        winPause(pid)
    else:
        linPause(pid)
#@+node:ekr.20060513122450.28: *5* winPause
def winPause(pid):

	import ctypes

	hp = ctypes.windll.Kernel32.OpenProcess(0x1F0FFF,0,int(pid))
	if hp == 0:
		return Error("xcc: ","can't open process: "+str(long(ctypes.windll.Kernel32.GetLastError())))

	if ctypes.windll.Kernel32.DebugBreakProcess(hp) == 0:
		return Warning("xcc: ","Unable to break into the target!")
#@+node:ekr.20060513122450.29: *5* linPause
def linPause(pid):	# theorical way to do it, untested!

	import signal
	os.kill(pid,signal.SIGINT)
#@+node:ekr.20060513142641.1: *4* Helpers
#@+node:ekr.20060513122450.33: *5* AddText
def AddText(text,node):

	c.setBodyText(node,node.b+text)
	l,c = LeoBody.index("end").split(".")
	LeoBody.see(l+".0")
#@+node:ekr.20060513122450.41: *5* CompressIcon
#@+at
# # Encode to base64, zip the data in a string and finally pickle it to be free from illegal char
# #the inflated file is a literal(without the quote)
# #to be embeded in code and passed to DecompressIcon func before use.
# 
# #to use:
# 	# remove "@" at the top
# 	# ctrl+e (execute script)
# 	# choose the file to translate, press save
# 	# open choosedfile.lit in notepade, select all(ctrl+a), copy(ctrl+c), close notepade
# 	# paste(ctrl+v) where you needed your literal (dont forget to add the quote)
# 
# from leoGlobals import *
# import tkFileDialog
# from pickle import *
# from base64 import *
# from zlib import *
# import os
# 
# 
# try:
# 	ft = ('All Files', '.*'),
# 	s = tkFileDialog.askopenfilename(filetypes=ft,title="Select file to convert...")
# 	if s:
# 		f = file(s,"rb")
# 		data = f.read()
# 		f.close()
# 		b64data = encodestring(data)
# 		zdata = compress(b64data,9)
# 		pdata = dumps(zdata)
# 		pdata = pdata.replace("\\","\\\\")
# 		pdata = pdata.replace("\'","\\\'")
# 		pdata = pdata.replace("\"","\\\"")
# 		pdata = pdata.replace("\n","\\n")
# 		name,ext = os.path.splitext(s)
# 		f = file(name+".lit","wb")
# 		f.write(pdata)
# 		f.close()
# except Exception as e:
# 	g.es(str(e))
#@+node:ekr.20060513122450.40: *5* DecompressIcon
def DecompressIcon(data):
	try:
		#unpickle
		zdata = pickle.loads(data)	
		#unzip
		return zlib.decompress(zdata)	#return a base64
	except Excetion:
		Traceback()
#@+node:ekr.20060513122450.34: *5* Error
def Error(module,error):
	g.es(module,newline = False,color = "blue")
	g.es(error,color = "red")
#@+node:ekr.20060513122450.38: *5* GetDictKey (not used)
if 0:
    def GetDictKey(dic,key,create=False,init=""):
        if key in dic:
            return dic[key]
        else:
            if create == True:
                dic[key] = init
                return dic[key]
            else:
                return None
#@+node:ekr.20060513122450.32: *5* GetNodePath
def GetNodePath(node,xas="->"):

	path = []
	for p in node.parents():
		path.insert(0,p.h+xas)

	path.append(node.h)
	return ''.join(path)
#@+node:ekr.20060513122450.37: *5* GetUnknownAttributes
def GetUnknownAttributes(vnode,create = False):

	if hasattr(vnode,"unknownAttributes") != True:
		if create == True:
			vnode.unknownAttributes = {}
		else:
			return None
	return vnode.unknownAttributes
#@+node:ekr.20060513122450.389: *5* GetXccNode
def GetXccNode(node):

	for p in node.parents():
		h = p.h
		if (h[0:5] == "@xcc "):
			return p

	return None
#@+node:ekr.20060513122450.394: *5* ImportFiles
def ImportFiles():

	Warning("TODO: ","Add import code in ImportFiles function!")
#@+node:ekr.20060513122450.390: *5* IsXcc
def IsXcc(node):

	if node.h[0:5] == "@xcc ":
		return True
	else:
		return False
#@+node:ekr.20060513122450.36: *5* Message
def Message(module,warning):

	g.es(module,newline = False,color = "blue")
	g.es(warning)
#@+node:ekr.20060513122450.393: *5* ReplaceVars
def ReplaceVars(exp):
	exp = exp.replace("_NAME_",NAME)
	exp = exp.replace("_EXT_",EXT)
	exp = exp.replace("_ABSPATH_",ABS_PATH)#.replace("\\","\\\\"))
	exp = exp.replace("_RELPATH_",REL_PATH)#.replace("\\","\\\\"))
	exp = exp.replace("_SRCEXT_",SRC_EXT)

	return exp
#@+node:ekr.20060513122450.39: *5* TraceBack
if 0:
    def TraceBack():
        typ,val,tb = sys.exc_info()
        lines = traceback.format_exception(typ,val,tb)
        for line in lines:
            # g.es(line,color = "red")
            g.pr(line)

TraceBack = g.es_exception
#@+node:ekr.20060513122450.35: *5* Warning
def Warning(module,warning):

	g.es(module,newline = False,color = "blue")
	g.es(warning,color = "orange")
#@+node:ekr.20060513122450.42: ** Classes
#@+node:ekr.20060513141418: *3* class controllerClass
class controllerClass:

    #@+others
    #@+node:ekr.20060513142641.2: *4* controller.ctor
    def __init__ (self,c):

        self.c = c

        #@+others
        #@+node:ekr.20060513122450.7: *5* Xcc Core
        self.XCC_INITED = False

        self.ACTIVE_NODE = None
        self.ACTIVE_DICT = None
        self.ACTIVE_PROCESS = None

        self.SELECTED_NODE = None
        self.SELECTED_DICT = None

        self.LOCATE_CHILD = True
        self.CHILD_NODE = None
        self.CHILD_DICT = {}
        self.CHILD_LINE = None
        self.CHILD_EXT = None

        self.Parser = None
        #@+node:ekr.20060513122450.8: *5* Browse Info
        self.NAME = ""
        self.EXT = ""
        self.SRC_EXT = ""
        self.ABS_PATH = ""
        self.REL_PATH = ""
        self.CWD = ""
        self.PARSE_ERROR = ""
        self.PARSE_ERROR_NODE = None
        #@+node:ekr.20060513122450.10: *5* Compile Info
        self.FIRST_ERROR = False
        self.CPL = {}
        #@+node:ekr.20060513122450.11: *5* Debug Info
        self.DBG = None

        self.DEBUGGER = ""
        self.TARGET_PID = ""

        self.DBG_RUNNING = False
        self.DBG_PROMPT = False

        self.DBG_TASK = []
        self.DBG_SD = []
        self.DBG_RD = []
        self.PROMPT_RD = []

        self.DBG_STEPPING = False
        self.WATCH_TASK = None

        #	pipe char buffering
        self.OutBuff = ""
        self.ErrBuff = ""
        #@+node:ekr.20060513122450.12: *5* Execute Info
        self.EXE = None
        #@+node:ekr.20060513122450.13: *5* Options
        self.FILTER_OUTPUT = False
        self.VERBOSE = False
        self.OPTS = {}
        #@+node:ekr.20060513122450.14: *5* Widgets
        self.ToolBar = None
        self.BreakBar = None
        self.Watcher = None
        self.Config = None
        #@-others

        self.initXcc(c)
    #@+node:ekr.20060513122450.391: *4* initXcc
    def initXcc(self,c):

        cc = self

        cc.CWD = os.getcwd()
        cc.LeoTop = c
        cc.LeoFrame = c.frame	

        cc.LeoBodyText = cc.LeoFrame.body.bodyCtrl
        cc.LeoYBodyBar = cc.LeoFrame.body.bodyBar.leo_bodyBar
        cc.LeoXBodyBar = cc.LeoFrame.body.bodyXBar.leo_bodyXBar

        cc.LeoFont = cc.LeoBodyText["font"]
        cc.LeoWrap = cc.LeoBodyText["wrap"]

        cc.Config = ConfigClass(cc)
        cc.BreakBar = BreakbarClass(cc)
        cc.Watcher = WatcherClass(cc)
        cc.ToolBar = ToolbarClass(cc) # must be created after BreakBar.
    #@+node:ekr.20060513152023: *4* controller event handlers
    #@+node:ekr.20060513152032.3: *5* onSelect
    def onSelect(self):

        cc = self ; p = cc.c.p

        if IsXcc(p):
            cc.sSelect(p)
            cc.cSelect()
        else:
            p2 = GetXccNode(p)
            if p2:
                if p2 != cc.SELECTED_NODE:
                    cc.sSelect(p2)
                cc.cSelect(p)			
            else:
                cc.sSelect()
                cc.cSelect()
    #@+node:ekr.20060513152032.4: *5* onIdle
    def onIdle(self):

        cc = self
        crash = None

        try:
            cc.UpdateProcess()
            cc.BreakBar.IdleUpdate()
        except Exception:
            if crash:
                TraceBack()
                crash.do(None)
    #@+node:ekr.20060513152032.5: *5* onCommand2
    def onCommand2(self,keywords):

        cc = self

        if keywords.get("label") in ["undo","redo"]:
            if cc.SELECTED_NODE:
                cc.BreakBar.bodychanged = True
    #@+node:ekr.20060513152032.6: *5* onBodyDoubleClick
    def onBodyDoubleClick(self):

        cc = self

        if cc.SELECTED_NODE == cc.c.p:
            cc.sGoToError()
    #@+node:ekr.20060513152032.7: *5* onBodyKey2
    def onBodyKey2(self,keywords):

        cc = self ; ch = keywords.get("ch")

        cc.LeoBodyText.tag_delete("xcc_error")
        if cc.CHILD_NODE and ch in ["\r","",str(chr(8))]:
            cc.BreakBar.BreaksFromTags()
    #@+node:ekr.20060513152032.8: *5* onHeadKey2
    def onHeadKey2(self,keywords):

        cc = self ; p = cc.c.p

        if IsXcc(p):
            if not cc.SELECTED_NODE:
                cc.sSelect(p)
                cc.sInitDict()
            else:
                cc.sGetBrowseInfo()
        else:
            ch = keywords.get("ch")
            if cc.CHILD_NODE and ch == "\r":
                cc.cSelect(cc.CHILD_NODE)
    #@+node:ekr.20060513152032.9: *5* onQuit
    def onQuit(self):

        cc = self

        if cc.ACTIVE_NODE:
            cc.GoToNode(cc.ACTIVE_NODE)
            cc.aStop()
            while cc.ACTIVE_NODE:
                cc.UpdateProcess()
    #@+node:ekr.20060514122829: *4* Utility
    #@+node:ekr.20060513122450.322: *5* Child Node Funcs
    #@+node:ekr.20060513122450.323: *6* cIs
    def cIs(self,node):

        for p in node.parents():
            if p.h[0:5] == "@xcc ":
                return True	
        return False
    #@+node:ekr.20060513122450.324: *6* cSet
    def cSet(self,name,value):

        cc = self
        cc.CHILD_DICT[name] = value
    #@+node:ekr.20060513122450.325: *6* cGet
    def cGet(self,name,init=""):

        cc = self

        if name not in cc.CHILD_DICT:
            cc.cSet(name,init)

        return cc.CHILD_DICT[name]
    #@+node:ekr.20060513122450.326: *6* cSelect
    def cSelect(self,node=None):

        cc = self

        if node:
            cc.Config.Hide()
            cc.CHILD_NODE = node
            cc.CHILD_DICT = cc.cGetDict()
            if cc.LOCATE_CHILD:
                loc = LocatorClass(cc,cc.CHILD_NODE,1)
                cc.CHILD_EXT = loc.FOUND_FILE_EXT
                cc.CHILD_LINE = loc.FOUND_FILE_LINE								
                cc.BreakBar.Show()
                if loc.FOUND_FILE_EXT:
                    cc.ToolBar.SyncDisplayToChild(loc)
                else:
                    cc.ToolBar.SyncDisplayToError()
        elif cc.CHILD_NODE:
            cc.BreakBar.Hide()
            cc.CHILD_NODE = None
            cc.CHILD_DICT = {}
            cc.CHILD_LINE = None
            cc.CHILD_EXT = None
    #@+node:ekr.20060513122450.327: *6* cGetDict
    def cGetDict(self,node=None):#Get xcc child dict alias "xcc_child_cfg" in ua	

        cc = self

        if node: node =	cc.CHILD_NODE
        if not node: return {}

        v = node.v
        if not hasattr(v,"unknownAttributes"):
            v.unknownAttributes = {}		

        if "xcc_child_cfg" not in v.unknownAttributes:
            v.unknownAttributes["xcc_child_cfg"] = {}

        return v.unknownAttributes.get("xcc_child_cfg")
    #@+node:ekr.20060513122450.31: *5* GoToNode
    def GoToNode(self,node,index=None,tagcolor=None):

        if not node: return
        cc = self ; c = cc.c ; w = cc.LeoBodyText

        if not node.isVisible(c):
            for p in node.parents():
                p.expand()
        c.selectPosition(node)
        c.redraw()

        if index is None: return
        w.mark_set("insert",index)
        w.see(index)

        if tagcolor is None: return 
        l,c = w.index("insert").split(".")
        w.tag_add("xcc_error",l+".0",l+".end")
        w.tag_config("xcc_error",background=tagcolor)
        w.tag_raise("xcc_error")
    #@+node:ekr.20060513122450.392: *5* UpdateProcess
    def UpdateProcess():

        g.trace(cc.ProcessList)

        cc = self
        if cc.ProcessList:
            process = cc.ProcessList[0]
            if process.Update():
                return
            if process.Close():
                cc.ProcessList = [] 
            else:
                cc.ProcessList.pop(0)
                if cc.ProcessList:
                    if not cc.ProcessList[0].Open():
                        cc.ProcessList = []
    #@+node:ekr.20060513122450.295: *4* Selected Node Funcs
    #@+node:ekr.20060513122450.296: *5* sGatherInfo NOT CALLED
    def sGatherInfo(self):

        cc = self

        g.trace(cc.SELECTED_NODE)

        if cc.SELECTED_NODE:
            cc.sExtractHeadInfo()

            #@+others
            #@+node:ekr.20060513122450.297: *6* Head
            cc.NAME = cc.sGet("NAME")
            cc.EXT = cc.sGet("EXT")
            cc.REL_PATH = cc.sGet("REL_PATH")
            cc.ABS_PATH = cc.sGet("ABS_PATH")
            cc.CWD = os.getcwd()

            if not cc.NAME:
                return Error("xcc: ","Node have no name!")
            #@+node:ekr.20060513122450.298: *6* Dicts
            cc.OPTS = cc.sGet("Options")
            cc.CPL = cc.sGet("Compiler")
            cc.DBG = cc.sGet("Debugger")
            cc.EXE = cc.sGet("Executable")
            #@+node:ekr.20060513122450.299: *6* File Creation
            cc.CREATE_FILES = cc.OPTS.get("Create files")

            if cc.CREATE_FILES:

                if cc.REL_PATH and os.access(cc.REL_PATH,os.F_OK) != 1:
                    os.makedirs(cc.REL_PATH)

                if cc.EXT == "h": cc.SRC_EXT = cc.EXT

                if cc.EXT == "exe": cc.SRC_EXT = "cpp"

                if cc.EXT == "cpp" or cc.EXT == "c":
                    cc.SRC_EXT = cc.EXT

                if cc.EXT == "dll": cc.SRC_EXT = "cpp"
            #@+node:ekr.20060513122450.300: *6* Compilation
            cc.COMPILE = cc.OPTS.get("Compile")

            if cc.COMPILE:
                cc.COMPILER = cc.CPL.get("Compiler")
                if not cc.COMPILER:
                    return Error("xcc: ","Compiler is undefined!")
            #@+node:ekr.20060513122450.301: *6* Execution
            cc.EXECUTE = cc.OPTS.get("Execute")
            #@+node:ekr.20060513122450.302: *6* Debugging
            cc.DEBUG = cc.OPTS.get("Debug")

            if cc.DEBUG:
                cc.DEBUGGER = cc.DBG.get("Debugger")
                if not cc.DEBUGGER:
                    return Error("xcc: ","Debugger is undefined!")

                if cc.OPTS.get("Seek breapoints") and not cc.DBG.get("Breaks start index"):
                    Warning("xcc: ","Breaks start index is undefined, using 0")
                    cc.DBG["Breaks start index"] = "0"
            #@-others

            cc.VERBOSE = cc.OPTS.get("Xcc verbose")
            cc.FILTER_OUTPUT = cc.OPTS.get("Filter output")
            return True

        return False
    #@+node:ekr.20060513122450.303: *5* sExtractHeadInfo
    def sExtractHeadInfo (self):

        cc = self

        w = cc.SELECTED_NODE.h [5:]
        if w:
            path, name = os.path.split(w)
            name, ext = os.path.splitext(name)
            ext = ext.lower().replace(".","") or 'exe'
        else:
            path, name, ext = '', '', ''

        cc.sSet("REL_PATH",path)
        cc.sSet("NAME",name)
        cc.sSet("EXT",ext)
        theDir = g.choose(path,cc.CWD+"\\"+path,cc.CWD)
        cc.sSet("ABS_PATH",theDir)
    #@+node:ekr.20060513122450.304: *5* sGetBrowseInfo
    def sGetBrowseInfo (self):

        cc = self

        w = cc.SELECTED_NODE.h [5:]
        if w:
            cc.REL_PATH, cc.NAME = os.path.split(w)
            cc.NAME, EXT = os.path.splitext(cc.NAME)
            cc.EXT = EXT.lower().replace(".","") or 'exe'
        else:
            cc.REL_PATH, cc.NAME, cc.EXT = '', '', 'exe'

        cc.CWD = cc.ABS_PATH = os.getcwd()

        if cc.REL_PATH: cc.ABS_PATH = cc.ABS_PATH + "\\" + cc.REL_PATH

        if cc.EXT == "h": cc.SRC_EXT = cc.EXT
        if cc.EXT == "exe": cc.SRC_EXT = "cpp"
        if cc.EXT in ('c','cpp'): cc.SRC_EXT = cc.EXT
        if cc.EXT == "dll": cc.SRC_EXT = "cpp"

        cc.PTS = cc.sGet("Options",{})
    #@+node:ekr.20060513122450.305: *5* sGetWriteInfo
    def sGetWriteInfo(self):

        cc = self

        if cc.NAME == "":
            return Error("xcc: ","Node have no name!")

        if cc.REL_PATH != "" and os.access(cc.REL_PATH,os.F_OK) != 1:
            os.makedirs(cc.REL_PATH)

        cc.COD = cc.sGet("Code")	
        #FILE_HDR = COD["File header"]
        #FILE_FTR = COD["File footer"]
        #CLASS_HDR = COD["Class header"]
        #CLASS_FTR = COD["Class footer"]
        #CLASS_OPN = COD["Class opening"]
        #CLASS_END = COD["Class closing"]
        if not cc.CLASS_OPN: cc.CLASS_OPN = "{\n"	
        if not cc.CLASS_END: cc.CLASS_END = "};\n"
        #FUNC_HDR = COD["Function header"]
        #FUNC_FTR = COD["Function footer"]
        #FUNC_OPN = COD["Function opening"]
        #FUNC_END = COD["Function closing"]
        if not cc.FUNC_OPN: cc.FUNC_OPN = "{\n"	
        if not cc.FUNC_END: cc.FUNC_END = "}\n"
        return True
    #@+node:ekr.20060513122450.306: *5* sGetCompileInfo
    def sGetCompileInfo(self):

        cc = self
        cc.CPL = cc.sGet("Compiler")

        g.trace(cc.CPL)

        if not cc.CPL.get("Compiler"):
            return Error("xcc: ","No compiler defined!")

        cc.VERBOSE = cc.OPTS.get("Xcc verbose")
        return True

    #@+node:ekr.20060513122450.307: *5* sGetDebugInfo
    def sGetDebugInfo(self):

        cc = self

        cc.DBG = cc.sGet("Debugger")
        if cc.DBG["Debugger"]:
            cc.VERBOSE = cc.OPTS.get("Xcc verbose")
            return True
        else:
            return Error("xcc: ","No debugger defined!")
    #@+node:ekr.20060513122450.308: *5* sGetExecInfo
    def sGetExecInfo():

        cc = self

        cc.EXE = cc.sGet("Executable")		
        return True
    #@+node:ekr.20060513122450.309: *5* sGoToError
    def sGoToError(self,e=None):

        cc = self

        mask = [" ",":","(",")"]
        if e == None:
            row,col = cc.LeoBodyText.index("insert").split(".")
            row = int(row)
            col = int(col)
            lines = cc.SELECTED_NODE.b.splitlines()
            e = lines[row-1]
            e=e.replace("/","\\")

        edexp = cc.CPL.get("Error detection")
        m = re.search(edexp,e,re.IGNORECASE)
        if m != None:
            try:
                file = m.group("FILE")
                line = m.group("LINE")
                id = m.group("ID")
                edef = m.group("DEF")
                path,name = os.path.split(CPL["Compiler"])
                Error(name+" : ","Error: "+id+" in "+file+" line "+line+" : "+edef)

            except Exception:
                Warning("xcc: ","Unable to process error detection!")
                return

            name,ext = os.path.splitext(file)
            if name == cc.NAME:
                SeekErrorClass(cc,int(line),ext.replace(".",""),color=ErrorColor)
    #@+node:ekr.20060513122450.310: *5* sGo
    def sGo(self):	#this is where the selected node also become the active node

        cc = self

        if not cc.NAME:
            return Error("xcc: ","Node has no name!")

        cc.sSetText("@language c++\n")

        if not cc.CreateFiles() or not cc.Compile():
            return False
        if cc.OPTS.get("Execute") == "True" and cc.OPTS.get("Debug") == "False":
            if not cc.Execute():
                return False
        if cc.OPTS.get("Debug") == "True":
            if not cc.Debug():
                return False
        return True
    #@+node:ekr.20060513122450.311: *5* sSet
    def sSet (self,name,value):

        cc = self

        cc.SELECTED_DICT [name] = value
    #@+node:ekr.20060513122450.312: *5* sGet
    def sGet(self,name,init=""):

        cc = self

        if name not in cc.SELECTED_DICT:
            cc.sSet(name,init)

        return cc.SELECTED_DICT[name]
    #@+node:ekr.20060513122450.313: *5* sIsDict
    def sIsDict(self):

        cc = self

        if not cc.SELECTED_NODE:
            return False

        v = cc.SELECTED_NODE.v	

        return hasattr(v,"unknownAttributes") and "xcc_cfg" in v.unknownAttributes
    #@+node:ekr.20060513122450.314: *5* sGetDict
    def sGetDict(self): # Get xcc parent dict alias "xcc_cfg" in ua

        cc = self

        if not cc.SELECTED_NODE:
            return None

        v = cc.SELECTED_NODE.v

        if not hasattr(v,"unknownAttributes"):
            v.unknownAttributes = {}

        if "xcc_cfg" in v.unknownAttributes:
            return v.unknownAttributes["xcc_cfg"]
        else:
            v.unknownAttributes["xcc_cfg"] = d = {}
            return d
    #@+node:ekr.20060513122450.315: *5* sInitDict
    def sInitDict(self):

        cc = self

        Warning("xcc: ","Writing blank configuration!")
        cc.sSetText("@language c++")
        cc.Config.ClearConfig()
        cc.Config.SaveToNode()
        cc.sSet("INITED","True")



    #@+node:ekr.20060513122450.316: *5* sSelect
    def sSelect(self,node=None):

        cc = self ; c = cc.c

        if node:
            if cc.SELECTED_NODE:
                cc.Config.Hide()
                if cc.SELECTED_NODE:
                    cc.SELECTED_NODE = node		
            else:
                cc.SELECTED_NODE = node

            cc.SELECTED_DICT = cc.sGetDict()

            if cc.SELECTED_NODE != cc.ACTIVE_NODE and cc.SELECTED_NODE.isMarked():
                cc.SELECTED_NODE.clearMarked()
                c.redraw()

            cc.sGetBrowseInfo()
            cc.sShow()
        elif cc.SELECTED_NODE:
            cc.Config.Hide()
            cc.sHide()
            cc.SELECTED_NODE = None
            cc.SELECTED_DICT = cc.sGetDict()
    #@+node:ekr.20060513122450.317: *5* sSync
    def sSync(self):

        cc = self

        cc.SELECTED_DICT = cc.sGetDict()
        if cc.SELECTED_DICT:
            cc.sExtractHeadInfo()

        cc.CHILD_DICT = cc.cGetDict()
    #@+node:ekr.20060513122450.318: *5* sShow
    def sShow(self):

        cc = self
        cc.LeoBodyText.pack_forget()
        cc.LeoYBodyBar.pack_forget()

        cc.ToolBar.Show()
        cc.LeoXBodyBar.pack(side="bottom",fill="x")
        cc.LeoYBodyBar.pack(side="right",fill="y")
        cc.LeoBodyText.pack(fill="both",expand=1)
        cc.LeoBodyText["wrap"] = 'none'

        cc.ToolBar.Spacer["state"] = 'normal'
        cc.ToolBar.Spacer.delete('1.0','end')
        cc.ToolBar.Spacer.insert("insert","."+cc.EXT)
        cc.ToolBar.Spacer["state"] = 'disabled'

        cc.ToolBar.Display["state"] = 'normal'
        cc.ToolBar.Display.delete('1.0','end')
        cc.ToolBar.Display["state"] = 'disabled'

        cc.Watcher.Sync()
    #@+node:ekr.20060513122450.319: *5* sHide
    def sHide(self):

        cc = self

        cc.LeoXBodyBar.pack_forget()
        cc.ToolBar.Hide()
        cc.LeoBodyText["wrap"]=cc.LeoWrap
    #@+node:ekr.20060513122450.320: *5* sSetText
    def sSetText(self,text=""):

        cc = self

        cc.setBodyText(SELECTED_NODE,text)
    #@+node:ekr.20060513122450.321: *5* sAddText
    def sAddText(self,text):

        cc = self

        cc.setBodyText(SELECTED_NODE,cc.SELECTED_NODE.b+text)

        if not cc.CHILD_NODE:
            l,c = cc.LeoBodyText.index("end").split(".")
            cc.LeoBodyText.see(l+".0")
    #@+node:ekr.20060513122450.281: *4* Active Node Funcs
    #@+node:ekr.20060513122450.282: *5* aSet
    def aSet(self,name,value):

        cc = self

        cc.ACTIVE_DICT[name] = value
    #@+node:ekr.20060513122450.283: *5* aGet
    def aGet(self,name,init=""):

        cc = self

        if name not in cc.ACTIVE_DICT:
            cc.aSet(name,init)

        return cc.ACTIVE_DICT[name]
    #@+node:ekr.20060513122450.284: *5* aGetDict
    def aGetDict(self):

        '''Get xcc parent dict alias "xcc_cfg" in uA.'''

        cc = self

        if not cc.ACTIVE_NODE:
            return None

        v = cc.ACTIVE_NODE.v	
        if not hasattr(v,"unknownAttributes"):
            v.unknownAttributes = {}

        if "xcc_cfg" not in v.unknownAttributes:
            v.unknownAttributes["xcc_cfg"] = {}

        return v.unknownAttributes.get("xcc_cfg")
    #@+node:ekr.20060513122450.285: *5* aGo
    def aGo(self):

        g.trace()

        cc = self

        if cc.ACTIVE_NODE:
            s = cc.DBG.get("Continue")
            if s:
                cc.aWrite(s)
                cc.LeoBodyText.tag_delete("xcc_error")
                cc.ToolBar.DisableStep()
    #@+node:ekr.20060513122450.286: *5* aStop
    def aStop(self):

        cc = self

        if not cc.ACTIVE_NODE or not cc.ACTIVE_PROCESS:
            return Error("xcc: ","Current xcc node is not active!")

        if cc.ACTIVE_NODE == cc.SELECTED_NODE and cc.TARGET_PID:
            stop = cc.DBG.get("Stop")
            if cc.DBG_PROMPT:
                if stop: cc.aWrite(stop)
            else:
                pause(cc.TARGET_PID)
                if stop: cc.DBG_TASK.append(DBGTASK(cc,stop))					

            cc.LeoBodyText.tag_delete("xcc_error")
            if cc.WATCH_TASK: cc.WATCH_TASK.Cancel()
    #@+node:ekr.20060513122450.287: *5* aStepIn
    def aStepIn(self):

        cc = self

        if (
            cc.ACTIVE_NODE and cc.ACTIVE_PROCESS and
            cc.ACTIVE_NODE == cc.SELECTED_NODE and
            cc.DBG["Step in"] != "" and cc.DBG_PROMPT
        ):
            cc.DBG_STEPPING = True
            cc.aWrite(DBG["Step in"])
            cc.ToolBar.DisableStep()
            cc.LeoBodyText.tag_delete("xcc_error")
            cc.DBG_TASK.append(QUERYGOTASK(cc))
    #@+node:ekr.20060513122450.288: *5* aStepOver
    def aStepOver(self):

        cc = self

        if (
            cc.ACTIVE_NODE and cc.ACTIVE_PROCESS and
            cc.ACTIVE_NODE == cc.SELECTED_NODE and
            cc.DBG.get("Step in") and cc.DBG_PROMPT
        ):
            cc.DBG_STEPPING = True			
            cc.aWrite(DBG["Step over"])
            cc.ToolBar.DisableStep()
            cc.LeoBodyText.tag_delete("xcc_error")
            cc.DBG_TASK.append(QUERYGOTASK(cc))
    #@+node:ekr.20060513122450.289: *5* aStepOut
    def aStepOut(self):

        cc = self

        if (
            cc.ACTIVE_NODE and cc.ACTIVE_PROCESS and
            cc.ACTIVE_NODE == cc.SELECTED_NODE and
            cc.DBG.get("Step in") and cc.DBG_PROMPT
        ):
            cc.DBG_STEPPING = True
            cc.aWrite(DBG["Step out"])
            cc.ToolBar.DisableStep()
            cc.LeoBodyText.tag_delete("xcc_error")
            cc.DBG_TASK.append(QUERYGOTASK(cc))
    #@+node:ekr.20060513122450.290: *5* aPause
    def aPause(self):

        cc = self

        if not cc.ACTIVE_NODE or not cc.ACTIVE_PROCESS:
            Error("xcc: ","Current xcc node is not active!")

        elif cc.ACTIVE_NODE == cc.SELECTED_NODE and cc.TARGET_PID:
            pause(cc.TARGET_PID)
    #@+node:ekr.20060513122450.291: *5* aWrite
    def aWrite(self,text):

        cc = self

        if not cc.FILTER_OUTPUT:
            cc.aAddText(text+"\n")

        eol = "" ; code = "eol = \""+cc.DBG["Pipe eol"]+"\""
        try:
            exec(code)
        except:
            TraceBack()
        if eol == "": eol = "\n"

        cc.ACTIVE_PROCESS.In.write(text+eol)
        cc.ACTIVE_PROCESS.In.flush()
        cc.DBG_PROMPT = False
        cc.ToolBar.PauseButton["state"] = 'normal'
        cc.ToolBar.HideInput()
    #@+node:ekr.20060513122450.292: *5* aSelect
    def aSelect(self,node=None):

        cc = self

        cc.ACTIVE_NODE = node
        cc.ACTIVE_DICT = cc.aGetDict()
    #@+node:ekr.20060513122450.293: *5* aSetText
    def aSetText(self,text=""):

        cc = self

        if cc.ACTIVE_NODE:
            cc.setBodyText(ACTIVE_NODE,text)
    #@+node:ekr.20060513122450.294: *5* aAddText
    def aAddText(self,text):

        cc = self

        if cc.ACTIVE_NOD:
            cc.setBodyText(cc.ACTIVE_NODE,cc.ACTIVE_NODE.b+text)

            if cc.SELECTED_NODE == cc.ACTIVE_NODE and cc.CHILD_NODE:
                l,c = LeoBodyText.index("end").split(".")
                cc.LeoBodyText.see(l+".0")
    #@+node:ekr.20060513122450.328: *4* Action Funcs
    #@+node:ekr.20060513122450.329: *5* CreateFiles
    def CreateFiles(self):

        cc = self

        g.trace(cc.OPTS)

        if cc.OPTS.get("Create files"):
            return cc.sGetWriteInfo() and WriterClass(cc).Result
        else:
            return None
    #@+node:ekr.20060513122450.330: *5* Compile
    def Compile(self):

        cc = self
        g.trace(cc.OPTS.get("Compile"))

        if not cc.OPTS.get("Compile"):
            return None
        if not cc.sGetCompileInfo():
            return False
        if len(ProcessList) > 1:
            return Error("xcc: ","already running!")

        process = cc.ProcessClass(cc,
            cc.SELECTED_NODE,
            cc.CPL.get("Compiler"),
            cc.CplCmd(),
            start=cc.CplStart,out=cc.CplOut,err=cc.CplErr,end=cc.CplEnd)

        ok = process.Open()
        if ok: cc.ProcessList.append(process)
        return ok
    #@+node:ekr.20060513122450.331: *5* CplCmd
    def CplCmd(self):

        g.trace()

        cc = self
        cwd = os.getcwd()

        if cc.OPTS.get("Debug"):
            cmd = cc.CPL["Debug arguments"]
        else:
            cmd = cc.CPL["Arguments"]

        cmd = cc.ReplaceVars(cmd.replace("\n"," ").strip())

        #@+others
        #@+node:ekr.20060513122450.332: *6* _INCPATHS_
        s = cc.CPL.get("Include path")
        if s:
            sym = s
            paths = cc.CPL.get("Include search paths",'').splitlines()
            cc.INCPATHS = ""
            for p in paths:
                if p != "":
                    cc.INCPATHS += " "+sym+"\""+p+"\""
            cmd = cmd.replace("_INCPATHS_",cc.INCPATHS.strip())
        #@+node:ekr.20060513122450.333: *6* _LIBPATHS_
        s = cc.CPL.get("Library path")
        if s:
            sym = s
            paths = cc.CPL.get("Library search paths",'').splitlines()
            cc.LIBPATHS = ""
            for p in paths:
                if p != "":
                    cc.LIBPATHS += " "+sym+"\""+p+"\""
            cmd = cmd.replace("_LIBPATHS_",cc.LIBPATHS.strip())
        #@+node:ekr.20060513122450.334: *6* _LIBRARIES_
        s = cc.CPL.get("Use library")
        if s:
            sym = s
            libs = cc.CPL.get("Used libraries",'').split()
            cc.LIBRARIES = ""
            for l in libs:
                if l != "":
                    cc.LIBRARIES += " "+sym+"\""+l+"\""
            cmd = cmd.replace("_LIBRARIES_",cc.LIBRARIES.strip())
        #@+node:ekr.20060513122450.335: *6* _BUILD_
        if cc.EXT == "exe":
            s = cc.CPL.get("Build exe")
            if s: cmd = cmd.replace("_BUILD_",s)

        if cc.EXT == "dll":
            s = CPL.get("Build dll")
            if s:
                cmd = cmd.replace("_BUILD_",s)
            else:
                Warning("xcc: ","Build dll requested but compiler build dll symbol is undefined!")
        #@-others

        return cmd


    #@+node:ekr.20060513122450.336: *5* Debug
    def Debug(self):

        g.trace()

        cc = self

        if cc.GetDebugInfo() and cc.EXT == "exe":
            p = ProcessClass(cc,
                cc.SELECTED_NODE,
                cc.DBG.get("Debugger"),
                cc.DbgCmd(),
                start=cc.DbgStart,
                out=cc.DbgOut,
                err=cc.DbgErr,
                end=cc.DbgEnd)
            cc.ProcessList.append(p)
    #@+node:ekr.20060513122450.337: *5* DbgCmd
    def DbgCmd(self):

        cc = self

        cmd = cc.DBG.get("Arguments").replace("\n"," ").strip()
        cmd = cc.ReplaceVars(cmd)

        g.trace(repr(cmd))
        return cmd
    #@+node:ekr.20060513122450.338: *5* Execute
    def Execute(self):

        g.trace()

        cc = self
        cc.sGetExecInfo()
        cmd = cc.ABS_PATH+"\\"+cc.NAME+"."+cc.EXT
        args = cc.EXE.get("Execution arguments")

        if cc.OPTS.get("Connect to pipe"):
            process = ProcessClass(cc,
                cc.SELECTED_NODE,cmd,args,
                start=cc.ProgStart,out=cc.ProgOut,
                err=cc.ProgErr,end=cc.ProgEnd)
        else:
            process = ProcessClass(cc,cc.SELECTED_NODE,cmd,args,spawn=True)

        cc.ProcessList.append(process)
    #@+node:ekr.20060513122450.339: *4* Compiler Events
    #@+node:ekr.20060513122450.340: *5* CplStart
    def CplStart(self):

        g.trace()

        cc = self
        cc.OutBuff = ""
        cc.ErrBuff = ""
        cc.FIRST_ERROR = False
        cc.aSelect(cc.SELECTED_NODE)
        process = cc.VProcessList[0]

        text = ""	
        if cc.VERBOSE:
            text += "\" Starting "+process.FileName+"...\n"
            text += "\" using arguments: "+process.Arguments+"\n"		
        text += "\""+("="*60)+"\n"

        cc.aAddText(text)

    #@+node:ekr.20060513122450.341: *5* CplOut
    def CplOut(self,text):

        g.trace(repr(text))

        cc = self
        cc.OutBuff += text
        lines = cc.OutBuff.splitlines(True)
        if lines[-1][-1] != "\n":
            cc.OutBuff = lines.pop()
        else:
            cc.OutBuff = ""

        text = ""	
        for l in lines:
            if l != "":
                if l.lower().find("error") > -1:
                    text += "// "+l
                    if cc.OPTS.get("Seek first error") and cc.FIRST_ERROR == False:
                        cc.FIRST_ERROR = True
                        cc.sGoToError(l)
                else:
                    if not cc.FILTER_OUTPUT:
                        text += "# "+l

        cc.aAddText(text)

    #@+node:ekr.20060513122450.342: *5* CplErr
    def CplErr(self,text):

        g.trace(repr(text))

        cc = self

        cc.ErrBuff += text
        lines = cc.ErrBuff.splitlines(True)
        if lines[-1][-1] != "\n":
            cc.ErrBuff = lines.pop()
        else:
            cc.ErrBuff = ""

        text = ""	
        for l in lines:
            text += "// "+l+"\n"

        cc.aAddText(text)
    #@+node:ekr.20060513122450.343: *5* CplEnd
    def CplEnd(self,exitcode):

        g.trace(repr(exitcode))

        cc = self

        text = "\""+("="*60)+"\n"
        if exitcode == None:
            text += "\" Build process successful!\n"
        else:
            text += "// Build process aborted!\n"
        text += "\""+("-"*60)+"\n"

        cc.aAddText(text)
        cc.aSelect()
    #@+node:ekr.20060513122450.344: *4* Debugger Events
    #@+node:ekr.20060513122450.379: *5* DbgStart
    def DbgStart(self):

        g.trace()
        cc = self
        cc.OutBuff = ""
        cc.ErrBuff = ""
        cc.ACTIVE_PROCESS=cc.ProcessList[0]
        cc.PROMPT_RD = []
        cc.DBG_STEPPING = False
        cc.DBG_PROMPT = False
        cc.TARGET_PID = ""
        cc.aSelect(cc.SELECTED_NODE)
        # set buttons
        cc.ToolBar.PauseButton["state"] = 'normal'
        cc.ToolBar.StopButton["state"] = 'normal'
        # startup banner
        text = ""	
        if cc.VERBOSE:
            text += "\" Starting "+cc.ACTIVE_PROCESS.FileName+"...\n"
            text += "\" using arguments: "+cc.ACTIVE_PROCESS.Arguments+"\n"
        text += "\""+("="*60)+"\n"
        cc.aAddText(text)
        cc.DBG_TASK = []
        cc.DBG_SD = []
        cc.DBG_RD = []
        OUTPUTTASK(cc)
        st = ReplaceVars(DBG["Startup task"]).splitlines()
        for t in st:
            DBGTASK(t)
        TARGETPIDTASK(cc)
        REGEXPTASK(cc)

        BREAKTASK(cc)
        DBGTASK(cc,DBG["Continue"])
    #@+node:ekr.20060513122450.380: *5* DbgOut
    def DbgOut(text):

        g.trace(repr(text))

        cc = self

        #Extract output lines and prompt
        if text:
            cc.OutBuff += text
            lines = OutBuff.splitlines(True)
            if lines[-1][-1] != "\n":
                cc.OutBuff = lines.pop()
            else:
                cc.OutBuff = ""

            # sending output to SENT tasks
            for l in lines:
                for r in cc.DBG_RD:
                    r(l)		

        # detect the prompt
        if cc.OutBuff and re.search(cc.DBG.get("Prompt pattern"),cc.OutBuff) != None:
            cc.ToolBar.PauseButton["state"] = 'disabled'
            for prd in cc.PROMPT_RD:
                prd()
            cc.DBG_PROMPT = True
            if cc.DBG_STEPPING:
                cc.DBG_STEPPING = False
                cc.ToolBar.EnableStep()
            if not cc.FILTER_OUTPUT:
                cc.AddText("# "+cc.OutBuff)
            cc.OutBuff = ""

        # send task to the debugger
        while cc.DBG_PROMPT and len(cc.DBG_SD) > 0:
            cc.DBG_SD[0]()

        if cc.DBG_PROMPT:
            cc.ToolBar.ShowInput()
    #@+node:ekr.20060513122450.381: *5* DbgErr
    def DbgErr(self,text):

        g.trace(repr(text))

        cc = self
        cc.ErrBuff += text
        lines = cc.ErrBuff.splitlines(True)
        if lines[-1][-1] != "\n":
            cc.ErrBuff = lines.pop()
        else:
            cc.ErrBuff = ""

        text = ""	
        for l in lines:
            text += "//err: "+l

        cc.aAddText(text)
    #@+node:ekr.20060513122450.382: *5* DbgEnd
    def DbgEnd(self,exitcode):

        cc = self
        text = "\""+("="*60)+"\n"
        if exitcode == None:
            text += "\" Debug session ended successfully!\n"
        else:
            text += "// Debug session aborted!\n"

        text += "\""+("-"*60)+"\n"

        cc.aAddText(text)
        cc.ToolBar.PauseButton["state"] = 'disabled'
        cc.ToolBar.StopButton["state"] = 'disabled'
        cc.ACTIVE_PROCESS = None
        cc.DBG_TASK = []
        cc.ToolBar.DisableStep()
        cc.LeoBodyText.tag_delete("xcc_error")	
        cc.TARGET_PID = ""
        cc.aSelect()
    #@+node:ekr.20060513122450.383: *4* Program Events
    #@+node:ekr.20060513122450.384: *5* ProgStart
    def ProgStart(self):

        g.trace()

        cc = self
        cc.OutBuff = ""
        cc.ErrBuff = ""
        cc.aSelect(cc.SELECTED_NODE)
        cc.ACTIVE_PROCESS=cc.ProcessList[0]

        text = ""	
        if cc.VERBOSE:
            text += "\" Starting "+cc.ACTIVE_PROCESS.FileName+"...\n"
            text += "\" using arguments: "+cc.ACTIVE_PROCESS.Arguments+"\n"		
        text += "\""+("="*60)+"\n"
        cc.aAddText(text)
    #@+node:ekr.20060513122450.385: *5* ProgOut
    def ProgOut(self,text):

        g.trace(repr(text))

        cc = self
        cc.OutBuff += text
        lines,cc.OutBuff = ExtractLines(OutBuff)

        text = ""	
        for l in lines:
            if l != "":
                text += "# "+l+"\n"			

        text += "# "+cc.OutBuff
        cc.OutBuff = ""
        cc.aAddText(text)
    #@+node:ekr.20060513122450.386: *5* ProgErr
    def ProgErr(self,text):

        g.trace(repr(text))

        cc = self
        cc.ErrBuff += text
        lines,cc.ErrBuff = ExtractLines(ErrBuff)

        text = ""	
        for l in lines:
            text += "// "+l+"\n"
        text += "# "+cc.ErrBuff
        cc.ErrBuff = ""
        cc.aAddText(text)
    #@+node:ekr.20060513122450.387: *5* ProgEnd
    def ProgEnd(self,exitcode):

        g.trace(exitcode)

        cc = self
        text = "\n\""+("="*60)+"\n"
        if exitcode == None:
            text += "\" Program exited normally!\n"
        else:
            text += "// Program exited with code: "+str(exitcode)+"\n"		
        text += "\""+("-"*60)+"\n"

        cc.aAddText(text)
        cc.ACTIVE_PROCESS = None
        cc.aSelect()
    #@-others
#@+node:ekr.20060513122450.345: *3* Debugger task classes
#@+node:ekr.20060513122450.346: *4* DBGTASK
class DBGTASK:
    #@+others
    #@+node:ekr.20060513122450.347: *5* __init__
    def __init__(self,cc,cmd,index=None):

        self.cc = cc
        cc.Command = cmd

        if index:
            DBG_SD.insert(index,cc.Send)
        else:
            DBG_SD.append(cc.Send)
    #@+node:ekr.20060513122450.348: *5* Send
    def Send(self):

        cc = self

        if cc.Command:
            cc.aWrite(cc.Command)
        cc.DBG_SD.remove(cc.Send)
    #@-others
#@+node:ekr.20060513122450.349: *4* OUTPUTTASK
class OUTPUTTASK(DBGTASK):
    #@+others
    #@+node:ekr.20060513122450.350: *5* __init__
    def __init__(self,cc):

        self.cc = cc
        cc.DBG_RD.append(self.Receive)
    #@+node:ekr.20060513122450.351: *5* Send
    def Send(self):
        pass	#we just receive
    #@+node:ekr.20060513122450.352: *5* Receive
    def Receive(self,line):

        cc = self.cc

        if cc.DBG_PROMPT == False and line != "":
            lower = line.lower()
            if lower.find("error") > -1 or lower.find("warning") > -1:
                cc.aAddText("//"+line)
            else:
                if cc.OPTS["Filter output"] == "False":
                    cc.aAddText("# "+line)
    #@-others
#@+node:ekr.20060513122450.353: *4* TARGETPIDTASK
class TARGETPIDTASK(DBGTASK):
    #@+others
    #@+node:ekr.20060513122450.354: *5* __init__
    def __init__(self,cc):

        self.cc = cc
        cc.DBG_SD.append(self.Send)

        self.PidTask = ReplaceVars(cc.DBG.get("Target pid task"))
        self.FindPid = ReplaceVars(cc.DBG.get("Find pid"))
    #@+node:ekr.20060513122450.355: *5* Send
    def Send(self):

        cc = self.cc
        if self.PidTask != "":		
            cc.aWrite(ReplaceVars(self.PidTask))
            cc.DBG_SD.remove(self.Send)
            cc.DBG_RD.append(self.Receive)
        else:
            cc.DBG_SD.remove(self.Send)
            Warning("xcc: ","Target pid task is undefined!")


    #@+node:ekr.20060513122450.356: *5* Receive
    def Receive(self,line):

        cc = self.cc
        if self.FindPid:
            if not cc.DBG_PROMPT:
                if line != "":
                    m = re.search(self.FindPid,line)
                    if m != None:
                        cc.TARGET_PID = int(m.group("PID"))		
                        if cc.VERBOSE:					
                            cc.aAddText("\" Target pid is: "+str(cc.TARGET_PID)+" \n")
                        cc.DBG_RD.remove(self.Receive)

        else:
            cc.DBG_RD.remove(self.Receive)
    #@-others
#@+node:ekr.20060513122450.357: *4* BREAKTASK
class BREAKTASK(DBGTASK):
    #@+others
    #@+node:ekr.20060513122450.358: *5* __init__
    def __init__(self,cc):

        self.cc = cc
        #gathering breaks
        bf = BreakFinderClass()
        self.Breaks = aGet("Breakpoints").copy()
        if len(self.Breaks) != 0:
            self.bpsym = DBG["Set break"]
            if self.bpsym == "":
                Waning("xcc: ","Set break symbol is undefined!")
            else:
                self.bpsym = ReplaceVars(self.bpsym)
                cc.DBG_SD.append(self.Send)

        regexp = DBG["Break detection"]
        if regexp != "":		
            regexp = regexp.splitlines()
            self.RegExp = []
            for e in regexp:
                self.RegExp.append(re.compile(e))		
        else:
            Warning("xcc: ","No break detection expression defined!")
    #@+node:ekr.20060513122450.359: *5* Send
    def Send(self):
        if len(self.Breaks) > 0:
            extl,s = self.Breaks.popitem()
            ext,l = extl.split(":")
            bpat = self.bpsym
            bpat = bpat.replace("_FILE_",NAME+"."+ext).replace("_LINE_",l)
            aWrite(bpat)
        else:
            DBG_SD.remove(self.Send)
            DBG_RD.append(self.Receive)

    #@+node:ekr.20060513122450.360: *5* Receive
    def Receive(self,line):

        cc = self.cc

        for r in self.RegExp:
            if r.search(line) != None:
                if cc.OPTS.get("Seek breakpoints"):
                    QUERYGOTASK(cc,0)
                if cc.VERBOSE:
                    aAddText("\" Break detected!\n")

                if cc.Watcher.visible and cc.ACTIVE_PROCESS and cc.SELECTED_NODE == cc.ACTIVE_NODE:
                    WATCHTASK(cc)
                    if cc.DBG_PROMPT:
                        cc.DbgOut("")

                cc.ToolBar.EnableStep()						
                return
    #@-others
#@+node:ekr.20060513122450.361: *4* REGEXPTASK
class REGEXPTASK(DBGTASK):
    #@+others
    #@+node:ekr.20060513122450.362: *5* __init__
    def __init__(self,cc):

        self.cc = cc
        cc.DBG_RD.append(self.Receive)

        self.Exps = ReplaceVars(cc.DBG.get("Regular expression",'')).splitlines()
        self.Task = ReplaceVars(cc.DBG.get("Task",'')).splitlines()
        self.on = False	
    #@+node:ekr.20060513122450.363: *5* Send
    def Send(self):
        pass	#receive only



    #@+node:ekr.20060513122450.364: *5* Receive
    def Receive(self,line):

        cc = self.cc

        if not self.on:
            self.on = True ; return
        i=1
        for e in self.Exps:
            if e != "" and re.search(e,line) != None:
                if len(self.Task) >= i:
                    t = self.Task[i-1]
                else:
                    t = ""
                DBGTASK(cc,t,0)
                self.on = False
            i += 1
    #@-others
#@+node:ekr.20060513122450.365: *4* WATCHTASK
class WATCHTASK(DBGTASK):
    #@+others
    #@+node:ekr.20060513122450.366: *5* __init__
    def __init__(self,index=0):

        self.cc = cc
        self.Index = index
        cc.WATCH_TASK = self
        self.Buffer = ""
        self.Count = 0

        cc.Watcher.OutBox.tag_delete("changed")
        self.Lines = ccWatcher.InBox.get(1.0,'end').strip().splitlines()	

        if len(self.Lines) != 0:
            d=DBG_SD.append(self.Send)

        for l in self.Lines:
            if l == "":
                del l

        self.nl = ""
        self.Inited = False
    #@+node:ekr.20060513122450.367: *5* Cancel
    def Cancel(self):
        global WATCH_TASK
        if self.Send in DBG_SD:
            DBG_SD.remove(self.Send)
        if self.Receive in DBG_RD:
            DBG_RD.remove(self.Receive)
        if self.OnPrompt in PROMPT_RD:
            PROMPT_RD.remove(self.OnPrompt)

        Watcher.wastching = False
        WATCH_TASK = None

    #@+node:ekr.20060513122450.368: *5* Send
    def Send(self):
        if len(self.Lines) > 0:
            Watcher.Watching = True
            vari = self.Lines.pop(0)
            aWrite(DBG["Evaluate"]+vari)
            DBG_SD.remove(self.Send)
            DBG_RD.append(self.Receive)
            PROMPT_RD.append(self.OnPrompt)
            self.Buffer = ""
            self.Count += 1
    #@+node:ekr.20060513122450.369: *5* Receive
    def Receive(self,line):
        if DBG_PROMPT == False:		
            self.Buffer += line
    #@+node:ekr.20060513122450.370: *5* OnPrompt
    def OnPrompt(self):
        global WATCH_TASK

        Watcher.OutBox["state"] = 'normal'
        s = str(self.Count)+".0"
        e = str(self.Count)+".end"

        self.Buffer = self.Buffer.replace("\n"," ")

        if self.Buffer != Watcher.OutBox.get(s,e):
            changed = True
        else:
            changed = False

        Watcher.OutBox.delete(s,e+"+1c")
        Watcher.OutBox.insert(s,self.Buffer+"\n")	

        if changed == True:
            Watcher.OutBox.tag_add("changed",s,e)
            Watcher.OutBox.tag_config("changed",foreground ="red")

        Watcher.OutBox["state"] = 'disabled'

        if len(self.Lines) != 0:
            DBG_SD.append(self.Send)		
        else:
            Watcher.Watching = False
            WATCH_TASK = None

        PROMPT_RD.remove(self.OnPrompt)	
        DBG_RD.remove(self.Receive)

    #@-others
#@+node:ekr.20060513122450.371: *4* QUERYGOTASK
class QUERYGOTASK(DBGTASK):

    #@+others
    #@+node:ekr.20060513122450.372: *5* __init__
    def __init__(self,cc,index=None):

        self.cc = cc
        self.Query = cc.DBG.get("Query location")
        self.Find = cc.ReplaceVars(cc.DBG.get("Find location"))
        if not self.Query:
            cc.DBG_TASK.remove(self)
            Warning("xcc: ","Query location task is undefined!")
        elif index:
            cc.DBG_SD.insert(index,self.Send)
        else:
            cc.DBG_SD.append(self.Send)
    #@+node:ekr.20060513122450.373: *5* Send
    def Send(self):

        cc = self.cc
        cc.aWrite(self.Query)
        cc.DBG_SD.remove(self.Send)
        cc.DBG_RD.append(self.Receive)
    #@+node:ekr.20060513122450.374: *5* Receive
    def Receive(self,line):

        cc = self.cc
        if cc.DBG_PROMPT == False:
            if line != "":
                m = re.search(self.Find,line,re.IGNORECASE)
                if m != None:
                    bline = m.group("LINE")
                    bext = m.group("EXT")

                    if bline and bext:
                        if cc.VERBOSE:					
                            cc.aAddText("\" Current location is: "+bline+" in "+bext+" file!\n")
                        bline = int(bline)	
                        SeekErrorClass(self.cc,bline,bext,color=BreakColor)
                    cc.DBG_RD.remove(self.Receive)

                    if cc.Watcher.visible and cc.ACTIVE_PROCESS:
                        if cc.SELECTED_NODE == cc.ACTIVE_NODE:
                            WATCHTASK(cc)
                        if cc.DBG_PROMPT:
                            cc.DbgOut("")
        else:
            cc.DBG_RD.remove(self.Receive)
    #@-others
#@+node:ekr.20060513122450.375: *4* BREAKIDTASK
class BREAKIDTASK(DBGTASK):
    #@+others
    #@+node:ekr.20060513122450.376: *5* __init__
    def __init__(self,b,index=0):

        cc = self.cc

        if len(b) >0:
            self.Break = b
            self.ListBreaks = cc.DBG["List breaks"]
            self.IdentifyBreak = ReplaceVars(cc.DBG["Identify break"])

            if self.ListBreaks and self.IdentifyBreak:
                if index:
                    cc.DBG_SD.insert(index,self.Send)
                else:
                    cc.DBG_SD.append(self.Send)
            else:
                Warning("xcc: ","Break Identification task is undefined!")
    #@+node:ekr.20060513122450.377: *5* Send
    def Send(self):
        aWrite(self.ListBreaks)
        DBG_SD.remove(self.Send)
        DBG_RD.append(self.Receive)

    #@+node:ekr.20060513122450.378: *5* Receive
    def Receive(self,line):

        cc = self.cc
        if not cc.DBG_PROMPT:
            if line:
                idb = cc.ReplaceVars(self.IdentifyBreak)

                idb = idb.replace("_FILE_",self.Break[0]).replace("_LINE_",self.Break[1])
                m = re.search(idb,line,re.IGNORECASE)
                if m != None:
                    bid = m.group("ID")					
                    if bid != None:
                        if cc.VERBOSE:					
                            cc.aAddText("\" Break id at line "+self.Break[1]+" in "+self.Break[0]+" is "+bid+"\n")
                        DBGTASK(cc,cc.ReplaceVars(cc.DBG["Clear break"]).replace("_ID_",bid))

        else:
            cc.DBG_RD.remove(self.Receive)
    #@-others
#@+node:ekr.20060513122450.43: *3* class ProcessClass
class ProcessClass:

    #@+others
    #@+node:ekr.20060513122450.44: *4* class ReadingThreadClass
    class ReadingThreadClass(threading.Thread):

        #@+others
        #@+node:ekr.20060513122450.45: *5* __init__
        def __init__(self):

            threading.Thread.__init__(self)
            self.File = None
            self.Lock = thread.allocate_lock()
            self.Buffer = ""
        #@+node:ekr.20060513122450.46: *5* run
        def run(self):

            global Encoding

            try:
                s=self.File.read(1)	
                while s:
                    self.Lock.acquire()			
                    self.Buffer = self.Buffer + g.ue(s,Encoding)
                    self.Lock.release()
                    s=self.File.read(1)

            except IOError as ioerr:
                self.Buffer = self.Buffer +"\n"+ "[@run] ioerror :"+str(ioerr)
        #@+node:ekr.20060513122450.47: *5* Update
        def Update(self,func):

            ret = True	
            if self.Lock.acquire(0) == 1:
                if self.Buffer and func:
                    func(self.Buffer)
                    self.Buffer=""
                else:
                    ret = self.isAlive()	
                self.Lock.release()	
            return ret


        #@-others
    #@+node:ekr.20060513122450.48: *4* __init__
    def __init__(self,cc,node,filename,args,start=None,out=None,err=None,end=None,spawn=False):

        self.cc = cc
        self.Node = node	
        self.Spawn = spawn	
        self.FileName = filename
        self.Arguments = args

        self.In = None
        self.OutThread = None
        self.ErrThread = None	

        self.OnStart = start
        self.Output = out
        self.Error = err
        self.OnEnd = end

        self.Kill = False
    #@+node:ekr.20060513122450.49: *4* Open
    def Open(self):

        g.trace(g.callers())

        cc = self.cc
        if self.Spawn:
            os.spawnl(os.P_NOWAIT,self.FileName,self.Arguments)
            cc.ProcessList.remove(self)
            return True

        path,fname = os.path.split(self.FileName)
        if fname == "" or os.access(self.FileName,os.F_OK) != 1:		
            return Error("xcc: ","PROCESS: "+self.FileName+" is invalid!")

        # Create the threads and open the pipe, saving and restoring the working directory.
        oldwdir=os.getcwd() ; os.chdir(path)	
        self.OutThread = self.ReadingThreadClass()
        self.ErrThread = self.ReadingThreadClass()
        self.In,self.OutThread.File,self.ErrThread.File	= os.popen3(
            fname+" "+self.Arguments)
        os.chdir(oldwdir)

        if not self.In or not self.OutThread.File or not self.ErrThread.File:
            return Error("xcc: ","PROCESS: Can't open file!")

        # Start the threads.
        self.OutThread.start()
        self.ErrThread.start()	

        self.Node.setMarked()	
        cc.LeoTop.redraw()
        return True
    #@+node:ekr.20060513122450.50: *4* Close
    def Close(self):

        cc = self.cc

        self.In and self.In.close()

        self.OutThread.File and self.OutThread.File.close()

        exitcode = self.ErrThread.File and self.ErrThread.File.close()

        self.Node.clearMarked()
        self.Node = None	

        self.OnEnd and self.OnEnd(exitcode)	

        cc.LeoTop.redraw()

        return exitcode
    #@+node:ekr.20060513122450.51: *4* Update
    def Update(self):

        if not self.OutThread or not self.ErrThread:
            return False

        # writing intro to console
        if self.OnStart:
            self.OnStart()
            self.OnStart = None

        return self.OutThread.Update(self.Output) or self.ErrThread.Update(self.Error)
    #@-others

#@+node:ekr.20060513122450.52: *3* Widget classes
#@+node:ekr.20060513122450.53: *4* class ConfigClass
class ConfigClass:
    #@+others
    #@+node:ekr.20060513122450.82: *5*   __init__
    def __init__(self,cc):

        self.cc = cc
        self.Pages = []
        self.Buttons = []
        self.ActivePage = None

        #switch frame
        self.SwitchFrame = Tk.Frame(
            cc.LeoFrame.split1Pane2,relief='groove',bd=2,height=40,width=100)

        #title
        self.Title = Tk.Entry(self.SwitchFrame,justify='center')
        self.Title.pack(side="top",fill="x",expand=1)	

        self.AddPages()	
        #add pages switches
        for page in self.Pages:
            if page:
                b = Tk.Button(self.SwitchFrame,text=page.name,width=10,command=page.Show,relief='groove')
                self.Buttons.append(b)
                b.pack(side="left")
                if not self.ActivePage:
                    self.ActivePage = page

        if 0: #Cancel button
            # Not needed.
            b = Tk.Button(self.SwitchFrame,text="Cancel",command=lambda: self.Hide(False))
            b.pack(side="right")

        #Load button
        b = Tk.Button(self.SwitchFrame,text="Load...",command=self.LoadFromFile)
        b.pack(side="right")

        #Save button
        b = Tk.Button(self.SwitchFrame,text="Save...",command=self.SaveToFile)
        b.pack(side="right")	

        self.BreakTags = {}
        self.visible = False
    #@+node:ekr.20060513122450.54: *5*   class PageClass
    class PageClass(Tk.Canvas):
        #@+others
        #@+node:ekr.20060513122450.55: *6* class CHECK
        class CHECK:
            #@+others
            #@+node:ekr.20060513122450.56: *7* __init__
            def __init__(self,master,n,x=0,y=0):

                self.Check = Tk.StringVar()
                self.Name = n
                c = Tk.Checkbutton(master,text=n,onvalue="True",offvalue="False",variable=self.Check)
                master.create_window(x,y,anchor='nw',window=c)
            #@+node:ekr.20060513122450.57: *7* Get
            def Get(self):
                return self.Check.get()
            #@+node:ekr.20060513122450.58: *7* Set
            def Set(self,value):
                self.Check.set(value)
            #@-others
        #@+node:ekr.20060513122450.59: *6* class ENTRY
        class ENTRY:
            #@+others
            #@+node:ekr.20060513122450.60: *7* __init__
            def __init__(self,c,n,w=175,h=22,e=1,a='nw',x=0,y=0,re=False,vs=False):
                self.Name = n

                if re != False: fg = RegExpFgColor
                else: fg = "black"

                if vs != False: bg = VarSupBgColor
                else: bg = "white"

                self.MasterFrame = mf = Tk.Frame(c,relief='groove',height=h,width=w)
                self.ID = c.create_window(x,y,anchor=a,window=mf,height=h,width=w)	

                self.Entry = Tk.Entry(mf,width=1,bg=bg)
                self.Entry.pack(side="right",fill="x",expand=e)
                l = Tk.Label(mf,text=n+":",fg=fg).pack(side="right")
            #@+node:ekr.20060513122450.61: *7* Get
            def Get(self):
                return self.Entry.get()
            #@+node:ekr.20060513122450.62: *7* Set
            def Set(self,text):
                self.Entry.delete(0,'end')
                self.Entry.insert('end',text)
            #@-others
        #@+node:ekr.20060513122450.63: *6* class TEXT
        class TEXT:
            #@+others
            #@+node:ekr.20060513122450.64: *7* __init__
            def __init__(self,c,n,w=350,h=80,a='nw',x=0,y=0,re=False,vs=False):#text are 3 column wide

                self.Name = n

                if re != False: fg = RegExpFgColor
                else: fg = "black"

                if vs != False: bg = VarSupBgColor
                else: bg = "white"

                self.MasterFrame = mf = Tk.Frame(c,relief='groove')
                self.ID = c.create_window(x,y+1,anchor=a,window=mf,width=w,height=h)

                lf = Tk.Frame(mf,relief='flat')
                lf.pack(side="top",fill="x",expand=1)			
                Tk.Label(lf,text=n+":",fg=fg).pack(side="left")

                self.Text = Tk.Text(mf,bg=bg)
                self.Text.pack(side="top",fill="x",expand=1)
            #@+node:ekr.20060513122450.65: *7* Get
            def Get(self):
                s = self.Text.get(1.0,'end')
                lines = s.splitlines()
                res = ""
                for l in lines:
                    if l != "":
                        res += l+"\n"
                return res
            #@+node:ekr.20060513122450.66: *7* Set
            def Set(self,text):
                self.Text.delete(1.0,'end')
                self.Text.insert('end',text)
            #@-others
        #@+node:ekr.20060513122450.67: *6* class LABEL
        class LABEL:
            #@+others
            #@+node:ekr.20060513122450.68: *7* __init__
            def __init__(self,c,text,w=175,h=22,e=1,a='nw',x=0,y=0,color="#%02x%02x%02x" % (150,150,150)):

                self.MasterFrame = mf = Tk.Frame(c,relief='groove',height=h,width=w)
                self.ID = c.create_window(x,y,anchor=a,window=mf,height=h,width=w)	

                self.Label = Tk.Label(c,text=text,justify='left',fg=color)
                self.ID = c.create_window(x,y,anchor=a,window=self.Label)
            #@-others
        #@+node:ekr.20060513122450.69: *6* class HELP
        class HELP(Tk.Button):
            #@+others
            #@+node:ekr.20060513122450.70: *7* __init__
            def __init__(self,c,buttontext="Help",boxtitle="Help",msg="!",x=5,y=0):

                self.Title = boxtitle
                self.Message = msg
                Tk.Button.__init__(self,c,text=buttontext,command=self.Help)
                self.ID = c.create_window(x,y,anchor='nw',window=self)
            #@+node:ekr.20060513122450.71: *7* Help
            def Help(self):
                tkMessageBox.showinfo(self.Title,self.Message)
            #@-others
        #@+node:ekr.20060513122450.72: *6* __init__
        def __init__(self,cc,name):

            self.cc = cc
            self.name = name
            self.Objects = []
            Tk.Canvas.__init__(self,cc.LeoFrame.split1Pane2)
            self.X=self.Y=self.W=self.H = 0
            self.CreateObjects(self)
        #@+node:ekr.20060513122450.73: *6* AddObject
        def AddObject(self,o):

            if o != None:
                self.Objects.append(o)
                self.X,self.Y,self.W,self.H = self.bbox('all')
        #@+node:ekr.20060513122450.74: *6* BBox
        def BBox(self):
            self.X,self.Y,self.W,self.H = self.bbox('all')
        #@+node:ekr.20060513122450.75: *6* AddSep
        def AddSep(self,length=380,color="black"):

            if length != None:
                l = length
            else:
                l = self.W
            self.create_line(5,self.H+4,l+5,self.H+4,fill=color)
            self.H += 10
        #@+node:ekr.20060513122450.76: *6* CreateObjects
        def CreateObjects(self,master):#must overide
            pass
        #@+node:ekr.20060513122450.77: *6* SaveObjects
        def SaveObjects(self,pd=None):

            cc = self.cc

            if pd == None:
                pd = cc.sGet(self.name,init={})

            for o in self.Objects:
                pd[o.Name] = o.Get()
        #@+node:ekr.20060513122450.78: *6* LoadObjects
        def LoadObjects(self,pd=None):	

            cc = self.cc
            if pd == None:
                pd = cc.sGet(self.name,{})

            g.trace(self.name,pd)

            for o in self.Objects:
                if o.Name not in pd:				
                    pd[o.Name] = o.Get()
                else:
                    o.Set(pd[o.Name])
        #@+node:ekr.20060513122450.79: *6* ClearObjects
        def ClearObjects(self,value=""):
            for o in self.Objects:
                o.Set(value)
        #@+node:ekr.20060513122450.80: *6* Hide
        def Hide(self):

            cc = self.cc
            self.pack_forget()

            b = cc.Config.GetButton(self.name)
            b.config(relief='groove',fg="black")

            cc.LeoYBodyBar.config(command=cc.LeoBodyText.yview)
            cc.LeoBodyText.config(yscrollcommand=cc.LeoYBodyBar.set)
        #@+node:ekr.20060513122450.81: *6* Show
        def Show(self):

            cc = self.cc

            if cc.Config.ActivePage:
                cc.Config.ActivePage.Hide()

            cc.Config.ActivePage = self
            b = cc.Config.GetButton(self.name)
            b.config(relief='sunken',fg="blue")	

            self.config(scrollregion=self.bbox('all'))
            self.config(yscrollcommand=cc.LeoYBodyBar.set)

            cc.LeoYBodyBar.config(command=self.yview)
            cc.LeoYBodyBar.pack(side="right",fill="y")
            self.pack(expand=1,fill="both")
        #@-others
    #@+node:ekr.20060513122450.126: *5*  class CodePageClass
    class CodePageClass(PageClass):
        #@+others
        #@+node:ekr.20060513122450.127: *6* __init__
        def __init__(self,cc):

            self.cc = cc
            ConfigClass.PageClass.__init__(self,"Code")
        #@+node:ekr.20060513122450.128: *6* CreateObjects
        def CreateObjects(self,master):#must overide
            bd=self["background"]
            x=10
            y=10
            text_w = 350
            text_h = 80
            #@+others
            #@+node:ekr.20060513122450.129: *7* Entries
            self.AddObject(self.TEXT(master,"File header",x=5,y=5,w=350,h=80))
            self.AddSep()
            self.AddObject(self.ENTRY(master,"Class opening",x=5,y=self.H,w=350,h=20))
            self.AddObject(self.ENTRY(master,"Class closing",x=5,y=self.H,w=350,h=20))
            self.AddObject(self.ENTRY(master,"Class header",x=5,y=self.H,w=350,h=20))
            self.AddObject(self.ENTRY(master,"Class footer",x=5,y=self.H,w=350,h=20))
            self.AddSep()
            self.AddObject(self.ENTRY(master,"Function header",x=5,y=self.H,w=350,h=20))
            self.AddObject(self.ENTRY(master,"Function footer",x=5,y=self.H,w=350,h=20))
            self.AddObject(self.ENTRY(master,"Function opening",x=5,y=self.H,w=350,h=20))
            self.AddObject(self.ENTRY(master,"Function closing",x=5,y=self.H,w=350,h=20))
            self.AddSep()
            self.AddObject(self.TEXT(master,"File footer",x=5,y=self.H,w=350,h=80))
            #@-others
            self.AddSep()
        #@-others
    #@+node:ekr.20060513122450.99: *5*  class CplPageClass
    class CplPageClass(PageClass):
        #@+others
        #@+node:ekr.20060513122450.100: *6* __init__
        def __init__(self,cc):

            self.cc = cc
            ConfigClass.PageClass.__init__(self,cc,"Compiler")
        #@+node:ekr.20060513122450.101: *6* Browse
        def Browse(self):

            for o in self.Objects:
                if o and o.Name == "Compiler":
                    break
            else: return

            ft = ('Executables', '.exe;.bin'),
            s = tkFileDialog.askopenfilename(filetypes=ft,title="Locate Compiler...")
            if s == None:
                return Error("xcc: ","Action canceled by user!")
            elif s == "":
                return Error("xcc: ","Empty path returned!")

            e.Set(os.path.normpath(s))
        #@+node:ekr.20060513122450.102: *6* AddPath
        def AddPath(self,name):
            d = tkFileDialog.askdirectory()
            if d != "":
                d = d.replace("/","\\")
                for o in self.Objects:
                    if o.Name == name:
                        opaths = o.Get().splitlines()
                        npaths = []

                        for p in opaths:
                            p = p.strip()
                            if p != "":
                                npaths.append(p)

                        npaths.append(d)

                        o.Set(string.join(npaths,"\n"))
        #@+node:ekr.20060513122450.103: *6* CreateObjects
        def CreateObjects(self,master): #must overide

            #@+others
            #@+node:ekr.20060513122450.104: *7* Executable
            x=10
            y=10
            text_w = 350
            text_h = 80

            # compiler entry -
            self.AddObject(self.ENTRY(master,"Compiler",x=5,y=5,w=350,h=20))
            b = Tk.Button(master,text=" ...",command=self.Browse)
            master.create_window(360,self.Y-2,anchor='nw',window=b)
            #@+node:ekr.20060513122450.105: *7* Arguments
            self.AddSep()
            #-------------------------------------------------

            t1 = self.TEXT(master,"Arguments",x=5,y=self.H,vs=True)
            self.HELP(master,boxtitle="Arguments info",msg=CplArgumentsHelp,x=360,y=self.H+20)
            self.AddObject(t1)

            #------------------------------------------
            t1 = self.TEXT(master,"Debug arguments",x=5,y=self.H,vs=True)
            self.HELP(master,boxtitle="Debug arguments info",msg=CplDebugArgumentsHelp,x=360,y=self.H+20)
            self.AddObject(t1)
            #@+node:ekr.20060513122450.106: *7* Paths
            self.AddSep()
            #-------------------------------------------------------------
            b = Tk.Button(master,text="Browse",command=lambda:self.AddPath("Include search paths"))
            master.create_window(360,self.H+58,anchor='nw',window=b)
            t1 = self.TEXT(master,"Include search paths",x=5,y=self.H)
            self.HELP(master,boxtitle="Include search paths info",msg=IncludeSearchPathsHelp,x=360,y=self.H+20)
            self.AddObject(t1)

            #-------------------------------------------------------------
            b = Tk.Button(master,text="Browse",command=lambda:self.AddPath("Library search paths"))
            master.create_window(360,self.H+58,anchor='nw',window=b)
            t1 = self.TEXT(master,"Library search paths",x=5,y=self.H)
            self.HELP(master,boxtitle="Library search paths info",msg=LibrarySearchPathsHelp,x=360,y=self.H+20)
            self.AddObject(t1)

            #-------------------------------------------------------------
            t1 = self.TEXT(master,"Used libraries",x=5,y=self.H)
            self.HELP(master,boxtitle="Used libraries info",msg=UsedLibrariesHelp,x=360,y=self.H+20)
            self.AddObject(t1)
            #@+node:ekr.20060513122450.107: *7* Symbols
            ww =19
            self.AddSep()
            #------------------------------------------------------
            lf = Tk.Frame(master,relief='flat',bd=2)
            master.create_window(self.X,self.H+2,width=text_w,height=20,anchor='nw',window=lf)
            Tk.Label(lf,text="Compiler symbols:").pack(side="left")
            self.H += 22

            self.HELP(master,boxtitle="Include path and Library path info",msg=IncludePathAndLibraryPathHelp,x=360,y=self.H)
            #Include path
            e1 = self.ENTRY(master,"Include path",x=5,y=self.H)
            #Library path
            e2 = self.ENTRY(master,"Library path",x=180,y=self.H)
            self.AddObject(e1)
            self.AddObject(e2)

            self.HELP(master,boxtitle="Use library and Check syntaxe info",msg=UseLibraryAndCheckSyntaxeHelp,x=360,y=self.H)
            #Use library
            e1 = self.ENTRY(master,"Use library",x=5,y=self.H)
            #Check syntaxe
            e2 = self.ENTRY(master,"Check syntaxe",x=180,y=self.H)
            self.AddObject(e1)
            self.AddObject(e2)

            self.HELP(master,boxtitle="Build exe and Build dll info",msg=BuildExeAndBuildDllHelp,x=360,y=self.H)
            #Build exe
            e1 = self.ENTRY(master,"Build exe",x=5,y=self.H)
            #Build dll
            e2 = self.ENTRY(master,"Build dll",x=180,y=self.H)
            self.AddObject(e1)
            self.AddObject(e2)

            self.HELP(master,boxtitle="Compile pch and Use pch info",msg=CompilePchAndUsePchHelp,x=360,y=self.H)
            #Compile pch
            e1 = self.ENTRY(master,"Compile pch",x=5,y=self.H)
            #Use pch
            e2 = self.ENTRY(master,"Use pch",x=180,y=self.H)
            self.AddObject(e1)
            self.AddObject(e2)
            #@+node:ekr.20060513122450.108: *7* Error Detection
            # ------------------
            self.AddSep()
            e = self.ENTRY(master,"Error detection",x=5,y=self.H,w=350,re=True)
            self.HELP(master,boxtitle="Error detection info",msg=CplArgumentsHelp,x=360,y=self.H)
            self.AddObject(e)
            #@-others



        #@-others
    #@+node:ekr.20060513122450.109: *5*  class DbgPageClass
    class DbgPageClass(PageClass):
        #@+others
        #@+node:ekr.20060513122450.110: *6* __init__
        def __init__(self,cc):

            self.cc = cc
            ConfigClass.PageClass.__init__(self,cc,"Debugger")
        #@+node:ekr.20060513122450.111: *6* Browse
        def Browse(self):

            for o in self.Objects:
                if o != None and o.Name == "Debugger":
                    break
            else: return

            ft = ('Executables', '.exe;.bin'),
            s = tkFileDialog.askopenfilename(filetypes=ft,title="Locate Debugger...")

            if s == None:
                return Error("xcc: ","Action canceled by user!")
            elif s == "":
                return Error("xcc: ","Empty path returned!")

            e.Set(os.path.normpath(s))
        #@+node:ekr.20060513122450.112: *6* CreateObjects
        def CreateObjects(self,master):#must overide
            #@+others
            #@+node:ekr.20060513122450.113: *7* Executable
            x=10
            y=10
            text_w = 350
            text_h = 80

            # compiler entry
            self.AddObject(self.ENTRY(master,"Debugger",x=5,y=5,w=350,h=20))
            b = Tk.Button(master,text=" ...",command=self.Browse)
            master.create_window(360,self.Y-2,anchor='nw',window=b)	
            #@+node:ekr.20060513122450.114: *7* Arguments
            self.AddSep()
            t1 = self.TEXT(master,"Arguments",x=5,y=self.H,vs=True)
            self.HELP(master,boxtitle="Arguments info",msg=DbgArgumentsHelp,x=360,y=self.H+20)
            self.AddObject(t1)
            #@+node:ekr.20060513122450.115: *7* Piping
            self.AddSep()
            e1 = self.ENTRY(master,"Prompt pattern",x=5,y=self.H,re=True) 
            e2 = self.ENTRY(master,"Pipe eol",x=180,y=self.H)

            self.HELP(master,boxtitle="Prompt pattern and Pipe eol info",msg=DbgPipingHelp,x=360,y=self.H)
            self.AddObject(e1)
            self.AddObject(e2)
            #@+node:ekr.20060513122450.116: *7* Symbols
            ww =19

            self.AddSep()

            lf = Tk.Frame(master,relief='flat',bd=2)
            master.create_window(5,self.H+2,width=text_w,height=20,anchor='nw',window=lf)
            Tk.Label(lf,text="Debugger commands symbols:").pack(side="left")
            self.H += 22

            # ------------------
            e1 = self.ENTRY(master,"Go",x=5,y=self.H)
            e2 = self.ENTRY(master,"Step in",x=180,y=self.H)
            self.AddObject(e1)
            self.AddObject(e2)

            # ------------------
            e1 = self.ENTRY(master,"Continue",x=5,y=self.H)
            e2 = self.ENTRY(master,"Step over",x=180,y=self.H)
            self.AddObject(e1)
            self.AddObject(e2)

            # ------------------
            e1 = self.ENTRY(master,"Stop",x=5,y=self.H)
            e2 = self.ENTRY(master,"Step out",x=180,y=self.H)
            self.AddObject(e1)
            self.AddObject(e2)

            # ------------------
            e1 = self.ENTRY(master,"Evaluate",x=5,y=self.H)
            self.AddObject(e1)
            #@+node:ekr.20060513122450.117: *7* Startup Task
            #------------------------------------------------------
            self.AddSep()
            t1 = self.TEXT(master,"Startup task",x=5,y=self.H,vs=True)

            self.HELP(master,boxtitle="Startup task info",msg=DbgStartupTaskHelp,x=360,y=self.H+20)

            self.AddObject(t1)
            #@+node:ekr.20060513122450.118: *7* Target PID
            # ------------------
            self.AddSep()
            e = self.ENTRY(master,"Target pid task",x=5,y=self.H,w=350,vs=True)

            self.HELP(master,boxtitle="Target pid task and Find pid info",msg=DbgTargetPidHelp,x=360,y=self.H)
            self.AddObject(e)

            e = self.ENTRY(master,"Find pid",x=5,y=self.H,w=350,re=True,vs=True)
            self.AddObject(e)
            #@+node:ekr.20060513122450.119: *7* Break info
            #------------------------------------------------------
            self.AddSep()
            self.HELP(master,boxtitle="Break detection info",msg=DbgBreakDetectionHelp,x=360,y=self.H+20)
            self.AddObject(self.TEXT(master,"Break detection",x=5,y=self.H,w=text_w,h=text_h,re=True))

            self.AddSep()
            e1 = self.ENTRY(master,"Set break",x=5,y=self.H,vs=True)
            e2 = self.ENTRY(master,"Clear break",x=180,y=self.H,vs=True)
            self.HELP(master,boxtitle="Set break and Clear break info",msg=DbgSetClearBreakHelp,x=360,y=self.H)
            self.AddObject(e1)
            self.AddObject(e2)

            self.AddSep()
            self.HELP(master,boxtitle="List breaks and Identify break info",msg=DbgBreakIdHelp,x=360,y=self.H)
            self.AddObject(self.ENTRY(master,"List breaks",x=5,y=self.H,w=350))
            e = self.ENTRY(master,"Identify break",x=5,y=self.H,w=350,re=True)
            self.AddObject(e)

            # ------------------
            self.AddSep()
            self.HELP(master,boxtitle="Query location and Find location info",msg=DbgLocationHelp,x=360,y=self.H)
            self.AddObject(self.ENTRY(master,"Query location",x=5,y=self.H,w=350))
            e = self.ENTRY(master,"Find location",x=5,y=self.H,w=350,re=True,vs=True)
            self.AddObject(e)
            #@+node:ekr.20060513122450.120: *7* Misc RE
            #-------------------------------------------------------------
            self.AddSep()
            t1 = self.TEXT(master,"Regular expression",x=4,y=self.H,w=173,re=True,vs=True)
            t2 = self.TEXT(master,"Task",x=180,y=self.H,w=173,vs=True)
            self.HELP(master,boxtitle="Regular expression and Task info",msg=DbgMiscExpHelp,x=360,y=self.H+20)
            self.AddObject(t1)
            self.AddObject(t2)
            #@-others
        #@-others
    #@+node:ekr.20060513122450.121: *5*  class ExePageClass
    class ExePageClass(PageClass):
        #@+others
        #@+node:ekr.20060513122450.122: *6* __init__
        def __init__(self,cc):

            self.cc = cc
            ConfigClass.PageClass.__init__(self,cc,"Executable")
        #@+node:ekr.20060513122450.123: *6* CreateObjects
        def CreateObjects(self,master):#must overide
            bd=self["background"]
            x=10
            y=10
            text_w = 350
            text_h = 80
            #@+others
            #@+node:ekr.20060513122450.124: *7* Args
            self.AddObject(self.TEXT(master,"Execution arguments",x=5,y=5))
            #@+node:ekr.20060513122450.125: *7* Dll Caller
            self.AddSep()
            e1 = self.ENTRY(master,"Dll caller",x=5,y=self.H,w=280,h=20)
            b = Tk.Button(master,text="Browse...",width=10,default='disabled')
            master.create_window(self.X+285,self.H,width=60,height=20,anchor='nw',window=b)
            self.AddObject(e1)
            #@-others
            self.create_line(0,self.H+5,self.W+1,self.H+5)
        #@-others
    #@+node:ekr.20060513122450.94: *5*  class OptPageClass
    class OptPageClass(PageClass):

        #@+others
        #@+node:ekr.20060513122450.95: *6* __init__
        def __init__(self,cc):

            self.cc = cc
            ConfigClass.PageClass.__init__(self,cc,"Options")
        #@+node:ekr.20060513122450.96: *6* CreateObjects
        def CreateObjects(self,master): # must overide

            #@+others
            #@+node:ekr.20060513122450.97: *7* Actions Switches
            s1 = self.CHECK(master,"Create files",x=5,y=5)
            s2 = self.CHECK(master,"Auto include header",x=100,y=5)
            self.AddObject(s1)
            self.AddObject(s2)

            self.AddSep(length=self.W)
            s1 = self.CHECK(master,"Compile",x=5,y=self.H)
            s2 = self.CHECK(master,"Seek first error",x=100,y=self.H)
            self.AddObject(s1)
            self.AddObject(s2)

            self.AddSep(length=self.W)
            s1 = self.CHECK(master,"Execute",x=5,y=self.H)
            s2 = self.CHECK(master,"Connect to pipe",x=100,y=self.H)
            self.AddObject(s1)
            self.AddObject(s2)

            self.AddSep(length=self.W)
            s1 = self.CHECK(master,"Debug",x=5,y=self.H)
            s2 = self.CHECK(master,"Seek breakpoints",x=100,y=self.H)
            self.AddObject(s1)
            self.AddObject(s2)

            #-------------------------------------------------------------
            self.AddSep(self.W)
            self.AddObject(self.CHECK(master,"Xcc verbose",x=5,y=self.H))
            self.AddObject(self.CHECK(master,"Filter output",x=5,y=self.H))
            #@+node:ekr.20060513122450.98: *7* Import
            #self.AddSep(self.W)
            #b = Tk.Button(master,text="Import...",width=10,default='disabled',command = ImportFiles)
            #master.create_window(self.X+5,self.H,width=60,height=20,anchor='nw',window=b)
            #c1 = self.CHECK(master,"Merge",x=80,y=self.H)
            #c2 = self.CHECK(master,"Use corresponding source/header",x=150,y=self.H)
            #self.AddObject(c1)
            #self.AddObject(c2)
            #@-others

            self.AddSep(length=self.W)
        #@-others
    #@+node:ekr.20060513122450.93: *5* AddPages
    def AddPages(self):

        cc = self.cc
        self.Pages.append(self.OptPageClass(cc))
        self.Pages.append(self.CplPageClass(cc))
        self.Pages.append(self.DbgPageClass(cc))
        self.Pages.append(self.ExePageClass(cc))
        #self.Pages.append(self.CodePageClass(cc))
    #@+node:ekr.20060513122450.92: *5* Apply
    def Apply(self):
        self.SaveToNode()
        self.Hide()
    #@+node:ekr.20060513122450.87: *5* ClearConfig
    def ClearConfig(self):
        for p in self.Pages:
            if p.name == "Options":
                p.ClearObjects("False")
            else:
                p.ClearObjects()
    #@+node:ekr.20060513122450.84: *5* GetButton
    def GetButton(self,name):

        for b in self.Buttons:
            if b and b["text"] == name:
                return b
    #@+node:ekr.20060513122450.83: *5* GetPage
    def GetPage(self,name):

        for p in self.Pages:
            if p and p.name == name:
                return p
    #@+node:ekr.20060513122450.85: *5* Hide
    def Hide(self,save=True):

        cc = self.cc

        if self.visible == True:
            self.ActivePage.Hide()	
            self.SwitchFrame.pack_forget()
            cc.LeoYBodyBar.config(command=cc.LeoBodyText.yview)
            cc.LeoBodyText.config(yscrollcommand=cc.LeoYBodyBar.set)
            cc.LeoXBodyBar.pack(side = "bottom",fill="x")
            if cc.CHILD_NODE:
                cc.BreakBar.Show()
            cc.LeoBodyText.pack(expand=1, fill="both")

            if save == True:
                self.SaveToNode()
            cc.ToolBar.ConfigButton.config(command=self.Show,relief='raised')
            cc.ToolBar.DisplayFrame.pack(side="top",fill="x",expand=1)
            self.visible = False
    #@+node:ekr.20060513122450.90: *5* LoadFromFile
    def LoadFromFile(self):
        try:
            ft = ('XCC Config files', '.xcc'),
            s = tkFileDialog.askopenfilename(filetypes=ft,title="Open xcc connfiguration file...")

            if s == "":
                Error("xcc: ","Load action canceled by user!")
                return

            #read file and compose code
            f = file(s,"r")
            td = None
            code = "td ="+f.readline()
            f.close()

            # load in temp dict
            try:
                exec(code)
            except Exception:
                TraceBack()
                Error("xcc: ","File content is invalid!")
                return

            #	load each pages
            for p in self.Pages:
                if p.name in td:
                    p.LoadObjects(td[p.name])

            #set title to file name
            name,ext = os.path.splitext(s)
            path,name = os.path.split(name)		
            self.Title.delete(0,'end')
            self.Title.insert('end',name)		

            #save to node to ensure integrity
            self.SaveToNode()

        except Exception:
            TraceBack()




    #@+node:ekr.20060513122450.88: *5* LoadFromNode
    def LoadFromNode(self):

        cc = self.cc
        self.Title.delete(0,'end')
        self.Title.insert('end',cc.sGet("Title"))

        for p in self.Pages:
            if p:
                p.LoadObjects()
    #@+node:ekr.20060513122450.91: *5* SaveToFile
    def SaveToFile(self):
        try:


            ft = ('XCC Config files', '.xcc'),
            s = tkFileDialog.asksaveasfilename(
            filetypes=ft,
            title="Save xcc connfiguration file...",
            initialfile = self.Title.get()
            )

            if s == "":
                Error("xcc: ","Save action canceled by user!")
                return		

            name,ext = os.path.splitext(s)

            td = {}

            # save each pages
            for p in self.Pages:
                td[p.name] = {}
                p.SaveObjects(td[p.name])	

            #write the dict to file
            f = file(name+".xcc","w+")
            Message("xcc: ","Writing config in "+name+".xcc")
            f.write(str(td))
            f.close()

            # reset title to file name
            path,name = os.path.split(name)		
            self.Title.delete(0,'end')
            self.Title.insert('end',name)

            # save to node
            self.SaveToNode()
        except Exception:
            TraceBack()







    #@+node:ekr.20060513122450.89: *5* SaveToNode
    def SaveToNode(self):

        cc = self.cc

        cc.sSet("Title",self.Title.get())

        for p in self.Pages:
            p and p.SaveObjects()
    #@+node:ekr.20060513122450.86: *5* Show
    def Show(self):

        cc = self.cc
        if cc.Watcher.visible:
            cc.Watcher.Hide()			
        if cc.BreakBar.visible:
            cc.BreakBar.Hide()
        cc.ToolBar.DisplayFrame.pack_forget()
        cc.LeoBodyText.pack_forget()
        cc.LeoXBodyBar.pack_forget()
        cc.LeoYBodyBar.pack_forget()

        self.SwitchFrame.pack(side="top", fill="x")
        self.LoadFromNode()
        self.ActivePage.Show()
        cc.ToolBar.ConfigButton.config(command=self.Hide,relief='sunken')
        self.visible = True
        cc.c.redraw()
    #@-others
#@+node:ekr.20060513122450.130: *4* class DBGHELP
#@+node:ekr.20060513122450.131: *5* DbgArgumentsHelp
DbgArgumentsHelp = """
Command line passed to to the debugger.
Each lines are concatenated using space.

The following variables are supported:

    _ABSPATH_
    _RELPATH_
    _NAME_
    _EXT_
    _SRCEXT_"""
#@+node:ekr.20060513122450.132: *5* DbgPipingHelp
DbgPipingHelp = """
Prompt pattern:
    Regular expression used to detect the debugger prompt.

Pipe eol:
    End of line character used when sending command to the debugger."""
#@+node:ekr.20060513122450.133: *5* DbgStartupTaskHelp
DbgStartupTaskHelp = """
Commands sent to the debugger at startup.
These commands must leave the debugger breaked
in the entry point of the target.

The following variables are supported:

    _ABSPATH_
    _RELPATH_
    _NAME_
    _EXT_
    _SRCEXT_"""
#@+node:ekr.20060513122450.134: *5* DbgTargetPidHelp
DbgTargetPidHelp = """
Target pid task:
    Command used to retreive the target process identifier.
    The target pid is used to break into the debugger.

    The following variables are supported:
        _ABSPATH_
        _RELPATH_
        _NAME_
        _EXT_
        _SRCEXT_

Find pid:
    Regular expression used to retreive the target pid when
    the "Target pid task" is sent to the debugger.

    The following variables are supported:

        _ABSPATH_
        _RELPATH_
        _NAME_
        _EXT_
        _SRCEXT_

    The following groups must be returned by the regular expression:

        PID"""
#@+node:ekr.20060513122450.135: *5* DbgBreakDetectionHelp
DbgBreakDetectionHelp = """
Regular expression used to detect a break in target code execution.

When an output line match one of the expressions, an attempt is 
made to find the current location in the target code using the
"Query location" and "Find location" fields.

Each line is a different regular expression."""
#@+node:ekr.20060513122450.136: *5* DbgSetClearBreakHelp
DbgSetClearBreakHelp = """
Set break:
    Command used to set a breakpoint.

    The following variables are supported:

        _ABSPATH_
        _RELPATH_
        _NAME_
        _EXT_
        _SRCEXT_
        _FILE_
        _LINE_

Clear break:
    Command used to clear/delete a breakpoint.

    The following variables are supported:

        _ABSPATH_
        _RELPATH_
        _NAME_
        _EXT_
        _SRCEXT_
        _FILE_
        _LINE_
        _ID_*

    *If _ID_ is used, attempt to find it using the
    "List breaks" and "Identify break" fields."""
#@+node:ekr.20060513122450.137: *5* DbgBreakIdHelp
DbgBreakIdHelp = """
List breaks:
    Command used to list the debugger's break table.

    This field is ignored if the "Clear break" field
    make no use of the _ID_ variable.

Identify break:
    Regular expresion used to find the id of a breakpoint
    when the "List breaks" command is sent to the debugger.

    This field is ignored if the "Clear break" field
    make no use of the _ID_ variable.

    The following variables are supported:

        _ABSPATH_
        _RELPATH_
        _NAME_
        _EXT_
        _SRCEXT_
        _FILE_
        _LINE_

    The following groups must be returned by the regular expression:

        ID"""
#@+node:ekr.20060513122450.138: *5* DbgLocationHelp
DbgLocationHelp = """
Query location:
    Command used to retreive the file and line where
    the debugger is currently breaked.

Find location:
    Regular expression used to retreiv the current 
    file and line when the "Query location" command
    is sent to the debugger.

    The following variables are supported:

        _ABSPATH_
        _RELPATH_
        _NAME_
        _EXT_
        _SRCEXT_

    The following groups must be returned by the regular expression:

        EXT
        LINE

"""
#@+node:ekr.20060513122450.139: *5* DbgMiscExpHelp
DbgMiscExpHelp = """
Regular expression:
    Each line is a separate regular expression.

    If an output line is matched by one of the expression,
    the corresponding "Task" line is sent to the debugger.

    The following variables are supported:

        _ABSPATH_
        _RELPATH_
        _NAME_
        _EXT_
        _SRCEXT_

Task:
    Each line is a separate task trigered by the corresponding
    "Regular expression" line.

    The following variables are supported:

        _ABSPATH_
        _RELPATH_
        _NAME_
        _EXT_
        _SRCEXT_"""
#@+node:ekr.20060513122450.140: *4* class CPLHELP
#@+node:ekr.20060513122450.141: *5* CplArgumentsHelp
CplArgumentsHelp = """
Command line passed to to the compiler.
Each lines are concatenated using space.

The following variables are supported:

    _ABSPATH_
    _RELPATH_
    _NAME_
    _EXT_
    _SRCEXT_
    _BUILD_
    _INCPATHS_
    _LIBPATHS_
    _LIBRARIES_"""
#@+node:ekr.20060513122450.142: *5* CplDebugArgumentsHelp
CplDebugArgumentsHelp = """
Command line passed to to the compiler 
when debugging is requested.
Each lines are concatenated using space.

The following variables are supported:

    _ABSPATH_
    _RELPATH_
    _NAME_
    _EXT_
    _SRCEXT_
    _BUILD_
    _INCPATHS_
    _LIBPATHS_
    _LIBRARIES_"""
#@+node:ekr.20060513122450.143: *5* IncludeSearchPathsHelp
IncludeSearchPathsHelp = """
Each lines is a path to be searched for include files.

These paths are assembled unsing the "Include path"
symbol to create the _INCPATHS_ variable."""
#@+node:ekr.20060513122450.144: *5* LibrarySearchPathsHelp
LibrarySearchPathsHelp = """
Each lines is a path to be searched for library files.

These paths are assembled unsing the "Library path"
symbol to create the _LIBPATHS_ variable."""
#@+node:ekr.20060513122450.145: *5* UsedLibrariesHelp
UsedLibrariesHelp = """
Each whitespace delimited word is a libary to be 
used while building the project.

These libraries are assembled unsing the "Use library"
symbol to create the _LIBRARIES_ variable."""
#@+node:ekr.20060513122450.146: *5* IncludePathAndLibraryPathHelp
IncludePathAndLibraryPathHelp = """
Include path:	
    Symbol used with "Include search path" field
    to create the _INCPATHS_ variable.

Library path:	
    Symbol used with "Library search path" field
    to create the _LIBPATHS_ variable."""
#@+node:ekr.20060513122450.147: *5* UseLibraryAndCheckSyntaxeHelp
UseLibraryAndCheckSyntaxeHelp = """
Use library:	
    Symbol used with "Used libraries" field
    to create the _LIBRARIES_ variable.

Check syntaxe:	
    Symbol used when the project is a single
    header (.h extension). Header alone cant be 
    built but some compiler offer a syntaxe check."""
#@+node:ekr.20060513122450.148: *5* BuildExeAndBuildDllHelp
BuildExeAndBuildDllHelp = """
One of these symbols will be used to replace
the _BUILD_ variable in the "Arguments" and 
"Debug arguments" fields.

The correct one is choosed according to the
project extension.

These generally determine if the output is 
single or multi-threaded.

Build exe:	
    Symbol used to build an executable.

Build dll:	
    Symbol used to build a dll."""
#@+node:ekr.20060513122450.149: *5* CompilePchAndUsePchHelp
CompilePchAndUsePchHelp = """
TODO: Support precompiled header auto creation/inclusion."""
#@+node:ekr.20060513122450.150: *5* ErrorDetectionHelp
ErrorDetectionHelp = """
Regular expression used to detect error 
from the compiler output.

The following groups must be defined by
the regular expression:

    FILE
    LINE
    ID *
    DEF *

    * = Facultative groups"""
#@+node:ekr.20060513122450.151: *4* class ToolbarClass
class ToolbarClass(Tk.Frame):

    #@+others
    #@+node:ekr.20060513122450.152: *5* __init__
    def __init__(self,cc):

        self.cc = cc ; c = cc.c

        Tk.Frame.__init__(self,cc.LeoFrame.split1Pane2)
        f = Tk.Frame(self)
        f.pack(side="top",fill="x",expand=1)

        self.Go_e=Tk.PhotoImage(data=DecompressIcon(Go_e))
        self.GoButton = Tk.Button(f,command=self.Go,image=self.Go_e)
        self.GoButton.pack(side="left")

        self.Pause_e=Tk.PhotoImage(data=DecompressIcon(Pause_e))
        self.PauseButton = Tk.Button(f,image=self.Pause_e,command=cc.aPause,state='disabled')
        self.PauseButton.pack(side="left")

        self.Stop_e=Tk.PhotoImage(data=DecompressIcon(Stop_e))
        self.StopButton = Tk.Button(f,image=self.Stop_e,command=cc.aStop,state='disabled')
        self.StopButton.pack(side="left")

        self.StepIn_e=Tk.PhotoImage(data=DecompressIcon(StepIn_e))
        self.StepButton = Tk.Button(f,image=self.StepIn_e,state='disabled',command=cc.aStepIn)
        self.StepButton.pack(side="left")

        self.StepOver_e=Tk.PhotoImage(data=DecompressIcon(StepOver_e))
        self.StepInButton = Tk.Button(f,image=self.StepOver_e,state='disabled',command=cc.aStepOver)
        self.StepInButton.pack(side="left")

        self.StepOut_e=Tk.PhotoImage(data=DecompressIcon(StepOut_e))
        self.StepOutButton = Tk.Button(f,image=self.StepOut_e,state='disabled',command=cc.aStepOut)
        self.StepOutButton.pack(side="left")	

        self.Prompt_e=Tk.PhotoImage(data=DecompressIcon(Prompt_e))
        self.PromptButton = Tk.Button(f,image=self.Prompt_e,command=self.Refresh)

        s="<<"
        e=">>"
        # command entry
        self.DbgEntry = Tk.Entry(f)
        c.bind(self.DbgEntry,"<Key>",self.OnKey)

        #---------------------------------------------------
        self.ConfigGif=Tk.PhotoImage(data=DecompressIcon(ConfigData))
        self.ConfigButton = Tk.Button(f,image=self.ConfigGif,command=cc.Config.Show)
        self.ConfigButton.pack(side="right")

        self.WatchGif=Tk.PhotoImage(data=DecompressIcon(WatchData))
        self.WatchButton = Tk.Button(f,image=self.WatchGif,command=cc.Watcher.Show)
        self.WatchButton.pack(side="right")

        self.DisplayFrame = Tk.Frame(self)
        self.DisplayFrame.pack(side="top",fill="x",expand=1)

        fgcolor = "#808080"#BreakBar.fgcolor
        self.Spacer = Tk.Text(
            self.DisplayFrame,height=1,fg=fgcolor,relief='flat',
            font=cc.LeoFont,width=4,state='disabled')
        self.Spacer.pack(side="left")

        self.Display = Tk.Text(
            self.DisplayFrame,height=1,relief='flat',fg=fgcolor,bg=cc.BreakBar["bg"],
            font=cc.LeoFont,state='disabled')
        self.Display.pack(side="left",fill="x",expand=1)
    #@+node:ekr.20060513122450.153: *5* Go
    def Go(self):

        cc = self.cc

        if not cc.ACTIVE_NODE:
            cc.sGo()
        elif cc.ACTIVE_NODE == cc.SELECTED_NODE:
            cc.aGo()
        else:
            Error("xcc: ",str(cc.ACTIVE_NODE)+" is already active!")
    #@+node:ekr.20060513122450.154: *5* Hide
    def Hide (self):

        cc = self.cc
        self.pack_forget()
        cc.LeoBodyText.config(wrap=cc.LeoWrap)
        if cc.Watcher.visible:
            cc.Watcher.Hide()
    #@+node:ekr.20060513122450.155: *5* Show
    def Show (self):

        cc = self.cc
        self.pack(side="top",fill="x")
        cc.LeoBodyText.config(wrap='none')

        if cc.Watcher.visible:
            cc.Watcher.Show()
    #@+node:ekr.20060513122450.156: *5* OnKey
    def OnKey(self,event=None):

        cc = self.cc

        if cc.ACTIVE_NODE:
            if len(event.char)==1 and ord(event.char) == 13:
                cc.aWrite(self.DbgEntry.get().replace("\n",""))
                self.DbgEntry.delete(0,'end')
    #@+node:ekr.20060513122450.157: *5* EnableStep
    def EnableStep(self):

        self.StepButton["state"] = 'normal'
        self.StepInButton["state"] = 'normal'
        self.StepOutButton["state"] = 'normal'
    #@+node:ekr.20060513122450.158: *5* DisableStep
    def DisableStep(self):

        self.StepButton["state"] = 'disabled'
        #self.StepButton["image"] = self.Step_d

        self.StepInButton["state"] = 'disabled'
        #self.StepInButton["image"] = self.StepIn_d

        self.StepOutButton["state"] = 'disabled'
        #self.StepOutButton["image"] = self.StepOut_d
    #@+node:ekr.20060513122450.159: *5* SyncDisplayToChild
    def SyncDisplayToChild(self,loc):

        cc = self.cc
        self.Display["cursor"] = ""
        self.Display.unbind("<Button-1>")
        self.Spacer["state"] = 'normal'
        self.Spacer.pack(side="left")
        if cc.BreakBar.visible:
            self.Spacer["width"] = int(cc.BreakBar["width"])+1
        else:
            self.Spacer["width"] = 4

        self.Spacer.delete(1.0,'end')
        self.Spacer.insert('insert',"."+loc.FOUND_FILE_EXT)
        self.Spacer["state"] = 'disabled'

        disp = ":: " ; xas = ""
        for c in loc.CLASS_LIST:
            xas += c+" :: "
        disp += xas	
        off = 0
        if loc.CURRENT_RULE and loc.CURRENT_RULE != "class":
            off = len(disp)
            disp += cc.CHILD_NODE.h	

        self.Display["state"] = 'normal'
        self.Display.delete(1.0,'end')
        self.Display.tag_delete("marking")
        self.Display.insert("insert",disp)

        if loc.CURRENT_RULE == "func":
            spec,ret,name,params,pure,dest,ctors = loc.CURRENT_MATCH_OBJECT

            v,s,e = spec
            if v != "":
                self.Display.tag_add("marking","1."+str(s+off),"1."+str(e+off))

            v,s,e = ret
            if s != -1 and e != -1:
                self.Display.tag_add("marking","1."+str(s+off),"1."+str(e+off))		

            params,s,e = params
            if params != "()":
                s += 1
                params = params.split(",")
                for p in params:
                    pmo = re.search("[( ]*(?P<TYPE>.+) +(?P<NAME>[^) ]+)[ )]*",p)
                    if pmo != None:
                        s2,e2 = pmo.span("TYPE")
                        self.Display.tag_add("marking","1."+str(s+off+s2-1),"1."+str(s+off+(e2-s2)))
                        off += len(p)+1

        self.Display.tag_config("marking",foreground="#7575e5")
        self.Display["state"] = 'disabled'
    #@+node:ekr.20060513122450.160: *5* SyncDisplayToError
    def SyncDisplayToError(self):
        self.Spacer["state"] = 'normal'

        if BreakBar.visible == True:
            self.Spacer["width"] = int(BreakBar["width"])+1
        else:
            self.Spacer["width"] = 4

        self.Spacer.delete(1.0,'end')
        self.Spacer.insert(INSERT,"ERR")
        self.Spacer["state"] = 'disabled'

        self.Display["state"] = 'normal'
        self.Display.delete(1.0,'end')
        self.Display.tag_delete("marking")

        self.Display.insert("insert",PARSE_ERROR)
        self.Display.tag_add("marking","1.0",'end')
        self.Display.tag_config("marking",foreground="red")
        self.Display["state"] = 'disabled'

        self.Display["cursor"] = "hand2"
        c.bind(self.Display,"<Button-1>",self.OnErrorLeftClick)

    #@+node:ekr.20060513122450.161: *5* SetError
    def SetError(self,err,node=None):
        global PARSE_ERROR,PARSE_ERROR_NODE

        PARSE_ERROR = err
        PARSE_ERROR_NODE = node
    #@+node:ekr.20060513122450.162: *5* OnErrorLeftClick
    def OnErrorLeftClick(self,event):

        self.cc.GoToNode(PARSE_ERROR_NODE)
    #@+node:ekr.20060513122450.163: *5* HideInput
    def HideInput(self):
        self.PromptButton.pack_forget()
        self.DbgEntry.pack_forget()
    #@+node:ekr.20060513122450.164: *5* ShowInput
    def ShowInput(self):

        self.ConfigButton.pack_forget()
        self.WatchButton.pack_forget()

        self.PromptButton.pack(side="left")
        self.DbgEntry.pack(side="left",fill="x",expand=1)

        self.ConfigButton.pack(side="right")
        self.WatchButton.pack(side="right")
    #@+node:ekr.20060513122450.165: *5* Refresh
    def Refresh(self):

        cc = self.cc

        if (
            cc.ACTIVE_NODE and cc.DBG_PROMPT and
            cc.ACTIVE_NODE != cc.SELECTED_NODE
        ):
            cc.GoToNode(ACTIVE_NODE)
            QUERYGOTASK(cc)
            cc.DbgOut("")
    #@-others

#@+node:ekr.20060513122450.166: *4* class WatcherClass
class WatcherClass(Tk.Frame):

    #@+others
    #@+node:ekr.20060513122450.167: *5* __init__
    def __init__(self,cc):

        self.cc = cc
        self.Watching = False
        self.visible = False

        Tk.Frame.__init__(self,cc.LeoFrame.split1Pane2,relief='groove')

        self.EditFrame = Tk.Frame(self,relief='groove')
        self.VarEntry = Tk.Entry(self.EditFrame)
        c.bind(self.VarEntry,"<Key>",self.OnEditKey)
        self.VarEntry.pack(side="left",fill="x",expand=1)
        self.EditFrame.pack(side="top",fill="x")

        self.BoxFrame = Tk.Frame(self,relief='groove')
        self.BoxBar = Tk.Scrollbar(self.BoxFrame,command=self.yview)
        self.InBox = Tk.Text(
            self.BoxFrame,
                yscrollcommand=self.BoxBar.set,font=cc.LeoFont,
                state='disabled',width=20,wrap='none',height=10,
                selectbackground="white",selectforeground="black")
        self.InBox.pack(side="left",fill="both",expand=1)
        self.BoxBar.pack(side="left",fill="y")

        self.OutBox = Tk.Text(
            self.BoxFrame,yscrollcommand=self.BoxBar.set,
            font=cc.LeoFont,state='disabled',width=20,wrap='none',height=10,
            selectbackground="white",selectforeground="black")
        self.OutBox.pack(side="left",fill="both",expand=1)

        self.BoxFrame.pack(fill="both",expand=1)
        c.bind(self.InBox,"<Delete>",self.OnDelete)
        c.bind(self.OutBox,"<Delete>",self.OnDelete)
        c.bind(self.InBox,"<Button-1>",self.OnLeftClick)
        c.bind(self.OutBox,"<Button-1>",self.OnLeftClick)
    #@+node:ekr.20060513122450.168: *5* OnEditKey
    def OnEditKey(self,event):

        cc = self.cc

        if not self.Watching and len(event.char)==1 and ord(event.char) == 13:
            self.InBox.config(state='normal')
            self.OutBox.config(state='normal')

            var = self.VarEntry.get()
            cc.sGet("Watch",[]).append(var)

            self.InBox.mark_set("insert",'end')			
            self.InBox.insert("insert",var+"\n")

            self.OutBox.mark_set("insert",'end')
            self.OutBox.insert("insert","- ?? -\n")

            self.InBox.config(state='disabled')
            self.OutBox.config(state='disabled')
            self.VarEntry.delete(0, 'end')

            if cc.ACTIVE_PROCESS and cc.DBG_PROMPT and cc.SELECTED_NODE == cc.ACTIVE_NODE:
                WATCHTASK(cc)
                cc.DbgOut("")
            #TODO: send a WATCHTASK if breaked
    #@+node:ekr.20060513122450.169: *5* OnLeftClick
    def OnLeftClick(self,event):

        if self.InBox.get(1.0,'end').replace("\n",""):
            w = event.widget
            w.mark_set("insert","@0,"+str(event.y))
            l,c = w.index("insert").split(".")

            self.InBox.tag_delete("current")
            self.InBox.tag_add("current",l+".0",l+".end")
            self.InBox.tag_config("current",background=BreakColor)

            self.OutBox.tag_delete("current")
            self.OutBox.tag_add("current",l+".0",l+".end")
            self.OutBox.tag_config("current",background=BreakColor)
    #@+node:ekr.20060513122450.170: *5* OnDelete
    def OnDelete(self,event):
        if "current" in self.InBox.tag_names():
            ib = self.InBox ; ob = self.OutBox
            ib.config(state='normal')
            ob.config(state='normal')
            s,e = ib.tag_nextrange("current","1.0")
            var = ib.get(s,e)	
            watchs = sGet("Watch",[])
            if var in watchs:
                watchs.remove(var)		
            ib.delete(s,e+"+1c")
            ib.tag_delete("current")

            s,e = ob.tag_nextrange("current","1.0")
            ob.delete(s,e+"+1c")
            ob.tag_delete("current")
            ib.config(state='disabled')
            ob.config(state='disabled')
    #@+node:ekr.20060513122450.171: *5* yview
    def yview(self, *args):

        apply(self.InBox.yview,args)
        apply(self.OutBox.yview,args)
    #@+node:ekr.20060513122450.172: *5* Hide
    def Hide(self):

        cc = self.cc
        self.pack_forget()
        self.visible = False
        cc.ToolBar.WatchButton.config(
            command=self.Show,relief='raised')
    #@+node:ekr.20060513122450.173: *5* Show
    def Show(self):

        cc = self.cc
        if cc.Config.visible:
            cc.Config.Hide()
        cc.LeoBodyText.pack_forget()
        cc.LeoXBodyBar.pack_forget()
        cc.LeoYBodyBar.pack_forget()
        self.pack(side = "bottom",fill="x")
        cc.LeoXBodyBar.pack(side = "bottom",fill="x")
        cc.LeoYBodyBar.pack(side="right",fill="y")
        if cc.BreakBar.visible:
            cc.BreakBar.Hide()
            cc.BreakBar.Show()
        cc.LeoBodyText.pack(fill="both",expand=1)
        cc.ToolBar.WatchButton.config(command=self.Hide,relief='sunken')
        self.visible = True
        self.Sync()
        if cc.ACTIVE_PROCESS and cc.DBG_PROMPT and cc.SELECTED_NODE == cc.ACTIVE_NODE:
            WATCHTASK(cc)
            cc.DbgOut("")
    #@+node:ekr.20060513122450.174: *5* Sync
    def Sync(self):

        cc = self.cc

        if self.visible == True:
            self.InBox.config(state='normal')
            self.OutBox.config(state='normal')

            self.InBox.delete(1.0,'end')
            self.OutBox.delete(1.0,'end')

            for v in cc.sGet("Watch",[]):
                self.InBox.mark_set("insert",'end')			
                self.InBox.insert("insert",v+"\n")

                self.OutBox.mark_set("insert",'end')
                self.OutBox.insert("insert","- ?? -\n")	

            self.InBox.config(state='disabled')
            self.OutBox.config(state='disabled')
    #@-others
#@+node:ekr.20060513122450.175: *4* class BreakbarClass
class BreakbarClass(Tk.Text):

    #@+others
    #@+node:ekr.20060513122450.176: *5* __init__
    def __init__(self,cc):

        self.cc = cc ; c = cc.c
        self.bodychanged = False	
        self.visible = False
        coffset = 10
        c = cc.LeoBodyText.winfo_rgb(cc.LeoBodyText["bg"])	
        red, green, blue = c[0]/256, c[1]/256, c[2]/256
        red -= coffset ; green -= coffset ; blue -= coffset	
        self.bgcolor = "#%02x%02x%02x" % (red,green,blue)
        red -= coffset*6 ; green -= coffset*6 ; blue -= coffset*6
        self.fgcolor = "#%02x%02x%02x" % (red,green,blue)

        Tk.Text.__init__(self,
            cc.LeoFrame.split1Pane2,
            name='sidebar',
            width=2,
            bd=cc.LeoBodyText["bd"],
            bg = self.bgcolor,
            relief='flat',
            setgrid=0,
            selectbackground = self.bgcolor,
            selectforeground = self.fgcolor,
            foreground = self.fgcolor,
            font=cc.LeoFont,
            pady=cc.LeoBodyText["pady"],
            cursor="hand2",
            wrap='none'
        )

        self.leowrap = cc.LeoBodyText["wrap"]
        c.bind(self,"<Button-1>",self.OnLeftClick)
        c.bind(self,"<Button-3>",self.OnRightClick)
        self["state"]='disabled'
        cc.LeoBodyText.pack_forget()
        cc.LeoXBodyBar.pack(side="bottom", fill="x")
        cc.LeoBodyText.pack(expand=1, fill="both")
    #@+node:ekr.20060513122450.177: *5* Scrollbar funcs
    #@+node:ekr.20060513122450.178: *6* yview
    def yview(self,cmd=None,arg1=None,arg2=None):

        cc = self.cc ; w = cc.LeoBodyText

        if cmd:
            if arg1 != None:
                if arg2 != None:
                    w.yview(cmd,arg1,arg2)
                    Tk.Text.yview(self,cmd,arg1,arg2)
                else:
                    w.yview(cmd,arg1)
                    Tk.Text.yview(self,cmd,arg1)
        else:
            return w.yview()
    #@+node:ekr.20060513122450.179: *6* setForBody
    def setForBody(self,lo, hi):

        cc = self.cc

        Tk.Text.yview(self,'moveto',lo)	
        cc.LeoYBodyBar.set(lo,hi)	
    #@+node:ekr.20060513122450.180: *6* setForBar
    def setForBar(self,lo, hi):

        cc = self.cc
        cc.LeoBodyText.yview('moveto',lo)	
        cc.LeoYBodyBar.set(lo,hi)
    #@+node:ekr.20060513122450.181: *6* Plug
    def Plug(self):

        cc = self.cc ; c = cc.c

        c.bind(cc.LeoBodyText,g.angleBrackets("Cut"),self.OnCut)
        c.bind(cc.LeoBodyText,g.angleBrackets("Paste"),self.OnPaste)
        cc.LeoYBodyBar.config(command=self.yview)
        cc.LeoBodyText["yscrollcommand"] = self.setForBody
        self["yscrollcommand"] = self.setForBar
    #@+node:ekr.20060513122450.182: *6* UnPlug
    def UnPlug(self):

        cc = self.cc ; c = cc.c

        c.bind(cc.LeoBodyText,g.angleBrackets("Cut"),cc.LeoFrame.OnCut)
        c.bind(cc.LeoBodyText,g.angleBrackets("Paste"),cc.LeoFrame.OnPaste)
        cc.LeoYBodyBar.config(command=cc.LeoBodyText.yview)
        cc.LeoBodyText["yscrollcommand"] = cc.LeoYBodyBar.set
        self["yscrollcommand"] = None
    #@+node:ekr.20060513122450.183: *5* Events
    #@+node:ekr.20060513122450.184: *6* OnCut
    def OnCut(self,event=None):
        LeoFrame.OnCut(event)#do normal stuff
        self.bodychanged = True
    #@+node:ekr.20060513122450.185: *6* OnPaste
    def OnPaste(self,event=None):
        LeoFrame.OnPaste(event)#do normal stuff
        self.bodychanged = True
    #@+node:ekr.20060513122450.186: *6* OnRightClick
    def OnRightClick(self,event):
        try:
            c = self.c
            m = Menu(self)
            c.add_command(m,label="Delete Node Breaks", command=self.DeleteNodeBreaks)
            c.add_command(m,label="Delete Project Breaks", command=self.DeleteProjectBreaks)
            m.add_separator()
            c.add_command(m,label="Cancel",command=lambda :self.Cancel(m))

            m.post(event.x_root,event.y_root)
        except Exception:
            TraceBack()
    #@+node:ekr.20060513122450.187: *6* OnLeftClick
    def OnLeftClick(self,event):

        cc = self.cc
        self["state"] = 'normal'	
        self.mark_set("insert","@0,"+str(event.y))
        self["state"] = 'disabled'
        l,c = self.index("insert").split(".")
        breaks = cGet("BreakPoints")

        loc = LocatorClass(cc,CHILD_NODE,l)
        if loc.FOUND_FILE_LINE == None:
            return

        filext = loc.FOUND_FILE_EXT.replace(".","")

        if l in breaks:
            self.DeleteBreak(filext,loc.FOUND_FILE_LINE,l)
        else:
            t = cc.LeoBodyText.get(str(l)+".0",str(l)+".end")
            if t != "\n" and t != "" and t.strip() != "@others":
                self.AddBreak(filext,loc.FOUND_FILE_LINE,l)

        self.tag_delete(SEL)
    #@+node:ekr.20060513122450.188: *5* Node breaks
    #@+node:ekr.20060513122450.189: *6* AddNodeBreak
    def AddNodeBreak(self,l,s="Enabled"):
        cGet("BreakPoints")[l] = s
    #@+node:ekr.20060513122450.190: *6* DeleteNodeBreak
    def DeleteNodeBreak(self,l):
        breaks = cGet("BreakPoints")
        if l in breaks:
            del breaks[l]
    #@+node:ekr.20060513122450.191: *6* ClearNodeBreaks
    def ClearNodeBreaks(self):
        cSet("BreakPoints",{})
    #@+node:ekr.20060513122450.192: *6* BreaksFromNode
    def BreaksFromNode(self):

        cc = self.cc
        self.ClearBreakTags()
        self.Sync()

        breaks = cc.cGet("BreakPoints",{})
        for l,s in breaks.iteritems():
            self.AddBarBreak(l,s)
            self.AddBreakTag(l)
    #@+node:ekr.20060513122450.193: *5* Bar Breaks
    #@+node:ekr.20060513122450.194: *6* AddBarBreak
    def AddBarBreak(self,l,s="Enabled"):
        self["state"] = 'normal'
        #----------------------------------------

        fl = self.get(l+".0",l+".end")
        self.insert(l+".end",(int(self["width"])-len(str(fl))-1)*" "+">")
        self.tag_add(l,l+".0",l+".end")

        if s == "Enabled":
            self.tag_config(l,foreground="blue")
        else:
            self.tag_config(l,foreground="gray")
        #-----------------------------------------
        self["state"] = 'disabled'

    #@+node:ekr.20060513122450.195: *6* DeleteBarBreak
    def DeleteBarBreak(self,l):
        self["state"] = 'normal'
        #----------------------------------------
        #self.insert(l+".end -2c","  ")
        self.delete(l+".end -1c",l+".end")
        self.tag_delete(l)	


        #-----------------------------------------
        self["state"] = 'disabled'
        self.update_idletasks()


    #@+node:ekr.20060513122450.196: *6* ClearBarBreaks
    def ClearBarBreaks(self):

        cc = self.cc
        self["state"] = 'normal'
        self.delete(1.0,'end')	
        #----------------------------------------
        if cc.CHILD_LINE and cc.CHILD_LINE != -1:
            fl = cc.CHILD_LINE
            lines = cc.CHILD_NODE.b.splitlines()

            while len(lines) > 0:
                l = lines.pop(0)
                if l.strip() != "@others":
                    self.insert("end",str(fl)+"\n")
                    fl += 1
                else:
                    break

            if len(lines) > 0 and l.strip() == "@others":
                self.insert("end","\n")

                loc = LocatorClass(cc,cc.CHILD_NODE,fl-cc.CHILD_LINE+2)
                fl = loc.FOUND_FILE_LINE

                if fl != None:
                    while len(lines) > 0:
                        l = lines.pop(0)
                        self.insert("end",str(fl)+"\n")
                        fl += 1

            self.config(width = len(str(fl))+1)
        #-----------------------------------------
        self["state"] = 'disabled'
    #@+node:ekr.20060513122450.197: *5* tag breaks
    #@+node:ekr.20060513122450.198: *6* AddBreakTag
    def AddBreakTag(self,l):

        w = self.cc.LeoBodyText

        w.tag_add("xcc_break",l+".0",l+".end")
    #@+node:ekr.20060513122450.199: *6* DeleteBreakTag
    def DeleteBreakTag(self,s,e=None):

        w = self.cc.LeoBodyText

        if e == None:
            w.tag_remove("xcc_break",s+".0",s+".end")
        else:
            w.tag_remove("xcc_break",s,e)
    #@+node:ekr.20060513122450.200: *6* ClearBreakTags
    def ClearBreakTags(self):

        w = self.cc.LeoBodyText
        w.tag_delete("xcc_break")
        w.tag_config("xcc_break",background=self.bgcolor)
    #@+node:ekr.20060513122450.201: *6* BreaksFromTags
    def BreaksFromTags(self):

        w = self.cc.LeoBodyText
        self.ClearNodeBreaks()
        self.ClearBarBreaks()
        range = w.tag_nextrange("xcc_break","1.0")
        while len(range) > 0:
            s,e = range
            el,ec = e.split(".")
            self.DeleteBreakTag(s,e)
            self.AddBreak(CHILD_EXT,CHILD_LINE,el)
            range = w.tag_nextrange("xcc_break",el+".end")
    #@+node:ekr.20060513122450.202: *5* AddBreak
    def AddBreak(self,filext,fileline,bodyline,state="Enabled"):

        cc = self.cc
        breaks = sGet("BreakPoints",{})

        breaks[filext+":"+str(fileline)] = state
        self.AddNodeBreak(bodyline,state)
        self.AddBarBreak(bodyline,state)
        self.AddBreakTag(bodyline)

        if cc.ACTIVE_PROCESS:
            bpat = cc.DBG.get("Set break")
            bpat = bpat.replace("_FILE_",cc.NAME+"."+filext).replace("_LINE_",str(fileline))
            DBGTASK(cc,bpat)
            if cc.DBG_PROMPT:
                cc.DbgOut("")

    #@+node:ekr.20060513122450.203: *5* DeleteBreak
    def DeleteBreak(self,filext,fileline,bodyline):

        cc = self.cc
        breaks = cc.sGet("BreakPoints",{})

        if filext+":"+str(fileline) in breaks:
            del breaks[filext+":"+str(fileline)]	

        self.DeleteNodeBreak(bodyline)
        self.DeleteBarBreak(bodyline)
        self.DeleteBreakTag(bodyline)

        if cc.ACTIVE_PROCESS:
            if cc.DBG.get("Clear break",'').find("_ID_") != -1:
                BREAKIDTASK(cc,[filext,str(fileline)])
            else:
                DBGTASK(cc,
                    ReplaceVars(cc.DBG["Clear break"]).replace("_FILE_",filext).replace("_LINE_",str(fileline)))

            if cc.DBG_PROMPT:
                cc.DbgOut("")
    #@+node:ekr.20060513122450.204: *5* DeleteNodeBreaks
    def DeleteNodeBreaks(self):

        cc = self.cc

        breaks = cGet("BreakPoints",{})

        if cc.CHILD_LINE and cc.CHILD_EXT and cc.ACTIVE_PROCESS:
            for bp in breaks.keys():				
                self.DeleteBreak(CHILD_EXT,CHILD_LINE+int(bp),int(bp))
                if cc.ACTIVE_PROCESS:
                    self.DeleteDbgBreaks()

        cSelect(cc.CHILD_NODE)
    #@+node:ekr.20060513122450.205: *5* DeleteProjectBreaks
    def DeleteProjectBreaks(self):

        cc = self.cc

        if cc.SELECTED_NODE:
            for c in cc.SELECTED_NODE.subtree():
                ua = cc.GetUnknownAttributes(c.v)
                if ua and "xcc_child_cfg" in ua.keys():
                    if "BreakPoints" in ua["xcc_child_cfg"].keys():
                        ua["xcc_child_cfg"]["BreakPoints"] = {}

            cc.cSelect(cc.CHILD_NODE)
    #@+node:ekr.20060513122450.206: *5* Hide
    def Hide(self,erase = False):

        w = self.cc.LeoBodyText
        self.UnPlug()
        self.pack_forget()
        w.pack(expand=1, fill="both")
        w.tag_delete("xcc_break")
        self.visible = False
    #@+node:ekr.20060513122450.207: *5* Show
    def Show (self):

        cc = self.cc ; w = cc.LeoBodyText
        self.Plug()
        w.pack_forget()
        if self.leowrap != 'none':
            cc.LeoXBodyBar.pack(side="bottom",fill="x")
        border = cc.LeoBodyText ["bd"]
        self.config(pady=cc.LeoBodyText["pady"],bd=border)
        self.pack(side='left',fill="y")
        cc.LeoBodyText.pack(expand=1,fill="both")
        self.BreaksFromNode()
        self.visible = True
    #@+node:ekr.20060513122450.208: *5* Sync
    def Sync(self):

        cc = self.cc
        self["state"] = 'normal'
        self.delete(1.0,'end')	
        #----------------------------------------
        w=4
        if cc.CHILD_LINE and cc.CHILD_LINE != -1:
            fl = cc.CHILD_LINE
            lines = cc.CHILD_NODE.b.splitlines()

            while len(lines) > 0:
                l = lines.pop(0)
                if l.strip() != "@others":
                    self.insert("end",str(fl)+"\n")
                    fl += 1
                else:
                    break

            if len(lines) > 0 and l.strip() == "@others":
                self.insert("end","\n")

                loc = LocatorClass(cc,cc.CHILD_NODE,fl-cc.CHILD_LINE+2)
                fl = loc.FOUND_FILE_LINE

                if fl != None:
                    while len(lines) > 0:
                        l = lines.pop(0)
                        self.insert("end",str(fl)+"\n")
                        fl += 1
            if len(str(fl))+1 < w:
                pass
            else:
                w = len(str(fl))+1
        self.config(width = w)
        #-----------------------------------------
        self["state"] = 'disabled'
    #@+node:ekr.20060513122450.209: *5* IdleUpdate
    def IdleUpdate(self):
        if self.bodychanged == True:
            self.Sync()
            self.bodychanged = False
    #@+node:ekr.20060513122450.210: *5* Cancel
    def Cancel(self,menu):
        menu.unpost()

    #@-others
#@+node:ekr.20060513122450.211: *3* Parsing classes
#@+node:ekr.20060513122450.212: *4* class CppParserClass
class CppParserClass:

    #@+others
    #@+node:ekr.20060513122450.213: *5* Rules
    #@+node:ekr.20060513122450.214: *6* LoadCppRules
    def LoadCppRules(self):

        parser = self

        self.OUTFUNC_RULES = [
            self.DocRuleClass(parser),
            self.COMMENTRULE(parser),	#placed fisrt to allow functions and class to be commented out
            self.FUNCRULE(parser),
            self.CLASSRULE(parser),	#must be after CppFuncRule or it will catch template funcs
            self.DEFAULTRULE(parser)	#must be the last rule cos it always proceed
        ]

        self.RULES = self.OUTFUNC_RULES

        self.INFUNC_RULES = [
            self.DocRuleClass(parser),
            self.FUNCCOMMENTRULE(parser),	#placed fisrt to allow functions and class to be commented out
            self.FUNCDEFAULTRULE(parser)	#must be the last rule cos it always proceed
        ]
    #@+node:ekr.20060513122450.215: *6* class DocRuleClass
    class DocRuleClass:

        #@+others
        #@+node:ekr.20060513225027: *7* ctor
        def __init__ (self,Parser):

            self.Parser = Parser
        #@+node:ekr.20060513122450.216: *7* Match
        def Match(self,head):

            if head.startswith("@"):
                return head
            else:
                return None
        #@+node:ekr.20060513122450.217: *7* OnMatch
        def OnMatch(self,mo,node):

            self.Parser.SetRealBodyDestination()	
            return True
        #@-others
    #@+node:ekr.20060513122450.218: *6* COMMENTRULE
    class COMMENTRULE:
        #@+others
        #@+node:ekr.20060513225814: *7* ctor
        def __init__ (self,Parser):

            self.Parser = Parser
        #@+node:ekr.20060513122450.219: *7* Match
        def Match(self,head):
            if head.startswith("//"):
                if head.endswith(";"):
                    return True
                else:
                    return False
            else:
                return None

        #@+node:ekr.20060513122450.220: *7* OnMatch
        def OnMatch(self,mo,node):

            Parser = self.Parser

            w = Parser.CLASS_WRITER or (mo and Parser.Define) or Parser.Declare
            Parser.SetRealBodyDestination(w)
            Parser.CURRENT_LOCATION = "head"
            w(Parser.TAB_STRING+"/*"+node.h[2:]+"\n")
            Parser.Tab()

            if Parser.WriteOthers(node,w) == False:
                return False

            Parser.CURRENT_LOCATION = "tail"
            Parser.UnTab()
            w(Parser.TAB_STRING+"*/\n")

            return True
        #@-others
    #@+node:ekr.20060513122450.221: *6* FUNCRULE
    class FUNCRULE:
        #@+others
        #@+node:ekr.20060513225814.1: *7* ctor
        def __init__ (self,Parser):

            self.Parser = Parser
        #@+node:ekr.20060513122450.222: *7* Match
        def Match(self,head):	
            params_e = head.rfind(")")
            if params_e > -1:

                tctors = head.split(":")
                head = tctors.pop(0)

                ctors = ""
                for c in tctors:
                    ctors += ":"+c		

                head = head.split()
                head = string.join(head)
                params_e = head.rfind(")")
                params_s = head.rfind("(",0,params_e)

                if params_s > -1:
                    # pure & dest ----------------------
                    pure_s = head.find("=0",params_e)
                    if pure_s > -1:				
                        pure = (head[pure_s:pure_s+2],pure_s,pure_s+2)
                        dest = (head[pure_s+2:],pure_s+2,len(head))
                    else:
                        pure = ("",-1,-1)
                        dest = (head[params_e+1:],params_e+1,len(head))

                    # params ------------------------			
                    params = (head[params_s:params_e+1],params_s,params_e+1)			

                    # name ---------------------------
                    name_s = head.find("operator")
                    if name_s == -1:
                        name_s = head.rfind(" ",0,params_s)
                        if name_s > -1:
                            name_s += 1

                    if name_s > 0:
                        name = (head[name_s:params_s],name_s,params_s)

                        ret_s = head.rfind(" ",0,name_s-1)

                        if ret_s > -1:
                            ret = (head[ret_s+1:name_s-1],ret_s+1,name_s-1)
                            spec = (head[:ret_s],0,ret_s)
                        else:
                            ret = (head[:name_s],0,name_s)
                            spec = ("",-1,-1)
                    else:
                        name = (head[:params_s],0,params_s)
                        ret = ("",-1,-1)
                        spec = ("",-1,-1)

                    r = (spec,ret,name,params,pure,dest,ctors)
                    return r




            return None

        #@+node:ekr.20060513122450.223: *7* OnMatch
        def OnMatch(self,mo,node):

            Parser = self.Parser
            Parser.CURRENT_RULE = "func"

            spec,ret,name,params,pure,dest,ctors = self.Groups = mo

            wf = Parser.CLASS_WRITER or (dest[0] == "" and Parser.Declare) or Parser.Define

            # if Parser.CLASS_WRITER:
                # wf = Parser.CLASS_WRITER
            # else:	
                # if dest[0] == "":
                    # wf = Parser.Declare#in hdr if EXT != cpp or EXT != c
                # else:
                    # wf = Parser.Define#in src if EXT != h	

            if pure[0] == "":#define the func, possibly splitted

                if dest[0] == "":#func is not splitted
                    return self.DefineFunc(wf,node,full=True)

                else:#func may be splitted
                    if Parser.Declare != Parser.Define and dest[0] != "":#func may be splitted
                        if Parser.CLASS_WRITER == None:#func may be splitted
                            if "!" not in dest[0]:
                                if self.DeclareFunc(Parser.Declare) == False:
                                    return False
                                return self.DefineFunc(Parser.Define,node)
                            else:
                                return self.DefineFunc(Parser.Define,node,full=True)

                        else:	#func may be splitted					
                            if Parser.CLASS_WRITER == Parser.Declare:#func is split
                                if self.DeclareFunc(Parser.Declare) == False:
                                    return False
                                return self.DefineFunc(Parser.Define,node,push=True)

                            else:#func is not splitted, written with the class	
                                return self.DefineFunc(Parser.CLASS_WRITER,node)

                    else:#func is not splitted
                        return self.DefineFunc(wf,node,full=True)

            else:#only declare the func, real destination depend upon DEST group and EXT
                return self.DeclareFunc(wf)

        #@+node:ekr.20060513122450.224: *7* DeclareFunc
        def DeclareFunc(self,wf):

            Parser = self.Parser
            spec,ret,name,params,pure,dest,ctors = self.Groups

            if name[0] == "":
                ToolBar.SetError("No function name in : "+GetNodePath(Parser.CURRENT_NODE),Parser.CURRENT_NODE)
                return False

            proto = spec[0] +" "+ ret[0] +" "+ name[0] + params[0] + pure[0] +";"

            Parser.SetRealBodyDestination()
            Parser.CURRENT_LOCATION = "head"
            Parser.CURRENT_FUNC = proto
            #wf(Parser.TAB_STRING+Parser.CODE_SPLITER)
            wf(Parser.TAB_STRING+proto.strip()+"\n")	

            return True
        #@+node:ekr.20060513122450.225: *7* DefineFunc
        def DefineFunc(self,wf,node,full=False,push=False):
            # global LOCATE_CHILD,PARSE_ERROR
            Parser = self.Parser
            spec,ret,name,params,pure,dest,ctors = self.Groups
            if name[0] == "":
                ToolBar.SetError("No function name in : "+GetNodePath(Parser.CURRENT_NODE),Parser.CURRENT_NODE)
                return False

            Parser.FUNC_WRITER = wf
            proto = ""
            xas = "" #access specifier

            if full == True:
                proto = spec[0]+" "
                params = params[0].strip("()")
            else:
                for n in Parser.CLASS_LIST:#if full == True, declared and defined at once, so no access specifier
                    if n != None:
                        xas = n+"::"+xas

                #if this is not a full definition, must remove default parameter assignement
                params = params[0].strip("()")
                paramslist = params.split(",")
                params = ""
                for p in paramslist:
                    pa = p.split("=")
                    if params != "":
                        params += ","+pa[0]
                    else:
                        params += pa[0]

            proto += ret[0]+" "+xas+name[0]+"("+params+")"+ctors
            proto = proto.strip()

            push and Parser.PushTab()

            Parser.SetRealBodyDestination(wf)
            Parser.CURRENT_LOCATION = "head"
            Parser.CURRENT_FUNC = proto
            if FUNC_HDR != "":
                wf(Parser.TAB_STRING+FUNC_HDR)
            wf(Parser.TAB_STRING+proto+FUNC_OPN)
            Parser.Tab()

            Parser.RULES = Parser.INFUNC_RULES	
            if Parser.WriteOthers(node,wf) == False:
                return False	
            Parser.RULES = Parser.OUTFUNC_RULES

            Parser.CURRENT_FUNC = ""
            Parser.UnTab()
            Parser.CURRENT_LOCATION = "tail"	
            wf(Parser.TAB_STRING+"}\n")
            if FUNC_FTR != "":
                wf(Parser.TAB_STRING+FUNC_FTR)

            push and Parser.PopTab()

            return True
        #@-others
    #@+node:ekr.20060513122450.226: *6* CLASSRULE
    class CLASSRULE:
        #@+others
        #@+node:ekr.20060513225814.2: *7* ctor
        def __init__ (self,Parser):

            self.Parser = Parser
        #@+node:ekr.20060513122450.227: *7* Match
        #"^(?P<SPEC>.*) *class +(?P<NAME>[^;:!]+)* *(?P<BASE>:[^;!]+)* *(?P<INST>![^;]+)* *(?P<DEST>;$)*"
        #spec class name base inst dest
        def Match(self,head):
            #return self.Matcher.search(head)
            class_s = head.find("class ")
            if class_s > -1:
                head = head.split()
                head = string.join(head)
                class_s = head.rfind("class ")

                spec = (head[:class_s],0,class_s)
                name_s = class_s+6		
                dest_s = head.find(";",name_s)
                inst_s = head.find("!",name_s)
                base_s = head.find(":",name_s)

                #dest -----------------------
                if dest_s > -1:
                    name_e = dest_s
                    dest = (head[dest_s:dest_s+1],dest_s,dest_s+1)
                    inst_e = dest_s
                    base_e = dest_s
                else:
                    dest = ("",-1,-1)
                    name_e = inst_e = base_e = len(head)

                #inst --------------------------
                if inst_s > -1:
                    name_e = inst_s
                    base_e = inst_s
                    inst = (head[inst_s:inst_e],inst_s,inst_e)
                else:
                    inst = ("",-1,-1)

                #base ---------------------------------		
                if base_s > -1:
                    name_e = base_s
                    base = (head[base_s:base_e],base_s,base_e)
                else:
                    base = ("",-1,-1)

                name = (head[name_s:name_e],name_s,name_e)

                return (spec,name,base,inst,dest)

            return None	
        #@+node:ekr.20060513122450.228: *7* OnMatch
        def OnMatch(self,mo,node):
            # global LOCATE_CHILD

            Parser = self.Parser
            Parser.CURRENT_RULE = "class"

            spec,name,base,inst,dest = mo

            #determine where to write
            if len(Parser.CLASS_LIST) == 0:#redirect only for the root class
                if dest[0] != "":#directed toward source
                    cw = Parser.CLASS_WRITER = Parser.Define
                else:
                    cw = Parser.CLASS_WRITER = Parser.Declare
            else:
                cw = Parser.CLASS_WRITER

            if Parser.CLASS_WRITER == Parser.Define and Parser.Declare != Parser.Define:
                push = True
            else:
                push = False

            cdec = ""

            if spec[0] != "":
                cdec += spec[0]+" "

            if name[0] == "":
                ToolBar.SetError("No name in class definition :"+GetNodePath(Parser.CURRENT_NODE),Parser.CURRENT_NODE)
                return False

            cdec += "class "+name[0]

            if base[0] != "":
                cdec += base[0]

            if push == True:
                Parser.PushTab()

            Parser.CLASS_LIST.append(name[0])
            Parser.CURRENT_LOCATION = "head"
            Parser.SetRealBodyDestination(cw)
            if CLASS_HDR != "":
                cw(Parser.TAB_STRING+CLASS_HDR)
            cw(Parser.TAB_STRING+cdec+FUNC_OPN)
            Parser.Tab()
            if Parser.WriteOthers(node,cw) == False:
                return False
            Parser.UnTab()
            Parser.CURRENT_LOCATION = "tail"
            cw(Parser.TAB_STRING+"}"+inst[0][1:]+";\n")
            if CLASS_FTR != "":
                cw(Parser.TAB_STRING+CLASS_FTR)	
            Parser.CLASS_LIST.pop()

            push and Parser.PopTab()

            if len(Parser.CLASS_LIST) == 0:
                Parser.CLASS_WRITER = None		

            return True
        #@-others
    #@+node:ekr.20060513122450.229: *6* DEFAULTRULE
    class DEFAULTRULE:
        #@+others
        #@+node:ekr.20060513122450.230: *7* __init__
        def __init__(self,Parser):

            self.Parser = Parser
            self.Matcher = re.compile("(?P<HEAD>[^;]*)(?P<DEST>;$)*")
        #@+node:ekr.20060513122450.231: *7* Match
        def Match(self,head):
            if head.endswith(";"):
                return True
            return False
        #@+node:ekr.20060513122450.232: *7* OnMatch
        def OnMatch(self,mo,node):

            Parser = self.Parser
            w = Parser.CLASS_WRITER or (mo and Parser.Define) or Parser.Declare

            # if Parser.CLASS_WRITER:
                # w = Parser.CLASS_WRITER
            # else:
                # if mo == True:
                    # w = Parser.Define			
                # else:
                    # w = Parser.Declare

            if mo:
                head = node.h[:-1]
            else:
                head = node.h

            Parser.SetRealBodyDestination(w)
            Parser.CURRENT_LOCATION = "head"
            w(Parser.TAB_STRING+"//"+head+"\n")
            Parser.Tab()

            if Parser.WriteOthers(node,w) == False:
                return False

            Parser.UnTab()	
            Parser.CURRENT_LOCATION = "tail"	
            w("\n")
            return True
        #@-others
    #@+node:ekr.20060513122450.233: *6* FUNCCOMMENTRULE
    class FUNCCOMMENTRULE:
        #@+others
        #@+node:ekr.20060513122450.234: *7* __init__
        def __init__(self,Parser):

            self.Parser = Parser	
            self.Matcher = re.compile("^//(?P<HEAD>.*)")
        #@+node:ekr.20060513122450.235: *7* Match
        def Match(self,head):
            return self.Matcher.search(head)
        #@+node:ekr.20060513122450.236: *7* OnMatch
        def OnMatch(self,mo,node):

            Parser = self.Parser
            w = Parser.FUNC_WRITER
            groups = mo.groupdict()

            head = groups["HEAD"]
            if head == None:
                head = ""

            Parser.CURRENT_LOCATION = "head"
            w(Parser.TAB_STRING+head+"\n")
            Parser.Tab()

            if Parser.WriteOthers(node,w) == False:
                return False

            Parser.CURRENT_LOCATION = "tail"
            Parser.UnTab()
            w(Parser.TAB_STRING+"*/\n")

            return True
        #@-others
    #@+node:ekr.20060513122450.237: *6* FUNCDEFAULTRULE
    class FUNCDEFAULTRULE:
        #@+others
        #@+node:ekr.20060513122450.238: *7* __init__
        def __init__(self,Parser):

            self.Parser = Parser
            self.Matcher = re.compile("(?P<HEAD>.*)")
        #@+node:ekr.20060513122450.239: *7* Match
        def Match(self,head):

            return self.Matcher.search(head)
        #@+node:ekr.20060513122450.240: *7* OnMatch
        def OnMatch(self,mo,node):

            Parser = self.Parser
            w = Parser.FUNC_WRITER
            groups = mo.groupdict()

            head = groups["HEAD"]
            if head == None:
                head = ""

            Parser.CURRENT_LOCATION = "head"
            w(Parser.TAB_STRING+"//"+head+"\n")
            Parser.Tab()

            if Parser.WriteOthers(node,w) == False:
                return False

            Parser.UnTab()	
            Parser.CURRENT_LOCATION = "tail"	
            w("\n")
            return True
        #@-others
    #@+node:ekr.20060513122450.241: *5* __init__
    def __init__(self):

        # global Parser
        # Parser = self
        self.InitData()
    #@+node:ekr.20060513122450.242: *5* Declare
    def Declare(self,text):
        if self.CURRENT_LOCATION == "body":
            self.CURRENT_BODY_LINE += 1		
        else:
            self.CURRENT_BODY_LINE = 0

        if self.DECLARE_IN_HEADER == False:
            self.CURRENT_SRC_LINE += 1								
        else:
            self.CURRENT_HDR_LINE += 1

        for d in self.DEC_PROC_LIST:
            d(text)
    #@+node:ekr.20060513122450.243: *5* Define
    def Define(self,text):
        if self.CURRENT_LOCATION == "body":
            self.CURRENT_BODY_LINE += 1		
        else:
            self.CURRENT_BODY_LINE = 0

        if self.DEFINE_IN_SOURCE == False:
            self.CURRENT_HDR_LINE += 1
        else:
            self.CURRENT_SRC_LINE += 1

        for d in self.DEF_PROC_LIST:
            d(text)
    #@+node:ekr.20060513122450.244: *5* Docum
    def Docum(self,text):
        if self.CURRENT_LOCATION == "body":
            self.CURRENT_BODY_LINE += 1		
        else:
            self.CURRENT_BODY_LINE = 0

        self.CURRENT_DOC_LINE += 1

        for d in self.DOC_PROC_LIST:
            d(text)
    #@+node:ekr.20060513122450.245: *5* PushBodyLine
    def PushBodyLine(self):
        self.BODY_LINE_STACK.insert(0,self.CURRENT_BODY_LINE)
    #@+node:ekr.20060513122450.246: *5* PopBodyLine
    def PopBodyLine(self):
        self.CURRENT_BODY_LINE = self.BODY_LINE_STACK.pop(0)


    #@+node:ekr.20060513122450.247: *5* SetRealBodyDestination
    def SetRealBodyDestination(self,func=None):

        Parser = self
        if func == None:
            self.CURRENT_BODY_DEST = "VOID"
            return self.CURRENT_BODY_DEST

        if func == Parser.Docum:
            self.CURRENT_BODY_DEST = "DOCUM"

        if self.Define == self.Declare:#only one probable file
            if EXT == "h":#this is a header so..
                self.CURRENT_BODY_DEST = "HEADER"
            else:#this is not a header so..
                self.CURRENT_BODY_DEST = "SOURCE"

        else:#two probable file, must use func pointer
            if func == self.Declare:
                self.CURRENT_BODY_DEST = "HEADER"
            if func == self.Define:
                self.CURRENT_BODY_DEST = "SOURCE"

        return self.CURRENT_BODY_DEST

    #@+node:ekr.20060513122450.248: *5* Tabing
    #@+node:ekr.20060513122450.249: *6* Tab
    def Tab(self):
        self.TAB_STRING += "\t"
    #@+node:ekr.20060513122450.250: *6* UnTab
    def UnTab(self):
        if len(self.TAB_STRING) > 0:
            self.TAB_STRING = self.TAB_STRING[:-1] 
    #@+node:ekr.20060513122450.251: *6* PushTab
    def PushTab(self):
        self.TAB_LIST.append(self.TAB_STRING)
        self.TAB_STRING = ""
    #@+node:ekr.20060513122450.252: *6* PopTab
    def PopTab(self):
        self.TAB_STRING = self.TAB_LIST.pop(-1)
    #@+node:ekr.20060513122450.253: *6* TabWrite
    def TabWrite(self,text,outfunc):
        lines = text.splitlines(True)
        for l in lines:
            outfunc(self.TAB_STRING+l)
    #@+node:ekr.20060513122450.254: *5* WriteOthers
    def WriteOthers(self,node,w):
        b = node.b
        o = b.find("@others")
        if o != -1:
            #--------------------
            lb = b[:o]
            pnl = lb.rfind("\n")
            if pnl > -1:
                lb = lb[:pnl]

            tb = b[o+7:]
            pnl = tb.find("\n")		
            if pnl > -1:
                tb = tb[pnl+1:]		

            self.CURRENT_LOCATION = "body"

            if lb != "":
                self.TabWrite(lb+"\n",w)
            self.PushBodyLine()
            if self.ParseNode(node) == False:
                return False
            self.PopBodyLine()
            self.CURRENT_LOCATION = "body"	
            self.TabWrite(b[o+7:]+"\n",w)
        else:
            self.CURRENT_LOCATION = "body"	
            self.TabWrite(b+"\n",w)	
            if self.ParseNode(node) == False:
                return False

        return True
    #@+node:ekr.20060513122450.255: *5* CppParse
    def CppParse(self,node,ext):

        cc = self.cc
        self.LoadCppRules()	

        #----------------------------------------------
        if ext in self.NO_HEADER_EXT:
            self.DECLARE_IN_HDR = False
        else:
            self.DECLARE_IN_HDR = True

        if ext in self.NO_SOURCE_EXT:
            self.DEFINE_IN_SRC = False
        else:
            self.DEFINE_IN_SRC = True

        #-----------------------------------------------------
        self.CURRENT_VNODE = node.v
        self.CURRENT_NODE = node	

        #-----------------------------------------------------
        if self.NOW_PARSING == True:
            Error("xcc: ","AutoParse was already parsing!")
            return False
        else:
            self.NOW_PARSING = True	

        #------------------------------------------------------
        if self.OnStart:
            if self.OnStart() == False:
                return False
        time.clock()
        start = time.clock()

        if self.DEFINE_IN_SRC == True and self.DECLARE_IN_HDR == True:
            if cc.OPTS.get("Auto include header") == "True":
                self.Define("#include \""+NAME+".h\"\n")

        #------------------------------------------------------		
        res = self.ParseNode(node,reset=True)	
        #------------------------------------------------------	
        self.PARSE_TIME = time.clock()-start
        self.OnEnd and self.OnEnd()	

        return res
    #@+node:ekr.20060513122450.256: *5* OnParseNode
    def OnParseNode(self,node,back=False):
        self.CURRENT_VNODE = node.v
        self.CURRENT_NODE = node.copy()	

        for opn in self.OPN_PROC_LIST:
            opn(node,back)
    #@+node:ekr.20060513122450.257: *5* ParseNode
    def ParseNode(self,node,reset=False):

        cc = self.cc

        if self.DO_PARSE == False:
            return False

        for cn in node.children():
            self.OnParseNode(cn)		
            ch = cn.h		

            self.CURRENT_RULE = None
            for r in self.RULES:
                result = r.Match(ch)
                if result != None:
                    self.CURRENT_MATCH_OBJECT = result
                    if r.OnMatch(result,cn) == False or self.DO_PARSE == False:
                        return False
                    break

        if node != cc.SELECTED_NODE:
            self.OnParseNode(node,True)

        return True
    #@+node:ekr.20060513122450.258: *5* InitData
    def InitData(self):
        self.DO_PARSE = True	
        self.NOW_PARSING = False

        self.RULES = []	
        self.OnStart = None
        self.OnEnd = None	


        self.DEC_PROC_LIST = []
        self.DEF_PROC_LIST = []
        self.DOC_PROC_LIST = []
        self.OPN_PROC_LIST = []

        self.BODY_LINE_STACK = []

        self.CURRENT_SRC_LINE = 0
        self.CURRENT_HDR_LINE = 0

        self.CURRENT_BODY_LINE = 0
        self.CURRENT_BODY_DEST = None
        self.CURRENT_VNODE = None
        self.CURRENT_NODE = None
        self.CURRENT_LOCATION = "head"

        self.CURRENT_RULE = ""
        self.CURRENT_MO = None

        self.DECLARE_IN_HEADER = True
        self.DEFINE_IN_SOURCE = True	

        self.CLASS_LIST = []
        self.CLASS_WRITER = None	


        self.NO_HEADER_EXT = ["cpp","c"]
        self.NO_SOURCE_EXT = ["h"]

        self.TAB_STRING = ""
        self.TAB_LIST = []

        self.PARSE_TIME = 0.0
    #@-others

#@+node:ekr.20060513122450.259: *4* class WriterClass (CppParserClass)
class WriterClass(CppParserClass):

    #@+others
    #@+node:ekr.20060513122450.260: *5* __init__
    def __init__(self,cc):

        self.cc = cc
        self.Result = False

        CppParserClass.__init__(self)
        self.OnStart = self.OnWriteStart
        self.OnEnd = self.OnWriteEnd

        self.Result = self.CppParse(cc.SELECTED_NODE,cc.EXT)
        g.trace('WriteClass.Result',self.Result)
    #@+node:ekr.20060513122450.261: *5* OnWriteStart
    def OnWriteStart(self):
        global SRC_EXT

        self.HDR_FILE = None
        self.SRC_FILE = None

        if REL_PATH != "":
            name = REL_PATH+"\\"+NAME
        else:
            name = NAME

        #create a header and verify syntaxe	
        if EXT == "h":
            sAddText("\" writing "+name+".h...\n")
            self.HDR_FILE = file(name+".h","w+")

        #create exe using .h and .cpp files
        if EXT == "exe":
            sAddText("\" writing "+name+".h and "+name+".cpp...\n")
            self.HDR_FILE = file(name+".h","w+")
            self.SRC_FILE = file(name+".cpp","w+")

        #create exe using .cpp or .c file
        if EXT == "cpp" or EXT == "c":
            sAddText("\" writing "+name+"."+EXT+"...\n")
            self.SRC_FILE = file(name+"."+EXT,"w+")

        #create a static .lib or dynamic .dll using .h and .cpp file	
        if EXT == "dll":
            sAddText("\" writing "+name+".h and "+name+".cpp...\n")
            self.HDR_FILE = file(name+".h","w+")
            self.SRC_FILE = file(name+".cpp","w+")

        if self.HDR_FILE == None and self.SRC_FILE == None:
            Error("xcc: ","Unable to open output file(s)!")
            return False	

        #------------------------------------------
        if self.DECLARE_IN_HDR == True:
            self.DEC_PROC_LIST.append(self.HDR_FILE.write)
        else:
            self.DEC_PROC_LIST.append(self.SRC_FILE.write)

        if self.DEFINE_IN_SRC == True:
            self.DEF_PROC_LIST.append(self.SRC_FILE.write)
        else:
            self.DEF_PROC_LIST.append(self.HDR_FILE.write)


        return True
    #@+node:ekr.20060513122450.262: *5* OnWriteEnd
    def OnWriteEnd(self):

        if self.HDR_FILE:
            self.HDR_FILE.write("\n")
            self.HDR_FILE.close()
            self.HDR_FILE = None

        if self.SRC_FILE:
            self.SRC_FILE.write("\n")
            self.SRC_FILE.close()
            self.SRC_FILE = None
    #@-others
#@+node:ekr.20060513122450.263: *4* class BreakFinderClass (CppParserClass)
class BreakFinderClass(CppParserClass):

    #@+others
    #@+node:ekr.20060513122450.264: *5* __init__
    def __init__(self,cc):

        self.cc = cc
        self.Result = False
        CppParserClass.__init__(self)
        self.OnStart = self.OnFindStart
        self.OnEnd = self.OnFindEnd
        self.Result = self.CppParse(controllerSELECTED_NODE,controllerEXT)
    #@+node:ekr.20060513122450.265: *5* OnFindStart
    def OnFindStart(self):
        # loading event funcs
        if self.DECLARE_IN_HDR == True:
            self.DEC_PROC_LIST.append(self.BreakDec)		
        else:
            self.DEC_PROC_LIST.append(self.BreakDef)

        if self.DEFINE_IN_SRC == True:
            self.DEF_PROC_LIST.append(self.BreakDef)
        else:
            self.DEF_PROC_LIST.append(self.BreakDec)		

        self.OPN_PROC_LIST.append(self.BreakOPN)

        sSet("Breakpoints",{})
        self.GLOBAL_BREAKS = sGet("Breakpoints")

        self.CURRENT_BREAKS = None

    #@+node:ekr.20060513122450.266: *5* OnFindEnd
    def OnFindEnd(self):
        sSet("Breakpoints",self.GLOBAL_BREAKS)

    #@+node:ekr.20060513122450.267: *5* BreakDec
    def BreakDec(self,text):

        cbl = self.CURRENT_BODY_LINE
        cb = self.CURRENT_BREAKS	

        #cGetDict(self.CURRENT_NODE)["BodyDestination"] = "HEADER"
        if cb and str(cbl) in cb:
            self.GLOBAL_BREAKS["h:"+str(self.CURRENT_HDR_LINE)] = cb[str(cbl)]
    #@+node:ekr.20060513122450.268: *5* BreakDef
    def BreakDef(self,text):

        cbl = self.CURRENT_BODY_LINE
        cb = self.CURRENT_BREAKS

        #cGetDict(self.CURRENT_NODE)["BodyDestination"] = "Source"
        if cb and str(cbl) in cb:
            self.GLOBAL_BREAKS[SRC_EXT+":"+str(self.CURRENT_SRC_LINE)] = cb[str(cbl)]
    #@+node:ekr.20060513122450.269: *5* BreakOPN
    def BreakOPN(self,node,back=False):

        cc = self.cc

        txcd = cc.cGetDict(node)

        self.CURRENT_BREAKS = txcd and txcd.get("BreakPoints")
    #@-others
#@+node:ekr.20060513122450.270: *4* class SeekErrorClass (CppParserClass)
class SeekErrorClass(CppParserClass):
    #@+others
    #@+node:ekr.20060513122450.271: *5* __init__
    def __init__(self,cc,line,ext,col="0",color="red"):

        self.cc = cc
        CppParserClass.__init__(self)		
        self.SEEK_LINE = line
        self.SEEK_COL = col
        self.SEEK_EXT = ext
        self.FOUND_NODE = None
        self.FOUND_INDEX = "1."+col
        self.OnStart = self.OnStartSeek

        if self.CppParse(cc.SELECTED_NODE,cc.EXT) == False and self.FOUND_NODE:
            cc.GoToNode(self.FOUND_NODE,self.FOUND_INDEX,tagcolor=color)
        else:
            Error("xcc: ","Unable to find line: "+str(line))
    #@+node:ekr.20060513122450.272: *5* OnStartSeek
    def OnStartSeek(self):
        if self.DECLARE_IN_HEADER == True:
            self.DEC_PROC_LIST.append(self.SeekDec)
        else:
            self.DEC_PROC_LIST.append(self.SeekDef)


        if self.DEFINE_IN_SOURCE == True:
            self.DEF_PROC_LIST.append(self.SeekDef)
        else:
            self.DEF_PROC_LIST.append(self.SeekDec)
    #@+node:ekr.20060513122450.273: *5* SeekDec
    def SeekDec(self,text):
        if self.DO_PARSE == True:
            index = None
            cbl = self.CURRENT_BODY_LINE

            if self.CURRENT_HDR_LINE == self.SEEK_LINE and self.SEEK_EXT == "h":			

                if self.CURRENT_LOCATION == "head":
                    index = "1.0"
                if self.CURRENT_LOCATION == "body":
                    index = str(cbl)+"."+self.SEEK_COL
                if self.CURRENT_LOCATION == "tail":
                    index = "1000.0"


                self.DO_PARSE = False
                self.FOUND_NODE = self.CURRENT_NODE.copy()
                self.FOUND_INDEX = index
    #@+node:ekr.20060513122450.274: *5* SeekDef
    def SeekDef(self,text):
        if self.DO_PARSE == True:
            index = None
            cbl = self.CURRENT_BODY_LINE

            if self.CURRENT_SRC_LINE == self.SEEK_LINE and self.SEEK_EXT == "cpp":

                if self.CURRENT_LOCATION == "head":
                    index = "1."+self.SEEK_COL
                if self.CURRENT_LOCATION == "body":
                    index = str(cbl)+"."+self.SEEK_COL
                if self.CURRENT_LOCATION == "tail":
                    index = "1000."+self.SEEK_COL

                self.DO_PARSE = False
                self.FOUND_NODE = self.CURRENT_NODE.copy()
                self.FOUND_INDEX = index
    #@-others
#@+node:ekr.20060513122450.275: *4* class LocatorClass (CppParserClass)
class LocatorClass(CppParserClass):
    #@+others
    #@+node:ekr.20060513122450.276: *5* __init__
    def __init__(self,cc,node,line):

        self.cc = cc

        CppParserClass.__init__(self)		

        self.LOCATE_NODE = node
        self.LOCATE_BODY_LINE = int(line)
        self.FOUND_FILE_LINE = None
        self.FOUND_FILE_EXT = None

        self.OnStart = self.OnStartLocate

        if not self.CppParse(cc.SELECTED_NODE,cc.EXT) and self.FOUND_FILE_LINE != None:
            pass
        else:
            #Error("xcc: ","Unable to locate line "+str(line)+" in "+str(node))
            pass
    #@+node:ekr.20060513122450.277: *5* OnStartLocate
    def OnStartLocate(self):
        if self.DECLARE_IN_HEADER == True:
            self.DEC_PROC_LIST.append(self.LocateDec)
        else:
            self.DEC_PROC_LIST.append(self.LocateDef)


        if self.DEFINE_IN_SOURCE == True:
            self.DEF_PROC_LIST.append(self.LocateDef)
        else:
            self.DEF_PROC_LIST.append(self.LocateDec)

        self.NODE_REACHED = False
    #@+node:ekr.20060513122450.278: *5* LocateDec
    def LocateDec(self,text):
        if self.DO_PARSE == True:
            if self.CURRENT_NODE == self.LOCATE_NODE:
                if self.CURRENT_RULE == "func" and self.CURRENT_MATCH_OBJECT[4][0]!= "":
                    self.FOUND_FILE_LINE = -1
                    self.FOUND_FILE_EXT = "h"
                    self.DO_PARSE = False
                    return
                if self.CURRENT_BODY_LINE == self.LOCATE_BODY_LINE:
                    self.FOUND_FILE_LINE = self.CURRENT_HDR_LINE
                    self.FOUND_FILE_EXT = "h"
                    self.DO_PARSE = False
    #@+node:ekr.20060513122450.279: *5* LocateDef
    def LocateDef(self,text):

        cc = self.cc

        if self.DO_PARSE == True:
            if self.CURRENT_NODE == self.LOCATE_NODE:
                if self.CURRENT_BODY_LINE == self.LOCATE_BODY_LINE:
                    self.FOUND_FILE_LINE = self.CURRENT_SRC_LINE
                    self.FOUND_FILE_EXT = cc.SRC_EXT
                    self.DO_PARSE = False
    #@-others
#@-others

#@-leo
