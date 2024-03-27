#@+leo-ver=5-thin
#@+node:ekr.20170619151859.2: * @file ../plugins/auto_colorize2_0.py
""" Manipulates appearance of individual tree widget items based on Yaml file.

Settings are defined in a node labeled "Headline Formats".

By Adrian Calvin.
"""
#@+<< imports auto_colorize2_0.py >>
#@+node:ekr.20170619151859.3: ** << imports auto_colorize2_0.py >>
import yaml
from leo.core import leoGlobals as g
try:
    from leo.core.leoQt import QtGui
    QBrush = QtGui.QBrush
    QColor = QtGui.QColor
except Exception:
    QBrush = QColor = None
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@-<< imports auto_colorize2_0.py >>
#@+others
#@+node:ekr.20170619151859.4: ** onCreate
def onCreate(tag, keys):
    """auto_colorize onCreate handler."""
    try:
        c = keys.get('c')
        init_dict(c)
        g.visit_tree_item.add(colorize)
    except Exception as e:
        g.es_trace("Could not load commander." + str(e))
#@+node:ekr.20170619151859.5: ** init
def init():
    def on_save(tag, key):
        c = key['c']
        init_dict(c)
        c.redraw()
    g.registerHandler("save2", on_save)
    g.registerHandler('after-create-leo-frame', onCreate)
    return True
#@+node:ekr.20170619151859.6: ** init_dict
def init_dict(c):
    """ (Re)Initialize the formats dictionary """
    cs = str(c)
    try:
        fbody = g.findNodeAnywhere(c, "Headline Formats").b
    except Exception as e:
        g.es_trace("This outline has no Headline Formats node\n" + str(e))
        return
    try:
        # There is something wrong. Both pylint and mypy complain.
        # pylint: disable=no-value-for-parameter
        formats = yaml.load(fbody)  # type:ignore
    except Exception as e:
        g.es_trace("Could not parse Headline Format yaml file\n" + str(e))
        return
    try:
        formats = formats["Headline Formats"]
    except Exception as e:
        g.es_trace("Yaml file does not have proper heading.\n" + str(e))
        return
    # preprocess multi headline styles
    g.app.permanentScriptDict[cs + 'formats'] = {}
    try:
        for k, f in formats.items():
            if "`" in k:
                _ = k.split("`")
                for _1 in _:
                    g.app.permanentScriptDict[cs + 'formats'][_1.strip()] = f
            else:
                g.app.permanentScriptDict[cs + 'formats'][k] = f
    except Exception as e:
        g.es_error(e)
#@+node:ekr.20170619151859.7: ** colorize
def colorize(c, p, item):
    """Colorize by reading "Headline Formats" node, or symbol in headline"""
    cs = str(c)
    font = item.font(0)
    try:
        g.app.permanentScriptDict[cs + 'formats']
    except Exception:
        g.app.permanentScriptDict[cs + 'formats'] = {}
    for k, f in g.app.permanentScriptDict[cs + 'formats'].items():
        def format_one(f):
            # color
            try:
                if f['color']:
                    item.setForeground(0, QBrush(QColor("#" + str(f['color']))))
            except Exception:
                print(item)
            # weight
            try:
                if f['font-weight']:
                    font.setBold(True)
            except Exception:
                pass
        if k == p.h:
            format_one(f)
    item.setFont(0, font)



#@-others
#@@language python
#@@tabwidth -4
#@-leo
