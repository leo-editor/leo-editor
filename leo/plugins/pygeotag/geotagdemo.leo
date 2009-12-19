<?xml version="1.0" encoding="utf-8"?>
<?xml-stylesheet ekr_test?>
<leo_file>
<leo_header file_format="2" tnodes="0" max_tnode_index="0" clone_windows="0"/>
<globals body_outline_ratio="0.5">
	<global_window_position top="48" left="1367" height="782" width="981"/>
	<global_log_window_position top="0" left="0" height="0" width="0"/>
</globals>
<preferences/>
<find_panel_settings/>
<vnodes>
<v t="tbrown.20091219110700.1329"><vh>@button geoopen</vh></v>
<v t="tbrown.20091219110700.1330"><vh>@button geoshow</vh></v>
<v t="tbrown.20091219110700.1331"><vh>@button geotag</vh></v>
<v t="tbrown.20091219110700.1332"><vh>Death Valley</vh>
<v t="tbrown.20091219110700.1333"><vh>@LatLng 36.531974 -117.092285 6 roadmap  Death Valley </vh></v>
</v>
<v t="tbrown.20091219110700.1334"><vh>Mojave National Preserve</vh>
<v t="tbrown.20091219110700.1335"><vh>@LatLng 35.007773 -115.488281 7 roadmap  Mojave National Preserve </vh></v>
</v>
<v t="tbrown.20091219110700.1336"><vh>Anza-Borrego Desert State Park</vh>
<v t="tbrown.20091219110700.1341"><vh>@LatLng 33.034272 -116.282043 8 roadmap  Anza-Borrego Desert State Park </vh></v>
</v>
<v t="tbrown.20091219110700.1337"><vh>Yosemite National Park</vh>
<v t="tbrown.20091219110700.1342"><vh>@LatLng 37.781830 -119.490051 7 terrain  Yosemite National Park </vh></v>
</v>
<v t="tbrown.20091219110700.1338"><vh>Kings Canyon National Park</vh>
<v t="tbrown.20091219110700.1343"><vh>@LatLng 36.921615 -118.561707 7 satellite  Kings Canyon National Park </vh></v>
</v>
<v t="tbrown.20091219110700.1339"><vh>Joshua Tree National Park</vh>
<v t="tbrown.20091219110700.1344"><vh>@LatLng 33.828062 -115.759163 14 hybrid  Joshua Tree National Park </vh></v>
</v>
<v t="tbrown.20091219110700.1340"><vh>Sequoia National Park</vh>
<v t="tbrown.20091219110700.1345"><vh>@LatLng 36.523145 -118.536987 8 roadmap  Sequoia National Park </vh></v>
</v>
<v t="tbrown.20091215231157.1354" a="E"><vh>@settings</vh>
<v t="tbrown.20091215231157.1356"><vh>@enabled-plugins</vh></v>
</v>
<v t="tbrown.20091215231157.1355"><vh>@chapters</vh></v>
</vnodes>
<tnodes>
<t tx="tbrown.20091215231157.1354"></t>
<t tx="tbrown.20091215231157.1355"></t>
<t tx="tbrown.20091215231157.1356"># Leo loads plugins in the order they appear here.
#
# The FIRST mention of a plugin controls whether the plugin is enable or not:
# - If the plugin's name is commented out, it is disabled, otherwise it is enabled.
# - Plugins not appearing here are disabled.
# 
# File names may be indented as desired.

##### Experimental.  Use with caution.
#ironPythonGui.py
#cursesGui.py

##### Standard plugins enabled in official distributions.

qtGui.py
qtframecommands.py
# Plugin_manager.py needs plugins_menu.py
# __wx_alt_gui.py
plugins_menu.py
plugin_manager.py
nav_qt.py
open_with.py
# initinclass.py
contextmenu.py

# nav_buttons.py

mod_scripting.py

# pywatch.py
# todo.py 
# geotag.py
# graphed.py
# quicksearch.py
# attrib_edit.py
# ctagscompleter.py
# codewisecompleter.py
# leomgp.py
# at_folder.py
# active_path.py
# leoinkslide.py
# rst3.py
# interact.py
UNL.py
# bookmarks.py
# backlink.py
# cleo.py
# stickynotes.py
# leoremote.py
# graphcanvas.py
# paste_as_headlines.py
# encryptNode.py
# quickMove.py



# multifile.py
# xemacs.py
# threading_colorizer.py
leo_to_html.py
# textnode.py
# newButtons.py
# gtkDialogs.py
ipython.py
rClick.py
geotag.py

# table.py
# chapter_hoist.py

##### Recent work by EKR

#__wx_gui.py
#leoOPML.py
#__jEdit_colorizer__.py
	# The new colorizer has some severe performance problems.

##### All other plugins.
##### Order is important for enabled plugins that add items to the icon area.

#ConceptualSort.py
#EditAttributes.py
#FileActions.py
#Library.py
#UASearch.py
#URLloader.py
#UniversalScrolling.py

#add_directives.py
#arrows.py
#at_folder.py
#at_view.py
#autotrees.py
#base64Packager.py
#bibtex.py
#chapter_hoist.py
#cleo.py
#color_markup.py
#datenodes.py
#detect_urls.py
#dyna_menu.py
#fastGotoNode.py
#footprints.py
#groupOperations.py
#hoist.py
#image.py
#import_cisco_config.py
#keybindings.py
#leo_to_html.py
#leo_to_rtf.py
#leoupdate.py
#macros.py
#mod_autosave.py
#mod_http.py
#mod_labels.py
#mod_read_dir_outline.py
#mod_shadow.py
#nav_buttons.py
#newButtons.py
#niceNosent.py
#nodebar.py
#nodenavigator.py
#open_shell.py
#paste_as_headlines.py
#pie_menus.py
#pretty_print.py
#print_cp.py
#quickMove.py
#rClick.py
#read_only_nodes.py
#rowcol.py
#run_nodes.py
#s_menu.py
#scheduler.py
#searchbox.py
#shortcut_button.py
#slideshow.py
#table.py
#templates.py
#trace_tags.py
#vim.py
#word_count.py
#word_export.py
#xcc_nodes.py
#xsltWithNodes.py
#zodb.py
</t>
<t tx="tbrown.20091219110700.1329" str_leo_pos="3">c.k.simulateCommand('geotag-open-server-page')</t>
<t tx="tbrown.20091219110700.1330">c.k.simulateCommand('geotag-show-node')</t>
<t tx="tbrown.20091219110700.1331">c.k.simulateCommand('geotag-tag-node')</t>
<t tx="tbrown.20091219110700.1332">Click the geoopen button to open the GoogleMap geotagging window

Then select a park and click geoshow to find it on the map

Click geotag to set a new position for a node
</t>
<t tx="tbrown.20091219110700.1333"></t>
<t tx="tbrown.20091219110700.1334"></t>
<t tx="tbrown.20091219110700.1335"></t>
<t tx="tbrown.20091219110700.1336"></t>
<t tx="tbrown.20091219110700.1337"></t>
<t tx="tbrown.20091219110700.1338"></t>
<t tx="tbrown.20091219110700.1339"></t>
<t tx="tbrown.20091219110700.1340"></t>
<t tx="tbrown.20091219110700.1341"></t>
<t tx="tbrown.20091219110700.1342"></t>
<t tx="tbrown.20091219110700.1343"></t>
<t tx="tbrown.20091219110700.1344"></t>
<t tx="tbrown.20091219110700.1345"></t>
</tnodes>
</leo_file>
