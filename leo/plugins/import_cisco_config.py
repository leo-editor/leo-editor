#@+leo-ver=5-thin
#@+node:edream.110203113231.669: * @file import_cisco_config.py
#@+<< docstring >>
#@+node:ekr.20050912180321: ** << docstring >>
''' Allows the user to import Cisco configuration files.

Adds the "File:Import:Import Cisco Configuration" menu item. The plugin will:

1)  Create a new node, under the current node, where the configuration will be
    written. This node will typically have references to several sections (see below).

2)  Create sections (child nodes) for the indented blocks present in the original
    config file. These child nodes will have sub-nodes grouping similar blocks (e.g.
    there will be an 'interface' child node, with as many sub-nodes as there are real
    interfaces in the configuration file).

3)  Create sections for the custom keywords specified in the customBlocks[] list in
    importCiscoConfig(). You can modify this list to specify different keywords. DO
    NOT put keywords that are followed by indented blocks (these are taken care of by
    point 2 above). The negated form of the keywords (for example, if the keyword is
    'service', the negated form is 'no service') is also included in the sections.


4)  Not display consecutive empty comment lines (lines with only a '!').

All created sections are alphabetically ordered.

'''
#@-<< docstring >>

import leo.core.leoGlobals as g

#@+others
#@+node:ekr.20050311102853.1: ** init
def init ():
    '''Return True if the plugin has loaded successfully.'''
    # This plugin is gui-independent.
    g.registerHandler(('new','menu2'),create_import_cisco_menu)
    g.plugin_signon(__name__)
    return True
#@+node:edream.110203113231.671: ** create_import_cisco_menu
def create_import_cisco_menu (tag,keywords):

    c = keywords.get('c')
    if not c or not c.exists: return

    importMenu = c.frame.menu.getMenu('import')

    def importCiscoConfigCallback(event=None,c=c):
        importCiscoConfig(c)

    newEntries = (
        ("-",None,None),
        ("Import C&isco Configuration","Shift+Ctrl+I",importCiscoConfigCallback))

    c.frame.menu.createMenuEntries(importMenu,newEntries,dynamicMenu=True)
#@+node:edream.110203113231.672: ** importCiscoConfig
def importCiscoConfig(c):

    if not c or not c.exists: return
    current = c.p
    #@+<< open file >>
    #@+node:edream.110203113231.673: *3* << open file >>
    # name = tkFileDialog.askopenfilename(
        # title="Import Cisco Configuration File",
        # filetypes=[("All files", "*")]
        # )

    name = g.app.gui.runOpenFileDialog (
        title="Import Cisco Configuration File",
        filetypes=[("All files", "*")],
        defaultextension='ini',
    )

    if not name:	return

    p = current.insertAsNthChild(0)
    c.setHeadString(p,"cisco config: %s" % name)
    c.redraw()

    try:
        fh = open(name)
        g.es("importing: %s" % name)
        linelist = fh.read().splitlines()
        fh.close()
    except IOError as msg:
        g.es("error reading %s: %s" % (name, msg))
        return
    #@-<< open file >>

    # define which additional child nodes will be created
    # these keywords must NOT be followed by indented blocks
    customBlocks = ['aaa','ip as-path','ip prefix-list','ip route',
                    'ip community-list','access-list','snmp-server','ntp',
                    'boot','service','logging']
    out = []
    blocks = {}
    children = []
    lines = len(linelist)
    i = 0
    skipToNextLine = 0
    # create level-0 and level-1 children
    while i<(lines-1):
        for customLine in customBlocks:
            if (linelist[i].startswith(customLine) or
                linelist[i].startswith('no %s' % customLine)):
                #@+<< process custom line >>
                #@+node:edream.110203113231.674: *3* << process custom line >>
                if not blocks.has_key(customLine):
                    blocks[customLine] = []
                    out.append(g.angleBrackets(customLine))
                    # create first-level child
                    child = p.insertAsNthChild(0)
                    c.setHeadString(child,g.angleBrackets(customLine))
                    children.append(child)

                blocks[customLine].append(linelist[i])
                #@-<< process custom line >>
                skipToNextLine = 1
                break
        if skipToNextLine:
            skipToNextLine = 0
        else:
            if linelist[i+1].startswith(' '):
                #@+<< process indented block >>
                #@+node:edream.110203113231.675: *3* << process indented block >>
                space = linelist[i].find(' ')
                if space == -1:
                    space = len(linelist[i])
                key = linelist[i][:space]
                if not blocks.has_key(key):
                    blocks[key] = []
                    out.append(g.angleBrackets(key))
                    # create first-level child
                    child = p.insertAsNthChild(0)
                    c.setHeadString(child,g.angleBrackets(key))
                    children.append(child)

                value = [linelist[i]]
                # loop through the indented lines
                i = i+1
                try:
                    while linelist[i].startswith(' '):
                        value.append(linelist[i])
                        i = i+1
                except:
                    # EOF
                    pass
                i = i-1 # restore index
                # now add the value to the dictionary
                blocks[key].append(value)
                #@-<< process indented block >>
            else:
                out.append(linelist[i])
        i=i+1
    # process last line
    out.append(linelist[i])

    #@+<< complete outline >>
    #@+node:edream.110203113231.676: *3* << complete outline >>
    # first print the level-0 text
    outClean = []
    prev = ''
    for line in out:
        if line=='!' and prev=='!':
            pass # skip repeated comment lines
        else:
            outClean.append(line)
        prev = line
    c.setBodyString(p,'\n'.join(outClean))

    # scan through the created outline and add children
    for child in children:
        # extract the key from the headline. Uhm... :)
        key = child.h.split('<<'
            )[1].split('>>')[0].strip()
        if blocks.has_key(key):
            if type(blocks[key][0]) == type(''):
                # it's a string, no sub-children, so just print the text
                c.setBodyString(child,'\n'.join(blocks[key]))
            else:
                # it's a multi-level node
                for value in blocks[key]:
                    # each value is a list containing the headline and then the text
                    subchild = child.insertAsNthChild(0)
                    c.setHeadString(subchild,value[0])
                    c.setBodyString(subchild,'\n'.join(value))
            # child.sortChildren()
        else:
            # this should never happen
            g.es("Unknown key: %s" % key)
    # p.sortChildren()
    current.expand()
    c.redraw_now()
    #@-<< complete outline >>
#@-others
#@@language python
#@@tabwidth -4
#@-leo
