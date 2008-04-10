#@+leo-ver=4-thin
#@+node:TL.20080221123824.2:@thin mod_tempfname.py
"""Replace Commands.openWithTempFilePath so Leo opens temporary
files with a filename that begins with the headline text, and
located in a "username_Leo" subdirectory of the temporary
directory. The "LeoTemp" prefix is omitted.  This makes it easier to
see which temporary file is related to which outline node."""

#@@language python
#@@tabwidth -4

import leoGlobals as g
import leoPlugins

import leoCommands
import getpass
import os
import tempfile

#@+others
#@+node:EKR.20040517075715.2:onStart
def onStart (tag,keywords):

    # g.trace("replacing openWithTempFilePath")

    g.funcToMethod(openWithTempFilePath,leoCommands.Commands,"openWithTempFilePath")
#@-node:EKR.20040517075715.2:onStart
#@+node:EKR.20040517075715.3:openWithTempFilePath
def openWithTempFilePath (self,v,ext):

    """Return the path to the temp file corresponding to v and ext.
       Replaces the Commands method."""    

    #TL: Replace use of unique id in filename to insure unique temporary file
    #    with creation of temporary directory structure based on node's
    #    hierarchy in Leo's outline.
    #    Note: Sibling nodes with same headline should not open at same time.
    #          Same temporary file will be used for both. (needs to be handled)
    #    Note: Only windows users supported, Others should be added

    #g.es("os = " + os.name)
    if(os.name == "dos" or os.name == "nt"):
       c = self
       atFileFoundAlready = False   #Track when at closest @file ancestor
       #Build list of all of node's parents
       ancestor = []
       p = c.currentPosition()
       while p:
           hs = p.isAnyAtFileNode() #Get file name if we're at a @file node
           if hs:
               #Get file extension from first found @file type node
               if atFileFoundAlready == False:
                   nameNotUsed,extension = g.os_path_splitext(hs)
                   if extension: #Found, use it instead of @language or default
                       ext = extension
                   atFileFoundAlready = True
           else:
               hs = p.headString()  #Otherwise, use the entire header

           #Remove unsupported dir & file name characters from node's text.
           #Note: Replacing characters increases chance of temp files matching.
           if(os.name == "dos" or os.name == "nt"):
              result = ""
              for ch in hs.strip():
                  if ch in g.string.whitespace: #Convert tabs to spaces
                      result += ' '
                  elif ch in ('\\','/',':','|','<','>'): #Not allowed in Windows
                      result += '_'
                  elif ch in ('"'): #Leo code can't handle the "
                      result += '\''   #replace with '
                  else:
                      result += ch
           #Add node's headstring (filtered) to the list of ancestors
           ancestor.append(result.strip())
           p = p.parent()

       #Put temporary directory structure under <tempdir>\Leo directory
       ancestor.append( "Leo" )
       td = os.path.abspath(tempfile.gettempdir())
       #Loop through all ancestor's of node
       while len(ancestor) > 1:
           #Build temporary directory structure
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
       name = g.sanitize_filename(v.headString()) + '_' + str(id(v.t))  + ext

    path = os.path.join(td,name)
    return path

#@-node:EKR.20040517075715.3:openWithTempFilePath
#@-others

if not g.app.unitTesting: # Not Ok for unit testing: it changes Leo's core.

    # Register the handlers...
    leoPlugins.registerHandler("start2", onStart)

    __version__ = "1.3"
    g.plugin_signon(__name__)
#@nonl
#@-node:TL.20080221123824.2:@thin mod_tempfname.py
#@-leo
