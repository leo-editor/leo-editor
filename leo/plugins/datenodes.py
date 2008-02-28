#@+leo-ver=4-thin
#@+node:ekr.20060807103814.1:@thin datenodes.py
"""
This plugin adds 'date nodes' (nodes with dates as their headlines) to the current outline.
Date nodes may be added one at a time, a month's-worth at a time, or a year's-worth at a time.
There are options to omit saturdays and sundays. The format of the labels (headlines) is configurable.
"""

#@@language python
#@@tabwidth -4

__version__ = "0.6"
#@<< version history >>
#@+node:gfunch.20041207100416.2:<< version history >>
#@@nocolor
#@+at
# 
# 0.1: Initial version.
# 0.2: Improved menu structure. Added ini file.
# 0.3: Changed docstring slightly.
# 0.4: Added event=None to insert_xxx_node.
# 0.5: Added options to omit saturdays and sundays. Use leoSettings.leo 
# instead of datenodes.ini for storing options.
# 0.6: Removed @c from most nodes: this is not needed.  Also removed .ini file 
# from cvs.
#@-at
#@nonl
#@-node:gfunch.20041207100416.2:<< version history >>
#@nl

#@<< imports >>
#@+node:gfunch.20041207100416.3:<< imports >>
import leoGlobals as g
import leoPlugins

import calendar
import codecs
import datetime
#@-node:gfunch.20041207100416.3:<< imports >>
#@nl

