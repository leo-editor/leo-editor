#@+leo-ver=5-thin
#@+node:ekr.20060807103814.1: * @file ../plugins/datenodes.py
#@+<< docstring >>
#@+node:bobjack.20080615065747.4: ** << docstring >>
"""
Allows users to insert headlines containing dates.

'Date nodes' are nodes that have dates in their headlines. They may be added to
the outline one at a time, a month's-worth at a time, or a year's-worth at a
time. The format of the labels (headlines) is configurable.

There are options to omit Saturdays and Sundays.

An 'Insert Date Nodes ...' submenu will be created (by default) in the 'Outline'
menu.  This menu can be suppressed by using either of the following settings:

    - @bool suppress-datenodes-menus
    - @bool suppress-all-plugins-menus

The following commands are available for use via the minibuffer or in
@menu/@popup settings.

    - datenodes-today
    - datenodes-this-month
    - datenodes-this-year

"""
#@-<< docstring >>

#@+<< todo >>
#@+node:bobjack.20080615065747.5: ** << todo >>
#@@nocolor
#@+at
#
# - add commands to allow day, month, year to be input via minibuffer
#
# - add a calendar widget to allow dates to be entered via gui
#
# - add extra methods to controller to make it easier to use the plugin from scripts
#
# - allow date ranges to be specified
#
# - add a dialog that allows all parameters to be slected prior to insertion
#@-<< todo >>

#@+<< imports >>
#@+node:gfunch.20041207100416.3: ** << imports >>
import calendar
import codecs
import datetime
from leo.core import leoGlobals as g
#@-<< imports >>

#@+others
#@+node:bobjack.20080615065747.2: ** init
def init():
    """Return True if the plugin has loaded successfully."""
    g.registerHandler("after-create-leo-frame", on_create)
    g.plugin_signon(__name__)
    return True  # OK for unit testing.
