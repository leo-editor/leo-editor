#@+leo-ver=4-thin
#@+node:EKR.20040517080049.1:@thin empty_leo_file.py
"""Open any empty file as a minimal .leo file"""

#@@language python
#@@tabwidth -4

import leoGlobals as g
import leoPlugins
import os

#@<< define minimal .leo file >>
#@+node:EKR.20040517080049.2:<< define minimal .leo file >>
empty_leo_file = """<?xml version="1.0" encoding="UTF-8"?>
<leo_file>
<leo_header/>
<globals/>
<preferences/>
<find_panel_settings/>
<vnodes/>
<tnodes/>
</leo_file>
"""
#@nonl
#@-node:EKR.20040517080049.2:<< define minimal .leo file >>
#@nl

#@+others
#@+node:EKR.20040517080049.3:onOpen
def onOpen (tag,keywords):

    file_name = keywords.get('fileName')

    if file_name and os.path.getsize(file_name)==0:
        # Rewrite the file before really opening it.
        g.es("rewriting empty .leo file: %s" % (file_name))
        file = open(file_name,'w')
        file.write(empty_leo_file)
        file.flush()
        file.close()

#@-node:EKR.20040517080049.3:onOpen
#@-others

if 1:  # Ok for unit testing.  Only rewrites empty files.

    # Register the handlers...
    leoPlugins.registerHandler("open1", onOpen)

    __version__ = "1.2"
    g.plugin_signon(__name__)
#@nonl
#@-node:EKR.20040517080049.1:@thin empty_leo_file.py
#@-leo
