#@+leo-ver=5-thin
#@+node:felix.20210621233316.1: * @file leoserver.py
#@@language python
#@@tabwidth -4
"""
Leo's internet server.

Written by Félix Malboeuf and Edward K. Ream.
"""
#@+<< leoserver imports >>
#@+node:felix.20210621233316.2: ** << leoserver imports >>
# pylint: disable=raise-missing-from
import argparse
import asyncio
from collections.abc import Callable
import fnmatch
import inspect
import itertools
import json
import os
import re
import sys
import socket
import textwrap
import time
from typing import Any, Generator, Iterable, Iterator, Optional, Union
import warnings

# Third-party.
try:
    import tkinter as Tk
except Exception:
    Tk = None
# #2300
try:
    import websockets
except Exception:
    websockets = None
# Make sure the parent of the leo directory is on sys.path.
core_dir = os.path.dirname(__file__)
leo_path = os.path.normpath(os.path.join(core_dir, '..', '..'))
assert os.path.exists(leo_path), repr(leo_path)
if leo_path not in sys.path:
    sys.path.insert(0, leo_path)
del core_dir, leo_path
# Leo
from leo.core.leoCommands import Commands as Cmdr  # noqa
from leo.core.leoNodes import Position, VNode  # noqa
from leo.core.leoGui import StringFindTabManager  # noqa
from leo.core.leoExternalFiles import ExternalFilesController  # noqa
#@-<< leoserver imports >>
#@+<< leoserver annotations >>
#@+node:ekr.20220820155747.1: ** << leoserver annotations >>
Event = Any  # More than one kind of Event!
Loop = Any
Match = re.Match
Match_Iter = Iterator[re.Match[str]]
Package = dict[str, Any]
Param = dict[str, Any]
RegexFlag = Union[int, re.RegexFlag]  # re.RegexFlag does not define 0
Response = str  # See _make_response.
Socket = Any

#@-<< leoserver annotations >>
#@+<< leoserver version >>
#@+node:ekr.20220820160619.1: ** << leoserver version >>
version_tuple = (1, 0, 10)
# Version History
# 1.0.1 Initial commit.
# 1.0.2 July 2022: Adding ui-scroll, undo/redo, chapters, ua's & node_tags info.
# 1.0.3 July 2022: Fixed original node selection upon opening a file.
# 1.0.4 September 2022: Full type checking.
# 1.0.5 October 2022: Fixed node commands when used from client's context menu.
# 1.0.6 February 2023: Fixed JSON serialization, improved search commands and syntax-coloring.
# 1.0.7 September 2023: Fixed message for file change detection.
# 1.0.8 October 2023: Added history commands, Fixed leo document change detection, allowed more minibuffer commands.
# 1.0.9 January 2024: Added support for UNL and specific commander targeting for any command.
# 1.0.10 Febuary 2024: Added support getting UNL for a specific node (for status bar display, etc.)
v1, v2, v3 = version_tuple
__version__ = f"leoserver.py version {v1}.{v2}.{v3}"
#@-<< leoserver version >>
#@+<< leoserver globals >>
#@+node:ekr.20220820160701.1: ** << leoserver globals >>
g = None  # The bridge's leoGlobals module.
# Server defaults
SERVER_STARTED_TOKEN = "LeoBridge started"  # Output when started successfully
# Websocket connections (to be sent 'notify' messages)
connectionsPool: set[Any] = set()
connectionsTotal = 0  # Current connected client total
# Customizable server options
argFile = ""
traces: list[str] = []  # list of traces names, to be used as flags to output traces
wsLimit = 1
wsPersist = False
wsSkipDirty = False
wsHost = "localhost"
wsPort = 32125
#@-<< leoserver globals >>
#@+others
#@+node:felix.20210712224107.1: ** class SetEncoder
class SetEncoder(json.JSONEncoder):

    def default(self, obj: Any) -> Any:
        # Sets become basic javascript arrays
        if isinstance(obj, set):
            return list(obj)
        # Leo Positions get converted with same simple algorithm as p_to_ap
        if isinstance(obj, Position):
            stack = [{'gnx': v.gnx, 'childIndex': childIndex}
                for (v, childIndex) in obj.stack]
            return {
                'childIndex': obj._childIndex,
                'gnx': obj.v.gnx,
                'stack': stack,
            }
        # Leo VNodes are represented as their gnx
        if isinstance(obj, VNode):
            return {'gnx': obj.gnx}
        return json.JSONEncoder.default(self, obj)  # otherwise, return default
#@+node:felix.20210621233316.3: ** Exception classes
class InternalServerError(Exception):  # pragma: no cover
    """The server violated its own coding conventions."""
    pass

class ServerError(Exception):  # pragma: no cover
    """The server received an erroneous package."""
    pass

class TerminateServer(Exception):  # pragma: no cover
    """Ask the server to terminate."""
    pass
#@+node:felix.20210626222905.1: ** class ServerExternalFilesController
class ServerExternalFilesController(ExternalFilesController):
    """EFC Modified from Leo's sources"""
    # pylint: disable=no-else-return

    #@+others
    #@+node:felix.20210626222905.2: *3* sefc.ctor
    def __init__(self) -> None:
        """Ctor for ServerExternalFiles class."""
        super().__init__()

        self.on_idle_count = 0
        # Keys are full paths, values are modification times.
        # DO NOT alter directly, use set_time(path) and
        # get_time(path), see set_time() for notes.
        self.yesno_all_time: float = 0.0  # time of answer (previous yes/no to all answer)
        self.yesno_all_answer = None  # answer, 'yes-all', or 'no-all'

        # if yesAll/noAll forced, then just show info message after idle_check_commander
        self.infoMessage: str = None
        # False or "detected", "refreshed" or "ignored"

        g.app.idleTimeManager.add_callback(self.on_idle)

        self.waitingForAnswer = False
        self.lastPNode: Position = None  # last p node that was asked for if not set to "AllYes\AllNo"
        self.lastCommander: Cmdr = None
    #@+node:felix.20210626222905.6: *3* sefc.clientResult
    def clientResult(self, p_result: Response) -> None:
        """Received result from connected client that was 'asked' yes/no/... """
        # Got the result to an asked question/warning from the client
        if not self.waitingForAnswer:
            print("ERROR: Received Result but no Asked Dialog", flush=True)
            return

        # check if p_result was from a warn (ok) or an ask ('yes','yes-all','no','no-all')
        # act accordingly

        # 1- if ok, unblock 'warn'
        # 2- if no, unblock 'ask'
        # ------------------------------------------ Nothing special to do

        # 3- if noAll: set noAll, and unblock 'ask'
        if p_result and "-all" in p_result.lower():
            self.yesno_all_time = time.time()
            self.yesno_all_answer = p_result.lower()
        # ------------------------------------------ Also covers setting yesAll in #5

        path = ""
        if self.lastPNode:
            path = g.fullPath(self.lastCommander, self.lastPNode)
            # 4- if yes: REFRESH self.lastPNode, and unblock 'ask'
            # 5- if yesAll: REFRESH self.lastPNode, set yesAll, and unblock 'ask'
            if bool(p_result and 'yes' in p_result.lower()):
                self.lastCommander.selectPosition(self.lastPNode)
                self.lastCommander.refreshFromDisk()
        elif self.lastCommander:
            path = self.lastCommander.fileName()
            # 6- Same but for Leo file commander (close and reopen .leo file)
            if bool(p_result and 'yes' in p_result.lower()):
                # self.lastCommander.close() Stops too much if last file closed
                g.app.closeLeoWindow(self.lastCommander.frame, finish_quit=False)
                g.leoServer.open_file({"filename": path})  # ignore returned value

        # Always update the path & time to prevent future warnings for this path.
        if path:
            self.set_time(path)
            self.checksum_d[path] = self.checksum(path)

        self.waitingForAnswer = False  # unblock
        # unblock: run the loop as if timer had hit
        if self.lastCommander:
            self.idle_check_commander(self.lastCommander)
    #@+node:felix.20210714205425.1: *3* sefc.entries
    #@+node:felix.20210626222905.19: *4* sefc.check_overwrite
    def check_overwrite(self, c: Cmdr, path: str) -> bool:
        if self.has_changed(path):
            package = {"async": "info", "message": "Overwritten " + path}
            g.leoServer._send_async_output(package, True)
        return True

    #@+node:felix.20210714205604.1: *4* sefc.on_idle & helpers
    def on_idle(self) -> None:
        """
        Check for changed open-with files and all external files in commanders
        for which @bool check_for_changed_external_file is True.
        """
        # Fix for flushing the terminal console to pass through
        sys.stdout.flush()

        if not g.app or g.app.killed:
            return
        if self.waitingForAnswer:
            return

        self.on_idle_count += 1

        if self.unchecked_commanders:
            # Check the next commander for which
            #@verbatim
            # @bool check_for_changed_external_file is True.
            c = self.unchecked_commanders.pop()
            self.lastCommander = c
            self.lastPNode = None  # when none, a client result means its for the leo file.
            self.idle_check_commander(c)
        else:
            # Add all commanders for which
            #@verbatim
            # @bool check_for_changed_external_file is True.
            self.unchecked_commanders = [
                z for z in g.app.commanders() if self.is_enabled(z)
            ]
    #@+node:felix.20210626222905.4: *5* sefc.idle_check_commander
    def idle_check_commander(self, c: Cmdr) -> None:
        """
        Check all external files corresponding to @<file> nodes in c for
        changes.
        """
        self.infoMessage = None  # reset infoMessage
        # False or "detected", "refreshed" or "ignored"

        # #1240: Check the .leo file itself.
        self.idle_check_leo_file(c)
        #
        # #1100: always scan the entire file for @<file> nodes.
        # #1134: Nested @<file> nodes are no longer valid, but this will do no harm.
        for p in c.all_unique_positions():
            if self.waitingForAnswer:
                break
            if p.isAnyAtFileNode():
                self.idle_check_at_file_node(c, p)

        # if yesAll/noAll forced, then just show info message
        if self.infoMessage:
            package = {"async": "info", "message": self.infoMessage}
            g.leoServer._send_async_output(package, True)
    #@+node:felix.20210627013530.1: *5* sefc.idle_check_leo_file
    def idle_check_leo_file(self, c: Cmdr) -> None:
        """Check c's .leo file for external changes."""
        path = c.fileName()
        if not self.has_changed(path):
            return
        # Always update the path & time to prevent future warnings.
        self.set_time(path)
        self.checksum_d[path] = self.checksum(path)
        # For now, ignore the #1888 fix method
        if self.ask(c, path):
            # reload Commander
            # self.lastCommander.close() Stops too much if last file closed
            g.app.closeLeoWindow(self.lastCommander.frame, finish_quit=False)
            g.leoServer.open_file({"filename": path})  # ignore returned value
    #@+node:felix.20210626222905.5: *5* sefc.idle_check_at_file_node
    def idle_check_at_file_node(self, c: Cmdr, p: Position) -> None:
        """Check the @<file> node at p for external changes."""
        trace = False
        path = c.fullPath(p)
        has_changed = self.has_changed(path)
        if trace:
            g.trace('changed', has_changed, p.h)
        if has_changed:
            self.lastPNode = p  # can be set here because its the same process for ask/warn
            if p.isAtAsisFileNode() or p.isAtNoSentFileNode():
                # Fix #1081: issue a warning.
                self.warn(c, path, p=p)
            elif self.ask(c, path, p=p):
                old_p = c.p  # To restore selection if refresh option set to yes-all & is descendant of at-file
                c.selectPosition(self.lastPNode)
                c.refreshFromDisk()  # Ends with selection on new c.p which is the at-file node
                # check with leoServer's config first, and if new c.p is ancestor of old_p
                if g.leoServer.leoServerConfig:
                    if g.leoServer.leoServerConfig["defaultReloadIgnore"].lower() == 'yes-all':
                        if c.positionExists(old_p) and c.p.isAncestorOf(old_p):
                            c.selectPosition(old_p)
            # Always update the path & time to prevent future warnings.
            self.set_time(path)
            self.checksum_d[path] = self.checksum(path)
    #@+node:felix.20210626222905.18: *4* sefc.open_with
    def open_with(self, c: Cmdr, d: dict[str, str]) -> None:
        """open-with is bypassed in leoserver (for now)"""
        return

    #@+node:felix.20210626222905.7: *3* sefc.utilities
    #@+node:felix.20210626222905.8: *4* sefc.ask
    # The base class returns str.
    def ask(self, c: Cmdr, path: str, p: Position = None) -> bool:  # type:ignore
        """
        Ask user whether to overwrite an @<file> tree.
        Return True if the user agrees by default, or skips and asks
        client, blocking further checks until result received.
        """
        _is_leo = path.endswith(('.leo', '.db', '.leojs'))

        # check with leoServer's config first
        if not _is_leo and g.leoServer.leoServerConfig:
            check_config = g.leoServer.leoServerConfig["defaultReloadIgnore"].lower()
            if not bool('none' in check_config):
                if bool('yes' in check_config):
                    self.infoMessage = "refreshed"
                    return True
                else:
                    self.infoMessage = "ignored"
                    return False
        # let original function resolve

        if self.yesno_all_time + 3 >= time.time() and self.yesno_all_answer:
            self.yesno_all_time = time.time()  # Still reloading?  Extend time
            # if yesAll/noAll forced, then just show info message
            yesno_all_bool = bool('yes' in self.yesno_all_answer.lower())
            return yesno_all_bool  # We already have our answer here, so return it
        if not p:
            where = 'the outline node'
        else:
            where = p.h

        _is_leo = path.endswith(('.leo', '.db', '.leojs'))

        if _is_leo:
            s = '\n'.join([
                f'{g.splitLongFileName(path)} has changed outside Leo.',
                'Reload it?'
            ])
        else:
            s = '\n'.join([
                f'{g.splitLongFileName(path)} has changed outside Leo.',
                f"Reload {where} in Leo?",
            ])

        package = {"async": "ask", "ask": 'Overwrite the version in Leo?',
                     "message": s, "yes_all": not _is_leo, "no_all": not _is_leo}

        g.leoServer._send_async_output(package)  # Ask the connected client
        self.waitingForAnswer = True  # Block the loop and further checks until 'clientResult'
        return False  # return false so as not to refresh until 'clientResult' says so
    #@+node:felix.20210626222905.13: *4* sefc.is_enabled
    def is_enabled(self, c: Cmdr) -> bool:
        """Return the cached @bool check_for_changed_external_file setting."""
        # check with the leoServer config first
        if g.leoServer.leoServerConfig:
            check_config = g.leoServer.leoServerConfig["checkForChangeExternalFiles"].lower()
            if bool('check' in check_config):
                return True
            if bool('ignore' in check_config):
                return False
        # let original function resolve
        return super().is_enabled(c)
    #@+node:felix.20210626222905.16: *4* sefc.warn
    def warn(self, c: Cmdr, path: str, p: Position) -> None:
        """
        Warn that an @asis or @nosent node has been changed externally.

        There is *no way* to update the tree automatically.
        """
        # check with leoServer's config first
        if g.leoServer.leoServerConfig:
            check_config = g.leoServer.leoServerConfig["defaultReloadIgnore"].lower()

            if check_config != "none":
                # if not 'none' then do not warn, just infoMessage 'warn' at most
                if not self.infoMessage:
                    self.infoMessage = "warn"
                return

        if g.unitTesting or c not in g.app.commanders():
            return
        if not p:
            g.trace('NO P')
            return

        s = '\n'.join([
            '%s has changed outside Leo.\n' % g.splitLongFileName(
                path),
            'Leo can not update this file automatically.\n',
            'This file was created from %s.\n' % p.h,
            'Warning: refresh-from-disk will destroy all children.'
        ])

        package = {"async": "warn",
                     "warn": 'External file changed', "message": s}

        g.leoServer._send_async_output(package, True)
        self.waitingForAnswer = True
    #@-others
#@+node:felix.20220225003906.1: ** class QuickSearchController (leoserver.py)
class QuickSearchController:

    #@+others
    #@+node:felix.20220225003906.2: *3* QSC.__init__
    def __init__(self, c: Cmdr) -> None:
        self.c = c
        self.lw: list = []  # empty list
        # Keys are id(w),values are either tuples in tuples (w (p,Position)) or tuples (w, f)
        self.its: dict[int, Any] = {}
        self.fileDirectives = [
            "@asis", "@auto",
            "@auto-md", "@auto-org", "@auto-otl", "@auto-rst",
            "@clean", "@file", "@edit",
        ]
        self._search_patterns: list[str] = []
        self.navText = ''
        self.showParents = True
        self.isTag = False  # added concept to combine tag pane functionality
        self.searchOptions = 0
        self.searchOptionsStrings = ["All", "Subtree", "File", "Chapter", "Node"]
    #@+node:ekr.20220818080756.1: *3* QSC: entries
    #@+node:felix.20220225003906.14: *4* QSC.qsc_search & helpers
    def qsc_search(self, pat: str) -> None:
        hitBase = False
        c = self.c
        flags: RegexFlag
        self.clear()
        self.pushSearchHistory(pat)
        if not pat.startswith('r:'):
            hpat = fnmatch.translate('*' + pat + '*').replace(r"\Z(?ms)", "")
            bpat = fnmatch.translate(pat).rstrip('$').replace(r"\Z(?ms)", "")
            # in python 3.6 there is no (?ms) at the end
            # only \Z
            bpat = bpat.replace(r'\Z', '')
            flags = re.IGNORECASE
        else:
            hpat = pat[2:]
            bpat = pat[2:]
            flags = 0
        combo = self.searchOptionsStrings[self.searchOptions]
        bNodes: Iterable[Position]
        hNodes: Iterable[Position]
        if combo == "All":
            hNodes = c.all_positions()
            bNodes = c.all_positions()
        elif combo == "Subtree":
            hNodes = c.p.self_and_subtree()
            bNodes = c.p.self_and_subtree()
        elif combo == "File":
            found = False
            node = c.p
            while not found and not hitBase:
                h = node.h
                if h:
                    h = h.split()[0]
                if h in self.fileDirectives:
                    found = True
                else:
                    if node.level() == 0:
                        hitBase = True
                    else:
                        node = node.parent()
            hNodes = node.self_and_subtree()
            bNodes = node.self_and_subtree()
        elif combo == "Chapter":
            found = False
            node = c.p
            while not found and not hitBase:
                h = node.h
                if h:
                    h = h.split()[0]
                if h == "@chapter":
                    found = True
                else:
                    if node.level() == 0:
                        hitBase = True
                    else:
                        node = node.parent()
            if hitBase:
                # If I hit the base then revert to all positions
                # this is basically the "main" chapter
                hitBase = False  #reset
                hNodes = c.all_positions()
                bNodes = c.all_positions()
            else:
                hNodes = node.self_and_subtree()
                bNodes = node.self_and_subtree()
        else:
            hNodes = [c.p]
            bNodes = [c.p]

        if not hitBase:
            # hNodes = list(hNodes)
            # bNodes = list(bNodes)
            hm = self.find_h(hpat, list(hNodes), flags)  # Returns a list of positions.
            bm = self.find_b(bpat, list(bNodes), flags)  # Returns a list of positions.
            bm_keys = [match[0].key() for match in bm]
            numOfHm = len(hm)  #do this before trim to get accurate count
            hm = [match for match in hm if match[0].key() not in bm_keys]
            if self.showParents:
                # Was: parents = OrderedDefaultDict(list)
                parents: dict[str, list[tuple[Position, Match_Iter]]] = {}

                for nodeList in [hm, bm]:
                    for node in nodeList:
                        key = 'Root' if node[0].level() == 0 else node[0].parent().gnx
                        aList: list[tuple[Position, Match_Iter]] = parents.get(key, [])
                        aList.append(node)
                        parents[key] = aList
                lineMatchHits = self.addParentMatches(parents)
            else:
                self.addHeadlineMatches(hm)
                lineMatchHits = self.addBodyMatches(bm)

            hits = numOfHm + lineMatchHits
            self.lw.insert(0, f"{hits} hits")

        else:
            if combo == "File":
                self.lw.insert(0, 'External file directive not found during search')
    #@+node:ekr.20220818083736.1: *5* QSC.pushSearchHistory
    def pushSearchHistory(self, pat: str) -> None:
        if pat in self._search_patterns:
            return
        self._search_patterns = ([pat] + self._search_patterns)[:30]

    #@+node:felix.20220225003906.5: *5* QSC.addBodyMatches
    def addBodyMatches(self, positions: list[tuple[Position, Match_Iter]]) -> int:
        lineMatchHits = 0
        for p in positions:
            it = {"type": "headline", "label": p[0].h}
            if self.addItem(it, (p[0], None)):
                return lineMatchHits
            ms = self.matchlines(p[0].b, p[1])
            for ml, pos in ms:
                lineMatchHits += 1
                it = {"type": "body", "label": ml}
                if self.addItem(it, (p[0], pos)):
                    return lineMatchHits
        return lineMatchHits


    #@+node:felix.20220225003906.11: *4* QSC.qsc_search_history & helper (not used)
    def qsc_search_history(self) -> None:

        self.clear()

        def sHistSelect(x: str) -> Callable:
            def _f() -> None:
                # self.widgetUI.lineEdit.setText(x)
                scon: QuickSearchController = self.c.patched_quicksearch_controller
                scon.navText = x
                self.qsc_search(x)
            return _f

        for pat in self._search_patterns:
            self.addGeneric(pat, sHistSelect(pat))
    #@+node:felix.20220225003906.7: *5* QSC.addGeneric
    def addGeneric(self, text: str, f: Callable) -> dict:
        """ Add generic callback """
        it = {"type": "generic", "label": text}
        self.its[id(it)] = (it, f)
        return it

    #@+node:felix.20220225003906.12: *4* QSC.qsc_sort_by_gnx
    def qsc_sort_by_gnx(self) -> None:
        """Return positions by gnx."""
        c = self.c
        timeline: list[tuple[Position, Match_Iter]] = [
            (p.copy(), None) for p in c.all_unique_positions()
        ]
        timeline.sort(key=lambda x: x[0].gnx, reverse=True)
        self.clear()
        self.addHeadlineMatches(timeline)
    #@+node:felix.20220225003906.15: *4* QSC.qsc_background_search
    def qsc_background_search(self, pat: str) -> tuple[
        list[tuple[Position, Match_Iter]],
        list[Position]
    ]:

        flags: RegexFlag
        if not pat.startswith('r:'):
            hpat = fnmatch.translate('*' + pat + '*').replace(r"\Z(?ms)", "")
            # bpat = fnmatch.translate(pat).rstrip('$').replace(r"\Z(?ms)","")
            flags = re.IGNORECASE
        else:
            hpat = pat[2:]
            flags = 0
        combo = self.searchOptionsStrings[self.searchOptions]
        hNodes: Iterable[Position]
        if combo == "All":
            hNodes = self.c.all_positions()
        elif combo == "Subtree":
            hNodes = self.c.p.self_and_subtree()
        else:
            hNodes = [self.c.p]
        hm = self.find_h(hpat, list(hNodes), flags)
        # Update the real quicksearch controller.
        self.clear()
        self.addHeadlineMatches(hm)
        return hm, []
    #@+node:felix.20220225003906.13: *4* QSC.qsc_find_changed
    def qsc_find_changed(self) -> None:
        c = self.c
        changed: list[tuple[Position, Match_Iter]] = [
            (p.copy(), None) for p in c.all_unique_positions() if p.isDirty()
        ]
        self.clear()
        self.addHeadlineMatches(changed)
    #@+node:felix.20220313183922.1: *4* QSC.qsc_find_tags & helpers
    def qsc_find_tags(self, pat: str) -> None:
        """
        Search for tags: outputs position list
        If empty pattern, list tags *strings* instead
        """
        if not pat:
            # No pattern! list all tags as string
            c = self.c
            self.clear()
            d: dict[str, Any] = {}
            for p in c.all_unique_positions():
                u = p.v.u
                tags = set(u.get('__node_tags', set([])))
                for tag in tags:
                    aList = d.get(tag, [])
                    aList.append(p.h)
                    d[tag] = aList
            if d:
                for key in sorted(d):
                    # key is unique tag
                    self.addTag(key)
            return
        # else: non empty pattern, so find tag!
        hm = self.find_tag(pat)
        self.clear()  # needed for external client ui replacement: fills self.its
        self.addHeadlineMatches(hm)  # added for external client ui replacement: fills self.its
    #@+node:felix.20220318222437.1: *5* QSC.addTag
    def addTag(self, text: str) -> dict:
        """ add Tag label """
        it = {"type": "tag", "label": text}
        self.its[id(it)] = (it, None)
        return it

    #@+node:felix.20220313185430.1: *5* QSC.find_tag
    def find_tag(self, pat: str) -> list[tuple[Position, Match_Iter]]:
        """
        Return list of all positions that have matching tags
        """
        #  USE update_list(self) from @file ../plugins/nodetags.py
        c = self.c

        tc = getattr(c, 'theTagController', None)
        if not tc:
            print("In find_tag: No 'theTagController' on commander.")
            print("Make sure nodetags.py is an active plugin in myLeoSettings.leo")
            print("", flush=True)
            return []

        gnxDict = c.fileCommands.gnxDict
        key = pat.strip()

        query = re.split(r'(&|\||-|\^)', key)
        tags = []
        operations = []
        for i, s in enumerate(query):
            if i % 2 == 0:
                tags.append(s.strip())
            else:
                operations.append(s.strip())
        tags.reverse()
        operations.reverse()

        resultset: set[str] = set(tc.get_tagged_gnxes(tags.pop()))
        while operations:
            op = operations.pop()
            nodes: set[str] = set(tc.get_tagged_gnxes(tags.pop()))
            if op == '&':
                resultset &= nodes
            elif op == '|':
                resultset |= nodes
            elif op == '-':
                resultset -= nodes
            elif op == '^':
                resultset ^= nodes
        aList: list[tuple[Position, Match_Iter]] = []
        for gnx in resultset:
            n = gnxDict.get(gnx)
            if n is not None:
                p = c.vnode2position(n)
                aList.append((p.copy(), None))
        return aList
    #@+node:felix.20220225003906.10: *4* QSC.qsc_get_history
    def qsc_get_history(self) -> None:
        headlines: list[tuple[Position, Match_Iter]] = [
            (po[0].copy(), None) for po in self.c.nodeHistory.beadList
        ]
        headlines.reverse()
        self.clear()
        self.addHeadlineMatches(headlines)
    #@+node:felix.20220225003906.18: *4* QSC.qsc_show_marked
    def qsc_show_marked(self) -> None:
        self.clear()
        c = self.c
        self.addHeadlineMatches([
            (z.copy(), None) for z in c.all_positions() if z.isMarked()
        ])
    #@+node:ekr.20220818083228.1: *3* QSC: helpers
    #@+node:felix.20220225003906.8: *4* QSC.addHeadlineMatches
    def addHeadlineMatches(self,
        position_list: list[tuple[Position, Match_Iter]]
    ) -> None:
        for p in position_list:
            it = {"type": "headline", "label": p[0].h}
            if self.addItem(it, (p[0], None)):
                return
    #@+node:felix.20220225003906.4: *4* QSC.addItem
    def addItem(self, it: Any, val: Any) -> bool:
        self.its[id(it)] = (it, val)
        # changed to 999 from 3000 to replace old threadutil behavior
        return len(self.its) > 999  # Limit to 999 for now
    #@+node:felix.20220225003906.6: *4* QSC.addParentMatches
    def addParentMatches(self,
        parent_list: dict[str, list[tuple[Position, Match_Iter]]],
    ) -> int:
        lineMatchHits = 0
        for parent_key, parent_value in parent_list.items():
            if isinstance(parent_key, str):
                v = self.c.fileCommands.gnxDict.get(parent_key)
                h = v.h if v else parent_key
                it = {"type": "parent", "label": h}
            else:
                it = {"type": "parent", "label": parent_key[0].h}
            if self.addItem(it, (parent_key, None)):
                return lineMatchHits
            for p, m in parent_value:
                it = {"type": "headline", "label": p.h}
                if self.addItem(it, (p, None)):
                    return lineMatchHits
                if m is not None:  #p might not have body matches
                    ms = self.matchlines(p.b, m)
                    for match_list, pos in ms:
                        lineMatchHits += 1
                        it = {"type": "body", "label": match_list}
                        if self.addItem(it, (p, pos)):
                            return lineMatchHits

        return lineMatchHits

    #@+node:felix.20220225003906.9: *4* QSC.clear
    def clear(self) -> None:
        self.its = {}
        self.lw.clear()

    #@+node:felix.20220225003906.17: *4* QSC.find_b
    def find_b(self,
        regex: str,
        positions: list[Position],
        flags: RegexFlag = re.IGNORECASE | re.MULTILINE,
    ) -> list[tuple[Position, Match_Iter]]:
        """
        Return list of all tuple (Position, matchiter/None) whose body matches regex one or more times.
        """
        try:
            pat = re.compile(regex, flags)
        except Exception:
            return []

        aList: list[tuple[Position, Match_Iter]] = []
        for p in positions:
            m = re.finditer(pat, p.b)
            t1, t2 = itertools.tee(m, 2)
            try:
                t1.__next__()
            except StopIteration:
                continue
            pc = p.copy()
            aList.append((pc, t2))

        return aList
    #@+node:felix.20220225003906.16: *4* QSC.find_h
    def find_h(self,
        regex: str,
        positions: list[Position],
        flags: RegexFlag = re.IGNORECASE,
    ) -> list[tuple[Position, Match_Iter]]:
        """
        Return the list of all tuple (Position, matchiter/None) whose headline matches the given pattern.
        """
        try:
            pat = re.compile(regex, flags)
        except Exception:
            return []
        return [(p.copy(), None) for p in positions if re.match(pat, p.h)]
    #@+node:felix.20220225224130.1: *4* QSC.matchlines
    def matchlines(self, b: str, miter: Match_Iter) -> list[tuple[str, tuple[int, int]]]:
        aList = []
        for m in miter:
            st, en = g.getLine(b, m.start())
            li = b[st:en].strip()
            aList.append((li, (m.start(), m.end())))
        return aList

    #@+node:felix.20220225003906.20: *4* QSC.onSelectItem (from quicksearch.py)
    def onSelectItem(self, it: Any, it_prev: Any = None) -> None:  # it_prev not used. Hard to annotate.
        c = self.c
        tgt = self.its.get(it)
        if not tgt:
            if not g.unitTesting:
                print("onSelectItem: no target found for 'it' as key:" + str(it))
            return

        # generic callable
        try:
            if callable(tgt[1]):
                tgt()
            elif len(tgt[1]) == 2:
                p, pos = tgt[1]
                if hasattr(p, 'v'):  # p might be "Root"
                    if not c.positionExists(p):
                        g.es("Node moved or deleted.\nMaybe re-do search.",
                            color='red')
                        return
                    c.selectPosition(p)
                    if pos is not None:
                        if hasattr(g.app.gui, 'show_find_success'):  # pragma: no cover
                            g.app.gui.show_find_success(c, False, 0, p)
                        st, en = pos
                        w = c.frame.body.wrapper
                        w.setSelectionRange(st, en)
                        w.seeInsertPoint()
                        c.bodyWantsFocus()
                        c.bodyWantsFocusNow()
                    else:
                        if hasattr(g.app.gui, 'show_find_success'):  # pragma: no cover
                            g.app.gui.show_find_success(c, True, 0, p)
        except Exception:
            raise ServerError("QuickSearchController onSelectItem error")
    #@-others