#@+others
#@+node:gfunch.20041207100416.5:class DateNodes
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
    boolean_settings = ["datenodes_month_node_omit_saturdays", "datenodes_month_node_omit_sundays", 
                        "datenodes_year_node_omit_saturdays", "datenodes_year_node_omit_sundays"]

    ascii_encoder = codecs.getencoder("ASCII")

    #@    @+others
    #@+node:gfunch.20041207100416.6:__init__
    def __init__(self, c):
        self.c = c
        self._get_settings()
    #@-node:gfunch.20041207100416.6:__init__
    #@+node:gfunch.20041209073652:_get_settings
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
    #@-node:gfunch.20041209073652:_get_settings
    #@+node:gfunch.20041208095742:_format_node_label
    def _format_node_label(self, date, fmt):
        """Format a node label (heading)."""

        # Convert fmt to ASCII string, because strftime() doesn't like Unicode strings
        try:
            ascii_fmt = DateNodes.ascii_encoder(fmt)[0]
        except UnicodeError:
            g.es("datenodes plugin: WARNING: The format string " + fmt + " contains non-ASCII characters.")
            ascii_fmt = DateNodes.ascii_encoder(fmt, replace)[0]

        return date.strftime(ascii_fmt)

    #@-node:gfunch.20041208095742:_format_node_label
    #@+node:dcb.20060806185031:_insert_date_node
    def _insert_date_node(self, parent, date, format):

        c = self.c

        node = parent.insertAsLastChild()

        label = self._format_node_label(date, format)

        c.setHeadString(node,label)

        return node

    #@-node:dcb.20060806185031:_insert_date_node
    #@+node:dcb.20060806183810:_insert_day_node
    def _insert_day_node(self, parent, date, day_fmt):

        c = self.c
        day_node = self._insert_date_node(parent, date, day_fmt)

        c.setBodyString(day_node,self.settings["body_text"])

        return day_node
    #@nonl
    #@-node:dcb.20060806183810:_insert_day_node
    #@+node:gfunch.20041207100416.11:_insert_month_node
    def _insert_month_node(self, parent, date, day_fmt, month_fmt, omit_saturdays, omit_sundays):
        """Insert a months-worth of date nodes into the outline ."""

        month_node = self._insert_date_node(parent, date, month_fmt)

        year, month = date.timetuple()[:2]

        first_day_of_month, num_days = calendar.monthrange(year, month)

        for day in range(1, num_days + 1):
            day_date = datetime.date(year, month, day)
            isoweekday = day_date.isoweekday()

            if (isoweekday == 6 and omit_saturdays) or (isoweekday == 7 and omit_sundays):
                continue

            self._insert_day_node(parent = month_node, date = day_date, day_fmt = day_fmt)

        return month_node
    #@-node:gfunch.20041207100416.11:_insert_month_node
    #@+node:gfunch.20041207100416.12:_insert_year_node
    def _insert_year_node(self, parent, date, day_fmt, month_fmt, year_fmt, omit_saturdays, omit_sundays):
        """Insert a years-worth of date nodes into the outline."""

        year_node = self._insert_date_node(parent, date, year_fmt)

        year, month, day = date.timetuple()[:3]

        for month in range(1, 13):
            month_date = datetime.date(year, month, day)

            self._insert_month_node(parent = year_node, date = month_date, day_fmt = day_fmt, month_fmt = month_fmt, 
                                    omit_saturdays = omit_saturdays, omit_sundays = omit_sundays)


        return year_node
    #@nonl
    #@-node:gfunch.20041207100416.12:_insert_year_node
    #@+node:gfunch.20041208074734:insert_day_node
    def insert_day_node(self, event = None):

        self.c.beginUpdate()

        today = datetime.date.today()
        day_fmt = self.settings["day_node_headline"]

        day_node = self._insert_day_node(self.c.currentPosition(), today, day_fmt)

        self.c.selectPosition(day_node)
        self.c.endUpdate()



    #@-node:gfunch.20041208074734:insert_day_node
    #@+node:dcb.20060806183928:insert_month_node
    def insert_month_node(self, event = None):

        self.c.beginUpdate()

        today = datetime.date.today()
        day_fmt = self.settings["month_node_day_headline"]
        month_fmt = self.settings["month_node_month_headline"]
        omit_saturdays = self.settings["month_node_omit_saturdays"]
        omit_sundays = self.settings["month_node_omit_sundays"]


        month_node = self._insert_month_node(self.c.currentPosition(), today, day_fmt, month_fmt, omit_saturdays, omit_sundays)

        self.c.selectPosition(month_node)
        self.c.endUpdate()


    #@-node:dcb.20060806183928:insert_month_node
    #@+node:dcb.20060806184117:insert_year_node
    def insert_year_node(self, event = None):
        self.c.beginUpdate()

        today = datetime.date.today()
        day_fmt = self.settings["year_node_day_headline"]
        month_fmt = self.settings["year_node_month_headline"]
        year_fmt = self.settings["year_node_year_headline"]
        omit_saturdays = self.settings["year_node_omit_saturdays"]
        omit_sundays = self.settings["year_node_omit_sundays"]

        year_node = self._insert_year_node(self.c.currentPosition(), today, day_fmt, month_fmt, year_fmt, omit_saturdays, omit_sundays)

        self.c.selectPosition(year_node)
        self.c.endUpdate()
    #@-node:dcb.20060806184117:insert_year_node
    #@-others
#@-node:gfunch.20041207100416.5:class DateNodes
#@+node:gfunch.20041207100654:on_create
def on_create(tag, keywords):

    c = keywords.get("c")

    # establish a class instance
    instance = DateNodes(c)


    # Create the plug-in menu.

    # create a menu separator
    c.frame.menu.createMenuItemsFromTable("Outline", [("-", None, None),])

    # create an expandable menu
    table = [("Single Day", None, instance.insert_day_node),
             ("Full Month", None, instance.insert_month_node),
             ("Full Year", None, instance.insert_year_node)]

    expandMenu = c.frame.menu.createNewMenu("Insert Date Nodes...", "Outline")
    c.frame.menu.createMenuEntries(expandMenu, table, dynamicMenu = True)
#@nonl
#@-node:gfunch.20041207100654:on_create
#@-others

if 1: # OK for unit testing.
    leoPlugins.registerHandler("after-create-leo-frame", on_create)
    g.plugin_signon(__name__)
#@nonl
#@-node:ekr.20060807103814.1:@thin datenodes.py
#@-leo
