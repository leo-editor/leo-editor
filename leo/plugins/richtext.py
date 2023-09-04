#@+leo-ver=5-thin
#@+node:tbrown.20130813134319.11942: * @file ../plugins/richtext.py
#@+<< docstring >>
#@+node:tbrown.20130813134319.14333: ** << docstring >> (richtext.py)
"""
richtext.py - Rich text editing
===============================

This plugin allows you to use CKEditor__ to edit rich text
in Leo.  Text is stored as HTML in Leo nodes.

__ http://ckeditor.com/

``richtext.py`` provides these ``Alt-X`` commands (also available from
Plugins -> richtext menu):

  cke-text-close
    Close the rich text editor, unhide the regular editor.
  cke-text-open
    Open the rich text editor, hide the regular editor.
  cke-text-switch
    Switch between regular and rich text editor.
  cke-text-toggle-autosave
    Toggle autosaving of changes when you leave a node.
    Be careful not to convert plain text (e.g. source code) to rich
    text unintentionally.  As long as you make no edits, the original
    text will not be changed.

Unless autosaving is enabled, you must confirm saving of edits
each time you edit a node with the rich text editor.

``@rich`` in the headline or first few lines (1000 characters) of a node or its
ancestors will automatically open the rich text editor. ``@norich`` cancels this
action.  Manually opened editors are not affected.

``richtext.py`` uses these ``@settings``:

  @bool richtext_cke_autosave = False
    Set this to True for rich text edits to be saved automatically.

    *BE CAREFUL* - plain-text nodes will be converted to rich text
    without confirmation if you edit them in rich text mode when
    this is True.

  @data richtext_cke_config Configuration info. for CKEditor, see
    http://docs.ckeditor.com/#!/guide/dev_configuration the content of this node
    is the javascript object passed to ``CKEDITOR.replace()`` as it's second
    argument. The version supplied in LeoSettings.leo sets up a sensible
    toolbar. To enable *all* CKEditor toolbar features copy this setting to
    myLeoSettings.leo and remove the default content, i.e. make this node blank,
    then CKEditor will generate a toolbar with all available features.

To make a button to toggle the editor on and off, use::

    @button rich
      c.doCommandByName('cke-text-switch')

"""
#@-<< docstring >>
#@+<< imports >>
#@+node:tbrown.20130813134319.14335: ** << imports >> (richtext.py)
import time
from urllib.parse import unquote
from leo.core import leoGlobals as g
from leo.core.leoQt import QtCore, QtWidgets, QtWebKit, QtWebKitWidgets
#
# Fail fast, right after all imports.
g.assertUi('qt')  # May raise g.UiTypeException, caught by the plugins manager.
#
# Alias.
real_webkit = QtWebKit and 'engine' not in g.os_path_basename(QtWebKit.__file__).lower()
#@-<< imports >>
#@+others
#@+node:tbrown.20130813134319.14337: ** init (richtext.py)
def init():
    """Return True if the plugin has loaded successfully."""
    if not QtWebKit:
        return False
    name = g.app.gui.guiName()
    ok = name == 'qt'
    if ok:
        g.registerHandler('after-create-leo-frame', onCreate)
        g.registerHandler('select3', at_rich_check)
        g.plugin_signon(__name__)
    elif name != 'nullGui':
        print('richtext.py plugin not loading because gui is not Qt')
    return ok
