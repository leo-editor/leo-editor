#@+leo-ver=5-thin
#@+node:ekr.20170313020320.1: * @file settings_finder.py
"""
Let the user pick settings from a menu, find the relevant @settings nodes and open them.
"""
import leo.core.leoGlobals as g
from leo.core.leoNodes import VNode
from copy import deepcopy

#@+others
#@+node:ekr.20170313021118.1: ** init
def init():
    '''Return True if the plugin has loaded successfully.'''
    g.registerHandler('after-create-leo-frame',onCreate)
    g.plugin_signon(__name__)
    return True

#@+node:ekr.20170313021152.1: ** onCreate
def onCreate (tag, key):

    c = key.get('c')
    if c:
        sf = SettingsFinder(c)
        sf.build_menu()

#@+node:tbrown.20150818161651.1: ** class SettingsFinder
class SettingsFinder:
    """SettingsFinder - Let the user pick settings from a menu and then
    find the relevant @settings nodes and open them.
    """

    def __init__(self, c):
        """bind to a controller

        :param controller c: outline to bind to
        """
        self.c = c
        self.callbacks = {} # keep track of callbacks made already
    #@+others
    #@+node:tbrown.20150818161651.2: *3* sf._outline_data_build_tree
    @classmethod
    def _outline_data_build_tree(cls, node, element, body):
        """see _outline_data_to_python, this just recursively
        copies info. from xml to VNode tree"""
        node.h = element.find('vh').text
        node.b = ''
        body[element.get('t')] = node
        for sub in element.findall('v'):
            cls._outline_data_build_tree(node.insertAsLastChild(), sub, body)
    #@+node:tbrown.20150818161651.3: *3* sf._outline_data_to_python
    def _outline_data_to_python(self, xml):
        """_outline_data_to_python - make xml from c.config.getOutlineData()
        into a detached VNode tree.

        FIXME this should be elsewhere, just here to allow build_menu() to
        wortk for now.

        :param str xml: xml returned by c.config.getOutlineData()
        :return: VNode tree representing outline data
        :rtype: VNode
        """
        from xml.etree import ElementTree
        # FIXME, probably shouldn't be going @settings tree -> xml -> VNode tree,
        # but @settings tree -> VNode tree, xml + paste to use is cumbersome
        body = {} # node ID to node mapping to fill in body text later
        top = VNode(self.c)
        dom = ElementTree.fromstring(xml)
        self._outline_data_build_tree(top, dom.find('vnodes').find('v'), body)
        for t in dom.find('tnodes').findall('t'):
            if t.text is not None:
                body[t.get('tx')].b = t.text
        return top
    #@+node:tbrown.20150818161651.4: *3* sf.build_menu
    def build_menu(self):
        """build_menu - build the menu of settings, called from handleSpecialMenus()
        """
        menu = self.c.frame.menu
        # Create the Edit Settings menu at the end of the Settings menu.
        settings_menu = menu.getMenu('Settings')
        menu.add_separator(settings_menu)
        menu.createNewMenu('Edit Settings', 'Settings')
        finder_menu = self._outline_data_to_python(
            self.c.config.getOutlineData("settings-finder-menu"))
        aList = []
        self.tree_to_menulist(aList, finder_menu)
        menu.createMenuFromConfigList("Edit Settings", aList[0][1])
            # #1144: Case must match.
            # aList is [['@outline-data settings-finder-menu', <list of submenus>, None]]
            # so aList[0][1] is the list of submenus
        return aList
    #@+node:tbrown.20150818162156.1: *3* sf.copy_recursively
    @staticmethod
    def copy_recursively(nd0, nd1):
        """Recursively copy subtree
        """
        nd1.h = nd0.h
        nd1.b = nd0.b
        nd1.v.u = deepcopy(nd0.v.u)
        for child in nd0.children():
            SettingsFinder.copy_recursively(child, nd1.insertAsLastChild())
    #@+node:tbrown.20150818161651.5: *3* sf.copy_to_my_settings
    def copy_to_my_settings(self, unl, which):
        """copy_to_my_settings - copy setting from leoSettings.leo

        :param str unl: Leo UNL to copy from
        :param int which: 1-3, leaf, leaf's parent, leaf's grandparent
        :return: unl of leaf copy in myLeoSettings.leo
        :rtype: str
        """
        path, unl = unl.split('#', 1)
        # Undo the replacements made in p.getUNL.
        path = path.replace("file://", "")
        path = path.replace("unl://", "")
            # Fix #434: Potential bug in settings
        unl = unl.replace('%20', ' ').split("-->")
        tail = []
        if which > 1: # copying parent or grandparent but select leaf later
            tail = unl[-(which - 1):]
        unl = unl[: len(unl) + 1 - which]
        my_settings_c = self.c.openMyLeoSettings()
        my_settings_c.save() # if it didn't exist before, save required
        settings = g.findNodeAnywhere(my_settings_c, '@settings')
        c2 = g.app.loadManager.openSettingsFile(path)
        if not c2:
            return '' # Fix 434.
        found, maxdepth, maxp = g.recursiveUNLFind(unl, c2)

        nd = settings.insertAsLastChild()
        dest = nd.get_UNL()
        self.copy_recursively(maxp, nd)
        my_settings_c.setChanged()
        my_settings_c.redraw()
        shortcutsDict, settingsDict = g.app.loadManager.createSettingsDicts(my_settings_c, False)
        self.c.config.settingsDict.update(settingsDict)
        my_settings_c.config.settingsDict.update(settingsDict)

        return '-->'.join([dest] + tail)
    #@+node:tbrown.20150818161651.6: *3* sf.find_setting
    def find_setting(self, setting):
        # g.es("Settings finder: find %s" % setting)
        key = g.app.config.canonicalizeSettingName(setting)
        value = self.c.config.settingsDict.get(key)
        which = None
        while value and isinstance(value.val, str) and value.val.startswith('@'):
            msg = ("The relevant setting, '@{specific}', is using the value of "
            "a more general setting, '{general}'.  Would you like to edit the "
            "more specific setting, '@{specific}', or the more general setting, "
            "'{general}'?  The more general setting may alter appearance / "
            "behavior in more places, which may or may not be what you prefer."
            ).format(specific=setting, general=value.val)
            which = g.app.gui.runAskYesNoCancelDialog(self.c, "Which setting?",
                message=msg, yesMessage='Edit Specific', noMessage='Edit General')
            if which != 'no':
                break
            setting = value.val
            key = g.app.config.canonicalizeSettingName(setting[1:])
            value = self.c.config.settingsDict.get(key)
        if which == 'cancel' or not value:
            return
        unl = value and value.unl
        if (
            g.os_path_realpath(value.path) == g.os_path_realpath(g.os_path_join(
            g.app.loadManager.computeGlobalConfigDir(), 'leoSettings.leo')
        )):

            msg = ("The setting '@{specific}' is in the Leo global configuration "
            "file 'leoSettings.leo'\nand should be copied to "
            "'myLeoSettings.leo' before editing.\n"
            "It may make more sense to copy a group or category of settings.\nIf "
            "'myLeoSettings.leo' contains duplicate settings, the last definition "
            "is used."
            "\n\nChoice:\n"
            "1. just select the node in 'leoSettings.leo', I will decide how much\n"
            "   to copy into 'myLeoSettings.leo' (Recommended).\n"
            "2. copy the one setting, '@{specific}'\n")

            # get the settings already defined in myLeoSettings
            my_settings_c = self.c.openMyLeoSettings()
            _, settingsDict = g.app.loadManager.createSettingsDicts(my_settings_c, False)
            # find this setting's node
            path, src_unl = unl.split('#', 1)
            path = path.replace("file://", "").replace("unl://", "")
            src_unl = src_unl.replace('%20', ' ').split("-->")
            c2 = g.app.loadManager.openSettingsFile(path)
            found, maxdepth, maxp = g.recursiveUNLFind(src_unl, c2)
            # scan this setting's group and category for conflicts
            up = maxp.parent()
            if up and self.no_conflict(up, settingsDict):
                msg += "3. copy the setting group, '{group}'\n"
                up = up.parent()
                if up and self.no_conflict(up, settingsDict):
                    msg += "4. copy the whole setting category, '{category}'\n"

            msg = msg.format(specific=setting.lstrip('@'),
                group=unl.split('-->')[-2].split(':', 1)[0].replace('%20', ' '),
                category=unl.split('-->')[-3].split(':', 1)[0].replace('%20', ' '))
            which = g.app.gui.runAskOkCancelNumberDialog(
                self.c, "Copy setting?", message=msg)
            if which is None:
                return
            which = int(which)
            if which > 1:
                unl = self.copy_to_my_settings(unl, which-1)
        if unl:
            g.handleUnl(unl, c=self.c)
    #@+node:tbrown.20150818161651.7: *3* sf.get_command
    def get_command(self, node):
        """return the name of a command to find the relevant setting,
        creating the command if needed
        """
        if not node.b.strip():
            return "settings-find-undefined"
        setting = node.b.strip()
        name = "settings-find-%s" % setting
        if name in self.callbacks:
            return name

        def f(event, setting=setting, self=self):
            self.find_setting(setting)

        g.command(name)(f)
        self.callbacks[name] = f
        return name
    #@+node:tbnorth.20170313094519.1: *3* sf.no_conflict
    def no_conflict(self, p, settings):
        """no_conflict - check for settings defined under p already in settings

        :param position p: node in settings tree
        :param SettingsDict settings: settings already defined
        :return: True if no conflicts
        """
        keys = settings.keys()
        for nd in p.subtree_iter():
            if nd.h.startswith('@') and not nd.h.startswith('@@'):
                name = nd.h.split()
                if len(name) > 1:
                    name = g.app.config.canonicalizeSettingName(name[1])
                    if name in keys:
                        return False
        return True
    #@+node:tbrown.20150818161651.8: *3* sf.settings_find_undefined
    @g.command("settings-find-undefined")
    def settings_find_undefined(self, event):
        g.es("Settings finder: no setting defined")
    #@+node:tbrown.20150818161651.9: *3* sf.tree_to_menulist
    def tree_to_menulist(self, aList, node):
        """recursive helper for build_menu(), copies VNode tree data
        to list format used by c.frame.menu.createMenuFromConfigList()
        """
        if node.children:
            child_list = []
            aList.append(["@menu " + node.h, child_list, None])
            for child in node.children:
                self.tree_to_menulist(child_list, child)
        else:
            aList.append(["@item", self.get_command(node), node.h])
    #@-others
#@-others
#@-leo
