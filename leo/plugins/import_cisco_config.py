#@+leo-ver=5-thin
#@+node:edream.110203113231.669: * @file ../plugins/import_cisco_config.py
#@+<< docstring >>
#@+node:ekr.20050912180321: ** << docstring >>
""" Allows the user to import Cisco configuration files.

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

"""
#@-<< docstring >>
from leo.core import leoGlobals as g

#@+others
#@+node:ekr.20050311102853.1: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    # This plugin is gui-independent.
    g.registerHandler(('new', 'menu2'), create_import_cisco_menu)
    g.plugin_signon(__name__)
    return True
#@+node:edream.110203113231.671: ** create_import_cisco_menu
def create_import_cisco_menu(tag, keywords):

    c = keywords.get('c')
    if not c or not c.exists:
        return

    importMenu = c.frame.menu.getMenu('import')

    def importCiscoConfigCallback(event=None, c=c):
        importCiscoConfig(c)

    table = (
        ("-", None, None),
        ("Import C&isco Configuration", "Shift+Ctrl+I", importCiscoConfigCallback))
    c.frame.menu.createMenuEntries(importMenu, table)
#@+node:edream.110203113231.672: ** importCiscoConfig
def importCiscoConfig(c):

    if not c or not c.exists:
        return
    current = c.p
    #@+<< open file >>
    #@+node:edream.110203113231.673: *3* << open file >>
    # name = tkFileDialog.askopenfilename(
        # title="Import Cisco Configuration File",
        # filetypes=[("All files", "*")]
        # )

    name = g.app.gui.runOpenFileDialog(c,
        title="Import Cisco Configuration File",
        filetypes=[("All files", "*"),],
        defaultextension='ini',
    )

    if not name:
        return

    p = current.insertAsNthChild(0)
    p.h = "cisco config: %s" % name
    c.redraw()

    try:
        fh = open(name)  # type:ignore
        g.es("importing: %s" % name)
        linelist = fh.read().splitlines()
        fh.close()
    except IOError as msg:
        g.es("error reading %s: %s" % (name, msg))
        return
    #@-<< open file >>

    # define which additional child nodes will be created
    # these keywords must NOT be followed by indented blocks
    customBlocks = ['aaa', 'ip as-path', 'ip prefix-list', 'ip route',
                    'ip community-list', 'access-list', 'snmp-server', 'ntp',
                    'boot', 'service', 'logging']
    out = []
    blocks: dict = {}
    children = []
    lines = len(linelist)
    i = 0
    skipToNextLine = 0
    # create level-0 and level-1 children
    while i < (lines - 1):
        for customLine in customBlocks:
            if (linelist[i].startswith(customLine) or
                linelist[i].startswith('no %s' % customLine)
            ):
                #@+<< process custom line >>
                #@+node:edream.110203113231.674: *3* << process custom line >> (import_cisco_config.py)
                if customLine not in blocks:
                    blocks[customLine] = []
                    out.append(g.angleBrackets(customLine))
                    # create first-level child
                    child = p.insertAsNthChild(0)
                    child.h = g.angleBrackets(customLine)
                    children.append(child)

                blocks[customLine].append(linelist[i])
                #@-<< process custom line >>
                skipToNextLine = 1
                break
        if skipToNextLine:
            skipToNextLine = 0
        else:
            if linelist[i + 1].startswith(' '):
                #@+<< process indented block >>
                #@+node:edream.110203113231.675: *3* << process indented block >> (import_cisco_config.py)
                space = linelist[i].find(' ')
                if space == -1:
                    space = len(linelist[i])
                key = linelist[i][:space]
                if key in blocks:
                    blocks[key] = []
                    out.append(g.angleBrackets(key))
                    # create first-level child
                    child = p.insertAsNthChild(0)
                    child.h = g.angleBrackets(key)
                    children.append(child)

                value = [linelist[i]]
                # loop through the indented lines
                i = i + 1
                try:
                    while linelist[i].startswith(' '):
                        value.append(linelist[i])
                        i = i + 1
                except Exception:
                    # EOF
                    pass
                i = i - 1  # restore index
                # now add the value to the dictionary
                blocks[key].append(value)
                #@-<< process indented block >>
            else:
                out.append(linelist[i])
        i = i + 1
    # process last line
    out.append(linelist[i])

    #@+<< complete outline >>
    #@+node:edream.110203113231.676: *3* << complete outline >>
    # first print the level-0 text
    outClean = []
    prev = ''
    for line in out:
        if line == '!' and prev == '!':
            pass  # skip repeated comment lines
        else:
            outClean.append(line)
        prev = line
    p.b = '\n'.join(outClean)

    # scan through the created outline and add children
    for child in children:
        # extract the key from the headline. Uhm... :)
        key = child.h.split('<<'
            )[1].split('>>')[0].strip()
        if key in blocks:
            if isinstance(blocks[key][0], str):
                # it's a string, no sub-children, so just print the text
                child.b = '\n'.join(blocks[key])
            else:
                # it's a multi-level node
                for value in blocks[key]:
                    # each value is a list containing the headline and then the text
                    subchild = child.insertAsNthChild(0)
                    subchild.h = value[0]
                    subchild.b = '\n'.join(value)
        else:
            # this should never happen
            g.es("Unknown key: %s" % key)
    current.expand()
    c.redraw()
    #@-<< complete outline >>
#@-others
#@@language python
#@@tabwidth -4
#@-leo