#@+node:tbrown.20130813134319.5691: ** class CKEEditor
class CKEEditor(QtWidgets.QWidget):  # type:ignore
    #@+others
    #@+node:tbrown.20130813134319.7225: *3* __init__ & reloadSettings (CKEEditor)
    def __init__(self, *args, **kwargs):

        self.c = kwargs['c']
        del kwargs['c']
        super().__init__(*args, **kwargs)
        # were we opened by an @ rich node? Calling code will set
        self.at_rich = False
        # are we being closed by leaving an @ rich node? Calling code will set
        self.at_rich_close = False
        # read settings.
        self.reloadSettings()
        # load HTML template
        template_path = g.os_path_join(g.computeLeoDir(), 'plugins', 'cke_template.html')
        self.template = open(template_path).read()
        path = g.os_path_join(g.computeLeoDir(), 'external', 'ckeditor')
        self.template = self.template.replace(
            '[CKEDITOR]', QtCore.QUrl.fromLocalFile(path).toString())
        # make widget containing QWebView
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        # enable inspector, if this really is QtWebKit
        if real_webkit:
            QtWebKit.QWebSettings.globalSettings().setAttribute(
                QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
        self.webview = QtWebKitWidgets.QWebView()
        self.layout().addWidget(self.webview)
        g.registerHandler('select3', self.select_node)
        g.registerHandler('unselect1', self.unselect_node)
        # load current node
        self.select_node('', {'c': self.c, 'new_p': self.c.p})

    def reloadSettings(self):
        c = self.c
        c.registerReloadSettings(self)
        # read autosave preference
        if not hasattr(self.c, '_ckeeditor_autosave'):
            auto = self.c.config.getBool("richtext-cke-autosave") or False
            self.c._ckeeditor_autosave = auto
            if auto:
                g.es("NOTE: automatic saving of rich text edits")
        # load config
        self.config = self.c.config.getData("richtext_cke_config")
        if self.config:
            self.config = '\n'.join(self.config).strip()
    #@+node:tbrown.20130813134319.7226: *3* select_node
    def select_node(self, tag, kwargs):
        c = kwargs['c']
        if c != self.c:
            return

        p = kwargs['new_p']

        self.v = p.v  # to ensure unselect_node is working on the right node
        # currently (20130814) insert doesn't trigger unselect/select, but
        # even if it did, this would be safest

        data = self.template
        if p.b.startswith('<'):  # already rich text, probably
            content = p.b
            self.was_rich = True
        else:
            self.was_rich = p.b.strip() == ''
            # put anything except whitespace in a <pre/>
            content = "<pre>%s</pre>" % p.b if not self.was_rich else ''

        data = data.replace('[CONTENT]', content)

        # replace textarea with CKEditor, with or without config.
        if self.config:
            data = data.replace('[CONFIG]', ', ' + self.config)
        else:
            data = data.replace('[CONFIG]', '')

        # try and make the path for URL evaluation relative to the node's path
        aList = g.get_directives_dict_list(p)
        path = c.scanAtPathDirectives(aList)
        if p.h.startswith('@'):  # see if it's a @<file> node of some sort
            nodepath = p.h.split(None, 1)[-1]
            nodepath = g.os_path_join(path, nodepath)
            if not g.os_path_isdir(nodepath):  # remove filename
                nodepath = g.os_path_dirname(nodepath)
            if g.os_path_isdir(nodepath):  # append if it's a directory
                path = nodepath

        self.webview.setHtml(data, QtCore.QUrl.fromLocalFile(path + "/"))
    #@+node:tbrown.20130813134319.7228: *3* unselect_node
    def unselect_node(self, tag, kwargs):

        c = kwargs['c']
        if c != self.c:
            return None
        # read initial content and request and wait for final content
        frame = self.webview.page().mainFrame()
        ele = frame.findFirstElement("#initial")
        text = str(ele.toPlainText()).strip()
        if text == '[empty]':
            return None  # no edit
        frame.evaluateJavaScript('save_final();')
        ele = frame.findFirstElement("#final")
        for attempt in range(10):  # wait for up to 1 second
            new_text = str(ele.toPlainText()).strip()
            if new_text == '[empty]':
                time.sleep(0.1)
                continue
            break
        if new_text == '[empty]':
            print("Didn't get new text")
            return None
        text = unquote(str(text))
        new_text = unquote(str(new_text))
        if new_text != text:
            if self.c._ckeeditor_autosave:
                ans = 'yes'
            else:
                text = "Save edits?"
                if not self.was_rich:
                    text += " *converting plain text to rich*"
                ans = g.app.gui.runAskYesNoCancelDialog(
                    self.c,
                    "Save edits?",
                    text
                )
            if ans == 'yes':
                c.vnode2position(self.v).b = new_text
                c.redraw()  # but node has content marker still doesn't appear?
            elif ans == 'cancel':
                return 'STOP'
            else:
                pass  # discard edits
        return None
    #@+node:tbrown.20130813134319.7229: *3* close
    def close(self):
        if self.c and not self.at_rich_close:
            # save changes?
            self.unselect_node('', {'c': self.c, 'old_p': self.c.p})
        self.c = None
        g.unregisterHandler('select3', self.select_node)
        g.unregisterHandler('unselect1', self.unselect_node)
        return QtWidgets.QWidget.close(self)
    #@-others
#@+node:tbrown.20130813134319.5694: ** class CKEPaneProvider
class CKEPaneProvider:
    ns_id = '_add_cke_pane'

    def __init__(self, c):
        self.c = c
        # Careful: we may be unit testing.
        if hasattr(c, 'free_layout'):
            splitter = c.free_layout.get_top_splitter()
            if splitter:
                splitter.register_provider(self)

    def ns_provides(self):
        return [('Rich text CKE editor', self.ns_id)]

    def ns_provide(self, id_):
        if id_ == self.ns_id:
            w = CKEEditor(c=self.c)
            return w
        return None

    def ns_provider_id(self):
        # used by register_provider() to unregister previously registered
        # providers of the same service
        return self.ns_id
#@+node:tbrown.20130813134319.14339: ** onCreate
def onCreate(tag, key):

    c = key.get('c')

    CKEPaneProvider(c)
#@+node:tbrown.20130814090427.22458: ** at_rich_check
def at_rich_check(tag, key):

    p = key.get('new_p')

    do = 'close'
    for nd in p.self_and_parents():
        if '@norich' in nd.h or '@norich' in nd.b[:1000]:
            do = 'close'
            break
        if '@rich' in nd.h or '@rich' in nd.b[:1000]:
            do = 'open'
            break

    if do == 'close':
        cmd_CloseEditor(key, at_rich=True)
    elif do == 'open':
        cmd_OpenEditor(key, at_rich=True)
#@+node:tbrown.20130813134319.5692: ** @g.command('cke-text-open')
@g.command('cke-text-open')
def cmd_OpenEditor(event=None, at_rich=False):
    """Open the rich text editor, hide the regular editor."""
    c = event.get('c')
    splitter = c.free_layout.get_top_splitter()
    rte = splitter.find_child(CKEEditor, '')
    if rte:
        if not at_rich:
            g.es("CKE Editor appears to be open already")
        return
    body = splitter.find_child(QtWidgets.QWidget, 'bodyFrame')
    w = CKEEditor(c=c)
    w.at_rich = at_rich
    splitter = body.parent()
    splitter.replace_widget(body, w)
#@+node:tbrown.20130813134319.5693: ** @g.command('cke-text-close')
@g.command('cke-text-close')
def cmd_CloseEditor(event=None, at_rich=False):
    """Close the rich text editor, unhide the regular editor."""
    c = event.get('c')
    splitter = c.free_layout.get_top_splitter()
    if not splitter:
        return
    rte = splitter.find_child(CKEEditor, '')
    if not rte:
        if not at_rich:
            g.es("No editor open")
        return
    if at_rich and not rte.at_rich:
        # don't close manually opened editor
        return
    body = splitter.get_provided('_leo_pane:bodyFrame')
    splitter = rte.parent()
    rte.at_rich_close = True
    splitter.replace_widget(rte, body)
#@+node:tbrown.20130813134319.7233: ** @g.command('cke-text-switch')
@g.command('cke-text-switch')
def cmd_SwitchEditor(event):
    """Switch between regular and rich text editor."""
    c = event.get('c')
    splitter = c.free_layout.get_top_splitter()
    rte = splitter.find_child(CKEEditor, '')
    if not rte:
        cmd_OpenEditor(event)
    else:
        cmd_CloseEditor(event)
#@+node:tbrown.20130813134319.7231: ** @g.command('cke-text-toggle-autosave')
@g.command('cke-text-toggle-autosave')
def cmd_ToggleAutosave(event):
    """
    Toggle autosaving of changes when you leave a node.

    Be careful not to convert plain text (e.g. source code) to rich
    text unintentionally.  As long as you make no edits, the original
    text will not be changed.
    """
    c = event.get('c')
    c._ckeeditor_autosave = not c._ckeeditor_autosave
    g.es("Rich text autosave " +
         ("ENABLED" if c._ckeeditor_autosave else "disabled"))
#@-others
#@@language python
#@@tabwidth -4
#@-leo
