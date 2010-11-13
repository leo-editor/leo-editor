#@+leo-ver=5-thin
#@+node:EKR.20040517075715.1: * @file mod_tempfname.py
#@+<< docstring >>
#@+node:ekr.20101112195628.5433: ** << docstring >>
""" Replaces c.openWithTempFilePath to create alternate temporary
directory paths.

Two alternates are supported. The default method creates temporary files with a
filename that begins with the headline text, and located in a "username_Leo"
subdirectory of the temporary directory. The "LeoTemp" prefix is omitted. If
'open_with_clean_filenames' is set to true then subdirectories mirror the node's
hierarchy in Leo. Either method makes it easier to see which temporary file is
related to which outline node.

"""
#@-<< docstring >>

#@@language python
#@@tabwidth -4

import leo.core.leoGlobals as g

import leo.core.leoCommands as leoCommands
import getpass
import os
import tempfile

__version__ = "1.3"

#@+others
#@+node:ekr.20100128091412.5382: ** init
def init():

    ok = not g.app.unitTesting
        # Not Ok for unit testing: it changes Leo's core.

    if ok:
        # Register the handlers...
        g.registerHandler("start2", onStart)
        g.plugin_signon(__name__)

    return ok
#@+node:EKR.20040517075715.2: ** onStart
def onStart (tag,keywords):

    # g.trace("replacing openWithTempFilePath")

    g.funcToMethod(openWithTempFilePath,leoCommands.Commands,"openWithTempFilePath")
#@+node:EKR.20040517075715.3: ** openWithTempFilePath
def openWithTempFilePath (self,v,ext):

    """Return the path to the temp file corresponding to v and ext.
       Replaces the Commands method."""

    #TL: Added support creating temporary directory structure based on node's
    #    hierarchy in Leo's outline.
    c = self
    if c.config.getBool('open_with_clean_filenames'):
        atFileFound = False   #Track when first ancestor @file found
        #Build list of all of node's parents
        ancestor = []
        p = c.p
        while p:
            hs = p.isAnyAtFileNode() #Get file name if we're at a @file node
            if not hs:
                hs = p.h  #Otherwise, use the entire header
            else:
#@verbatim
                #@file type node
                if c.config.getBool('open_with_uses_derived_file_extensions'):
                    #Leo configured to use node's derived file's extension
                    if(atFileFound == False):
                        atFileFound = True #no need to look any more.
                        #Found first ancestor @file node in outline
                        atFileBase,atFileExt = g.os_path_splitext(hs)
                        if(p == c.p):
                            #node to edit is an @file, Move ext from hs to ext
                            hs = atFileBase
                        if atFileExt: #It has an extension
                            ext = atFileExt #use it

            #Remove unsupported directory & file name characters
            #if(os.name == "dos" or os.name == "nt"):
            if 1:
                hsClean = ""
                for ch in hs:
                    if ch in g.string.whitespace: #Convert tabs to spaces
                        hsClean += ' '
                    elif ch in ('\\','/',':','|','<','>','*', '"'): #Not allowed in Dos/Windows
                        hsClean += '_'
                    elif ch in ('"'): #Leo code can't handle the "
                        hsClean += '\''   #replace with '
                    else:
                        hsClean += ch
                #Windows directory and file names can't end with a period
                if hsClean.endswith( '.' ):
                    hsClean += '_'
            else:
                hsClean = g.sanitize_filename(hs)
            #Add node's headstring (filtered) to the list of ancestors
            ancestor.append(hsClean)
            p = p.parent()

        #Put temporary directory structure under <tempdir>\Leo<uniqueId> directory
        ancestor.append( "Leo" + str(id(v)))

        #Build temporary directory
        td = os.path.abspath(tempfile.gettempdir())
        #Loop through all of node's ancestors
        while len(ancestor) > 1:
            #Add each ancestor of node from nearest to farthest
            td = os.path.join(td, ancestor.pop()) #Add next subdirectory
            if not os.path.exists(td):
                os.mkdir(td)
        #Add filename with extension to the path (last entry in ancestor list)
        name = ancestor.pop() + ext
    else:
        #Use old method for unsupported operating systems
        try:
            leoTempDir = getpass.getuser() + "_" + "Leo"
        except:
            leoTempDir = "LeoTemp"
            g.es("Could not retrieve your user name.")
            g.es("Temporary files will be stored in: %s" % leoTempDir)
        td = os.path.join(os.path.abspath(tempfile.gettempdir()), leoTempDir)
        if not os.path.exists(td):
            os.mkdir(td)
        name = g.sanitize_filename(v.h) + '_' + str(id(v)) + ext

    path = os.path.join(td,name)

    return path

#@-others
#@-leo