#@+node:felix.20210621233316.4: ** class LeoServer
class LeoServer:
    """Leo Server Controller"""
    #@+others
    #@+node:felix.20210621233316.5: *3* server.__init__
    def __init__(self, testing: bool = False) -> None:

        import leo.core.leoApp as leoApp
        import leo.core.leoBridge as leoBridge

        global g
        t1 = time.process_time()
        #
        # Init ivars first.
        self.c: Cmdr = None  # Currently Selected Commander.
        self.dummy_c: Cmdr = None  # Set below, after we set g.
        self.action: str = None
        self.bad_commands_list: list[str] = []  # Set below.
        #
        # Debug utilities
        self.current_id = 0  # Id of action being processed.
        self.log_flag = False  # set by "log" key
        #
        # Start the bridge.
        self.bridge = leoBridge.controller(
            gui='nullGui',
            loadPlugins=True,  # True: attempt to load plugins.
            readSettings=True,  # True: read standard settings files.
            silent=True,  # True: don't print signon messages.
            verbose=False,  # True: prints messages that would be sent to the log pane.
        )
        self.g = g = self.bridge.globals()  # Also sets global 'g' object
        g.in_leo_server = True  # #2098.
        g.leoServer = self  # Set server singleton global reference
        self.leoServerConfig: Param = None
        #
        # * Intercept Log Pane output: Sends to client's log pane
        g.es = self._es  # pointer - not a function call
        g.es_print = self._es  # Also like es, because es_print would double strings in client
        #
        # Set in _init_connection
        self.web_socket = None  # Main Control Client
        self.loop: Loop = None
        #
        # To inspect commands
        self.dummy_c = g.app.newCommander(fileName=None)
        self.bad_commands_list = self._bad_commands(self.dummy_c)
        #
        # * Replacement instances to Leo's codebase : getScript, IdleTime and externalFilesController
        g.getScript = self._getScript
        g.IdleTime = self._idleTime
        #
        # * hook open2 for commander creation completion and inclusion in windowList
        #
        g.registerHandler('open2', self._open2Hook)
        # override for selectLeoWindow
        g.app.selectLeoWindow = self._selectLeoWindow
        #
        # override for "revert to file" operation
        g.app.gui.runAskOkDialog = self._runAskOkDialog
        g.app.gui.runAskYesNoDialog = self._runAskYesNoDialog
        g.app.gui.runAskYesNoCancelDialog = self._runAskYesNoCancelDialog
        g.app.gui.show_find_success = self._show_find_success
        self.headlineWidget = g.bunch(_name='tree')
        #
        # Complete the initialization, as in LeoApp.initApp.
        g.app.idleTimeManager = leoApp.IdleTimeManager()
        g.app.externalFilesController = ServerExternalFilesController()  # Replace
        g.app.idleTimeManager.start()
        t2 = time.process_time()
        if not testing:
            print(f"LeoServer: init leoBridge in {t2-t1:4.2} sec.", flush=True)
    #@+node:felix.20240110004711.1: *3* server.finishCreate
    def finishCreate(self, c: Cmdr) -> None:
        """Finalize commander creation and add to windowList in leoserver"""
        if c:
            if not hasattr(c, 'patched_quicksearch_controller'):
                # Add ftm. This won't happen if opened outside leoserver
                c.findCommands.ftm = StringFindTabManager(c)  # type: ignore
                cc = QuickSearchController(c)
                # Patch up quick-search controller to the commander
                c.patched_quicksearch_controller = cc
                # Patch up for 'selection range' in headlines left by the search commands.
                c.frame.tree.endEditLabel = self._endEditLabel
                c.recreateGnxDict()  # refresh c.fileCommands.gnxDict used in ap_to_p
                self._check_outline(c)
                g.app.windowList.append(c.frame)

        # print(str(tag))
        # print(str(keywords))
    #@+node:felix.20210622235127.1: *3* server.leo overridden methods
    #@+node:felix.20240109225617.1: *4* LeoServer_open2Hook
    def _open2Hook(self, tag: Any, keywords: Any) -> None:
        """Hook for finalizing commander creation and add to windowList in leoserver"""
        c = keywords.get('c')
        g.leoServer.finishCreate(c)
        # print(str(tag))
        # print(str(keywords))
    #@+node:felix.20240108011940.1: *4* LeoServer._selectLeoWindow
    def _selectLeoWindow(self, c: Cmdr) -> None:
        """Replaces selectLeoWindow in Leo server"""
        g.leoServer.c = c
        g.leoServer.c.selectPosition(c.p)
        g.leoServer.c.recreateGnxDict()
        g.leoServer._check_outline(c)

    #@+node:felix.20230206202334.1: *4* LeoServer._endEditLabel
    def _endEditLabel(self) -> None:
        """Overridden : End editing of a headline and update p.h."""
        if not hasattr(self, 'c') or not self.c:
            return
        try:
            gui_w = self.c.edit_widget(self.c.p)
            gui_w.setSelectionRange(0, 0, insert=0)
        except Exception:
            print("Could not reset headline cursor")
        # Important: this will redraw if necessary.
        self.c.frame.tree.onHeadChanged(self.c.p)
    #@+node:felix.20210711194729.1: *4* LeoServer._runAskOkDialog
    def _runAskOkDialog(self, c: Cmdr, title: str, message: str = None, text: str = "Ok") -> None:
        """Create and run an askOK dialog ."""
        # Called by many commands in Leo
        if message:
            s = title + " " + message
        else:
            s = title
        package = {"async": "info", "message": s}
        g.leoServer._send_async_output(package)
    #@+node:felix.20210711194736.1: *4* LeoServer._runAskYesNoDialog
    def _runAskYesNoDialog(self,
        c: Cmdr,
        title: str,
        message: str = None,
        yes_all: bool = False,
        no_all: bool = False,
    ) -> str:
        """Create and run an askYesNo dialog."""
        # used in ask with title: 'Overwrite the version in Leo?'
        # used in revert with title: 'Revert'
        # used in create ly leo settings with title: 'Create myLeoSettings.leo?'
        # used in move nodes with title: 'Move Marked Nodes?'
        s = "runAskYesNoDialog called"
        if title.startswith('Overwrite'):
            s = "@<file> tree was overwritten"
        elif title.startswith('Revert'):
            s = "Leo outline reverted to last saved contents"
        elif title.startswith('Create'):
            s = "myLeoSettings.leo created"
        elif title.startswith('Move'):
            s = "Marked nodes were moved"
        package = {"async": "info", "message": s}
        g.leoServer._send_async_output(package)
        return "yes"
    #@+node:felix.20210711194745.1: *4* LeoServer._runAskYesNoCancelDialog
    def _runAskYesNoCancelDialog(
        self,
        c: Cmdr,
        title: str,
        message: str = None,
        yesMessage: str = "Yes",
        noMessage: str = "No",
        yesToAllMessage: str = None,
        defaultButton: str = "Yes",
        cancelMessage: str = None,
    ) -> str:
        """Create and run an askYesNoCancel dialog ."""
        # used in dangerous write with title: 'Overwrite existing file?'
        # used in prompt for save with title: 'Confirm'
        s = "runAskYesNoCancelDialog called"
        if title.startswith('Overwrite'):
            s = "File Overwritten"
        elif title.startswith('Confirm'):
            s = "File Saved"
        package = {"async": "info", "message": s}
        g.leoServer._send_async_output(package)
        return "yes"
    #@+node:felix.20210622235209.1: *4* LeoServer._es
    def _es(self, *args: Any, **keys: Any) -> None:  # pragma: no cover (tested in client).
        """Output to the Log Pane"""
        d = {
            'color': None,
            'commas': False,
            'newline': True,
            'spaces': True,
            'tabName': 'Log',
            'nodeLink': None,
        }
        d = g.doKeywordArgs(keys, d)
        color = d.get('color')
        color = g.actualColor(color)
        s = g.translateArgs(args, d)
        package = {"async": "log", "log": s}
        if color:
            package["color"] = color
        self._send_async_output(package, True)
    #@+node:felix.20210626002856.1: *4* LeoServer._getScript
    def _getScript(
        self,
        c: Cmdr,
        p: Position,
        useSelectedText: bool = True,
        forcePythonSentinels: bool = True,
        useSentinels: bool = True,
    ) -> str:
        """
        Return the expansion of the selected text of node p.
        Return the expansion of all of node p's body text if
        p is not the current node or if there is no text selection.
        """
        w = c.frame.body.wrapper
        if not p:
            p = c.p
        try:
            if w and p == c.p and useSelectedText and w.hasSelection():
                s = w.getSelectedText()
            else:
                s = p.b
            # Remove extra leading whitespace so the user may execute indented code.
            s = textwrap.dedent(s)
            s = g.extractExecutableString(c, p, s)
            script = g.composeScript(c, p, s,
                                      forcePythonSentinels=forcePythonSentinels,
                                      useSentinels=useSentinels)
        except Exception:
            g.es_print("unexpected exception in g.getScript", flush=True)
            g.es_exception()
            script = ''
        return script
    #@+node:felix.20210627004238.1: *4* LeoServer._asyncIdleLoop
    async def _asyncIdleLoop(self, seconds: Union[int, float], func: Callable) -> None:
        while True:
            await asyncio.sleep(seconds)
            func(self)
    #@+node:felix.20210627004039.1: *4* LeoServer._idleTime
    def _idleTime(self, fn: Callable, delay: Union[int, float], tag: str) -> None:

        warnings.simplefilter("ignore")

        asyncio.get_event_loop().create_task(self._asyncIdleLoop(delay / 1000, fn))
    #@+node:felix.20210626003327.1: *4* LeoServer._show_find_success
    def _show_find_success(self,
        c: Cmdr,
        in_headline: bool,
        insert: Any,
        p: Position,
    ) -> None:
        """Handle a successful find match."""
        if in_headline:
            g.app.gui.set_focus(c, self.headlineWidget)
        # no return
    #@+node:felix.20210621233316.6: *3* server.public commands
    #@+node:felix.20210621233316.7: *4* server.button commands
    # These will fail unless the open_file inits c.theScriptingController.
    #@+node:felix.20210621233316.8: *5* _check_button_command
    def _check_button_command(self, c: Cmdr, tag: str) -> dict:  # pragma: no cover (no scripting controller)
        """
        Check that a button command is possible.
        Raise ServerError if not. Otherwise, return sc.buttonsDict.
        """
        sc = getattr(c, "theScriptingController", None)
        if not sc:
            # This will happen unless mod_scripting is loaded!
            raise ServerError(f"{tag}: no scripting controller")
        return sc.buttonsDict
    #@+node:felix.20220220203658.1: *5* _get_rclickTree
    def _get_rclickTree(self, rclicks: list[Any]) -> list[dict[str, Any]]:
        rclickList: list[dict[str, Any]] = []
        for rc in rclicks:
            children = []
            if rc.children:
                children = self._get_rclickTree(rc.children)
            rclickList.append({"name": rc.position.h, "children": children})
        return rclickList


    #@+node:felix.20210621233316.9: *5* server.click_button
    def click_button(self, param: Param) -> Response:  # pragma: no cover (no scripting controller)
        """Handles buttons clicked in client from the '@button' panel"""
        tag = 'click_button'
        index = param.get("index")
        c = self._check_c(param)

        if not index:
            raise ServerError(f"{tag}: no button index given")
        d = self._check_button_command(c, tag)
        button = None
        for key in d:
            # Some button keys are objects so we have to convert first
            if str(key) == index:
                button = key

        if not button:
            raise ServerError(f"{tag}: button {index!r} does not exist")

        try:
            w_rclick = param.get("rclick", False)
            if w_rclick and hasattr(button, 'rclicks'):
                # not zero
                toChooseFrom = button.rclicks
                for i_rc in w_rclick:
                    w_rclickChosen = toChooseFrom[i_rc]
                    toChooseFrom = w_rclickChosen.children
                if w_rclickChosen:
                    sc = getattr(c, "theScriptingController", None)
                    sc.executeScriptFromButton(button, "", w_rclickChosen.position, "")

            else:
                button.command()
        except Exception as e:
            raise ServerError(f"{tag}: exception clicking button {index!r}: {e}")
        # Tag along a possible return value with info sent back by _make_response
        return self._make_response()
    #@+node:felix.20210621233316.10: *5* server.get_buttons
    def get_buttons(self, param: dict) -> Response:  # pragma: no cover (no scripting controller)
        """
        Gets the currently opened file's @buttons list
        as an array of dict.

        Typescript RClick recursive interface:
        RClick: {name: string, children: RClick[]}

        Typescript return interface:
            {
                name: string;
                index: string;
                rclicks: RClick[];
            }[]
        """
        c = self._check_c(param)
        d = self._check_button_command(c, 'get_buttons')

        buttons = []
        # Some button keys are objects so we have to convert first
        for key in d:
            rclickList = []
            if hasattr(key, 'rclicks'):
                rclickList = self._get_rclickTree(key.rclicks)
                # buttonRClicks = key.rclicks
                # for rc in buttonRClicks:
                #     rclickList.append(rc.position.h)

            entry = {"name": d[key], "index": str(key), "rclicks": rclickList}
            buttons.append(entry)

        return self._make_minimal_response({
            "buttons": buttons
        })
    #@+node:felix.20210621233316.11: *5* server.remove_button
    def remove_button(self, param: dict) -> Response:  # pragma: no cover (no scripting controller)
        """Remove button by index 'key string'."""
        tag = 'remove_button'
        index = param.get("index")
        c = self._check_c(param)

        if not index:
            raise ServerError(f"{tag}: no button index given")
        d = self._check_button_command(c, tag)
        # Some button keys are objects so we have to convert first
        key = None
        for i_key in d:
            if str(i_key) == index:
                key = i_key
        if key:
            try:
                del d[key]
            except Exception as e:
                raise ServerError(f"{tag}: exception removing button {index!r}: {e}")
        else:
            raise ServerError(f"{tag}: button {index!r} does not exist")

        return self._make_response()
    #@+node:felix.20211016235830.1: *5* server.goto_script
    def goto_script(self, param: dict) -> Response:  # pragma: no cover (no scripting controller)
        """Goto the script this button originates."""
        tag = 'goto_script'
        index = param.get("index")
        c = self._check_c(param)

        if not index:
            raise ServerError(f"{tag}: no button index given")
        d = self._check_button_command(c, tag)
        # Some button keys are objects so we have to convert first
        key = None
        for i_key in d:
            if str(i_key) == index:
                key = i_key
        if key:
            try:
                gnx = key.command.gnx
                sc = getattr(c, "theScriptingController", None)
                c2, p = sc.open_gnx(c, gnx)
                if c2:
                    self.c = c2
                    c2.selectPosition(p)
            except Exception as e:
                raise ServerError(f"{tag}: exception going to script of button {index!r}: {e}")
        else:
            raise ServerError(f"{tag}: button {index!r} does not exist")

        return self._make_response()
    #@+node:felix.20210621233316.12: *4* server.file commands
    #@+node:felix.20210621233316.13: *5* server.open_file
    def open_file(self, param: Param) -> Response:
        """
        Open a leo file with the given filename.
        Create a new document if no name.
        """
        found, tag = False, 'open_file'
        filename = param.get('filename')  # Optional.
        if filename:
            for c in g.app.commanders():
                if c.fileName() == filename:
                    found = True
                    break
        if not found:
            c = self.bridge.openLeoFile(filename)
        if not c:  # pragma: no cover
            raise ServerError(f"{tag}: bridge did not open {filename!r}")
        if not c.frame.body.wrapper:  # pragma: no cover
            raise ServerError(f"{tag}: no wrapper")
        # Assign self.c
        self.c = c

        if g.unitTesting and isinstance(g.app.pluginsController, g.NullObject):
            # REPLACE PLUGIN SYSTEM !
            self.finishCreate(c)

        if self.log_flag:  # pragma: no cover
            self._dump_outline(c)

        result = {"total": len(g.app.commanders()), "filename": self.c.fileName()}

        return self._make_response(result)
    #@+node:felix.20210621233316.14: *5* server.open_files
    def open_files(self, param: Param) -> Response:
        """
        Opens an array of leo files.
        Returns an object with total opened files
        and name of currently last opened & selected document.
        """
        files = param.get('files')  # Optional.
        if files:
            for i_file in files:
                if os.path.isfile(i_file):
                    self.open_file({"filename": i_file})
        total = len(g.app.commanders())
        filename = self.c.fileName() if total else ""
        result = {"total": total, "filename": filename}
        return self._make_response(result)
    #@+node:felix.20210621233316.15: *5* server.set_opened_file
    def set_opened_file(self, param: Param) -> Response:
        """
        Choose the new active commander from array of opened files.
        Returns an object with total opened files
        and name of currently last opened & selected document.
        """
        tag = 'set_opened_file'
        total = len(g.app.commanders())

        # By Commander's id
        commanderId = param.get('commanderId')
        if commanderId:
            commanders = g.app.commanders()
            for commander in commanders:
                if id(commander) == commanderId:
                    self.c = commander  #  Found commander by id!
                    self.c.selectPosition(self.c.p)
                    self._check_outline(self.c)
                    result = {"total": total, "filename": self.c.fileName()}
                    return self._make_response(result)

        # By Index
        index = param.get('index') or 0
        if total and index < total:
            self.c = g.app.commanders()[index]
            # maybe needed for frame wrapper
            self.c.selectPosition(self.c.p)
            self._check_outline(self.c)
            result = {"total": total, "filename": self.c.fileName()}
            return self._make_response(result)

        raise ServerError(f"{tag}: commander at index {index} does not exist")
    #@+node:felix.20210621233316.16: *5* server.close_file
    def close_file(self, param: Param) -> Response:
        """
        Closes an outline opened with open_file.
        Use a 'forced' flag to force close.
        Returns a 'total' member in the package if close is successful.
        """
        c = self._check_c(param)
        forced = param.get("forced")
        if c:
            # First, revert to prevent asking user.
            if forced and c.changed:
                if c.fileName():
                    c.revert()
                else:
                    c.changed = False  # Needed in g.app.closeLeoWindow
            # Then, if still possible, close it.
            if forced or not c.changed:
                # c.close() # Stops too much if last file closed
                g.app.closeLeoWindow(c.frame, finish_quit=False)
            else:
                # Cannot close, return empty response without 'total'
                # (ask to save, ignore or cancel)
                return self._make_response()
        # New 'c': Select the first open outline, if any.
        commanders = g.app.commanders()
        self.c = commanders and commanders[0] or None
        if self.c:
            result = {"total": len(g.app.commanders()), "filename": self.c.fileName()}
        else:
            result = {"total": 0}
        return self._make_response(result)
    #@+node:felix.20210621233316.17: *5* server.save_file
    def save_file(self, param: Param) -> Response:  # pragma: no cover (too dangerous).
        """Save the leo outline."""
        tag = 'save_file'
        c = self._check_c(param)
        if c:
            try:
                if "name" in param:
                    c.save(fileName=param['name'])
                else:
                    c.save()
            except Exception as e:
                print(f"{tag} Error while saving {param['name']}", flush=True)
                print(e, flush=True)

        return self._make_response()  # Just send empty as 'ok'
    #@+node:felix.20210621233316.18: *5* server.import_any_file
    def import_any_file(self, param: Param) -> Response:
        """
        Import file(s) from array of file names
        """
        tag = 'import_any_file'
        c = self._check_c(param)
        ic = c.importCommands
        names = param.get('filenames')
        if names:
            g.chdir(names[0])
        if not names:
            raise ServerError(f"{tag}: No file names provided")
        # New in Leo 4.9: choose the type of import based on the extension.
        derived = [z for z in names if c.looksLikeDerivedFile(z)]
        others = [z for z in names if z not in derived]
        if derived:
            ic.importDerivedFiles(parent=c.p, paths=derived)
        for fn in others:
            junk, ext = g.os_path_splitext(fn)
            ext = ext.lower()  # #1522
            if ext.startswith('.'):
                ext = ext[1:]
            if ext == 'csv':
                ic.importMindMap([fn])
            elif ext in ('cw', 'cweb'):
                ic.importWebCommand([fn], "cweb")
            # Not useful. Use @auto x.json instead.
            # elif ext == 'json':
                # ic.importJSON([fn])
            elif fn.endswith('mm.html'):
                ic.importFreeMind([fn])
            elif ext in ('nw', 'noweb'):
                ic.importWebCommand([fn], "noweb")
            elif ext == 'more':
                # (Félix) leoImport Should be on c?
                c.leoImport.MORE_Importer(c).import_file(fn)  # #1522.
            elif ext == 'txt':
                # (Félix) import_txt_file Should be on c?
                # #1522: Create an @edit node.
                c.import_txt_file(c, fn)
            else:
                # Make *sure* that parent.b is empty.
                last = c.lastTopLevel()
                parent = last.insertAfter()
                parent.v.h = 'Imported Files'
                ic.importFilesCommand(
                    files=[fn],
                    parent=parent,
                    treeType='@auto',  # was '@clean'
                    # Experimental: attempt to use permissive section ref logic.
                )
        return self._make_response()  # Just send empty as 'ok'
    #@+node:felix.20220808210033.1: *4* server.export commands
    #@+node:felix.20220808211111.2: *5* server.export-headlines
    def export_headlines(self, param: Param) -> Response:
        """
        Export Outline (export headlines)
        """
        tag = 'export_headlines'
        c = self._check_c(param)
        if c and "name" in param:
            try:
                fileName = param.get("name")
                if fileName:
                    g.setGlobalOpenDir(fileName)
                    g.chdir(fileName)
                    c.importCommands.exportHeadlines(fileName)

            except Exception as e:
                print(f"{tag} Error while writing {param['name']}", flush=True)
                print(e, flush=True)

        return self._make_response()
    #@+node:felix.20220808211111.4: *5* server.flatten-outline
    def flatten_outline(self, param: Param) -> Response:
        """
        Flatten Selected Outline
        """
        tag = 'flatten_outline'
        c = self._check_c(param)
        if c and "name" in param:
            try:
                fileName = param.get("name")
                if fileName:
                    g.setGlobalOpenDir(fileName)
                    g.chdir(fileName)
                    c.importCommands.flattenOutline(fileName)
            except Exception as e:
                print(f"{tag} Error while writing {param['name']}", flush=True)
                print(e, flush=True)
        return self._make_response()
    #@+node:felix.20220808211111.5: *5* server.outline-to-cweb
    def outline_to_cweb(self, param: Param) -> Response:
        """
        Outline To CWEB
        """
        tag = 'outline_to_cweb'
        c = self._check_c(param)
        if c and "name" in param:
            try:
                fileName = param.get("name")
                if fileName:
                    g.setGlobalOpenDir(fileName)
                    g.chdir(fileName)
                    c.importCommands.outlineToWeb(fileName, "cweb")
            except Exception as e:
                print(f"{tag} Error while writing {param['name']}", flush=True)
                print(e, flush=True)
        return self._make_response()
    #@+node:felix.20220808211111.6: *5* server.outline-to-noweb

    def outline_to_noweb(self, param: Param) -> Response:
        """
        Outline To Noweb
        """
        tag = 'outline_to_noweb'
        c = self._check_c(param)
        if c and "name" in param:
            try:
                fileName = param.get("name")
                if fileName:
                    g.setGlobalOpenDir(fileName)
                    g.chdir(fileName)
                    c.importCommands.outlineToWeb(fileName, "noweb")
                    c.outlineToNowebDefaultFileName = fileName
            except Exception as e:
                print(f"{tag} Error while writing {param['name']}", flush=True)
                print(e, flush=True)
        return self._make_response()
    #@+node:felix.20220808211111.7: *5* server.remove-sentinels
    def remove_sentinels(self, param: Param) -> Response:
        """
        Remove Sentinels
        """
        tag = 'remove_sentinels'
        c = self._check_c(param)
        if c and "names" in param:
            try:
                names = param.get("names")
                if names:
                    g.chdir(names[0])
                    c.importCommands.removeSentinelsCommand(names)
            except Exception as e:
                print(f"{tag} Error while running remove_sentinels", flush=True)
                print(e, flush=True)
        return self._make_response()
    #@+node:felix.20220808211111.8: *5* server.weave
    def weave(self, param: Param) -> Response:
        """
        Weave
        """
        tag = 'weave'
        c = self._check_c(param)
        if c and "name" in param:
            try:
                fileName = param.get("name")
                if fileName:
                    g.setGlobalOpenDir(fileName)
                    g.chdir(fileName)
                    c.importCommands.weave(fileName)
            except Exception as e:
                print(f"{tag} Error while writing {param['name']}", flush=True)
                print(e, flush=True)
        return self._make_response()
    #@+node:felix.20220808221351.1: *5* server.write-file-from-node
    def write_file_from_node(self, param: Param) -> Response:
        """
        Write file from node
        """
        tag = 'write_file_from_node'
        c = self._check_c(param)
        if c and "name" in param:
            try:
                fileName = param.get("name")
                if fileName:
                    p = c.p
                    s = p.b
                    with open(fileName, 'w') as f:
                        g.chdir(fileName)
                        if s.startswith('@nocolor\n'):
                            s = s[len('@nocolor\n') :]
                        f.write(s)
                        f.flush()
                        g.blue('wrote:', fileName)
            except Exception as e:
                print(f"{tag} Error while writing {param['name']}", flush=True)
                print(e, flush=True)
        return self._make_response()
    #@+node:felix.20220810001309.1: *5* server.read-file-into-node
    def read_file_into_node(self, param: Param) -> Response:
        """
        Read a file into a single node.
        """
        tag = 'read_file_into_node'
        undoType = 'Read File Into Node'
        c = self._check_c(param)
        if c and "name" in param:
            try:
                fileName = param.get("name")
                if fileName:
                    s, e = g.readFileIntoString(fileName)
                    if s is None:
                        return None
                    g.chdir(fileName)
                    s = '@nocolor\n' + s
                    p = c.insertHeadline(op_name=undoType)
                    # New node does not need c.setHeadString. p.setHeadString is ok.
                    p.setHeadString('@read-file-into-node ' + fileName)
                    p.setBodyString(s)
            except Exception as err:
                print(f"{tag} Error while reading {param['name']}", flush=True)
                print(err, flush=True)
        return self._make_response()


    #@+node:felix.20220309010334.1: *4* server.nav commands
    #@+node:felix.20240107215312.1: *5* server.handle_unl
    def handle_unl(self, param: Param) -> Response:
        tag = 'handle_unl'
        c = self._check_c(param)
        unl = param.get('unl', '')
        try:
            if unl and g.isValidUrl(unl):
                # Part 2: handle the url
                p = c.p
                if not g.doHook("@url1", c=c, p=p, url=unl):
                    g.handleUrl(unl, c=c, p=p)
                g.doHook("@url2", c=c, p=p)
        except Exception as e:
            raise ServerError(f"{tag}: exception handling unl: {unl}: {e}")

        total = len(g.app.commanders())
        filename = c.fileName() if total else ""
        result = {"total": total, "filename": filename}
        return self._make_response(result)

    #@+node:felix.20220714000930.1: *5* server.chapter_main
    def chapter_main(self, param: Param) -> Response:
        tag = 'chapter_main'
        c = self._check_c(param)
        try:
            cc = c.chapterController
            cc.selectChapterByName('main')
        except Exception as e:
            raise ServerError(f"{tag}: exception selecting main chapter: {e}")
        return self._make_response()
    #@+node:felix.20220714000942.1: *5* server.chapter_select
    def chapter_select(self, param: Param) -> Response:
        tag = 'chapter_select'
        c = self._check_c(param)
        try:
            cc = c.chapterController
            chapter = param.get('name', 'main')
            cc.selectChapterByName(chapter)
        except Exception as e:
            raise ServerError(f"{tag}: exception selecting a chapter: {chapter}, {e}")

        return self._make_response()
    #@+node:felix.20220305211743.1: *5* server.nav_headline_search
    def nav_headline_search(self, param: Param) -> Response:
        """
        Performs nav 'headline only' search and fills results of go to panel
        Triggered by just typing in nav input box
        """
        tag = 'nav_headline_search'
        c = self._check_c(param)
        # Tag search override!
        try:
            scon: QuickSearchController = c.patched_quicksearch_controller
            inp = scon.navText
            if scon.isTag:
                scon.qsc_find_tags(inp)
            else:
                exp = inp.replace(" ", "*")
                scon.qsc_background_search(exp)
        except Exception as e:
            raise ServerError(f"{tag}: exception doing nav headline search: {e}")
        return self._make_response()


    #@+node:felix.20220305211828.1: *5* server.nav_clear
    def nav_clear(self, param: Param) -> Response:
        """
        Clear goto pane (nav/tag) content
        """
        tag = 'nav_clear'
        c = self._check_c(param)
        scon: QuickSearchController = c.patched_quicksearch_controller
        try:
            scon.clear()
        except Exception as e:
            raise ServerError(f"{tag}: exception doing nav clear: {e}")
        return self._make_response()

    #@+node:felix.20220925180823.1: *5* server.nav_search
    def nav_search(self, param: Param) -> Response:
        """
        Performs nav search and fills results of go to panel
        Triggered by pressing 'Enter' in the nav input box
        """
        tag = 'nav_search'
        c = self._check_c(param)
        scon: QuickSearchController = c.patched_quicksearch_controller
        # Tag search override!
        try:
            inp = scon.navText
            if scon.isTag:
                scon.qsc_find_tags(inp)
            else:
                scon.qsc_search(inp)
        except Exception as e:
            raise ServerError(f"{tag}: exception doing nav search: {e}")
        return self._make_response()


    #@+node:felix.20220305215239.1: *5* server.get_goto_panel
    def get_goto_panel(self, param: Param) -> Response:
        """
        Gets the content of the goto panel
        """
        tag = 'get_goto_panel'
        c = self._check_c(param)
        try:
            scon: QuickSearchController = c.patched_quicksearch_controller
            result: dict[str, Any] = {}
            navlist = [
                {
                    "key": k,
                    "h": scon.its[k][0]["label"],
                    "t": scon.its[k][0]["type"]
                } for k in scon.its.keys()
            ]
            result["navList"] = navlist
            result["messages"] = scon.lw
            result["navText"] = scon.navText
            result["navOptions"] = {"isTag": scon.isTag, "showParents": scon.showParents}
        except Exception as e:
            raise ServerError(f"{tag}: exception doing nav search: {e}")
        return self._make_response(result)

    #@+node:felix.20220309010558.1: *5* server.find_quick_timeline
    def find_quick_timeline(self, param: Param) -> Response:
        """Fill with nodes ordered by gnx."""
        c = self._check_c(param)
        scon: QuickSearchController = c.patched_quicksearch_controller
        scon.qsc_sort_by_gnx()
        return self._make_response()

    #@+node:felix.20220309010607.1: *5* server.find_quick_changed
    def find_quick_changed(self, param: Param) -> Response:
        # fill with list of all dirty nodes
        c = self._check_c(param)
        scon: QuickSearchController = c.patched_quicksearch_controller
        scon.qsc_find_changed()
        return self._make_response()
    #@+node:felix.20220309010647.1: *5* server.find_quick_history
    def find_quick_history(self, param: Param) -> Response:
        # fill with list from history
        c = self._check_c(param)
        scon: QuickSearchController = c.patched_quicksearch_controller
        scon.qsc_get_history()
        return self._make_response()
    #@+node:felix.20220309010704.1: *5* server.find_quick_marked
    def find_quick_marked(self, param: Param) -> Response:
        # fill with list of marked nodes
        c = self._check_c(param)
        scon: QuickSearchController = c.patched_quicksearch_controller
        scon.qsc_show_marked()
        return self._make_response()

    #@+node:felix.20220309205509.1: *5* server.goto_nav_entry
    def goto_nav_entry(self, param: Param) -> Response:
        # activate entry in scon.its
        tag = 'goto_nav_entry'
        c = self._check_c(param)
        scon: QuickSearchController = c.patched_quicksearch_controller
        try:
            it = param.get('key')
            scon.onSelectItem(it)
            focus = self._get_focus()
            result = {"focus": focus}
        except Exception as e:
            raise ServerError(f"{tag}: exception selecting a nav entry: {e}")
        return self._make_response(result)

    #@+node:felix.20210621233316.19: *4* server.search commands
    #@+node:felix.20210621233316.20: *5* server.get_search_settings
    def get_search_settings(self, param: Param) -> Response:
        """
        Gets search options
        """
        tag = 'get_search_settings'
        c = self._check_c(param)
        scon: QuickSearchController = c.patched_quicksearch_controller
        try:
            settings = c.findCommands.ftm.get_settings()
            # Use the "__dict__" of the settings, to be serializable as a json string.
            result = {"searchSettings": settings.__dict__}
            result["searchSettings"]["nav_text"] = scon.navText
            result["searchSettings"]["show_parents"] = scon.showParents
            result["searchSettings"]["is_tag"] = scon.isTag
            result["searchSettings"]["search_options"] = scon.searchOptions
        except Exception as e:
            raise ServerError(f"{tag}: exception getting search settings: {e}")
        return self._make_response(result)
    #@+node:felix.20210621233316.21: *5* server.set_search_settings
    def set_search_settings(self, param: Param) -> Response:
        """
        Sets search options. Init widgets and ivars from param.searchSettings
        """
        tag = 'set_search_settings'
        c = self._check_c(param)
        scon: QuickSearchController = c.patched_quicksearch_controller
        find = c.findCommands
        ftm = c.findCommands.ftm
        searchSettings = param.get('searchSettings')
        if not searchSettings:
            raise ServerError(f"{tag}: searchSettings object is missing")
        # Try to set the search settings
        try:
            # nav settings
            scon.navText = searchSettings.get('nav_text')
            scon.showParents = searchSettings.get('show_parents')
            scon.isTag = searchSettings.get('is_tag')
            scon.searchOptions = searchSettings.get('search_options')

            # Find/change text boxes.
            table = (
                ('find_findbox', 'find_text', ''),
                ('find_replacebox', 'change_text', ''),
            )
            for widget_ivar, setting_name, default in table:
                w = getattr(ftm, widget_ivar)
                s = searchSettings.get(setting_name) or default
                w.clear()
                w.insert(s)
            # Check boxes.
            table2 = (
                ('ignore_case', 'check_box_ignore_case'),
                ('mark_changes', 'check_box_mark_changes'),
                ('mark_finds', 'check_box_mark_finds'),
                ('pattern_match', 'check_box_regexp'),
                ('search_body', 'check_box_search_body'),
                ('search_headline', 'check_box_search_headline'),
                ('whole_word', 'check_box_whole_word'),
            )
            for setting_name, widget_ivar in table2:
                w = getattr(ftm, widget_ivar)
                val = searchSettings.get(setting_name)
                setattr(find, setting_name, val)
                if val != w.isChecked():
                    w.toggle()
            # Radio buttons
            table3 = (
                ('node_only', 'node_only', 'radio_button_node_only'),
                ('file_only', 'file_only', 'radio_button_file_only'),
                ('entire_outline', None, 'radio_button_entire_outline'),
                ('suboutline_only', 'suboutline_only', 'radio_button_suboutline_only'),
            )
            for setting_name, ivar, widget_ivar in table3:
                w = getattr(ftm, widget_ivar)
                val = searchSettings.get(setting_name, False)
                if ivar is not None:
                    assert hasattr(find, setting_name), setting_name
                    setattr(find, setting_name, val)
                    if val != w.isChecked():
                        w.toggle()
            # Ensure one radio button is set.
            w = ftm.radio_button_entire_outline
            nodeOnly = searchSettings.get('node_only', False)
            fileOnly = searchSettings.get('file_only', False)
            suboutlineOnly = searchSettings.get('suboutline_only', False)
            if not nodeOnly and not suboutlineOnly and not fileOnly:
                find.entire_outline = True
                if not w.isChecked():
                    w.toggle()
            else:
                find.entire_outline = False
                if w.isChecked():
                    w.toggle()
        except Exception as e:
            raise ServerError(f"{tag}: exception setting search settings: {e}")
        # Confirm by sending back the settings to the client
        try:
            settings = ftm.get_settings()
            # Use the "__dict__" of the settings, to be serializable as a json string.
            result = {"searchSettings": settings.__dict__}
        except Exception as e:
            raise ServerError(f"{tag}: exception getting search settings: {e}")
        return self._make_response(result)
    #@+node:felix.20230204161405.1: *5* server.interactive_search
    def interactive_search(self, param: Param) -> Response:
        """
        Interactive Search to implement search-backward, re-search, word-search. etc.
        """
        tag = 'interactive_search'
        c = self._check_c(param)
        fc = c.findCommands
        ftm = fc.ftm

        if "fromOutline" in param:
            fromOutline = param.get("fromOutline", False)
            fromBody = not fromOutline
            #
            focus = self._get_focus()
            inOutline = ("tree" in focus) or ("head" in focus)
            inBody = not inOutline
            #
            if fromOutline and inBody:
                fc.in_headline = True
            elif fromBody and inOutline:
                fc.in_headline = False
                c.bodyWantsFocus()
                c.bodyWantsFocusNow()

        backward = param.get("backward")
        regex = param.get("regex")
        word = param.get("word")
        find_pattern = param.get("findText")
        if backward:
            # Set flag for show_find_options.
            fc.reverse = True
            # Set flag for do_find_next().
            fc.request_reverse = True
        if regex:
            # Set flag for show_find_options.
            fc.pattern_match = True
            # Set flag for do_find_next().
            fc.request_pattern_match = True
        if word:
            # Set flag for show_find_options.
            fc.whole_word = True
            # Set flag for do_find_next().
            fc.request_whole_word = True

        fc.show_find_options()
        ftm.set_find_text(find_pattern)
        fc.update_find_list(find_pattern)
        fc.init_vim_search(find_pattern)
        # fc.init_in_headline()  # Handled by the 'fromOutline' param
        try:
            settings = fc.ftm.get_settings()
            p, pos, newpos = fc.do_find_next(settings)
        except Exception as e:
            raise ServerError(f"{tag}: Running interactive_search gave exception: {e}")
        #
        # get focus again after the operation
        focus = self._get_focus()
        selRange = self._get_sel_range()
        result = {"found": bool(p), "pos": pos, "range": selRange,
                    "newpos": newpos, "focus": focus}
        return self._make_response(result)
    #@+node:felix.20210621233316.22: *5* server.find_all
    def find_all(self, param: Param) -> Response:
        """Run Leo's find all command and return results."""
        tag = 'find_all'
        c = self._check_c(param)
        fc = c.findCommands
        try:
            settings = fc.ftm.get_settings()
            result = fc.do_find_all(settings)
        except Exception as e:
            raise ServerError(f"{tag}: exception running 'find all': {e}")
        focus = self._get_focus()
        return self._make_response({"found": result, "focus": focus})
    #@+node:felix.20210621233316.23: *5* server.find_next
    def find_next(self, param: Param) -> Response:
        """Run Leo's find-next command and return results."""
        tag = 'find_next'
        c = self._check_c(param)
        p = c.p
        fc = c.findCommands
        fromOutline = param.get("fromOutline", False)
        fromBody = not fromOutline
        #
        focus = self._get_focus()
        inOutline = ("tree" in focus) or ("head" in focus)
        inBody = not inOutline
        #
        if fromOutline and inBody:
            fc.in_headline = True
        elif fromBody and inOutline:
            fc.in_headline = False
            c.bodyWantsFocus()
            c.bodyWantsFocusNow()
        #
        # if fc.in_headline:
        #     ins = len(p.h)
        #     gui_w = c.edit_widget(p)
        #     gui_w.setSelectionRange(ins, ins, insert=ins)
        #
        try:
            settings = fc.ftm.get_settings()
            p, pos, newpos = fc.do_find_next(settings)
        except Exception as e:
            raise ServerError(f"{tag}: Running find operation gave exception: {e}")
        #
        # get focus again after the operation
        focus = self._get_focus()
        selRange = self._get_sel_range()
        result = {"found": bool(p), "pos": pos, "range": selRange,
                    "newpos": newpos, "focus": focus}
        return self._make_response(result)
    #@+node:felix.20210621233316.24: *5* server.find_previous
    def find_previous(self, param: Param) -> Response:
        """Run Leo's find-previous command and return results."""
        tag = 'find_previous'
        c = self._check_c(param)
        p = c.p
        fc = c.findCommands
        fromOutline = param.get("fromOutline", False)
        fromBody = not fromOutline
        #
        focus = self._get_focus()
        inOutline = ("tree" in focus) or ("head" in focus)
        inBody = not inOutline
        #
        if fromOutline and inBody:
            fc.in_headline = True
        elif fromBody and inOutline:
            fc.in_headline = False
            c.bodyWantsFocus()
            c.bodyWantsFocusNow()
        #
        # if fc.in_headline:
        #     gui_w = c.edit_widget(p)
        #     gui_w.setSelectionRange(0, 0, insert=0)
        #
        try:
            settings = fc.ftm.get_settings()
            p, pos, newpos = fc.do_find_prev(settings)
        except Exception as e:
            raise ServerError(f"{tag}: Running find operation gave exception: {e}")
        #
        # get focus again after the operation
        focus = self._get_focus()
        selRange = self._get_sel_range()
        result = {"found": bool(p), "pos": pos, "range": selRange,
                    "newpos": newpos, "focus": focus}
        return self._make_response(result)
    #@+node:felix.20210621233316.25: *5* server.replace
    def replace(self, param: Param) -> Response:
        """Run Leo's replace command and return results."""
        tag = 'replace'
        c = self._check_c(param)
        p = c.p
        fc = c.findCommands
        fromOutline = param.get("fromOutline", False)
        fromBody = not fromOutline
        #
        focus = self._get_focus()
        inOutline = ("tree" in focus) or ("head" in focus)
        inBody = not inOutline
        #
        if fromOutline and inBody:
            fc.in_headline = True
        elif fromBody and inOutline:
            fc.in_headline = False
            c.bodyWantsFocus()
            c.bodyWantsFocusNow()
        #
        try:
            settings = fc.ftm.get_settings()
            fc.init_ivars_from_settings(settings)
            fc.change_selection(p)
        except Exception as e:
            raise ServerError(f"{tag}: Running change operation gave exception: {e}")
        focus = self._get_focus()
        selRange = self._get_sel_range()
        result = {"found": True, "focus": focus, "range": selRange}
        # print("range: " + str(selRange[0]) + str(selRange[1]))
        return self._make_response(result)
    #@+node:felix.20210621233316.26: *5* server.replace_then_find
    def replace_then_find(self, param: Param) -> Response:
        """Run Leo's replace then find next command and return results."""
        tag = 'replace_then_find'
        c = self._check_c(param)
        p = c.p
        fc = c.findCommands
        fromOutline = param.get("fromOutline", False)
        fromBody = not fromOutline
        #
        focus = self._get_focus()
        inOutline = ("tree" in focus) or ("head" in focus)
        inBody = not inOutline
        #
        if fromOutline and inBody:
            fc.in_headline = True
        elif fromBody and inOutline:
            fc.in_headline = False
            c.bodyWantsFocus()
            c.bodyWantsFocusNow()
        #
        try:
            settings = fc.ftm.get_settings()
            fc.init_ivars_from_settings(settings)
            result = False
            if fc.change_selection(p):
                result = bool(fc.do_find_next(settings))
        except Exception as e:
            raise ServerError(f"{tag}: Running change operation gave exception: {e}")
        focus = self._get_focus()
        selRange = self._get_sel_range()
        # print("range: " + str(selRange[0]) + str(selRange[1]))
        return self._make_response({"found": result, "focus": focus, "range": selRange})
    #@+node:felix.20210621233316.27: *5* server.replace_all
    def replace_all(self, param: Param) -> Response:
        """Run Leo's replace all command and return results."""
        tag = 'replace_all'
        c = self._check_c(param)
        fc = c.findCommands
        try:
            settings = fc.ftm.get_settings()
            result = fc.do_change_all(settings)
        except Exception as e:
            raise ServerError(f"{tag}: Running change operation gave exception: {e}")
        focus = self._get_focus()
        return self._make_response({"found": result, "focus": focus})
    #@+node:felix.20210621233316.28: *5* server.clone_find_all
    def clone_find_all(self, param: Param) -> Response:
        """Run Leo's clone-find-all command and return results."""
        tag = 'clone_find_all'
        c = self._check_c(param)
        fc = c.findCommands
        try:
            settings = fc.ftm.get_settings()
            result = fc.do_clone_find_all(settings)
        except Exception as e:
            raise ServerError(f"{tag}: Running clone find operation gave exception: {e}")
        focus = self._get_focus()
        return self._make_response({"found": result, "focus": focus})
    #@+node:felix.20210621233316.29: *5* server.clone_find_all_flattened
    def clone_find_all_flattened(self, param: Param) -> Response:
        """Run Leo's clone-find-all-flattened command and return results."""
        tag = 'clone_find_all_flattened'
        c = self._check_c(param)
        fc = c.findCommands
        try:
            settings = fc.ftm.get_settings()
            result = fc.do_clone_find_all_flattened(settings)
        except Exception as e:
            raise ServerError(f"{tag}: Running clone find operation gave exception: {e}")
        focus = self._get_focus()
        return self._make_response({"found": result, "focus": focus})
    #@+node:felix.20210621233316.30: *5* server.find_var
    def find_var(self, param: Param) -> Response:
        """Run Leo's find-var command and return results."""
        tag = 'find_var'
        c = self._check_c(param)
        fc = c.findCommands
        try:
            fc.find_var()
        except Exception as e:
            raise ServerError(f"{tag}: Running find symbol definition gave exception: {e}")
        focus = self._get_focus()
        return self._make_response({"found": True, "focus": focus})
    #@+node:felix.20210722010004.1: *5* server.clone_find_all_flattened_marked
    def clone_find_all_flattened_marked(self, param: Param) -> Response:
        """Run Leo's clone-find-all-flattened-marked command."""
        tag = 'clone_find_all_flattened_marked'
        c = self._check_c(param)
        fc = c.findCommands
        try:
            fc.do_find_marked(flatten=True)
        except Exception as e:
            raise ServerError(f"{tag}: Running find symbol definition gave exception: {e}")
        focus = self._get_focus()
        return self._make_response({"found": True, "focus": focus})
    #@+node:felix.20210722010005.1: *5* server.clone_find_all_marked
    def clone_find_all_marked(self, param: Param) -> Response:
        """Run Leo's clone-find-all-marked command """
        tag = 'clone_find_all_marked'
        c = self._check_c(param)
        fc = c.findCommands
        try:
            fc.do_find_marked(flatten=False)
        except Exception as e:
            raise ServerError(f"{tag}: Running find symbol definition gave exception: {e}")
        focus = self._get_focus()
        return self._make_response({"found": True, "focus": focus})
    #@+node:felix.20210621233316.31: *5* server.find_def
    def find_def(self, param: Param) -> Response:
        """Run Leo's find-def command and return results."""
        tag = 'find_def'
        c = self._check_c(param)
        fc = c.findCommands
        try:
            fc.find_def()
        except Exception as e:
            raise ServerError(f"{tag}: Running find symbol definition gave exception: {e}")
        focus = self._get_focus()
        return self._make_response({"found": True, "focus": focus})
    #@+node:felix.20210621233316.32: *5* server.goto_global_line
    def goto_global_line(self, param: Param) -> Response:
        """Run Leo's goto-global-line command and return results."""
        tag = 'goto_global_line'
        c = self._check_c(param)
        gc = c.gotoCommands
        line = param.get('line', 1)
        try:
            p, junk_offset = gc.find_file_line(n=int(line))
        except Exception as e:
            raise ServerError(f"{tag}: Running goto-global-line gave exception: {e}")
        focus = self._get_focus()
        return self._make_response({"found": bool(p), "focus": focus})
    #@+node:felix.20210621233316.33: *5* server.clone_find_tag
    def clone_find_tag(self, param: Param) -> Response:
        """Run Leo's clone-find-tag command and return results."""
        tag = 'clone_find_tag'
        c = self._check_c(param)
        fc = c.findCommands
        tag_param = param.get("tag")
        if not tag_param:  # pragma: no cover
            raise ServerError(f"{tag}: no tag")
        settings = fc.ftm.get_settings()
        if self.log_flag:  # pragma: no cover
            g.printObj(settings, tag=f"{tag}: settings for {c.shortFileName()}")
        n, p = fc.do_clone_find_tag(tag_param)
        if self.log_flag:  # pragma: no cover
            g.trace("tag: {tag_param} n: {n} p: {p and p.h!r}")
            print('', flush=True)
        return self._make_response({"n": n})
    #@+node:felix.20210621233316.34: *5* server.tag_children
    def tag_children(self, param: Param) -> Response:
        """Run Leo's tag-children command"""
        # This is not a find command!
        tag = 'tag_children'
        c = self._check_c(param)
        fc = c.findCommands
        tag_param = param.get("tag")
        if tag_param is None:  # pragma: no cover
            raise ServerError(f"{tag}: no tag")
        # Unlike find commands, do_tag_children does not use a settings dict.
        fc.do_tag_children(c.p, tag_param)
        return self._make_response()
    #@+node:felix.20220313215348.1: *5* server.tag_node
    def tag_node(self, param: Param) -> Response:
        """Set tag on selected node"""
        # This is not a find command!
        tag = 'tag_node'
        c = self._check_c(param)
        tag_param = param.get("tag")
        if tag_param is None:  # pragma: no cover
            raise ServerError(f"{tag}: no tag")
        try:
            p = self._get_p(param)
            tc = getattr(c, 'theTagController', None)
            if not tc:
                print("In tag_node. No 'theTagController' on commander.")
                print("Make sure nodetags.py is an active plugin in myLeoSettings.leo")
                print("", flush=True)
            if hasattr(tc, 'add_tag'):
                tc.add_tag(p, tag_param)
        except Exception as e:
            raise ServerError(f"{tag}: Running tag_node gave exception: {e}")
        return self._make_response()
    #@+node:felix.20220313215353.1: *5* server.remove_tag
    def remove_tag(self, param: Param) -> Response:
        """Remove specific tag on selected node"""
        # This is not a find command!
        tag = 'remove_tag'
        c = self._check_c(param)
        tag_param = param.get("tag")
        if tag_param is None:  # pragma: no cover
            raise ServerError(f"{tag}: no tag")
        try:
            p = self._get_p(param)
            v = p.v
            tc = getattr(c, 'theTagController', None)
            if not tc:
                print("In remove_tag. No 'theTagController' on commander.")
                print("Make sure nodetags.py is an active plugin in myLeoSettings.leo")
                print("", flush=True)
            if hasattr(tc, 'remove_tag'):
                if v.u and '__node_tags' in v.u:
                    tc.remove_tag(p, tag_param)
        except Exception as e:
            raise ServerError(f"{tag}: Running remove_tag gave exception: {e}")
        return self._make_response()
    #@+node:felix.20220313220807.1: *5* server.remove_tags
    def remove_tags(self, param: Param) -> Response:
        """Remove all tags on selected node"""
        # This is not a find command!
        tag = 'remove_tags'
        c = self._check_c(param)
        try:
            p = self._get_p(param)
            v = p.v
            if v.u and '__node_tags' in v.u:
                del v.u['__node_tags']
                tc = getattr(c, 'theTagController', None)
                if not tc:
                    print("In remove_tags. No 'theTagController' on commander.")
                    print("Make sure nodetags.py is an active plugin in myLeoSettings.leo")
                    print("", flush=True)
                if hasattr(tc, 'initialize_taglist'):
                    tc.initialize_taglist()  # reset tag list: some may have been removed
        except Exception as e:
            raise ServerError(f"{tag}: Running remove_tags gave exception: {e}")
        return self._make_response()
    #@+node:felix.20210621233316.35: *4* server.getter commands
    #@+node:felix.20210621233316.36: *5* server.get_all_open_commanders
    def get_all_open_commanders(self, param: Param) -> Response:
        """Return array describing each commander in g.app.commanders()."""
        files = [
            {
                "id": id(c),
                "changed": c.isChanged(),
                "name": c.fileName(),
                "selected": c == self.c,
            } for c in g.app.commanders()
        ]
        return self._make_minimal_response({"files": files})
    #@+node:felix.20210621233316.37: *5* server.get_all_positions
    def get_all_positions(self, param: Param) -> Response:
        """
        Return a list of position data for all positions.

        Useful as a sanity check for debugging.
        """
        c = self._check_c(param)
        result = [
            self._get_position_d(p, c) for p in c.all_positions(copy=False)
        ]
        return self._make_minimal_response({"position-data-list": result})
    #@+node:felix.20220617184559.1: *5* server.get_structure
    def get_structure(self, param: Param) -> Response:
        """
        Returns an array of ap's, the direct descendants of the hidden root node.
        Each having required 'children' array, to give the whole structure of ap's.
        """
        c = self._check_c(param)
        result = []
        p = c.rootPosition()  # first child of hidden root node as first item in top array
        while p:
            result.append(self._get_position_d(p, c, includeChildren=True))
            p.moveToNodeAfterTree()
        # return selected node either ways
        return self._make_minimal_response({"structure": result})

    #@+node:felix.20210621233316.38: *5* server.get_all_gnx
    def get_all_gnx(self, param: Param) -> Response:
        """Get gnx array from all unique nodes"""
        if self.log_flag:  # pragma: no cover
            print('\nget_all_gnx\n', flush=True)
        c = self._check_c(param)
        all_gnx = [p.v.gnx for p in c.all_unique_positions(copy=False)]
        return self._make_minimal_response({"gnx": all_gnx})
    #@+node:felix.20221031010236.1: *5* server.get_branch
    def get_branch(self, param: Param) -> Response:
        """
        Return the branch and commit of the currently opened document, if any.
        """
        c = self._check_c(param)
        fileName = c.fileName()
        branch, commit = g.gitInfoForFile(fileName)
        return self._make_minimal_response({"branch": branch, "commit": commit})
    #@+node:felix.20210621233316.39: *5* server.get_body
    def get_body(self, param: Param) -> Response:
        """
        Return the body content body specified via GNX.
        """
        c = self._check_c(param)
        gnx = param.get("gnx")
        v = c.fileCommands.gnxDict.get(gnx)  # vitalije
        body = ""
        if v:
            body = v.b or ""
        # Support asking for unknown gnx when client switches rapidly
        return self._make_minimal_response({"body": body})
    #@+node:felix.20210621233316.40: *5* server.get_body_length
    def get_body_length(self, param: Param) -> Response:
        """
        Return p.b's length in bytes, where p is c.p if param["ap"] is missing.
        """
        c = self._check_c(param)
        gnx = param.get("gnx")
        w_v = c.fileCommands.gnxDict.get(gnx)  # vitalije
        if w_v:
            # Length in bytes, not just by character count.
            return self._make_minimal_response({"len": len(w_v.b.encode('utf-8'))})
        return self._make_minimal_response({"len": 0})  # empty as default
    #@+node:felix.20210621233316.41: *5* server.get_body_states
    def get_body_states(self, param: Param) -> Response:
        """
        Return body data for p, where p is c.p if param["ap"] is missing.
        The cursor positions are given as {"line": line, "col": col, "index": i}
        with line and col along with a redundant index for convenience and flexibility.
        """
        c = self._check_c(param)
        p = self._get_p(param)
        wrapper = c.frame.body.wrapper

        def row_col_wrapper_dict(i: int) -> dict:
            if not i:
                i = 0  # prevent none type
            # BUG: this uses current selection wrapper only, use
            # g.convertPythonIndexToRowCol instead !
            line, col = wrapper.toPythonIndexRowCol(i)
            return {"line": line, "col": col, "index": i}

        def row_col_pv_dict(i: int, s: str) -> dict:
            if not i:
                i = 0  # prevent none type
            # BUG: this uses current selection wrapper only, use
            # g.convertPythonIndexToRowCol instead !
            line, col = g.convertPythonIndexToRowCol(s, i)
            return {"line": line, "col": col, "index": i}

        # Handle @killcolor and @nocolor-node when looking for language
        if c.frame.body.colorizer.useSyntaxColoring(p):
            # Get the language.
            aList = g.get_directives_dict_list(p)
            d = g.scanAtCommentAndAtLanguageDirectives(aList)
            language = (
                d and d.get('language')
                or g.getLanguageFromAncestorAtFileNode(p)
                or c.config.getLanguage('target-language')
                or 'plain'
            )
        else:
            # No coloring at all for this node.
            language = 'plain'

        # Get the body wrap state
        wrap = g.scanAllAtWrapDirectives(c, p)
        tabWidth = g.scanAllAtTabWidthDirectives(c, p)
        if not isinstance(tabWidth, int):
            tabWidth = False

        # get values from wrapper if it's the selected node.
        if c.p.v.gnx == p.v.gnx:
            insert = wrapper.getInsertPoint()
            try:
                start, end = wrapper.getSelectionRange(True)
            except Exception:  # pragma: no cover
                start, end = 0, 0
            scroll = wrapper.getYScrollPosition()
            states = {
                'language': language.lower(),
                'wrap': wrap,
                'tabWidth': tabWidth,
                'selection': {
                    "gnx": p.v.gnx,
                    "scroll": scroll,
                    "insert": row_col_wrapper_dict(insert),
                    "start": row_col_wrapper_dict(start),
                    "end": row_col_wrapper_dict(end)
                }
            }
        else:  # pragma: no cover
            insert = p.v.insertSpot
            start = p.v.selectionStart
            end = p.v.selectionStart + p.v.selectionLength
            scroll = p.v.scrollBarSpot
            states = {
                'language': language.lower(),
                'wrap': wrap,
                'tabWidth': tabWidth,
                'selection': {
                    "gnx": p.v.gnx,
                    "scroll": scroll,
                    "insert": row_col_pv_dict(insert, p.v.b),
                    "start": row_col_pv_dict(start, p.v.b),
                    "end": row_col_pv_dict(end, p.v.b)
                }
            }
        return self._make_minimal_response(states)
    #@+node:felix.20220714001051.1: *5* server.get_chapters
    def get_chapters(self, param: Param) -> Response:
        c = self._check_c(param)
        cc = c.chapterController
        chapters = []
        if cc:
            chapters = cc.setAllChapterNames()
        return self._make_minimal_response({"chapters": chapters})
    #@+node:felix.20210621233316.42: *5* server.get_children
    def get_children(self, param: Param) -> Response:
        """
        Return the node data for children of p,
        where p is root if param.ap is missing
        """
        c = self._check_c(param)
        children = []  # default empty array
        if param.get("ap"):
            # Maybe empty param, for tree-root children(s).
            # Call _get_optional_p:
            # we don't want c.p. after switch to another document while refreshing.
            p = self._get_optional_p(param)
            if p and p.hasChildren():
                children = [self._get_position_d(child, c) for child in p.children()]
        else:
            if c.hoistStack:
                topHoistPos = c.hoistStack[-1].p
                if g.match_word(topHoistPos.h, 0, '@chapter'):
                    children = [self._get_position_d(child, c) for child in topHoistPos.children()]
                else:
                    # start hoisted tree with single hoisted root node
                    children = [self._get_position_d(topHoistPos, c)]
            else:
                # this outputs all Root Children
                children = [self._get_position_d(child, c) for child in self._yieldAllRootChildren(c)]
        return self._make_minimal_response({"children": children})
    #@+node:felix.20210621233316.43: *5* server.get_focus
    def get_focus(self, param: Param) -> Response:
        """
        Return a representation of the focused widget,
        one of ("body", "tree", "headline", repr(the_widget)).
        """
        return self._make_minimal_response({"focus": self._get_focus()})
    #@+node:felix.20210621233316.44: *5* server.get_parent
    def get_parent(self, param: Param) -> Response:
        """
        Return the node data for the parent of position p,
        where p is c.p if param["ap"] is missing.
        """
        c = self._check_c(param)
        p = self._get_p(param)
        parent: Optional[Position] = p.parent()
        if c.hoistStack:
            topHoistPos = c.hoistStack[-1].p
            if parent == topHoistPos:
                parent = None
        data = self._get_position_d(parent, c) if parent else None
        return self._make_minimal_response({"node": data})
    #@+node:felix.20210621233316.45: *5* server.get_position_data
    def get_position_data(self, param: Param) -> Response:
        """
        Return a dict of position data for all positions.

        Useful as a sanity check for debugging.
        """
        c = self._check_c(param)
        result = {
            p.v.gnx: self._get_position_d(p, c)
                for p in c.all_unique_positions(copy=False)
        }
        return self._make_minimal_response({"position-data-dict": result})
    #@+node:felix.20240302203609.1: *5* server.get_recent_files
    def get_recent_files(self, param: Param) -> Response:
        """
        Return the recent files list
        """
        try:
            recentFiles = g.app.recentFilesManager.recentFiles
        except Exception:  # pragma: no cover
            recentFiles = []
        return self._make_minimal_response({"files": recentFiles})
    #@+node:felix.20210621233316.46: *5* server.get_ua
    def get_ua(self, param: Param) -> Response:
        """Return p.v.u, making sure it can be serialized."""
        self._check_c(param)
        p = self._get_p(param)
        try:
            ua = {"ua": p.v.u}
            json.dumps(ua, separators=(',', ':'), cls=SetEncoder)
            response = {"ua": p.v.u}
        except Exception:  # pragma: no cover
            response = {"ua": repr(p.v.u)}
        # _make_response adds all the cheap redraw data.
        return self._make_minimal_response(response)
    #@+node:felix.20210621233316.48: *5* server.get_ui_states
    def get_ui_states(self, param: Param) -> Response:
        """
        Return the enabled/disabled UI states for the open commander, or defaults if None.
        """
        tag = 'get_ui_states'
        c = self._check_c(param)
        p = self._get_p(param)

        w_canHoist = True
        if c.hoistStack:
            bunch = c.hoistStack[len(c.hoistStack) - 1]
            w_ph = bunch.p
            if p == w_ph:
            # p is already the hoisted node
                w_canHoist = False
        else:
            # not hoisted, was it the single top child of the real root?
            if c.rootPosition() == p and len(c.hiddenRootNode.children) == 1:
                w_canHoist = False

        inChapter = False
        topHoistChapter = False
        if c.config.getBool('use-chapters') and c.chapterController:
            cc = c.chapterController
            inChapter = cc.inChapter()
            if c.hoistStack:
                bunch = c.hoistStack[len(c.hoistStack) - 1]
                if g.match_word(bunch.p.h, 0, '@chapter'):
                    topHoistChapter = True

        try:
            states = {
                "changed": c and c.changed,
                "canUndo": c and c.canUndo(),
                "canRedo": c and c.canRedo(),
                "canGoBack": c and c.nodeHistory.beadPointer > 0,
                "canGoNext": c and c.nodeHistory.beadPointer + 1 < len(c.nodeHistory.beadList),
                "canDemote": c and c.canDemote(),
                "canPromote": c and c.canPromote(),
                "canDehoist": c and c.canDehoist(),
                "canHoist": w_canHoist,
                "inChapter": inChapter,
                "topHoistChapter": topHoistChapter
            }
        except Exception as e:  # pragma: no cover
            raise ServerError(f"{tag}: Exception setting state: {e}")
        return self._make_minimal_response({"states": states})
    #@+node:felix.20211210213603.1: *5* server.get_undos
    def get_undos(self, param: Param) -> Response:
        """Return list of undo operations"""
        c = self._check_c(param)
        undoer = c.undoer
        undos = []
        try:
            for bead in undoer.beads:
                undos.append(bead.undoType)
            response = {"bead": undoer.bead, "undos": undos}
        except Exception:  # pragma: no cover
            response = {"bead": 0, "undos": []}
        # _make_response adds all the cheap redraw data.
        return self._make_minimal_response(response)
    #@+node:felix.20240213234032.1: *5* server.get_unl
    def get_unl(self, param: Param) -> Response:
        """
        Return UNL for specific position, or currently selected node.
        This defaults to using the normal status bar UNL indicator method
        unless 'short' or 'legacy' boolean parameters are used.
        """
        c = self._check_c(param)
        p = self._get_p(param)
        if not p or not p.v:
            response = {"unl": ""}
            return self._make_minimal_response(response)

        # Set a method to get an UNL: either specific, or the default status-bar method.
        if 'short' in param or 'legacy' in param:
            # Parameter given: Use a specific method.
            short = param.get('short', True)
            legacy = param.get('legacy', False)
            if short:
                method = p.get_short_legacy_UNL if legacy else p.get_short_gnx_UNL
            else:
                method = p.get_full_legacy_UNL if legacy else p.get_full_gnx_UNL
        else:
            # No parameter: (UNL for status bar): use same logic as original Leo.
            kind = c.config.getString('unl-status-kind') or ''
            method = p.get_legacy_UNL if kind.lower() == 'legacy' else p.get_UNL

        # Get the unl.
        try:
            unl = method()
        except Exception:  # pragma: no cover
            unl = ""

        # Return the response.
        response = {"unl": unl}
        return self._make_minimal_response(response)

    #@+node:felix.20210621233316.49: *4* server.node commands
    #@+node:felix.20210621233316.50: *5* server.clone_node
    def clone_node(self, param: Param) -> Response:
        """
        Clone a node.
        Try to keep selection, then return the selected node that remains.
        """
        c = self._check_c(param)
        p = self._get_p(param)
        if p == c.p:
            c.clone()
        else:
            oldPosition = c.p
            c.selectPosition(p)
            c.clone()
            if c.positionExists(oldPosition):
                c.selectPosition(oldPosition)
            else:
                oldPosition._childIndex = oldPosition._childIndex + 1
                # Try again with childIndex incremented
                if c.positionExists(oldPosition):
                    # additional try with lowered childIndex
                    c.selectPosition(oldPosition)

        # return selected node either ways
        return self._make_response()

    #@+node:felix.20210621233316.51: *5* server.contract_node
    def contract_node(self, param: Param) -> Response:
        """
        Contract (Collapse) the node at position p, where p is c.p if p is missing.
        """
        p = self._get_p(param)
        p.contract()
        return self._make_response()
    #@+node:felix.20210621233316.52: *5* server.copy_node
    def copy_node(self, param: Param) -> Response:  # pragma: no cover (too dangerous, for now)
        """
        Copy a node, don't select it.
        Also supports 'asJSON' parameter to get as JSON
        Try to keep selection, then return the selected node.
        """
        c = self._check_c(param)
        p = self._get_p(param)

        copyMethod = c.copyOutline
        if "asJSON" in param:
            if param["asJSON"]:
                copyMethod = c.copyOutlineAsJSON

        if p == c.p:
            s = copyMethod()
        else:
            oldPosition = c.p  # not same node, save position to possibly return to
            c.selectPosition(p)
            s = copyMethod()
            if c.positionExists(oldPosition):
                # select if old position still valid
                c.selectPosition(oldPosition)
        g.app.gui.replaceClipboardWith(s)
        return self._make_response({"string": s})

    #@+node:felix.20220815193758.1: *5* server.copy_node_as_json
    def copy_node_as_json(self, param: Param) -> Response:  # pragma: no cover (too dangerous, for now)
        """
        Copy a node as JSON, don't select it.
        Also supports 'asJSON' parameter to get as JSON
        Try to keep selection, then return the selected node.
        """
        c = self._check_c(param)
        p = self._get_p(param)
        if p == c.p:
            s = c.copyOutlineAsJSON()
        else:
            oldPosition = c.p  # not same node, save position to possibly return to
            c.selectPosition(p)
            s = c.copyOutlineAsJSON()
            if c.positionExists(oldPosition):
                # select if old position still valid
                c.selectPosition(oldPosition)
        g.app.gui.replaceClipboardWith(s)
        return self._make_response({"string": s})

    #@+node:felix.20220222172507.1: *5* server.cut_node
    def cut_node(self, param: Param) -> Response:  # pragma: no cover (too dangerous, for now)
        """
        Cut a node, don't select it.
        Try to keep selection, then return the selected node that remains.
        """
        c = self._check_c(param)
        p = self._get_p(param)
        copyMethod = c.copyOutline
        if "asJSON" in param:
            if param["asJSON"]:
                copyMethod = c.copyOutlineAsJSON
        if p == c.p:
            s = copyMethod()
            c.cutOutline()  # already on this node, so cut it
        else:
            oldPosition = c.p  # not same node, save position to possibly return to
            c.selectPosition(p)
            s = copyMethod()
            c.cutOutline()
            if c.positionExists(oldPosition):
                # select if old position still valid
                c.selectPosition(oldPosition)
            else:
                oldPosition._childIndex = oldPosition._childIndex - 1
                # Try again with childIndex decremented
                if c.positionExists(oldPosition):
                    # additional try with lowered childIndex
                    c.selectPosition(oldPosition)
        g.app.gui.replaceClipboardWith(s)
        return self._make_response({"string": s})
    #@+node:felix.20210621233316.53: *5* server.delete_node
    def delete_node(self, param: Param) -> Response:  # pragma: no cover (too dangerous, for now)
        """
        Delete a node, don't select it.
        Try to keep selection, then return the selected node that remains.
        """
        c = self._check_c(param)
        p = self._get_p(param)
        if p == c.p:
            c.deleteOutline()  # already on this node, so cut it
        else:
            oldPosition = c.p  # not same node, save position to possibly return to
            c.selectPosition(p)
            c.deleteOutline()
            if c.positionExists(oldPosition):
                # select if old position still valid
                c.selectPosition(oldPosition)
            else:
                oldPosition._childIndex = oldPosition._childIndex - 1
                # Try again with childIndex decremented
                if c.positionExists(oldPosition):
                    # additional try with lowered childIndex
                    c.selectPosition(oldPosition)
        return self._make_response()
    #@+node:felix.20210621233316.54: *5* server.expand_node
    def expand_node(self, param: Param) -> Response:
        """
        Expand the node at position p, where p is c.p if p is missing.
        """
        p = self._get_p(param)
        p.expand()
        return self._make_response()
    #@+node:felix.20210621233316.55: *5* server.insert_node
    def insert_node(self, param: Param) -> Response:
        """
        Insert a node at given node. If a position is given
        that is not the current position, re-select the original position.
        """
        c = self._check_c(param)
        p = self._get_p(param)

        if p == c.p:
            c.insertHeadline()  # Handles undo, sets c.p
        else:
            oldPosition = c.p
            c.selectPosition(p)
            c.insertHeadline()  # Handles undo, sets c.p
            if c.positionExists(oldPosition):
                c.selectPosition(oldPosition)
            else:
                oldPosition._childIndex = oldPosition._childIndex + 1
                # Try again with childIndex incremented
                if c.positionExists(oldPosition):
                    # additional try with lowered childIndex
                    c.selectPosition(oldPosition)

        return self._make_response()
    #@+node:felix.20210703021435.1: *5* server.insert_child_node
    def insert_child_node(self, param: Param) -> Response:
        """
        Insert a child node at given node. If a position is given
        that is not the current position, re-select the original position.
        """
        c = self._check_c(param)
        p = self._get_p(param)

        if p == c.p:
            c.insertHeadline(op_name='Insert Child', as_child=True)  # Handles undo, sets c.p
        else:
            oldPosition = c.p
            c.selectPosition(p)
            c.insertHeadline(op_name='Insert Child', as_child=True)  # Handles undo, sets c.p
            if c.positionExists(oldPosition):
                c.selectPosition(oldPosition)
        # return selected node either ways
        return self._make_response()
    #@+node:felix.20210621233316.56: *5* server.insert_named_node
    def insert_named_node(self, param: Param) -> Response:
        """
        Insert a node at given node, set its headline. If a position is given
        that is not the current position, re-select the original position.
        """
        c = self._check_c(param)
        p = self._get_p(param)
        oldPosition: Optional[Position] = None if p == c.p else c.p

        newHeadline = param.get('name')
        bunch = c.undoer.beforeInsertNode(p)
        newNode = p.insertAfter()
        # Set this node's new headline
        newNode.h = newHeadline
        newNode.setDirty()
        c.setChanged()
        c.undoer.afterInsertNode(newNode, 'Insert Node', bunch)

        c.selectPosition(newNode)
        if oldPosition:
            if c.positionExists(oldPosition):
                c.selectPosition(oldPosition)
            else:
                oldPosition._childIndex = oldPosition._childIndex + 1
                # Try again with childIndex incremented
                if c.positionExists(oldPosition):
                    # additional try with lowered childIndex
                    c.selectPosition(oldPosition)

        c.setChanged()
        return self._make_response()
    #@+node:felix.20210703021441.1: *5* server.insert_child_named_node
    def insert_child_named_node(self, param: Param) -> Response:
        """
        Insert a child node at given node, set its headline, select it and finally return it
        """
        c = self._check_c(param)
        p = self._get_p(param)
        newHeadline = param.get('name')
        bunch = c.undoer.beforeInsertNode(p)
        if c.config.getBool('insert-new-nodes-at-end'):
            newNode = p.insertAsLastChild()
        else:
            newNode = p.insertAsNthChild(0)
        # Set this node's new headline
        newNode.h = newHeadline
        newNode.setDirty()
        c.setChanged()
        c.undoer.afterInsertNode(
            newNode, 'Insert Node', bunch)
        c.selectPosition(newNode)
        return self._make_response()
    #@+node:felix.20220616010755.1: *5* server.scroll_top
    def scroll_top(self, param: Param) -> Response:
        """
        Utility method for connected clients to simulate scroll to the top
        """
        c = self._check_c(param)
        p = c.firstVisible()
        if p:
            c.treeSelectHelper(p)
        return self._make_response()
    #@+node:felix.20220616010756.1: *5* server.scroll_bottom
    def scroll_bottom(self, param: Param) -> Response:
        """
        Utility method for connected clients to simulate scroll to bottom
        """
        c = self._check_c(param)
        p = c.lastVisible()
        if p:
            c.treeSelectHelper(p)
        return self._make_response()
    #@+node:felix.20210621233316.57: *5* server.page_down
    def page_down(self, param: Param) -> Response:
        """
        Tree page-down command:
        If no 'n steps' are passed, this selects last sibling or next vis if already last sibling.
        Otherwise selects a node "n" steps down in the tree to simulate page down.
        """
        c = self._check_c(param)
        n = param.get("n", 0)
        if n:
            for _z in range(n):
                c.selectVisNext()
        else:
            parent = c.p.parent()
            if not parent:
                c.goToLastSibling()
                return self._make_response()

            siblings = [* parent.children(copy=True)]
            lastSibling = siblings[-1]
            if lastSibling == c.p:
                c.selectVisNext()  # already last sibling
            else:
                c.goToLastSibling()

        return self._make_response()
    #@+node:felix.20210621233316.58: *5* server.page_up
    def page_up(self, param: Param) -> Response:
        """
        Tree page-up command:
        If no 'n steps' are passed, this selects first sibling, or previous vis if already first sibling.
        Otherwise selects a node "N" steps up in the tree to simulate page up.
        """
        c = self._check_c(param)
        n = param.get("n", 0)
        if n:
            for _z in range(n):
                c.selectVisBack()
        else:
            parent = c.p.parent()
            if not parent:
                c.goToFirstSibling()
                return self._make_response()

            siblings = [* parent.children(copy=True)]
            firstSibling = siblings[0]
            if firstSibling == c.p:
                c.selectVisBack()  # already first sibling
            else:
                c.goToFirstSibling()

        return self._make_response()
    #@+node:felix.20220222173659.1: *5* server.paste_node
    def paste_node(self, param: Param) -> Response:
        """
        Pastes a node,
        Try to keep selection, then return the selected node.
        """
        tag = 'paste_node'
        c = self._check_c(param)
        p = self._get_p(param)
        s = param.get('name')
        if s is None:  # pragma: no cover
            raise ServerError(f"{tag}: no string given")
        g.app.gui.replaceClipboardWith(s)
        if p == c.p:
            c.pasteOutline(s=s)
        else:
            oldPosition = c.p  # not same node, save position to possibly return to
            c.selectPosition(p)
            c.pasteOutline(s=s)
            if c.positionExists(oldPosition):
                # select if old position still valid
                c.selectPosition(oldPosition)
            else:
                oldPosition._childIndex = oldPosition._childIndex + 1
                # Try again with childIndex incremented
                if c.positionExists(oldPosition):
                    # additional try with higher childIndex
                    c.selectPosition(oldPosition)
        return self._make_response()
    #@+node:felix.20220222173707.1: *5* server.paste_as_clone_node
    def paste_as_clone_node(self, param: Param) -> Response:
        """
        Pastes a node as a clone,
        Try to keep selection, then return the selected node.
        """
        tag = 'paste_as_clone_node'
        c = self._check_c(param)
        p = self._get_p(param)
        s = param.get('name')
        if s is None:  # pragma: no cover
            raise ServerError(f"{tag}: no string given")
        g.app.gui.replaceClipboardWith(s)
        if p == c.p:
            c.pasteOutlineRetainingClones(s=s)
        else:
            oldPosition = c.p  # not same node, save position to possibly return to
            c.selectPosition(p)
            c.pasteOutlineRetainingClones(s=s)
            if c.positionExists(oldPosition):
                # select if old position still valid
                c.selectPosition(oldPosition)
            else:
                oldPosition._childIndex = oldPosition._childIndex + 1
                # Try again with childIndex incremented
                if c.positionExists(oldPosition):
                    # additional try with higher childIndex
                    c.selectPosition(oldPosition)
        return self._make_response()
    #@+node:felix.20220815220429.1: *5* server.paste_as_template
    def paste_as_template(self, param: Param) -> Response:
        """
        Paste as template clones only nodes that were already clones
        """
        tag = 'paste_as_template'
        c = self._check_c(param)
        p = self._get_p(param)
        s = param.get('name')
        if s is None:  # pragma: no cover
            raise ServerError(f"{tag}: no string given")
        g.app.gui.replaceClipboardWith(s)
        if p == c.p:
            c.pasteAsTemplate()
        else:
            oldPosition = c.p  # not same node, save position to possibly return to
            c.selectPosition(p)
            c.pasteAsTemplate()
            if c.positionExists(oldPosition):
                # select if old position still valid
                c.selectPosition(oldPosition)
            else:
                oldPosition._childIndex = oldPosition._childIndex + 1
                # Try again with childIndex incremented
                if c.positionExists(oldPosition):
                    # additional try with higher childIndex
                    c.selectPosition(oldPosition)
        return self._make_response()
    #@+node:felix.20210621233316.59: *5* server.redo
    def redo(self, param: Param) -> Response:
        """Undo last un-doable operation with optional redo repeat count"""
        c = self._check_c(param)
        u = c.undoer
        total = param.get('repeat', 1)  # Facultative repeat redo count
        for _i in range(total):
            if u.canRedo():
                u.redo()
        return self._make_response()
    #@+node:felix.20210621233316.60: *5* server.set_body
    def set_body(self, param: Param) -> Response:
        """
        Undoably set body text of a v node.
        (Only if new string is different from actual existing body string)
        """
        tag = 'set_body'
        c = self._check_c(param)
        gnx = param.get('gnx')
        body = param.get('body')
        u, wrapper = c.undoer, c.frame.body.wrapper
        if body is None:  # pragma: no cover
            raise ServerError(f"{tag}: no body given")
        for p in c.all_positions():
            if p.v.gnx == gnx:
                if body == p.v.b:
                    return self._make_response()
                    # Just exit if there is no need to change at all.
                bunch = u.beforeChangeNodeContents(p)
                p.v.setBodyString(body)
                u.afterChangeNodeContents(p, "Body Text", bunch)
                if c.p == p:
                    wrapper.setAllText(body)
                if not c.isChanged():  # pragma: no cover
                    c.setChanged()
                if not p.v.isDirty():  # pragma: no cover
                    p.setDirty()
                break
        # additional forced string setting
        if gnx:
            v = c.fileCommands.gnxDict.get(gnx)  # vitalije
            if v:
                v.b = body
        return self._make_response()
    #@+node:felix.20210621233316.61: *5* server.set_current_position
    def set_current_position(self, param: Param) -> Response:
        """Select position p. Or try to get p with gnx if not found."""
        tag = "set_current_position"
        c = self._check_c(param)
        p = self._get_p(param)
        if p:
            if c.positionExists(p):
                # set this node as selection
                c.selectPosition(p)
            else:
                ap = param.get('ap')
                foundPNode = self._positionFromGnx(ap.get('gnx', ""), c)
                if foundPNode:
                    c.selectPosition(foundPNode)
                else:
                    print(
                        f"{tag}: node does not exist! "
                        f"ap was: {json.dumps(ap, cls=SetEncoder)}", flush=True)
        return self._make_response()
    #@+node:felix.20210621233316.62: *5* server.set_headline
    def set_headline(self, param: Param) -> Response:
        """
        Undoably set p.h, where p is c.p if package["ap"] is missing.
        """
        c = self._check_c(param)
        p = self._get_p(param)
        u = c.undoer
        h: str = param.get('name', '')
        oldH: str = p.h
        if h == oldH:
            return self._make_response()
        bunch = u.beforeChangeHeadline(p)
        c.setHeadString(p, h)  # c.setHeadString fixes the headline revert bug of p.initHeadString(h)
        c.setChanged()
        p.setDirty()
        u.afterChangeHeadline(p, 'Change Headline', bunch)
        return self._make_response()
    #@+node:felix.20210621233316.63: *5* server.set_selection
    def set_selection(self, param: Param) -> Response:
        """
        Set the selection range for p.b, where p is c.p if package["ap"] is missing.

        Set the selection in the wrapper if p == c.p

        Package has these keys:

        - "ap":     An archived position for position p.
        - "start":  The start of the selection.
        - "end":    The end of the selection.
        - "active": The insert point. Must be either start or end.
        - "scroll": An optional scroll position.

        Selection points can be sent as {"col":int, "line" int} dict
        or as numbers directly for convenience.
        """
        c = self._check_c(param)
        p = self._get_p(param)  # Will raise ServerError if p does not exist.
        v = p.v
        wrapper = c.frame.body.wrapper
        convert = g.convertRowColToPythonIndex
        start = param.get('start', 0)
        end = param.get('end', 0)
        active = param.get('insert', 0)  # temp var to check if int.
        scroll = param.get('scroll', 0)
        # If sent as number, use 'as is'
        if isinstance(active, int):
            insert = active
            startSel = start
            endSel = end
        else:
            # otherwise convert from line+col data.
            insert = convert(
                v.b, active['line'], active['col'])
            startSel = convert(
                v.b, start['line'], start['col'])
            endSel = convert(
                v.b, end['line'], end['col'])
        # If it's the currently selected node set the wrapper's states too
        if p == c.p:
            wrapper.setSelectionRange(startSel, endSel, insert)
            wrapper.setYScrollPosition(scroll)
        # Always set vnode attrs.
        v.scrollBarSpot = scroll
        v.insertSpot = insert
        v.selectionStart = startSel
        v.selectionLength = abs(startSel - endSel)
        return self._make_response()
    #@+node:felix.20211114202046.1: *5* server.set_ua_member
    def set_ua_member(self, param: Param) -> Response:
        """
        Set a single member of a node's ua.
        """
        self._check_c(param)
        p = self._get_p(param)
        name = param.get('name')
        value = param.get('value', '')
        if not p.v.u:
            p.v.u = {}  # assert at least an empty dict if null or non existent
        if name and isinstance(name, str):
            p.v.u[name] = value
        return self._make_response()
    #@+node:felix.20211114202058.1: *5* server.set_ua
    def set_ua(self, param: Param) -> Response:
        """
        Replace / set the whole user attribute dict of a node.
        """
        self._check_c(param)
        p = self._get_p(param)
        ua = param.get('ua', {})
        p.v.u = ua
        return self._make_response()
    #@+node:felix.20210621233316.64: *5* server.toggle_mark
    def toggle_mark(self, param: Param) -> Response:
        """
        Toggle the mark at position p.
        Try to keep selection, then return the selected node that remains.
        """
        c = self._check_c(param)
        p = self._get_p(param)
        if p == c.p:
            c.markHeadline()
        else:
            oldPosition = c.p
            c.selectPosition(p)
            c.markHeadline()
            if c.positionExists(oldPosition):
                c.selectPosition(oldPosition)
        # return selected node either ways
        return self._make_response()
    #@+node:felix.20210621233316.65: *5* server.mark_node
    def mark_node(self, param: Param) -> Response:
        """
        Mark a node.
        Try to keep selection, then return the selected node that remains.
        """
        # pylint: disable=no-else-return
        self._check_c(param)
        p = self._get_p(param)
        if p.isMarked():
            return self._make_response()
        else:
            return self.toggle_mark(param)

    #@+node:felix.20210621233316.66: *5* server.unmark_node
    def unmark_node(self, param: Param) -> Response:
        """
        Unmark a node.
        Try to keep selection, then return the selected node that remains.
        """
        # pylint: disable=no-else-return
        self._check_c(param)
        p = self._get_p(param)
        if not p.isMarked():
            return self._make_response()
        else:
            return self.toggle_mark(param)
    #@+node:felix.20210621233316.67: *5* server.undo
    def undo(self, param: Param) -> Response:
        """Undo last un-doable operation with optional undo repeat count"""
        c = self._check_c(param)
        u = c.undoer
        total = param.get('repeat', 1)  # Facultative repeat undo count
        for _i in range(total):
            if u.canUndo():
                u.undo()
        # Félix: Caller can get focus using other calls.
        return self._make_response()
    #@+node:felix.20210621233316.68: *4* server.server commands
    #@+node:felix.20210914230846.1: *5* server.get_version
    def get_version(self, param: Param) -> Response:
        """
        Return this server program name and version as a string representation
        along with the three version members as numbers 'major', 'minor' and 'patch'.
        """
        # uses the __version__ global constant and the v1, v2, v3 global version numbers
        result = {"version": __version__, "major": v1, "minor": v2, "patch": v3}
        return self._make_minimal_response(result)
    #@+node:felix.20220326190000.1: *5* server.get_leoid
    def get_leoid(self, param: Param) -> Response:
        """
        Returns g.app.leoID
        """
        # uses the __version__ global constant and the v1, v2, v3 global version numbers
        result = {"leoID": g.app.leoID}
        return self._make_minimal_response(result)
    #@+node:felix.20220326190008.1: *5* server.set_leoid
    def set_leoid(self, param: Param) -> Response:
        """
        Sets g.app.leoID
        """
        # uses the __version__ global constant and the v1, v2, v3 global version numbers
        leoID = param.get('leoID', '')
        # Same test/fix as in Leo
        if leoID:
            try:
                leoID = leoID.replace('.', '').replace(',', '').replace('"', '').replace("'", '')
                # Remove *all* whitespace: https://stackoverflow.com/questions/3739909
                leoID = ''.join(leoID.split())
            except Exception:
                g.es_exception()
                leoID = 'None'
            if len(leoID) > 2:
                g.app.leoID = leoID
                g.app.nodeIndices.defaultId = leoID
                g.app.nodeIndices.userId = leoID
        return self._make_response()
    #@+node:felix.20210818012827.1: *5* server.do_nothing
    def do_nothing(self, param: Param) -> Response:
        """Simply return states from _make_response"""
        return self._make_response()
    #@+node:felix.20210621233316.69: *5* server.set_ask_result
    def set_ask_result(self, param: Param) -> Response:
        """Got the result to an asked question/warning from client"""
        tag = "set_ask_result"
        result = param.get("result")
        if not result:
            raise ServerError(f"{tag}: no param result")
        g.app.externalFilesController.clientResult(result)
        return self._make_response()
    #@+node:felix.20210621233316.70: *5* server.set_config
    def set_config(self, param: Param) -> Response:
        """Got auto-reload's config from client"""
        self.leoServerConfig = param  # PARAM IS THE CONFIG-DICT
        return self._make_response()
    #@+node:felix.20210621233316.71: *5* server.error
    def error(self, param: Param) -> None:
        """For unit testing. Raise ServerError"""
        raise ServerError("error called")
    #@+node:felix.20210621233316.72: *5* server.get_all_leo_commands & helper
    def get_all_leo_commands(self, param: Param) -> Response:
        """Return a list of all commands that make sense for connected clients."""
        tag = 'get_all_leo_commands'
        # #173: Use the present commander to get commands created by @button and @command.
        c = self._check_c(param)
        d: dict = c.commandsDict if c else {}  # keys are command names, values are functions.
        bad_names = self._bad_commands(c)  # #92.
        good_names = self._good_commands()
        duplicates = set(bad_names).intersection(set(good_names))
        if duplicates:  # pragma: no cover
            print(f"{tag}: duplicate command names...", flush=True)
            for z in sorted(duplicates):
                print(z, flush=True)
        result = []
        for command_name in d:
            func = d.get(command_name)
            if not func:  # pragma: no cover
                print(f"{tag}: no func: {command_name!r}", flush=True)
                continue
            if command_name in bad_names:  # #92.
                continue
            doc = func.__doc__ or ''
            result.append({
                "label": command_name,  # Kebab-cased Command name to be called
                "detail": doc,
            })
        if self.log_flag:  # pragma: no cover
            print(f"\n{tag}: {len(result)} leo commands\n", flush=True)
            g.printObj([z.get("label") for z in result], tag=tag)
            print('', flush=True)
        return self._make_minimal_response({"commands": result})
    #@+node:felix.20210621233316.73: *6* server._bad_commands
    def _bad_commands(self, c: Cmdr) -> list[str]:
        """Return the list of command names that connected clients should ignore."""
        d = c.commandsDict if c else {}  # keys are command names, values are functions.
        bad = []
        #
        # leoInteg #173: Remove only vim commands.
        for command_name in sorted(d):
            if command_name.startswith(':'):
                bad.append(command_name)
        #
        # Remove other commands.
        # This is a hand-curated list.
        bad_list = [
            'restart-leo',

            'demangle-recent-files',
            'clean-main-spell-dict',
            'clean-persistence',
            'clean-recent-files',
            'clean-spellpyx',
            'clean-user-spell-dict',
            'clear-recent-files',
            'delete-first-icon',
            'delete-last-icon',
            'delete-node-icons',
            'insert-icon',

            'count-region',  # Uses wrapper, already available in client

            'export-headlines',  # (overridden by client)
            'export-jupyter-notebook',  # (overridden by client)
            'flatten-outline',  # (overridden by client)
            'outline-to-cweb',  # (overridden by client)
            'outline-to-noweb',  # (overridden by client)
            'remove-sentinels',  # (overridden by client)
            'weave',  # (overridden by client)
            'write-file-from-node',  # (overridden by client)

            'save-all',
            'save-file-as-zipped',
            'edit-setting',
            'edit-shortcut',
            'goto-line',
            'pdb',
            'xdb',
            'compare-two-leo-files',
            'file-compare-two-leo-files',
            'edit-recent-files',
            'exit-leo',
            'help',
            'help-for-abbreviations',
            'help-for-autocompletion',
            'help-for-bindings',
            'help-for-command',
            'help-for-creating-external-files',
            'help-for-debugging-commands',
            'help-for-drag-and-drop',
            'help-for-dynamic-abbreviations',
            'help-for-find-commands',
            'help-for-keystroke',
            'help-for-minibuffer',
            'help-for-python',
            'help-for-regular-expressions',
            'help-for-scripting',
            'help-for-settings',
            'join-leo-irc',  # Some online irc - parameters not working anymore

            'print-body',
            'print-cmd-docstrings',
            'print-expanded-body',
            'print-expanded-html',
            'print-html',
            'print-marked-bodies',
            'print-marked-html',
            'print-marked-nodes',
            'print-node',
            'print-sep',
            'print-tree-bodies',
            'print-tree-html',
            'print-tree-nodes',
            'print-window-state',
            'quit-leo',
            'reload-style-sheets',
            'save-buffers-kill-leo',
            'screen-capture-5sec',
            'screen-capture-now',
            'set-reference-file',  # TODO : maybe offer this
            'show-style-sheet',
            'sort-recent-files',
            'view-lossage',

            # Buffers commands (Usage?)
            'buffer-append-to',
            'buffer-copy',
            'buffer-insert',
            'buffer-kill',
            'buffer-prepend-to',
            'buffer-switch-to',
            'buffers-list',
            'buffers-list-alphabetically',

            # Open specific files... (MAYBE MAKE AVAILABLE?)
            # 'ekr-projects',
            'leo-cheat-sheet',  # These duplicates are useful.
            'leo-dist-leo',
            'leo-docs-leo',
            'leo-plugins-leo',
            'leo-py-leo',
            'leo-quickstart-leo',
            'leo-scripts-leo',
            'leo-unittest-leo',

            # 'scripts',
            'settings',

            'open-cheat-sheet-leo',
            'cheat-sheet-leo',
            'cheat-sheet',
            'open-desktop-integration-leo',
            'desktop-integration-leo',
            'open-leo-dist-leo',
            'leo-dist-leo',
            'open-leo-docs-leo',
            'leo-docs-leo',
            'open-leo-plugins-leo',
            'leo-plugins-leo',
            'open-leo-py-leo',
            'leo-py-leo',
            'open-leo-py-ref-leo',
            'leo-py-ref-leo',
            'open-leo-py',
            'open-leo-settings',
            'open-leo-settings-leo',
            'open-local-settings',
            'my-leo-settings',
            'open-my-leo-settings',
            'open-my-leo-settings-leo',
            'leo-settings',
            'open-quickstart-leo',
            'leo-quickstart-leo',
            'open-scripts-leo',
            'leo-scripts-leo',
            'open-unittest-leo',
            'leo-unittest-leo',

            # Open other places...
            'desktop-integration-leo',

            'open-offline-tutorial',
            'open-online-home',
            'open-online-toc',
            'open-online-tutorials',
            'open-online-videos',
            'open-recent-file',
            'open-theme-file',
            'open-url',
            'open-url-under-cursor',
            'open-users-guide',

            # Diffs - needs open file dialog
            'diff-and-open-leo-files',
            'diff-leo-files',

            # --- ORIGINAL BAD COMMANDS START HERE ---
            # Abbreviations...
            'abbrev-kill-all',
            'abbrev-list',
            'dabbrev-completion',
            'dabbrev-expands',

            # Autocompletion...
            'auto-complete',
            'auto-complete-force',
            'disable-autocompleter',
            'disable-calltips',
            'enable-autocompleter',
            'enable-calltips',

            # Debugger...
            'debug',
            'db-again',
            'db-b',
            'db-c',
            'db-h',
            'db-input',
            'db-l',
            'db-n',
            'db-q',
            'db-r',
            'db-s',
            'db-status',
            'db-w',

            # File operations...
            'directory-make',
            'directory-remove',
            'file-delete',
            'file-diff-files',
            'file-insert',
            'file-save-by-name',  # only body pane to file (confusing w/ save as...)
            'save-file-by-name',  # only body pane to file (confusing w/ save as...)
            # 'file-new',
            # 'file-open-by-name',

            # All others...
            'shell-command',
            'shell-command-on-region',
            'cheat-sheet',
            'dehoist',  # Duplicates of de-hoist.
            # 'find-clone-all',
            # 'find-clone-all-flattened',
            # 'find-clone-tag',
            # 'find-all',
            'find-character',
            'find-character-extend-selection',
            # 'find-next',
            # 'find-prev',
            'find-word',
            'find-word-in-line',

            'global-search',

            'isearch-backward',
            'isearch-backward-regexp',
            'isearch-forward',
            'isearch-forward-regexp',
            'isearch-with-present-options',

            # 'replace',
            # 'replace-all',
            'replace-current-character',
            # 'replace-then-find',

            # 're-search-backward',
            # 're-search-forward',

            # 'search-backward',
            # 'search-forward',
            'search-return-to-origin',

            # 'set-find-everywhere',
            # 'set-find-node-only',
            # 'set-find-suboutline-only',
            'set-replace-string',
            'set-search-string',

            # 'show-find-options',

            # 'start-search',

            'toggle-find-collapses-nodes',
            # 'toggle-find-ignore-case-option',
            # 'toggle-find-in-body-option',
            # 'toggle-find-in-headline-option',
            # 'toggle-find-mark-changes-option',
            # 'toggle-find-mark-finds-option',
            # 'toggle-find-regex-option',
            # 'toggle-find-word-option',
            'toggle-find-wrap-around-option',

            # 'word-search-backward',
            # 'word-search-forward',

            # Buttons...
            'delete-script-button-button',

            # Clicks...
            'click-click-box',
            'click-icon-box',
            'ctrl-click-at-cursor',
            'ctrl-click-icon',
            'double-click-icon-box',
            'right-click-icon',

            # Editors...
            'add-editor', 'editor-add',
            'delete-editor', 'editor-delete',
            'detach-editor-toggle',
            'detach-editor-toggle-max',

            # Focus...
            'cycle-editor-focus', 'editor-cycle-focus',
            'focus-to-body',
            'focus-to-find',
            'focus-to-log',
            'focus-to-minibuffer',
            'focus-to-nav',
            'focus-to-spell-tab',
            'focus-to-tree',

            'tab-cycle-next',
            'tab-cycle-previous',
            'tab-detach',

            # Headlines..
            'abort-edit-headline',
            'edit-headline',
            'end-edit-headline',

            # Layout and panes...
            'adoc',
            'adoc-with-preview',

            'contract-body-pane',
            'contract-log-pane',
            'contract-outline-pane',

            'edit-pane-csv',
            'edit-pane-test-open',
            'equal-sized-panes',
            'expand-log-pane',
            'expand-body-pane',
            'expand-outline-pane',

            'free-layout-context-menu',
            'free-layout-load',
            'free-layout-restore',
            'free-layout-zoom',

            'zoom-in',
            'zoom-out',

            # Log
            'clear-log',

            # Menus...
            'activate-cmds-menu',
            'activate-edit-menu',
            'activate-file-menu',
            'activate-help-menu',
            'activate-outline-menu',
            'activate-plugins-menu',
            'activate-window-menu',
            'context-menu-open',
            'menu-shortcut',

            # Modes...
            'clear-extend-mode',

            # Outline... (Commented off by Félix, Should work)
            # 'contract-or-go-left',
            # 'contract-node',
            # 'contract-parent',

            # Scrolling...
            'scroll-down-half-page',
            'scroll-down-line',
            'scroll-down-page',
            'scroll-outline-down-line',
            'scroll-outline-down-page',
            'scroll-outline-left',
            'scroll-outline-right',
            'scroll-outline-up-line',
            'scroll-outline-up-page',
            'scroll-up-half-page',
            'scroll-up-line',
            'scroll-up-page',

            # Windows...
            'about-leo',

            'cascade-windows',
            'close-others',
            'close-window',

            'iconify-frame',

            'find-tab-hide',
            'help-for-highlight-current-line',
            'help-for-right-margin-guide',

            # 'find-tab-open',

            'hide-body-dock',
            'hide-body-pane',
            'hide-invisibles',
            'hide-log-pane',
            'hide-outline-dock',
            'hide-outline-pane',
            'hide-tabs-dock',

            'minimize-all',

            'resize-to-screen',

            'show-body-dock',
            'show-hide-body-dock',
            'show-hide-outline-dock',
            'show-hide-render-dock',
            'show-hide-tabs-dock',
            'show-tabs-dock',
            'clean-diff',
            'cm-external-editor',

            'delete-@button-parse-json-button',
            'delete-trace-statements',

            'disable-idle-time-events',

            'enable-idle-time-events',
            'enter-quick-command-mode',
            'exit-named-mode',

            'F6-open-console',

            'flush-lines',
            'full-command',

            'get-child-headlines',

            'history',

            'insert-file-name',
            'insert-jupyter-toc',
            'insert-markdown-toc',

            'justify-toggle-auto',

            'keep-lines',
            'keyboard-quit',

            'line-number',
            'line-numbering-toggle',
            'line-to-headline',

            'marked-list',

            'mode-help',

            'open-python-window',

            'open-with-idle',
            'open-with-open-office',
            'open-with-scite',
            'open-with-word',

            'recolor',
            'redraw',

            'repeat-complex-command',

            'session-clear',
            'session-create',
            'session-refresh',
            'session-restore',
            'session-snapshot-load',
            'session-snapshot-save',

            'set-colors',
            'set-command-state',
            'set-comment-column',
            'set-extend-mode',
            'set-fill-column',
            'set-fill-prefix',
            'set-font',
            'set-insert-state',
            'set-overwrite-state',
            'set-silent-mode',

            'show-buttons',
            'show-calltips',
            'show-calltips-force',
            'show-color-names',
            'show-color-wheel',
            'show-commands',
            # 'show-file-line',

            'show-focus',
            'show-fonts',

            'show-invisibles',
            # 'show-node-uas',
            'show-outline-dock',
            'show-plugin-handlers',
            'show-plugins-info',
            # 'show-settings',
            'show-settings-outline',
            'show-spell-info',
            'show-stats',
            'show-tips',

            'style-set-selected',

            'suspend',

            'toggle-abbrev-mode',
            'toggle-active-pane',
            'toggle-angle-brackets',
            'toggle-at-auto-at-edit',
            'toggle-autocompleter',
            'toggle-calltips',
            'toggle-case-region',
            'toggle-extend-mode',
            'toggle-idle-time-events',
            'toggle-input-state',
            'toggle-invisibles',
            'toggle-line-numbering-root',
            'toggle-sparse-move',
            'toggle-split-direction',

            'what-line',
            # 'eval',
            'eval-block',
            # 'eval-last',
            # 'eval-last-pretty',
            # 'eval-replace',

            'find-quick',
            'find-quick-changed',
            'find-quick-selected',
            'find-quick-test-failures',
            'find-quick-timeline',

            # 'goto-next-history-node',
            # 'goto-prev-history-node',

            'preview',
            'preview-body',
            'preview-expanded-body',
            'preview-expanded-html',
            'preview-html',
            'preview-marked-bodies',
            'preview-marked-html',
            'preview-marked-nodes',
            'preview-node',
            'preview-tree-bodies',
            'preview-tree-html',
            'preview-tree-nodes',

            'spell-add',
            'spell-as-you-type-next',
            'spell-as-you-type-toggle',
            'spell-as-you-type-undo',
            'spell-as-you-type-wrap',
            'spell-change',
            'spell-change-then-find',
            'spell-find',
            'spell-ignore',
            'spell-tab-hide',
            'spell-tab-open',

            # 'tag-children',

            'todo-children-todo',
            'todo-dec-pri',
            'todo-find-todo',
            'todo-fix-datetime',
            'todo-inc-pri',

            'vr',
            'vr-contract',
            'vr-expand',
            'vr-hide',
            'vr-lock',
            'vr-pause-play-movie',
            'vr-show',
            'vr-toggle',
            'vr-unlock',
            'vr-update',
            'vr-zoom',

            'vs-create-tree',
            'vs-dump',
            'vs-reset',
            'vs-update',

            # Connected client's text editing commands should cover all of these...
            # 'add-comments',
            'add-space-to-lines',
            'add-tab-to-lines',
            'align-eq-signs',  # does not exist
            'always-indent-region',
            'capitalize-words-or-selection',
            'cls',

            # reformat are Ok to use from leobridge
            # 'reformat-body',
            # 'reformat-paragraph',
            # 'reformat-selection',

            'back-char',
            'back-char-extend-selection',
            'back-page',
            'back-page-extend-selection',
            'back-paragraph',
            'back-paragraph-extend-selection',
            'back-sentence',
            'back-sentence-extend-selection',
            'back-to-home',
            'back-to-home-extend-selection',
            'back-to-indentation',
            'back-word',
            'back-word-extend-selection',
            'back-word-smart',
            'back-word-smart-extend-selection',
            'backward-delete-char',
            'backward-delete-word',
            'backward-delete-word-smart',
            'backward-find-character',
            'backward-find-character-extend-selection',
            'backward-kill-paragraph',
            'backward-kill-sentence',
            'backward-kill-word',
            'beginning-of-buffer',
            'beginning-of-buffer-extend-selection',
            'beginning-of-line',
            'beginning-of-line-extend-selection',

            'capitalize-word',
            'center-line',
            'center-region',
            'clean-all-blank-lines',
            'clean-all-lines',
            'clean-body',
            'clean-lines',
            'clear-kill-ring',
            'clear-selected-text',
            'convert-blanks',
            'convert-tabs',
            'copy-text',
            'cut-text',

            'delete-char',
            'delete-comments',
            'delete-indentation',
            'delete-spaces',
            'delete-word',
            'delete-word-smart',
            'downcase-region',
            'downcase-word',

            'end-of-buffer',
            'end-of-buffer-extend-selection',
            'end-of-line',
            'end-of-line-extend-selection',

            'exchange-point-mark',

            'extend-to-line',
            'extend-to-paragraph',
            'extend-to-sentence',
            'extend-to-word',

            'fill-paragraph',
            'fill-region',
            'fill-region-as-paragraph',

            'finish-of-line',
            'finish-of-line-extend-selection',

            'forward-char',
            'forward-char-extend-selection',
            'forward-end-word',
            'forward-end-word-extend-selection',
            'forward-page',
            'forward-page-extend-selection',
            'forward-paragraph',
            'forward-paragraph-extend-selection',
            'forward-sentence',
            'forward-sentence-extend-selection',
            'forward-word',
            'forward-word-extend-selection',
            'forward-word-smart',
            'forward-word-smart-extend-selection',

            'go-anywhere',
            'go-back',
            'go-forward',
            'goto-char',

            'indent-region',
            'indent-relative',
            'indent-rigidly',
            'indent-to-comment-column',

            'insert-hard-tab',
            'insert-newline',
            'insert-parentheses',
            'insert-soft-tab',

            'kill-line',
            'kill-paragraph',
            'kill-pylint',
            'kill-region',
            'kill-region-save',
            'kill-sentence',
            'kill-to-end-of-line',
            'kill-word',
            'kill-ws',

            'match-brackets',

            'move-lines-down',
            'move-lines-up',
            'move-past-close',
            'move-past-close-extend-selection',

            'newline-and-indent',
            'next-line',
            'next-line-extend-selection',
            'next-or-end-of-line',
            'next-or-end-of-line-extend-selection',

            'previous-line',
            'previous-line-extend-selection',
            'previous-or-beginning-of-line',
            'previous-or-beginning-of-line-extend-selection',

            'rectangle-clear',
            'rectangle-close',
            'rectangle-delete',
            'rectangle-kill',
            'rectangle-open',
            'rectangle-string',
            'rectangle-yank',

            'remove-blank-lines',
            'remove-newlines',
            'remove-space-from-lines',
            'remove-tab-from-lines',

            'reverse-region',
            'reverse-sort-lines',
            'reverse-sort-lines-ignoring-case',

            'paste-text',
            'pop-cursor',
            'push-cursor',

            'select-all',
            'select-next-trace-statement',
            'select-to-matching-bracket',

            'sort-columns',
            'sort-fields',
            'sort-lines',
            'sort-lines-ignoring-case',

            'split-defs',
            'split-line',

            'start-of-line',
            'start-of-line-extend-selection',

            'tabify',
            'transpose-chars',
            'transpose-lines',
            'transpose-words',

            'unformat-paragraph',
            'unindent-region',

            'untabify',

            'upcase-region',
            'upcase-word',
            'update-ref-file',

            'yank',
            'yank-pop',

            'zap-to-character',

        ]
        bad.extend(bad_list)
        result = list(sorted(bad))
        return result
    #@+node:felix.20210621233316.74: *6* server._good_commands
    def _good_commands(self) -> list[str]:
        """Defined commands that should be available in a connected client"""
        good_list = [

            'contract-all',
            'contract-all-other-nodes',
            'clone-node',
            'copy-node',
            'copy-marked-nodes',
            'cut-node',

            'de-hoist',
            'delete-marked-nodes',
            'delete-node',
            # 'demangle-recent-files',
            'demote',
            'do-nothing',
            'expand-and-go-right',
            'expand-next-level',
            'expand-node',
            'expand-or-go-right',
            'expand-prev-level',
            'expand-to-level-1',
            'expand-to-level-2',
            'expand-to-level-3',
            'expand-to-level-4',
            'expand-to-level-5',
            'expand-to-level-6',
            'expand-to-level-7',
            'expand-to-level-8',
            'expand-to-level-9',
            'expand-all',
            'expand-all-subheads',
            'expand-ancestors-only',

            'find-next-clone',

            'goto-first-node',
            'goto-first-sibling',
            'goto-first-visible-node',
            'goto-last-node',
            'goto-last-sibling',
            'goto-last-visible-node',
            'goto-next-changed',
            'goto-next-clone',
            'goto-next-marked',
            'goto-next-node',
            'goto-next-sibling',
            'goto-next-visible',
            'goto-parent',
            'goto-prev-marked',
            'goto-prev-node',
            'goto-prev-sibling',
            'goto-prev-visible',

            'hoist',

            'insert-node',
            'insert-node-before',
            'insert-as-first-child',
            'insert-as-last-child',
            'insert-child',

            'mark',
            'mark-changed-items',
            'mark-first-parents',
            'mark-subheads',

            'move-marked-nodes',
            'move-outline-down',
            'move-outline-left',
            'move-outline-right',
            'move-outline-up',

            'paste-node',
            'paste-retaining-clones',
            'promote',
            'promote-bodies',
            'promote-headlines',

            'sort-children',
            'sort-siblings',

            'tangle',
            'tangle-all',
            'tangle-marked',

            'unmark-all',
            'unmark-first-parents',
            # 'clean-main-spell-dict',
            # 'clean-persistence',
            # 'clean-recent-files',
            # 'clean-spellpyx',
            # 'clean-user-spell-dict',

            'clear-all-caches',
            'clear-all-hoists',
            'clear-all-uas',
            'clear-cache',
            'clear-node-uas',
            # 'clear-recent-files',

            # 'delete-first-icon', # ? maybe move to bad commands?
            # 'delete-last-icon', # ? maybe move to bad commands?
            # 'delete-node-icons', # ? maybe move to bad commands?

            'dump-caches',
            'dump-clone-parents',
            'dump-expanded',
            'dump-node',
            'dump-outline',

            # 'insert-icon', # ? maybe move to bad commands?

            'set-ua',

            'show-all-uas',
            'show-bindings',
            'show-clone-ancestors',
            'show-clone-parents',

            'typescript-to-py',

            # Import files... # done through import all
            'import-MORE-files',
            'import-file',
            'import-free-mind-files',
            'import-jupyter-notebook',
            'import-legacy-external-files',
            'import-mind-jet-files',
            'import-tabbed-files',
            'import-todo-text-files',
            'import-zim-folder',

            # Read outlines...
            'read-at-auto-nodes',
            'read-at-file-nodes',
            'read-at-shadow-nodes',
            'read-file-into-node',
            'read-ref-file',

            # Save Files.
            'file-save',
            'file-save-as',
            # 'file-save-by-name',
            'file-save-to',
            'save',
            'save-as',
            'save-file',
            'save-file-as',
            # 'save-file-by-name',
            'save-file-to',
            'save-to',

            # Write parts of outlines...
            'write-at-auto-nodes',
            'write-at-file-nodes',
            'write-at-shadow-nodes',
            'write-dirty-at-auto-nodes',
            'write-dirty-at-file-nodes',
            'write-dirty-at-shadow-nodes',
            'write-edited-recent-files',
            # 'write-file-from-node',
            'write-missing-at-file-nodes',
            'write-outline-only',

            'clone-find-all',
            'clone-find-all-flattened',
            'clone-find-all-flattened-marked',
            'clone-find-all-marked',
            'clone-find-parents',
            'clone-find-tag',
            'clone-marked-nodes',
            'clone-node-to-last-node',

            'clone-to-at-spot',

            # 'edit-setting',
            # 'edit-shortcut',

            'execute-pytest',
            'execute-script',
            'extract',
            'extract-names',

            'goto-any-clone',
            'goto-global-line',
            # 'goto-line',
            'git-diff', 'gd',

            'log-kill-listener', 'kill-log-listener',
            'log-listen', 'listen-to-log',

            'make-stub-files',

            # 'pdb',

            'redo',
            'rst3',
            'run-all-unit-tests-externally',
            'run-all-unit-tests-locally',
            'run-marked-unit-tests-externally',
            'run-marked-unit-tests-locally',
            'run-selected-unit-tests-externally',
            'run-selected-unit-tests-locally',
            'run-tests',

            'undo',

            # 'xdb',

            # Beautify, blacken, fstringify...
            'beautify-files',
            'beautify-files-diff',
            'blacken-files',
            'blacken-files-diff',
            # 'diff-and-open-leo-files',
            'diff-beautify-files',
            'diff-fstringify-files',
            # 'diff-leo-files',
            'diff-marked-nodes',
            'fstringify-files',
            'fstringify-files-diff',
            'fstringify-files-silent',
            'pretty-print-c',
            'silent-fstringify-files',

            # All other commands...
            'at-file-to-at-auto',

            'beautify-c',

            # 'cls',
            'c-to-python',
            'c-to-python-clean-docs',
            'check-derived-file',
            'check-outline',
            'code-to-rst',
            # 'compare-two-leo-files',
            'convert-all-blanks',
            'convert-all-tabs',
            'count-children',
            'count-pages',
            # 'count-region',

            # 'desktop-integration-leo',

            # 'edit-recent-files',
            # 'exit-leo',

            # 'file-compare-two-leo-files',
            'find-def',
            'find-long-lines',
            'find-missing-docstrings',
            'flake8-files',
            # 'flatten-outline',
            'flatten-outline-to-node',
            'flatten-script',

            'gc-collect-garbage',
            'gc-dump-all-objects',
            'gc-dump-new-objects',
            'gc-dump-objects-verbose',
            'gc-show-summary',

            # 'help',  # To do.
            # 'help-for-abbreviations',
            # 'help-for-autocompletion',
            # 'help-for-bindings',
            # 'help-for-command',
            # 'help-for-creating-external-files',
            # 'help-for-debugging-commands',
            # 'help-for-drag-and-drop',
            # 'help-for-dynamic-abbreviations',
            # 'help-for-find-commands',
            # 'help-for-keystroke',
            # 'help-for-minibuffer',
            # 'help-for-python',
            # 'help-for-regular-expressions',
            # 'help-for-scripting',
            # 'help-for-settings',

            'insert-body-time',  # ?
            'insert-headline-time',
            # 'insert-jupyter-toc',
            # 'insert-markdown-toc',

            'find-var',

            # 'join-leo-irc',
            'join-node-above',
            'join-node-below',
            'join-selection-to-node-below',

            'move-lines-to-next-node',

            'new',

            'open-outline',

            'parse-body',
            'parse-json',
            'pandoc',
            'pandoc-with-preview',
            'paste-as-template',

            # 'print-body',
            # 'print-cmd-docstrings',
            # 'print-expanded-body',
            # 'print-expanded-html',
            # 'print-html',
            # 'print-marked-bodies',
            # 'print-marked-html',
            # 'print-marked-nodes',
            # 'print-node',
            # 'print-sep',
            # 'print-tree-bodies',
            # 'print-tree-html',
            # 'print-tree-nodes',
            # 'print-window-state',

            'pyflakes',
            'pylint',
            'pylint-kill',
            'python-to-coffeescript',

            # 'quit-leo',

            # 'reformat-body',
            # 'reformat-paragraph',
            'refresh-from-disk',
            'reload-settings',
            # 'reload-style-sheets',
            'revert',

            # 'save-buffers-kill-leo',
            # 'screen-capture-5sec',
            # 'screen-capture-now',
            'script-button',  # ?
            # 'set-reference-file',
            # 'show-style-sheet',
            # 'sort-recent-files',
            'sphinx',
            'sphinx-with-preview',
            'style-reload',  # ?

            'untangle',
            'untangle-all',
            'untangle-marked',

            # 'view-lossage',  # ?

            # Dubious commands (to do)...
            'act-on-node',

            'cfa',
            'cfam',
            'cff',
            'cffm',
            'cft',

            # 'buffer-append-to',
            # 'buffer-copy',
            # 'buffer-insert',
            # 'buffer-kill',
            # 'buffer-prepend-to',
            # 'buffer-switch-to',
            # 'buffers-list',
            # 'buffers-list-alphabetically',

            'chapter-back',
            'chapter-next',
            # 'chapter-select', #
            'chapter-select-main'
        ]
        return good_list
    #@+node:felix.20210621233316.75: *5* server.get_all_server_commands & helpers
    def get_all_server_commands(self, param: Param) -> Response:
        """
        Public server method:
        Return the names of all callable public methods of the server.
        """
        tag = 'get_all_server_commands'
        names = self._get_all_server_commands()
        if self.log_flag:  # pragma: no cover
            print(f"\n{tag}: {len(names)} server commands\n", flush=True)
            g.printObj(names, tag=tag)
            print('', flush=True)
        return self._make_response({"server-commands": names})
    #@+node:felix.20210914231602.1: *6* _get_all_server_commands
    def _get_all_server_commands(self) -> list[str]:
        """
        Private server method:
        Return the names of all callable public methods of the server.
        (Methods that do not start with an underscore '_')
        """
        members = inspect.getmembers(self, inspect.ismethod)
        return sorted([name for (name, value) in members if not name.startswith('_')])
    #@+node:felix.20231008201016.1: *5* server.history getters & setters
    #@+node:felix.20231008201231.1: *6* get_history
    def get_history(self, param: Param) -> Response:
        """Get current commander's command history"""
        c = self._check_c(param)
        k = c.k
        if k and k.commandHistory:
            h = k.commandHistory
        else:
            h = []
        return self._make_response({"history": h})
    #@+node:felix.20231008201237.1: *6* set_history
    def set_history(self, param: Param) -> Response:
        """Set current commander's command history"""
        c = self._check_c(param)
        k = c.k
        h = param.get('history', [])
        if k and isinstance(h, list) and all(isinstance(item, str) for item in h):
            k.commandHistory = h
        else:
            k.commandHistory = []
        return self._make_response()
    #@+node:felix.20231008201242.1: *6* add_history
    def add_history(self, param: Param) -> Response:
        """Add a command to the current commander's command history"""
        c = self._check_c(param)
        k = c.k
        command = param.get('command', "")
        if k and command and isinstance(command, str):
            k.addToCommandHistory(command)
        return self._make_response()
    #@+node:felix.20210621233316.76: *5* server.init_connection
    def _init_connection(self, web_socket: Socket) -> None:  # pragma: no cover (tested in client).
        """Begin the connection."""
        global connectionsTotal
        if connectionsTotal == 1:
            # First connection, so "Master client" setup
            self.web_socket = web_socket
            self.loop = asyncio.get_event_loop()
        else:
            # already exist, so "spectator-clients" setup
            pass  # nothing for now
    #@+node:felix.20210621233316.77: *5* server.shut_down
    def shut_down(self, param: Param) -> None:
        """Shut down the server."""
        tag = 'shut_down'
        n = len(g.app.commanders())
        if n:  # pragma: no cover
            raise ServerError(f"{tag}: {n} open outlines")
        raise TerminateServer("client requested shut down")
    #@+node:felix.20210621233316.78: *3* server.server utils
    #@+node:felix.20210621233316.79: *4* server._ap_to_p
    def _ap_to_p(self, ap: dict[str, Any], c: Cmdr) -> Optional[Position]:
        """
        Convert ap (archived position, a dict) to a valid Leo position.

        Return False on any kind of error to support calls to invalid positions
        after a document has been closed of switched and interface interaction
        in the client generated incoming calls to 'getters' already sent. (for the
        now inaccessible leo document commander.)
        """
        tag = '_ap_to_p'
        gnx_d = c.fileCommands.gnxDict
        try:
            outer_stack = ap.get('stack')
            if outer_stack is None:  # pragma: no cover.
                raise ServerError(f"{tag}: no stack in ap: {ap!r}")
            if not isinstance(outer_stack, (list, tuple)):  # pragma: no cover.
                raise ServerError(f"{tag}: stack must be tuple or list: {outer_stack}")

            def d_to_childIndex_v(d: dict[str, str]) -> tuple[int, VNode]:
                """Helper: return childIndex and v from d ["childIndex"] and d["gnx"]."""
                childIndex: int
                childIndex_s: str = d.get('childIndex')
                if childIndex_s is None:
                    raise ServerError(f"{tag}: no childIndex in {d}")
                try:
                    childIndex = int(childIndex_s)
                except Exception:  # pragma: no cover.
                    raise ServerError(f"{tag}: bad childIndex: {childIndex!r}")
                gnx = d.get('gnx')
                if gnx is None:  # pragma: no cover.
                    raise ServerError(f"{tag}: no gnx in {d}.")
                v = gnx_d.get(gnx)
                if v is None:  # pragma: no cover.
                    raise ServerError(f"{tag}: gnx not found: {gnx!r}")
                return childIndex, v

            # Compute p.childIndex and p.v.
            childIndex, v = d_to_childIndex_v(ap)

            # Create p.stack.
            stack = []
            for stack_d in outer_stack:
                stack_childIndex, stack_v = d_to_childIndex_v(stack_d)
                stack.append((stack_v, stack_childIndex))

            # Make p and check p.
            p = Position(v, childIndex, stack)
            if not c.positionExists(p):  # pragma: no cover.
                raise ServerError(f"{tag}: p does not exist in {c.shortFileName()}")
        except Exception:
            if self.log_flag or traces:
                print(
                    f"{tag}: Bad ap: {ap!r}\n"
                    f"{tag}: v {v!r} childIndex: {childIndex!r}\n"
                    f"{tag}: stack: {stack!r}", flush=True)
            return None  # Return None on any error so caller can react.
        return p
    #@+node:felix.20210621233316.80: *4* server._check_c
    def _check_c(self, param: Param = None) -> Cmdr:
        """
        Return self.c, or a specific commander chosen by id,
        or raise ServerError no commander found.
        """
        tag = '_check_c'
        c = self.c
        if param:
            commanderId = param.get('commanderId')
            if commanderId:
                commanders = g.app.commanders()
                for commander in commanders:
                    if id(commander) == commanderId:
                        c = commander  #  Found commander by id!
                        break
        # Still not found?
        if not c:  # pragma: no cover
            raise ServerError(f"{tag}: no open commander")
        return c
    #@+node:felix.20210621233316.81: *4* server._check_outline
    def _check_outline(self, c: Cmdr) -> None:
        """Check self.c for consistency."""
        # Check that all positions exist.
        self._check_outline_positions(c)
        # Test round-tripping.
        self._test_round_trip_positions(c)
    #@+node:felix.20210621233316.82: *4* server._check_outline_positions
    def _check_outline_positions(self, c: Cmdr) -> None:
        """Verify that all positions in c exist."""
        tag = '_check_outline_positions'
        for p in c.all_positions(copy=False):
            if not c.positionExists(p):  # pragma: no cover
                message = f"{tag}: position {p!r} does not exist in {c.shortFileName()}"
                print(message, flush=True)
                self._dump_position(p)
                raise ServerError(message)
    #@+node:felix.20210621233316.84: *4* server._do_leo_command_by_name
    def _do_leo_command_by_name(self, command_name: str, param: Param) -> Response:
        """
        Generic call to a command in Leo's Commands class or any subcommander class.

        The param["ap"] position is to be selected before having the command run,
        while the param["keep"] parameter specifies wether the original position
        should be re-selected afterward.

        command_name: the name of a Leo command (a kebab-cased string).
        param["ap"]: an archived position.
        param["keep"]: preserve the current selection, if possible.

        """
        tag = '_do_leo_command_by_name'
        c = self._check_c(param)

        if command_name in self.bad_commands_list:  # pragma: no cover
            raise ServerError(f"{tag}: disallowed command: {command_name!r}")

        keepSelection = False  # Set default, optional component of param
        if "keep" in param:
            keepSelection = param["keep"]

        func = c.commandsDict.get(command_name)  # Getting from kebab-cased 'Command Name'
        if not func:  # pragma: no cover
            raise ServerError(f"{tag}: Leo command not found: {command_name!r}")

        p = self._get_p(param)
        try:
            if p == c.p:
                value = func(event={"c": c})  # no need for re-selection
            else:
                old_p = c.p  # preserve old position
                c.selectPosition(p)  # set position upon which to perform the command
                value = func(event={"c": c})
                if keepSelection and c.positionExists(old_p):
                    # Only if 'keep' old position was set, and old_p still exists
                    c.selectPosition(old_p)
        except Exception as e:
            print(f"_do_leo_command Recovered from Error {e!s}", flush=True)
            return self._make_response()  # Return empty on error
        #
        # Tag along a possible return value with info sent back by _make_response
        if self._is_jsonable(value):
            return self._make_response({"return-value": value})
        return self._make_response()
    #@+node:ekr.20210722184932.1: *4* server._do_leo_function_by_name
    def _do_leo_function_by_name(self, function_name: str, param: Param) -> Response:
        """
        Generic call to a method in Leo's Commands class or any subcommander class.

        The param["ap"] position is to be selected before having the command run,
        while the param["keep"] parameter specifies wether the original position
        should be re-selected afterward.

        command: the name of a method
        param["ap"]: an archived position.
        param["keep"]: preserve the current selection, if possible.

        """
        tag = '_do_leo_function_by_name'
        c = self._check_c(param)

        keepSelection = False  # Set default, optional component of param
        if "keep" in param:
            keepSelection = param["keep"]

        func = self._get_commander_method(function_name, c)  # GET FUNC
        if not func:  # pragma: no cover
            raise ServerError(f"{tag}: Leo command not found: {function_name!r}")

        p = self._get_p(param)
        try:
            if p == c.p:
                value = func(event={"c": c})  # no need for re-selection
            else:
                old_p = c.p  # preserve old position
                c.selectPosition(p)  # set position upon which to perform the command
                value = func(event={"c": c})
                if keepSelection and c.positionExists(old_p):
                    # Only if 'keep' old position was set, and old_p still exists
                    c.selectPosition(old_p)
        except Exception as e:
            print(f"_do_leo_command Recovered from Error {e!s}", flush=True)
            return self._make_response()  # Return empty on error
        #
        # Tag along a possible return value with info sent back by _make_response
        if self._is_jsonable(value):
            return self._make_response({"return-value": value})
        return self._make_response()
    #@+node:felix.20210621233316.85: *4* server._do_message
    def _do_message(self, d: dict[str, Any]) -> Response:
        """
        Handle d, a python dict representing the incoming request.
        The d dict must have the three (3) following keys:

        "id": A positive integer.

        "action": A string, which is either:
            - The name of public method of this class, prefixed with '!'.
            - The name of a Leo command, prefixed with '-'
            - The name of a method of a Leo class, without prefix.

        "param": A dict to be passed to the called "action" method.
            (Passed to the public method, or the _do_leo_command. Often contains ap, text & keep)

        Return a dict, created by _make_response or _make_minimal_response
        that contains at least an 'id' key.

        """
        global traces
        tag = '_do_message'
        trace, verbose = 'request' in traces, 'verbose' in traces
        func: Callable
        action: Optional[str]

        # Require "id" and "action" keys
        id_: Optional[int] = d.get("id")
        if id_ is None:  # pragma: no cover
            raise ServerError(f"{tag}: no id")
        action = d.get("action")
        if action is None:  # pragma: no cover
            raise ServerError(f"{tag}: no action")

        param: Optional[dict] = d.get('param', {})
        # Set log flag.
        if param:
            self.log_flag = param.get("log")
        else:
            param = {}

        # Handle traces.
        if trace and verbose:  # pragma: no cover
            g.printObj(d, tag=f"request {id_}")
            print('', flush=True)
        elif trace:  # pragma: no cover
            keys = sorted(param.keys())
            if action == '!set_config':
                keys_s = f"({len(keys)} keys)"
            elif len(keys) > 5:
                keys_s = '\n  ' + '\n  '.join(keys)
            else:
                keys_s = ', '.join(keys)
            print(f" request {id_:<4} {action:<30} {keys_s}", flush=True)

        # Set the current_id and action ivars for _make_response.
        self.current_id = id_
        self.action = action

        # Execute the requested action.
        if action[0] == "!":
            action = action[1:]  # Remove exclamation point "!"
            func = self._do_server_command  # Server has this method.
        elif action[0] == '-':
            action = action[1:]  # Remove dash "-"
            func = self._do_leo_command_by_name  # It's a command name.
        else:
            func = self._do_leo_function_by_name  # It's the name of a method in some commander.
        result = func(action, param)
        if result is None:  # pragma: no cover
            raise ServerError(f"{tag}: no response: {action!r}")
        return result
    #@+node:felix.20210621233316.86: *4* server._do_server_command
    def _do_server_command(self, action: str, param: Param) -> Response:
        tag = '_do_server_command'
        # Disallow hidden methods.
        if action.startswith('_'):  # pragma: no cover
            raise ServerError(f"{tag}: action starts with '_': {action!r}")
        # Find and execute the server method.
        func = getattr(self, action, None)
        if not func:
            raise ServerError(f"{tag}: action not found: {action!r}")  # pragma: no cover
        if not callable(func):
            raise ServerError(f"{tag}: not callable: {func!r}")  # pragma: no cover
        return func(param)
    #@+node:felix.20210621233316.87: *4* server._dump_*
    def _dump_outline(self, c: Cmdr) -> None:  # pragma: no cover
        """Dump the outline."""
        tag = '_dump_outline'
        print(f"{tag}: {c.shortFileName()}...\n", flush=True)
        for p in c.all_positions():
            self._dump_position(p)
        print('', flush=True)

    def _dump_position(self, p: Position) -> None:  # pragma: no cover
        level_s = ' ' * 2 * p.level()
        print(f"{level_s}{p.childIndex():2} {p.v.gnx} {p.h}", flush=True)
    #@+node:felix.20210624160812.1: *4* server._emit_signon
    def _emit_signon(self) -> None:
        """Simulate the Initial Leo Log Entry"""
        tag = 'emit_signon'
        if self.loop:
            g.app.computeSignon()
            signon = []
            for z in (g.app.signon, g.app.signon1):
                for z2 in z.split('\n'):
                    signon.append(z2.strip())
            g.es("\n".join(signon))
        else:
            raise ServerError(f"{tag}: no loop ready for emit_signon")
    #@+node:felix.20210625230236.1: *4* server._get_commander_method
    def _get_commander_method(self, command: str, c: Cmdr) -> Callable:
        """ Return the given method (p_command) in the Commands class or subcommanders."""
        func = getattr(c, command, None)
        if func:
            return func
        # Otherwise, search all subcommanders for the method.
        table = (  # This table comes from c.initObjects.
            'abbrevCommands',
            'bufferCommands',
            'chapterCommands',
            'controlCommands',
            'convertCommands',
            'debugCommands',
            'editCommands',
            'editFileCommands',
            # 'evalController',  # Previously, set in mod_scripting.py.
            'gotoCommands',
            'helpCommands',
            'keyHandler',
            'keyHandlerCommands',
            'killBufferCommands',
            'leoCommands',
            'macroCommands',
            'miniBufferWidget',
            'printingController',
            'queryReplaceCommands',
            'rectangleCommands',
            'spellCommands',
            'vimCommands',  # Not likely to be useful.
        )
        for ivar in table:
            subcommander = getattr(c, ivar, None)
            if subcommander:
                func = getattr(subcommander, command, None)
                if func:
                    return func
        return None
    #@+node:felix.20210621233316.91: *4* server._get_focus
    def _get_focus(self) -> str:
        """Server helper method to get the focused panel name string"""
        tag = '_get_focus'
        try:
            w = g.app.gui.get_focus()
            focus = g.app.gui.widget_name(w)
        except Exception as e:
            raise ServerError(f"{tag}: exception trying to get the focused widget: {e}")
        return focus
    #@+node:ekr.20220817091731.1: *4* server._get_optional_p
    def _get_optional_p(self, param: dict) -> Optional[Position]:
        """
        Return _ap_to_p(param["ap"]) or None.
        """
        tag = '_get_ap'
        c = self._check_c(param)
        if not c:  # pragma: no cover
            raise ServerError(f"{tag}: no c")
        ap = param.get("ap")
        if ap:
            p = self._ap_to_p(ap, c)  # Conversion
            if p:
                if not c.positionExists(p):  # pragma: no cover
                    raise ServerError(f"{tag}: position does not exist. ap: {ap!r}")
                return p  # Return the position
        return None
    #@+node:felix.20210621233316.90: *4* server._get_p
    def _get_p(self, param: dict) -> Position:
        """
        Return _ap_to_p(param["ap"]) or c.p.
        """
        tag = '_get_ap'
        c = self._check_c(param)
        if not c:  # pragma: no cover
            raise ServerError(f"{tag}: no c")

        ap = param.get("ap")
        if ap:
            p = self._ap_to_p(ap, c)  # Conversion
            if p:
                if not c.positionExists(p):  # pragma: no cover
                    raise ServerError(f"{tag}: position does not exist. ap: {ap!r}")
                return p  # Return the position
        # Fallback to c.p
        if not c.p:  # pragma: no cover
            raise ServerError(f"{tag}: no c.p")
        return c.p
    #@+node:felix.20210621233316.92: *4* server._get_position_d
    def _get_position_d(self, p: Position, c: Cmdr, includeChildren: bool = False) -> dict:
        """
        Return a python dict that is adding
        graphical representation data and flags
        to the base 'ap' dict from _p_to_ap.
        (To be used by the connected client GUI.)
        """
        d = self._p_to_ap(p)
        d['headline'] = p.h
        if p.v.u:
            # tags quantity first if any ua's present
            tagsQty = len(p.v.u.get("__node_tags", []))
            # Tags only if there are some present.
            if tagsQty > 0:
                d['nodeTags'] = tagsQty

            # Check for flag to send ua quantity instead of full ua's
            uAsBoolean = False
            uAsNumber = False
            if g.leoServer.leoServerConfig:
                uAsBoolean = g.leoServer.leoServerConfig.get("uAsBoolean", False)
                uAsNumber = g.leoServer.leoServerConfig.get("uAsNumber", False)
            if g.leoServer.leoServerConfig and (uAsBoolean or uAsNumber):
                uaQty = len(p.v.u)  # number will be 'true' if any keys are present
                if tagsQty > 0 and uaQty > 0:
                    uaQty = uaQty - 1
                # set number pre-decremented if __node_tags were present
                d['u'] = uaQty
            else:
                # Normal output if no tags set
                d['u'] = p.v.u
        if bool(p.b):
            d['hasBody'] = True
        if p.hasChildren():
            d['hasChildren'] = True
            # includeChildren flag is used by get_structure
            if includeChildren:
                d['children'] = [
                    self._get_position_d(child, c, includeChildren=True) for child in p.children()
                ]

        if p.isCloned():
            d['cloned'] = True
        if p.isDirty():
            d['dirty'] = True
        if p.isExpanded():
            d['expanded'] = True
        if p.isMarked():
            d['marked'] = True
        if p.isAnyAtFileNode():
            d['atFile'] = True
        if p == c.p:
            d['selected'] = True
        return d
    #@+node:felix.20230202225736.1: *4* server._get_sel_range
    def _get_sel_range(self) -> tuple[int, int]:
        """
        Returns the selection range from either the body widget,
        or the selected node headline widget.

        Returns [0, 0] if any problem occurs getting leoBridge's current focused widget
        """
        w = g.app.gui.get_focus()
        try:
            if hasattr(w, "sel"):
                return w.sel[0], w.sel[1]
            c = self.c
            gui_w = c.edit_widget(c.p)
            selRange = gui_w.getSelectionRange()
            return selRange
        except Exception:
            print("Error retrieving current focused widget selection range.")
            return 0, 0
    #@+node:felix.20210705211625.1: *4* server._is_jsonable
    def _is_jsonable(self, x: Any) -> bool:
        """
        Makes sure that an object is serializable in JSON.
        Returns true if it is. False otherwise.
        """
        try:
            json.dumps(x, cls=SetEncoder)
            return True
        except(TypeError, OverflowError):
            return False
    #@+node:felix.20210621233316.94: *4* server._make_minimal_response
    def _make_minimal_response(self, package: Package = None) -> str:
        """
        Return a json string representing a response dict.

        The 'package' kwarg, if present, must be a python dict describing a
        response. package may be an empty dict or None.

        The 'p' kwarg, if present, must be a position.

        First, this method creates a response (a python dict) containing all
        the keys in the 'package' dict.

        Then it adds 'id' to the package.

        Finally, this method returns the json string corresponding to the
        response.
        """
        if package is None:
            package = {}

        if not self._is_jsonable(package):
            package = {}

        # Always add id.
        package["id"] = self.current_id

        return json.dumps(package, separators=(',', ':'), cls=SetEncoder)
    #@+node:felix.20210621233316.93: *4* server._make_response
    def _make_response(self, package: Package = None) -> str:
        """
        Return a json string representing a response dict.

        The 'package' kwarg, if present, must be a python dict describing a
        response. package may be an empty dict or None.

        The 'p' kwarg, if present, must be a position.

        First, this method creates a response (a python dict) containing all
        the keys in the 'package' dict, with the following added keys:

        - "id":         The incoming id.
        - "commander":  A dict describing self.c.
        - "node":       None, or an archived position describing self.c.p.

        Finally, this method returns the json string corresponding to the
        response.
        """
        global traces
        tag = '_make_response'
        trace = self.log_flag or 'response' in traces
        verbose = 'verbose' in traces
        c = self.c  # It is valid for c to be None.
        if package is None:
            package = {}
        p = package.get("p")
        if p:
            del package["p"]
        # if not serializable, include 'p' if present at best.
        if not self._is_jsonable(package):
            if p:
                package = {'p': p}
            else:
                package = {}

        # Raise an *internal* error if checks fail.
        if isinstance(package, str):  # pragma: no cover
            raise InternalServerError(f"{tag}: bad package kwarg: {package!r}")
        if p and not isinstance(p, Position):  # pragma: no cover
            raise InternalServerError(f"{tag}: bad p kwarg: {p!r}")
        if p and not c:  # pragma: no cover
            raise InternalServerError(f"{tag}: p but not c")
        if p and not c.positionExists(p):  # pragma: no cover
            raise InternalServerError(f"{tag}: p does not exist: {p!r}")
        if c and not c.p:  # pragma: no cover
            raise InternalServerError(f"{tag}: empty c.p")

        # Always add id
        package["id"] = self.current_id

        # The following keys are relevant only if there is an open commander.
        if c:
            # Allow commands, especially _get_redraw_d, to specify p!
            p = p or c.p
            package["commander"] = {
                "changed": c.isChanged(),
                "fileName": c.fileName(),  # Can be None for new files.
                "id": id(c),
            }
            # Add all the node data, including:
            # - "node": self._p_to_ap(p) # Contains p.gnx, p.childIndex and p.stack.
            # - All the *cheap* redraw data for p.
            redraw_d = self._get_position_d(p, c)
            package["node"] = redraw_d

        # Handle traces.
        if trace and verbose:  # pragma: no cover
            g.printObj(package, tag=f"response {self.current_id}")
            print('', flush=True)
        elif trace:  # pragma: no cover
            keys = sorted(package.keys())
            keys_s = ', '.join(keys)
            print(f"response {self.current_id:<4} {keys_s}", flush=True)

        return json.dumps(package, separators=(',', ':'), cls=SetEncoder)
    #@+node:felix.20210621233316.95: *4* server._p_to_ap
    def _p_to_ap(self, p: Position) -> dict:
        """
        * From Leo plugin leoflexx.py *

        Convert Leo position p to a serializable archived position.

        This returns only position-related data.
        get_position_data returns all data needed to redraw the screen.
        """
        stack = [{'gnx': v.gnx, 'childIndex': childIndex}
            for (v, childIndex) in p.stack]
        return {
            'childIndex': p._childIndex,
            'gnx': p.v.gnx,
            'stack': stack,
        }
    #@+node:felix.20210621233316.96: *4* server._positionFromGnx
    def _positionFromGnx(self, gnx: str, c: Cmdr) -> Optional[Position]:
        """Return first p node with this gnx or false"""
        for p in c.all_unique_positions():
            if p.v.gnx == gnx:
                return p
        return None
    #@+node:felix.20210622232409.1: *4* server._send_async_output & helper
    def _send_async_output(self, package: Package, toAll: bool = False) -> None:
        """
        Send data asynchronously to the client
        """
        tag = "send async output"
        jsonPackage = json.dumps(package, separators=(',', ':'), cls=SetEncoder)
        if "async" not in package:
            raise InternalServerError(f"\n{tag}: async member missing in package {jsonPackage} \n")
        if self.loop:
            self.loop.create_task(self._async_output(jsonPackage, toAll))
        elif not g.unitTesting:
            raise InternalServerError(f"\n{tag}: loop not ready {jsonPackage} \n")
    #@+node:felix.20210621233316.89: *5* server._async_output
    async def _async_output(self,
        json: str,
        toAll: bool = False,
    ) -> None:  # pragma: no cover (tested in server)
        """Output json string to the web_socket"""
        global connectionsTotal
        tag = '_async_output'
        outputBytes = bytes(json, 'utf-8')
        if toAll:
            if connectionsPool:  # asyncio.wait doesn't accept an empty list
                await asyncio.wait([
                    asyncio.create_task(client.send(outputBytes)) for client in connectionsPool
                ])
            else:
                g.trace(f"{tag}: no web socket. json: {json!r}")
        else:
            if self.web_socket:
                await self.web_socket.send(outputBytes)
            else:
                g.trace(f"{tag}: no web socket. json: {json!r}")
    #@+node:felix.20210621233316.97: *4* server._test_round_trip_positions
    def _test_round_trip_positions(self, c: Cmdr) -> None:  # pragma: no cover (tested in client).
        """Test the round tripping of p_to_ap and ap_to_p."""
        tag = '_test_round_trip_positions'
        for p in c.all_unique_positions():
            ap = self._p_to_ap(p)
            p2 = self._ap_to_p(ap, c)
            if p != p2:
                self._dump_outline(c)
                raise ServerError(f"{tag}: round-trip failed: ap: {ap!r}, p: {p!r}, p2: {p2!r}")
    #@+node:felix.20210625002950.1: *4* server._yieldAllRootChildren
    def _yieldAllRootChildren(self, c: Cmdr) -> Generator:
        """Return all root children P nodes"""
        p = c.rootPosition()
        while p:
            yield p
            p.moveToNext()

    #@-others
