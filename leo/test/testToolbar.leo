<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet ekr_test?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5">
	<global_window_position top="72" left="231" height="648" width="1052"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="bobjack.20080424195922.3" str_leo_pos="1,0"><vh>Startup</vh>
<v t="bobjack.20080424195922.2"><vh>@chapters</vh></v>
</v>
<v t="bobjack.20080616090010.4" a="E"><vh>@settings</vh>
<v t="bobjack.20080616090010.5"><vh>@data shortcut_button_data</vh></v>
</v>
<v t="bobjack.20080424195922.90" a="E"><vh>Buttons</vh>
<v t="bobjack.20080427085237.1"><vh>@button Fav Button</vh></v>
<v t="bobjack.20080427084403.1"><vh>@button Say Hello!</vh></v>
<v t="bobjack.20080427183647.2"><vh>@button show-menu-tables</vh></v>
<v t="bobjack.20080424195922.94"><vh>@button Do Unit Tests</vh></v>
</v>
<v t="bobjack.20080611190121.2" a="E"><vh>Howto . . .</vh>
<v t="bobjack.20080611190121.3"><vh>. . . use compound widgets and dragHandles</vh></v>
</v>
<v t="bobjack.20080427091720.1" a="EM"><vh>@popup test-button-menu</vh>
<v t="bobjack.20080427091720.2"><vh>@item toolbar-delete-button</vh></v>
</v>
<v t="bobjack.20080613111554.19" a="M"><vh>@popup test-widget-menu</vh>
<v t="bobjack.20080613111554.20"><vh>@item toolbar-delete-button</vh></v>
</v>
<v t="bobjack.20080424195922.89" a="E"><vh>Unit Tests</vh>
<v t="bobjack.20080424195922.87" a="E"><vh>Test Plugin Controller</vh>
<v t="bobjack.20080424224706.1"><vh>@test module has required functions</vh></v>
<v t="bobjack.20080424195922.88"><vh>@test ivars exist and have correct type</vh></v>
<v t="bobjack.20080424224706.2" a="E"><vh>@test Controller Methods</vh>
<v t="bobjack.20080424224706.8"><vh>@test getPublicCommands</vh></v>
<v t="bobjack.20080424224706.22"><vh>@test getCommandList</vh></v>
<v t="bobjack.20080424224706.15"><vh>@test onClose</vh></v>
<v t="bobjack.20080424224706.16"><vh>@test onCreate</vh></v>
<v t="bobjack.20080424224706.23"><vh>@test registerCommands</vh></v>
<v t="bobjack.20080511155621.2"><vh>@test setDefaultContextMenus</vh></v>
</v>
</v>
</v>
</vnodes>
<tnodes>
<t tx="bobjack.20080424195922.2"></t>
<t tx="bobjack.20080424195922.3"></t>
<t tx="bobjack.20080424195922.87"></t>
<t tx="bobjack.20080424195922.88">import toolbar
plugin = toolbar

testController = tc = plugin.pluginController(c)

liveController = lc = plugin.controllers.get('c')

ivars = plugin.requiredIvars

for ivar, kind in ivars:
    
    if lc:
        assert hasattr(lc, ivar), \
            "Live controller does not have attribute: %s" % ivar
    
    assert hasattr(tc, ivar), \
        "Test controller does not have attribute: %s" % ivar
    
    if not kind:
        continue
        
    if lc:
        val = getattr(lc, ivar)
        assert isinstance(val, kind), \
            "Live Controller has ivar of wrong type\n\tGot type: %s\n\tExpected: %s" %(
                type(val), kind)
    
       
    val = getattr(tc, ivar)
    assert isinstance(val, kind), \
        "Test Controller has ivar of wrong type\n\tGot type: %s\n\tExpected: %s" %(
            type(val), kind)</t>
<t tx="bobjack.20080424195922.89"></t>
<t tx="bobjack.20080424195922.90">@
The following buttons are provided:

    show-toolbar-tables:

        This button pretty prints the rclick menu tables in
        c.context_menus to the log panel.

    show-button-events:

        After clicking this button, all clicks to the radio and
        check button menu items will be reported in the log
        panel.


    show-button-data:

        This button prints the status of the radio groups and check
        buttons that are used in the menus.

    do-unit-tests:

        This button runs all the unit tests for the toolbar
        plugin.  There are not many of them yet but that will
        change over time.

</t>
<t tx="bobjack.20080424195922.94">@
@btn fg = red
@btn bg = white
@btn tooltip = Run All Unit Tests
@btn menu = test-button-menu
@c

import leoTest
leoTest.doTests(c,all=True)
</t>
<t tx="bobjack.20080424224706.1">import toolbar
plugin = toolbar

for name in (
    'init',
    'onPreCreate',
    'onCreate',
    'onClose',
    'pluginController',
):
    assert hasattr(plugin, name), \
        "%s is missing"
