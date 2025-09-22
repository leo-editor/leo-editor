#@+leo-ver=5-thin
#@+node:felix.20250921202124.1: * @file ../plugins/leo_to_html_outline_viewer.py
#@+<< docstring >>
#@+node:felix.20250921202236.1: ** << docstring >>
r""" 
Outputs a Leo outline as a self-contained HTML interactive outline viewer:
The file is saved in the user's home/.leo folder and also opened with your default viewer.

Made by Félix Malboeuf (https://github.com/boltex)
"""
#@-<< docstring >>

# HTML Outline Viewer

#@+<< imports >>
#@+node:felix.20250921202247.1: ** << imports >>
import os
import json
from tempfile import NamedTemporaryFile
import time
import webbrowser
from leo.core import leoGlobals as g
#@-<< imports >>

#@+others
#@+node:felix.20250921211044.1: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    # Ok for unit testing: creates menu.
    g.registerHandler("create-optional-menus", createExportMenu)
    g.registerHandler('after-create-leo-frame', onCreate)
    g.plugin_signon(__name__)
    return True
#@+node:felix.20250921211058.1: ** onCreate
def onCreate(tag, keys):

    """
    Handle 'after-create-leo-frame' hooks by creating a plugin
    controller for the commander issuing the hook.
    """
    c = keys.get('c')
    if c:
        # Warning: hook handlers must use keywords.get('c'), NOT self.c.
        c.k.registerCommand('export-html-outline-viewer', export_html_outline_viewer)

#@+node:felix.20250921215659.1: ** createExportMenu (leo_to_html_outline_viewer)
def createExportMenu(tag, keywords):

    c = keywords.get("c")
    if not c:
        return

    c.frame.menu.insert('Export Files', 2,
        label='Export HTML Outline Viewer',
        command=lambda c=c, cmd='export-html-outline-viewer': c.doCommandByName('export-html-outline-viewer')
    )
#@+node:felix.20250921215929.1: ** export_html_outline_viewer
def export_html_outline_viewer(event=None):
    """
    Outputs the Leo outline as a self-contained HTML interactive outline viewer in
    the user's home/.leo folder, and open it with the default viewer.
    """
    if not event:
        return
    c = event.get("c")
    if not c:
        return

    g.es('Exporting HTML Outline Viewer...')
    fileName = g.os_path_join(g.app.loadDir, "..", "plugins", "html_outline_viewer.html")

    template_content, encoding = g.readFileIntoString(fileName)
    htmlPrefix = template_content.split("        /* Start of data */")[0]
    htmlSuffix = template_content.split("        /* End of data */")[1]
    g.es('Loaded HTML template.')
    g.es('encoding: %s' % (encoding))
    g.es('template_start length: %s' % (len(htmlPrefix)))
    g.es('template_end length: %s' % (len(htmlSuffix)))
    # Create the data to be embedded in the HTML file

    TEMPDIR = os.path.expanduser(r'~/.leo')

    unix_timestamp_string = str(int(time.time()))
    myFilePath = c.fileName()
    filename = os.path.splitext(os.path.basename(myFilePath))[0]

    vnode_dict = {}  # This is 'data'
    gnx_map = {}  # gnx -> compact id
    gnx_counter = 0  # counter for compact ids

    def map_gnx(gnx):
        """Return the compact integer id for a gnx, creating it if missing."""
        nonlocal gnx_counter
        if gnx not in gnx_map:
            gnx_map[gnx] = gnx_counter
            gnx_counter += 1
        return gnx_map[gnx]

    def buildTree(children):
        """Builds the outline structure recursively"""
        result = []
        for child in children:
            is_clone = child.gnx in gnx_map
            gnx_id = map_gnx(child.gnx)
            node = {
                "gnx": gnx_id,
            }
            if gnx_id not in vnode_dict:
                vnode_dict[gnx_id] = {
                    "headString": child.headString(),
                    "bodyString": child.bodyString(),
                }
            # recurse children only if gnx not already seen (dont re-write clones)
            # IMPORTANT: the script using this output will have to handle that!
            if child.children and not is_clone:
                node["children"] = buildTree(child.children)
            result.append(node)
        return result

    # Start from Leo's hidden root
    tree = {
        "gnx": map_gnx(c.hiddenRootNode.gnx),
        "children": buildTree(c.hiddenRootNode.children)
    }

    prefixTitle = f'\n        const title = "{filename}";'
    prefixgenTimestamp = f'\n        const genTimestamp = "{unix_timestamp_string}";'
    prefixTree = '\n        const tree = '
    prefixData = ';\n        const data = '  # includes ';' for ending tree.
    suffixData = ';'

    # Define a simple wrapper that replaces </script> on-the-fly
    class SafeWriter:
        def __init__(self, f):
            self.f = f
        def write(self, s):
            # Replace the dangerous substring
            s = s.replace("</script>", "<\\/script>")
            self.f.write(s)

    with NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.html',
                            prefix=filename, dir=TEMPDIR, delete=False) as out:

        writer = SafeWriter(out)

        writer.write(htmlPrefix)

        writer.write(prefixTitle)
        writer.write(prefixgenTimestamp)
        writer.write(prefixTree)

        json.dump(tree, writer, ensure_ascii=False, separators=(",", ":"))  # to 'writer'
        writer.write(prefixData)
        json.dump(vnode_dict, writer, ensure_ascii=False, separators=(",", ":"))  # to 'writer'
        writer.write(suffixData)

        out.write(htmlSuffix)

    webbrowser.open(out.name)
    g.es('HTML document generated at ' + out.name)

#@-others
#@@language python
#@@tabwidth -4
#@-leo