#@+node:felix.20210621233316.105: ** main & helpers
def main() -> None:  # pragma: no cover (tested in client)
    """python script for leo integration via leoBridge"""

    global websockets
    global wsHost, wsPort, wsLimit, wsPersist, wsSkipDirty, argFile
    if not websockets:
        print('websockets not found')
        print('pip install websockets')
        return

    #@+others
    #@+node:felix.20210807214524.1: *3* function: cancel_tasks
    def cancel_tasks(to_cancel: Any, loop: Loop) -> None:
        if not to_cancel:
            return

        for task in to_cancel:
            task.cancel()

        loop.run_until_complete(asyncio.gather(*to_cancel, return_exceptions=True))

        for task in to_cancel:
            if task.cancelled():
                continue
            if task.exception() is not None:
                loop.call_exception_handler(
                    {
                        "message": "unhandled exception during asyncio.run() shutdown",
                        "exception": task.exception(),
                        "task": task,
                    }
                )
    #@+node:ekr.20210825115746.1: *3* function: center_tk_frame
    def center_tk_frame(top: Any) -> None:
        """Center the top-level Frame."""
        # https://stackoverflow.com/questions/3352918
        top.update_idletasks()
        screen_width = top.winfo_screenwidth()
        screen_height = top.winfo_screenheight()
        size = tuple(int(_) for _ in top.geometry().split('+')[0].split('x'))
        x = screen_width / 2 - size[0] / 2
        y = screen_height / 2 - size[1] / 2
        top.geometry("+%d+%d" % (x, y))
    #@+node:felix.20210804130751.1: *3* function: close_server
    def close_Server() -> None:
        """
        Close the server by stopping the loop
        """
        print('Closing Leo Server', flush=True)
        if loop.is_running():
            loop.stop()
        else:
            print('Loop was not running', flush=True)
    #@+node:ekr.20210825172913.1: *3* function: general_yes_no_dialog & helpers
    def general_yes_no_dialog(
        c: Cmdr,
        title: str,  # Not used.
        message: str = None,  # Must exist.
        yesMessage: str = "&Yes",  # Not used.
        noMessage: str = "&No",  # Not used.
        yesToAllMessage: str = None,  # Not used.
        defaultButton: str = "Yes",  # Not used
        cancelMessage: str = None,  # Not used.
    ) -> str:
        """
        Monkey-patched implementation of LeoQtGui.runAskYesNoCancelDialog
        offering *only* Yes/No buttons.

        This will fallback to a tk implementation if the qt library is unavailable.

        This raises a dialog and return either 'yes' or 'no'.
        """
        #@+others  # define all helper functions.
        #@+node:ekr.20210801175921.1: *4* function: tk_runAskYesNoCancelDialog & helpers
        def tk_runAskYesNoCancelDialog(c: Cmdr) -> str:
            """
            Tk version of LeoQtGui.runAskYesNoCancelDialog, with *only* Yes/No buttons.
            """
            if g.unitTesting:
                return None
            root = top = val = None  # Non-locals
            #@+others  # define helper functions
            #@+node:ekr.20210801180311.4: *5* function: create_yes_no_frame
            def create_yes_no_frame(message: str, top: Any) -> None:
                """Create the dialog's frame."""
                frame = Tk.Frame(top)
                frame.pack(side="top", expand=1, fill="both")
                label = Tk.Label(frame, text=message, bg="white")
                label.pack(pady=10)
                # Create buttons.
                f = Tk.Frame(top)
                f.pack(side="top", padx=30)
                b = Tk.Button(f, width=6, text="Yes", bd=4, underline=0, command=yesButton)
                b.pack(side="left", padx=5, pady=10)
                b = Tk.Button(f, width=6, text="No", bd=2, underline=0, command=noButton)
                b.pack(side="left", padx=5, pady=10)
            #@+node:ekr.20210801180311.5: *5* function: callbacks
            def noButton(event: Event = None) -> None:
                """Do default click action in ok button."""
                nonlocal val
                print(f"Not saved: {c.fileName()}")
                val = "no"
                top.destroy()

            def yesButton(event: Event = None) -> None:
                """Do default click action in ok button."""
                nonlocal val
                print(f"Saved: {c.fileName()}")
                val = "yes"
                top.destroy()
            #@-others
            root = Tk.Tk()
            root.withdraw()
            root.update()

            top = Tk.Toplevel(root)
            top.title("Saved changed outline?")
            create_yes_no_frame(message, top)
            top.bind("<Return>", yesButton)
            top.bind("y", yesButton)
            top.bind("Y", yesButton)
            top.bind("n", noButton)
            top.bind("N", noButton)
            top.lift()

            center_tk_frame(top)

            top.grab_set()  # Make the dialog a modal dialog.

            root.update()
            root.wait_window(top)

            top.destroy()
            root.destroy()
            return val
        #@+node:ekr.20210825170952.1: *4* function: qt_runAskYesNoCancelDialog
        def qt_runAskYesNoCancelDialog(c: Cmdr) -> str:
            """
            Qt version of LeoQtGui.runAskYesNoCancelDialog, with *only* Yes/No buttons.
            """
            if g.unitTesting:
                return None
            dialog = QtWidgets.QMessageBox(None)
            dialog.setIcon(Information.Warning)
            dialog.setWindowTitle("Saved changed outline?")
            if message:
                dialog.setText(message)
            # Creation order determines returned value.
            yes = dialog.addButton(yesMessage, ButtonRole.YesRole)
            dialog.addButton(noMessage, ButtonRole.NoRole)
            dialog.setDefaultButton(yes)
            # Set the Leo icon.
            core_dir = os.path.dirname(__file__)
            icon_path = os.path.join(core_dir, "..", "Icons", "leoApp.ico")
            if os.path.exists(icon_path):
                pixmap = QtGui.QPixmap()
                pixmap.load(icon_path)
                icon = QtGui.QIcon(pixmap)
                dialog.setWindowIcon(icon)
            # None of these grabs focus from the console window.
            dialog.raise_()
            dialog.setFocus()
            g.app.processEvents()
            # val is the same as the creation order.
            val = dialog.exec()
            if val == 0:
                print(f"Saved: {c.fileName()}")
                return 'yes'
            print(f"Not saved: {c.fileName()}")
            return 'no'
        #@-others
        try:
            # Careful: raise the Tk dialog if there are errors in the Qt code.
            from leo.core.leoQt import QtGui, QtWidgets
            from leo.core.leoQt import ButtonRole, Information
            if QtGui and QtWidgets:
                app = QtWidgets.QApplication([])
                assert app
                val = qt_runAskYesNoCancelDialog(c)
                assert val in ('yes', 'no')
                return val
        except Exception:
            pass
        if Tk:
            return tk_runAskYesNoCancelDialog(c)
        # #2512: There is no way to raise a dialog.
        return 'yes'  # Just save the file!

    #@+node:felix.20210621233316.107: *3* function: get_args
    def get_args() -> None:  # pragma: no cover
        """
        Get arguments from the command line and sets them globally.
        """
        global wsHost, wsPort, wsLimit, wsPersist, wsSkipDirty, argFile, traces

        def leo_file(s: str) -> str:
            if os.path.exists(s):
                return s
            print(f"\nNot a .leo file: {s!r}")
            sys.exit(1)

        description = ''.join([
            "  leoserver.py\n",
            "  ------------\n",
            "  Offers single or multiple concurrent websockets\n",
            "  for JSON based remote-procedure-calls\n",
            "  to a shared instance of leo.core.leoBridge\n",
            "  \n",
            "  Clients may be written in any language:\n",
            "  - leo.core.leoclient is an example client written in python.\n",
            "  - leoInteg (https://github.com/boltex/leointeg) is written in typescript.\n"
        ])
        # Usage:
        # leoserver.py [-a <address>] [-p <port>] [-l <limit>] [-f <file>] [--dirty] [--persist]
        usage = 'python leo.core.leoserver [options...]'
        trace_s = 'request,response,verbose'
        valid_traces = [z.strip() for z in trace_s.split(',')]
        parser = argparse.ArgumentParser(description=description, usage=usage,
            formatter_class=argparse.RawTextHelpFormatter)
        add = parser.add_argument
        add('-a', '--address', dest='wsHost', type=str, default=wsHost, metavar='STR',
            help='server address. Defaults to ' + str(wsHost))
        add('-p', '--port', dest='wsPort', type=int, default=wsPort, metavar='N',
            help='port number. Defaults to ' + str(wsPort))
        add('-l', '--limit', dest='wsLimit', type=int, default=wsLimit, metavar='N',
            help='maximum number of clients. Defaults to ' + str(wsLimit))
        add('-f', '--file', dest='argFile', type=leo_file, metavar='PATH',
            help='open a .leo file at startup')
        add('--persist', dest='wsPersist', action='store_true',
            help='do not quit when last client disconnects')
        add('-d', '--dirty', dest='wsSkipDirty', action='store_true',
            help='do not warn about dirty files when quitting')
        add('--trace', dest='traces', type=str, metavar='STRINGS',
            help=f"comma-separated list of {trace_s}")
        add('-v', '--version', dest='v', action='store_true',
            help='show version and exit')
        # Parse
        args = parser.parse_args()
        # Handle the args and set them up globally
        wsHost = args.wsHost
        wsPort = args.wsPort
        wsLimit = args.wsLimit
        wsPersist = bool(args.wsPersist)
        wsSkipDirty = bool(args.wsSkipDirty)
        argFile = args.argFile
        if args.traces:
            ok = True
            for z in args.traces.split(','):
                if z in valid_traces:
                    traces.append(z)
                else:
                    ok = False
                    print(f"Ignoring invalid --trace value: {z!r}", flush=True)
            if not ok:
                print(f"Valid traces are: {','.join(valid_traces)}", flush=True)
            print(f"--trace={','.join(traces)}", flush=True)
        if args.v:
            print(__version__)
            sys.exit(0)
        # Sanitize limit.
        if wsLimit < 1:
            wsLimit = 1
    #@+node:felix.20210803174312.1: *3* function: notify_clients
    async def notify_clients(action: str, excludedConn: Any = None) -> None:
        global connectionsTotal
        if connectionsPool:  # asyncio.wait doesn't accept an empty list
            opened = bool(controller.c)  # c can be none if no files opened
            m = json.dumps({
                "async": "refresh",
                "action": action,
                "opened": opened,
            }, separators=(',', ':'), cls=SetEncoder)
            clientSetCopy = connectionsPool.copy()
            if excludedConn:
                clientSetCopy.discard(excludedConn)
            if clientSetCopy:
                # if still at least one to notify
                await asyncio.wait([
                    asyncio.create_task(client.send(m)) for client in clientSetCopy
                ])
    #@+node:felix.20210803174312.2: *3* function: register_client
    async def register_client(websocket: Socket) -> None:
        global connectionsTotal
        connectionsPool.add(websocket)
        await notify_clients("unregister", websocket)
    #@+node:felix.20210807160828.1: *3* function: save_dirty
    def save_dirty() -> None:
        """
        Ask the user about dirty files if any remained opened.
        """
        # Monkey-patch the dialog method first.
        g.app.gui.runAskYesNoCancelDialog = general_yes_no_dialog
        # Loop all commanders and 'close' them for dirty check
        commanders = g.app.commanders()
        for commander in commanders:
            if commander.isChanged() and commander.fileName():
                commander.close()  # Patched 'ask' methods will open dialog
    #@+node:felix.20210803174312.3: *3* function: unregister_client
    async def unregister_client(websocket: Socket) -> None:
        global connectionsTotal
        connectionsPool.remove(websocket)
        await notify_clients("unregister")
    #@+node:felix.20210621233316.106: *3* function: ws_handler (server)
    async def ws_handler(websocket: Socket, path: str) -> None:
        """
        The web socket handler: server.ws_server.

        It must be a coroutine accepting two arguments: a WebSocketServerProtocol and the request URI.
        """
        global connectionsTotal, wsLimit
        tag = 'server'
        trace = False
        verbose = False
        connected = False

        try:
            # Websocket connection startup
            if connectionsTotal >= wsLimit:
                print(f"{tag}: User Refused, Total: {connectionsTotal}, Limit: {wsLimit}", flush=True)
                await websocket.close(1001)
                return
            connected = True  # local variable
            connectionsTotal += 1  # global variable
            print(f"{tag}: User Connected, Total: {connectionsTotal}, Limit: {wsLimit}", flush=True)
            # If first connection set it as the main client connection
            controller._init_connection(websocket)
            await register_client(websocket)
            # Start by sending empty as 'ok'.
            n = 0
            await websocket.send(controller._make_response({"leoID": g.app.leoID}))
            controller._emit_signon()

            # Websocket connection message handling loop
            async for json_message in websocket:
                try:
                    n += 1
                    d = None
                    d = json.loads(json_message)
                    if trace and verbose:
                        print(f"{tag}: got: {d}", flush=True)
                    elif trace:
                        print(f"{tag}: got: {d}", flush=True)
                    answer = controller._do_message(d)
                except TerminateServer as e:
                    rcvd = websockets.frames.Close(websockets.frames.CloseCode.NORMAL_CLOSURE, e.__str__())
                    raise websockets.exceptions.ConnectionClosed(rcvd, None, None)
                except ServerError as e:
                    data = f"{d}" if d else f"json syntax error: {json_message!r}"
                    error = f"{tag}:  ServerError: {e}...\n{tag}:  {data}"
                    print("", flush=True)
                    print(error, flush=True)
                    print("", flush=True)
                    package = {
                        "id": controller.current_id,
                        "action": controller.action,
                        "request": data,
                        "ServerError": f"{e}",
                    }
                    answer = json.dumps(package, separators=(',', ':'), cls=SetEncoder)
                except InternalServerError as e:  # pragma: no cover
                    print(f"{tag}: InternalServerError {e}", flush=True)
                    break
                except Exception as e:  # pragma: no cover
                    print(f"{tag}: Unexpected Exception! {e}", flush=True)
                    g.print_exception()
                    print('', flush=True)
                    break
                await websocket.send(answer)

                # If not a 'getter' send refresh signal to other clients
                if controller.action[0:5] != "!get_" and controller.action != "!do_nothing":
                    await notify_clients(controller.action, websocket)

        except websockets.exceptions.ConnectionClosedError as e:  # pragma: no cover
            print(f"{tag}: connection closed error: {e}")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"{tag}: connection closed: {e}")
        finally:
            if connected:
                connectionsTotal -= 1
                await unregister_client(websocket)
                print(f"{tag} connection finished.  Total: {connectionsTotal}, Limit: {wsLimit}")
            # Check for persistence flag if all connections are closed
            if connectionsTotal == 0 and not wsPersist:
                print("Shutting down leoserver")
                # Preemptive closing of tasks
                for task in asyncio.all_tasks():
                    task.cancel()
                close_Server()  # Stops the run_forever loop
    #@-others

    # Make the first real line of output more visible.
    print("", flush=True)

    # Sets sHost, wsPort, wsLimit, wsPersist, wsSkipDirty fileArg and traces
    get_args()  # Set global values from the command line arguments
    print(f"Starting LeoBridge Server {v1}.{v2}.{v3} (Launch with -h for help)", flush=True)

    # Open leoBridge.
    controller = LeoServer()  # Single instance of LeoServer, i.e., an instance of leoBridge
    if argFile:
        # Open specified file argument
        try:
            print(f"Opening file: {argFile}", flush=True)
            controller.open_file({"filename": argFile})
        except Exception:
            print("Opening file failed", flush=True)

    # Start the server.
    loop = asyncio.get_event_loop()

    try:
        try:
            server = websockets.serve(ws_handler, wsHost, wsPort, max_size=None)
            realtime_server = loop.run_until_complete(server)
        except OSError as e:
            print(e)
            print("Trying with IPv4 Family", flush=True)
            server = websockets.serve(
                ws_handler, wsHost, wsPort,
                family=socket.AF_INET, max_size=None)
            realtime_server = loop.run_until_complete(server)

        signon = SERVER_STARTED_TOKEN + f" at {wsHost} on port: {wsPort}.\n"
        if wsPersist:
            signon = signon + "Persistent server\n"
        if wsSkipDirty:
            signon = signon + "No prompt about dirty file(s) when closing server\n"
        if wsLimit > 1:
            signon = signon + f"Total client limit is {wsLimit}.\n"
        signon = signon + "Ctrl+c to break"
        print(signon, flush=True)
        loop.run_forever()

    except KeyboardInterrupt:
        print("Process interrupted", flush=True)

    finally:
        # Execution continues here after server is interrupted (e.g. with ctrl+c)
        realtime_server.close()
        if not wsSkipDirty:
            print("Checking for changed commanders...", flush=True)
            save_dirty()
        cancel_tasks(asyncio.all_tasks(loop), loop)
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        asyncio.set_event_loop(None)
        print("Stopped leobridge server", flush=True)
#@-others
if __name__ == '__main__':
    # pytest will *not* execute this code.
    main()
#@-leo
