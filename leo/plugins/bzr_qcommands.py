#@+leo-ver=5-thin
#@+node:ekr.20101110084839.5682: * @file ../plugins/bzr_qcommands.py
""" Adds a context menu to each node containing all the commands in the bzr Qt
interface. Bzr is invoked based on the path of the current node.

*Requires contextmenu.py.*

"""
# by TNB
import subprocess
from leo.core import leoGlobals as g
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#@+others
#@+node:tbrown.20101101135104.15789: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    g.tree_popup_handlers.append(bzr_qcommands)
    return True
#@+node:ekr.20140918072425.17927: ** bzr_qcommands
def bzr_qcommands(c, p, menu):
    """see module docs."""

    menu = menu.addMenu("bzr")

    # special case, no q* command for stat
    def bzr_stat(c=c, p=p):
        path = g.scanAllAtPathDirectives(c, p) or c.getNodePath(p)
        cmd = subprocess.Popen(['bzr', 'stat', path], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_bytes, stderr_bytes = cmd.communicate()
        stdout = g.toUnicode(stdout_bytes)
        stderr = g.toUnicode(stderr_bytes)
        g.es("\n\n".join([stdout, stderr]))
    action = menu.addAction('stat')
    # action.connect(action, QtCore.SIGNAL("triggered()"), bzr_stat)
    action.triggered.connect(bzr_stat)
    qcoms = (
        "qadd qannotate qbind qbranch qbrowse qcat qcommit qconfig "
        "qconflicts qdiff qexport qgetnew qgetupdates qinfo qinit "
        "qlog qmerge qplugins qpull qpush qrevert qrun qsend "
        "qswitch qtag qunbind quncommit qupdate qversion qviewer"
    ).split()
    for qcom in qcoms:
        def cmd(c=c, p=p, qcom=qcom):
            path = g.scanAllAtPathDirectives(c, p) or c.getNodePath(p)
            cmd = subprocess.Popen(['bzr', qcom, path])
            cmd.communicate()
        action = menu.addAction(qcom)
        # action.connect(action, QtCore.SIGNAL("triggered()"), cmd)
        action.triggered.connect(cmd)
#@-others
#@@language python
#@@tabwidth -4
#@-leo