#@+node:gfunch.20041207100416.5: ** class DateNodes
class DateNodes:
    """Main DateNodes class"""

    # The defaults for all possible settings.
    default_settings = {
        "datenodes_body_text": "To do...",
        "datenodes_day_node_headline": "%Y-%m-%d",
        "datenodes_month_node_day_headline": "%d: %A",
        "datenodes_month_node_month_headline": "%B %Y",
        "datenodes_month_node_omit_saturdays": True,
        "datenodes_month_node_omit_sundays": True,
        "datenodes_year_node_day_headline": "%d: %A",
        "datenodes_year_node_month_headline": "%B",
        "datenodes_year_node_year_headline": "%Y",
        "datenodes_year_node_omit_saturdays": True,
        "datenodes_year_node_omit_sundays": True
    }
    # Names of settings that have to be read with getBool()
    boolean_settings = [
        "datenodes_month_node_omit_saturdays",
        "datenodes_month_node_omit_sundays",
        "datenodes_year_node_omit_saturdays",
        "datenodes_year_node_omit_sundays"
    ]
    ascii_encoder = codecs.getencoder("ASCII")

    #@+others
    #@+node:gfunch.20041207100416.6: *3* __init__(DateNodes, datenodes.py)
    def __init__(self, c):
        self.c = c
        self._get_settings()

        for commandName, method in (
            ('datenodes-today', self.insert_day_node),
            ('datenodes-this-month', self.insert_month_node),
            ('datenodes-this-year', self.insert_year_node),
        ):
            c.k.registerCommand(commandName, method)
    #@+node:gfunch.20041209073652: *3* _get_settings
    def _get_settings(self):
        """Get any configuration options."""
        settings = {}
        for setting in DateNodes.default_settings:
            if setting in DateNodes.boolean_settings:
                getter = self.c.config.getBool
            else:
                getter = self.c.config.getString
            value = getter(setting)
            if value is None:
                value = DateNodes.default_settings[setting]
            settings[setting[10:]] = value  # Omit datenodes_ prefix
        self.settings = settings
    #@+node:dcb.20060806185031: *3* _insert_date_node
    def _insert_date_node(self, parent, date, format):

        p = parent.insertAsLastChild()
        p.h = date.strftime(g.toUnicode(format))
        return p
    #@+node:dcb.20060806183810: *3* _insert_day_node
    def _insert_day_node(self, parent, date, day_fmt):

        p = self._insert_date_node(parent, date, day_fmt)
        p.b = self.settings.get("body_text", '')
        return p
    #@+node:gfunch.20041207100416.11: *3* _insert_month_node
    def _insert_month_node(self, parent, date, day_fmt, month_fmt, omit_saturdays, omit_sundays):
        """Insert a months-worth of date nodes into the outline ."""

        month_node = self._insert_date_node(parent, date, month_fmt)
        year, month = date.timetuple()[:2]
        first_day_of_month, num_days = calendar.monthrange(year, month)
        for day in range(1, num_days + 1):
            day_date = datetime.date(year, month, day)
            isoweekday = day_date.isoweekday()
            if (
                (isoweekday == 6 and omit_saturdays) or
                (isoweekday == 7 and omit_sundays)
            ):
                continue
            self._insert_day_node(
                parent=month_node,
                date=day_date,
                day_fmt=day_fmt)
        return month_node
    #@+node:gfunch.20041207100416.12: *3* _insert_year_node
    def _insert_year_node(self,
        parent,
        date,
        day_fmt,
        month_fmt,
        year_fmt,
        omit_saturdays,
        omit_sundays,
    ):
        """Insert a years-worth of date nodes into the outline."""
        year_node = self._insert_date_node(parent, date, year_fmt)
        year, month, day = date.timetuple()[:3]
        for month in range(1, 13):
            month_date = datetime.date(year, month, day)
            self._insert_month_node(
                parent=year_node,
                date=month_date,
                day_fmt=day_fmt,
                month_fmt=month_fmt,
                omit_saturdays=omit_saturdays,
                omit_sundays=omit_sundays)
        return year_node
    #@+node:gfunch.20041208074734: *3* insert_day_node
    def insert_day_node(self, event=None):

        c = self.c
        today = datetime.date.today()
        day_fmt = self.settings["day_node_headline"]
        day_node = self._insert_day_node(self.c.p, today, day_fmt)
        c.selectPosition(day_node)
        c.redraw()
    #@+node:dcb.20060806183928: *3* insert_month_node
    def insert_month_node(self, event=None):

        c = self.c
        today = datetime.date.today()
        day_fmt = self.settings["month_node_day_headline"]
        month_fmt = self.settings["month_node_month_headline"]
        omit_saturdays = self.settings["month_node_omit_saturdays"]
        omit_sundays = self.settings["month_node_omit_sundays"]
        month_node = self._insert_month_node(
            c.p, today, day_fmt, month_fmt, omit_saturdays, omit_sundays)
        c.selectPosition(month_node)
        c.redraw()



    #@+node:dcb.20060806184117: *3* insert_year_node
    def insert_year_node(self, event=None):

        c = self.c
        today = datetime.date.today()
        day_fmt = self.settings["year_node_day_headline"]
        month_fmt = self.settings["year_node_month_headline"]
        year_fmt = self.settings["year_node_year_headline"]
        omit_saturdays = self.settings["year_node_omit_saturdays"]
        omit_sundays = self.settings["year_node_omit_sundays"]
        year_node = self._insert_year_node(
            c.p, today, day_fmt, month_fmt, year_fmt, omit_saturdays, omit_sundays)
        c.selectPosition(year_node)
        c.redraw()

    #@-others
#@+node:gfunch.20041207100654: ** on_create
def on_create(tag, keywords):

    c = keywords.get("c")
    if not (c and c.exists):
        return

    # Rewrite to eliminate a pylint complaint.
    if hasattr(c, 'theDateNodesController'):
        return

    # establish a class instance
    c.theDateNodesController = instance = DateNodes(c)

    #@+<< Create the plug-in menu. >>
    #@+node:bobjack.20080615065747.3: *3* << Create the plug-in menu. >>
    if not c.config.getBool('suppress-datenodes-menus'):
        # create a menu separator
        c.frame.menu.createMenuItemsFromTable("Outline", [("-", None, None),])

        # create an expandable menu
        table = [
            ("Single Day", None, instance.insert_day_node),
            ("Full Month", None, instance.insert_month_node),
            ("Full Year", None, instance.insert_year_node),
        ]
        expandMenu = c.frame.menu.createNewMenu("Insert Date Nodes...", "Outline")
        c.frame.menu.createMenuEntries(expandMenu, table)
    #@-<< Create the plug-in menu. >>

#@-others
#@@language python
#@@tabwidth -4

#@-leo