</t>
<t tx="bobjack.20080424224706.2">from toolbar import pluginController

controller = pluginController(c)

headlines = [p.headString() for p in p.children_iter()]

for h in headlines:
    if h.startswith('@test'):
        h = h[5:].strip()
        
        assert hasattr(controller, h), \
            "Controller has no method %s" % h
            
# test for unknown methods


</t>
<t tx="bobjack.20080424224706.8"># test the commands are classes and instance of </t>
<t tx="bobjack.20080424224706.15"></t>
<t tx="bobjack.20080424224706.16"></t>
<t tx="bobjack.20080424224706.22"></t>
<t tx="bobjack.20080424224706.23"></t>
<t tx="bobjack.20080427084403.1">@
@btn bg = lightgreen
@btn fg = blue
@btn tooltip = Say: Hello!
@btn menu = test-button-menu
@c
g.es('Hello!')</t>
<t tx="bobjack.20080427085237.1">@
@btn icon = Tango\16x16\emblems\emblem-favorite.png
@btn bg=
@btn tooltip = Say: I Love Leo
@btn menu = test-button-menu
@c

g.es('I LOVE LEO')</t>
<t tx="bobjack.20080427091720.1"></t>
<t tx="bobjack.20080427091720.2">Remove Button

icon = Tango\16x16\actions\stop.png</t>
<t tx="bobjack.20080427183647.2">@
@btn tooltip=Pretty print c.context_menus
@c

from pprint import pformat

g.es_print(pformat(c.context_menus))</t>
<t tx="bobjack.20080511155621.2"></t>
<t tx="bobjack.20080611190121.2"></t>
<t tx="bobjack.20080611190121.3">@
In this howto I will demonstrate how to create a set of buttons (Cut, Copy and
Paste) and have the iconBar handle them as a single unit.

Use execute-script on this node to see the results of the demo code.

Icons will only be shown in the buttons if the Python Imaging Library is
availiable.

@c

bar = c.frame.iconBars['iconbar']

import Tkinter as Tk

# create the frame BEFORE the buttons

# a normal Tk.Frame may be used but getting the frame this way
# makes sure it has the proper parent and a default deleteButton method
# (which only actually removes the widget from the toolbar)

compoundFrame = bar.getWidgetFrame()

# the above statement could have been
#compoundFrame = c.frame.getIconWidgetFrame()


cutButton = bar.getButton(
    text='Cut',
    icon='Tango/16x16/actions/editcut.png',
    command='cut-text',
)

copyButton = bar.getButton(
    text='Copy',
    icon='Tango/16x16/actions/editcopy.png',
    command='copy-text',
)

pasteButton = bar.getButton(
    text='Paste',
    icon='Tango/16x16/actions/editpaste.png',
    command='paste-text',
)

buttons = (cutButton, copyButton, pasteButton)


for button in buttons:
    # must use 'in=master' as button have c.frame.top as a parent
    button.pack(in_=compoundFrame, side='left')
    # try it with side='top' :)



# add a list of widgets that can be used as drag handles
# in this case all the buttons are drag handles.

compoundFrame.leoDragHandle = buttons

# a single embedded widget could be used as the drag handle
# uncomment the statement below to set cutButtons as the only
# drag handle. Notice that right click only has effect over the
# the widget(s) identified as drag handles.

#compoundFrame.leoDragHandle = cutButton



# optionally add an rClick menu to the frame
# comment out the next statement to test with no rclick menu

compoundFrame.context_menu = 'test-widget-menu'



@
Set compoundFrame.deleteOnRightClick to True if you wish to allow the
widget to be removed from the iconBar.
@c

compoundFrame.deleteOnRightClick = True

@
The above statement will only have effect if there is no context_menu set for
the buttons or the compoundFrame.
@c

# add the compound widget in the first position of the bar
bar.addWidget(compoundFrame, index=0)


</t>
<t tx="bobjack.20080613111554.19"></t>
<t tx="bobjack.20080613111554.20">Remove Compound Widget

icon = Tango\16x16\actions\stop.png</t>
<t tx="bobjack.20080616090010.4"></t>
<t tx="bobjack.20080616090010.5"># The name of the iconBar to which the buttons should initially be placed
# This is ignored unless the toolbar.py plugin is enabled

iconbar = 


# An icon to be used in place of text if the toolbar.py plugin is enabled
# The PIL module must also be availiable for icons to be visible
# Value may be a full path or a path relative to leo/icons or leave empty for text only 

icon = 


# The colors to be used for the 'shortcut' button

master-fg = IndianRed4
master-bg = aquamarine1


# The colors to be used for the buttons generated by the 'shortcut' button

slave-fg = blue
slave-bg = burlywood2


# The rClick menu to use for the 'shortcut' button and generated buttons
# These will be ignored unless both rClick.py and tooblar.py plugins are enabled

master-menu = test-button-menu
slave-menu = test-button-menu

</t>
</tnodes>
</leo_file>
