
# Leo's demo.py plugin

At present, these are more design docs than actual descriptions of reality.

## Overview

This plugin runs dynamic demos from Leo files.

A **script tree**, a tree of **demo scripts**, controls the demo. Pressing the space bar executes the next script in the tree. Demo scripts typically alter the outline, freeing the presenter from having to type correctly or remember sequences of desired actions. 

To run a demo, you create a **top-level script** that creates an instance of the Demo class. Top-level scripts are free to subclass the Demo class. The top-level script calls my_demo.start(p), where p is the root of the script tree. For example:

```python
import leo.plugins.demo as demo

class Demo1(demo.Demo):
    
    def setup(self, p):
        fn = 'c:/demos/demo1.leo'
        demo.user_d['c'] = g.openWithFileName(fn, old_c=c)

Demo1(c).start(g.findNodeInTree(c, p, 'demo1-commands'))
```

Demo scripts have access to the 'demo' variable, which is bound to the Demo instance. This allows demo scripts to use any **helper method** in the Demo class. These methods can:

- Animate typing in headlines, body text, the minibuffer, or anywhere else.
- Overlay a scaled image on the screen.
- Open any Leo menu, selecting particular menu items.
- Scale font sizes.
- Open another .leo file and present the demo in the new outline window.
- And many other things, as described below.

**demo.user_d** is a Python dictionary that demo scripts may freely use.

## The Demo class

The Demo class controls key handling during demos and executes demo scripts as the demo moves from node to node.

During a demo, the Demo class traps only the space-bar key (*or right-arrow key?*), passing all other keys to Leo's key-handling code. This allows key handling in key-states during the execution of a demo. For example::

```python
    demo.single_key('Alt-X')
    demo.plain_keys('ins\\tno\\t\\n')
```

executes the insert-node command!

## Helper methods

*These descriptions may change at any time, without notice*:

**demo.body(s)**, **demo.log(s)** and **demo.tree(s)** Create a caption with text s in the indicated pane. A **caption** is a text area that overlays part of Leo's screen. By default, captions have a distinctive yellow background. The appearance of captions can be changed using Qt stylesheets. See below.

**demo.body_keys(s,n1=None,n2=None)** Draws the string s in the body pane of
the presently selected node. n1 and n2 give the range of delays to be
inserted between typing. If n1 and n2 are both None, values are given that
approximate a typical typing rate.

**demo.command(command_name)** Executes the named command.

**demo.dismiss_menubar()** Dismisses the menu opened with demo.open_menu.

**demo.focus(pane)** Immediately forces focus to the indicated pane. Valid values are 'body', 'log' or 'tree'.

**demo.image(pane,fn,center=None,height=None,width=None)** Overlays an image in a pane. The valid values for `pane` are 'body', 'log' or 'tree'. `fn` is the path to the image file, resolved to the leo/Icons directory if fn is a relative path. If `height` is given, the image is scaled so it is height pixels high. If `width` is given, the image is scaled so it width pixels wide. If `center` is True, the image is centered horizontally in the given pane.

**demo.head_keys(s,n1=None,n2=None)** Same as demo.body_keys, except that the
keys are "typed" into the headline of the presently selected node.

**demo.open_menu(menu_name)** Opens the menu whose name is given, ignoring case and any non-alpha characters in menu_name. This method shows all parent menus, so demo.open_menu('cursorback') suffices to show the "Cmds\:Cursor/Selection\:Cursor Back..." menu.

**demo.plain_keys(s,n1=None,n2=None,pane='body')** Same as demo.body_keys, except that the keys are typed into the designated pane. The valid values for the 'pane' argument are 'body','log' or 'tree'.

**demo.quit** ends the demo and calls the teardown script. The Demo class calls the teardown script whenever the demo ends.

**demo.redraw(p)** Forces an immediate redraw of the outline pane. If p is
given, that position becomes c.p, the presently selected node.

**demo.selectPosition(p)** Same as demo.redraw(p)

**demo.single_key(setting)** generates a key event. Examples::

   demo.single_key('Alt-X') # Activates the minibuffer
   demo.single_key('Ctrl-F') # Activates Leo's Find command

The 'setting' arg can be anything that would be a valid key setting. The following are equivalent: "ctrl-f", "Ctrl-f", "Ctrl+F", etc., but "ctrl-F" is different from "ctrl-shift-f".

**demo.start(p)** Starts a demo, where p is the root of demo script tree.

## demo.setup and demo.teardown

The Demo class defines two do-nothing methods: demo.setup and demo.teardown. These may be overridden in subclasses. Just as with unit tests, the Demo class executes the setup method before executing the first demo script and executes the teardown method whenever quitting the demo.

## The program counter, demo.p

The demo.p ivar points to the to-be-executed node in the script tree. You can think of demo.p as the demo's program counter. demo scripts should rarely need to change demo.p.

After executing a demo script, the Demo class advances demo.p to the next non-empty, non-ignored node in the script tree, unless the previous script has changed demo.p. By default, the Demo class keeps the script tree collapsed.

In contrast, c.p is the presently selected (and therefore visible) node. demo scripts will can use c.selectPosition(p) or c.redraw(p) as usual to make *other* nodes visible by calling 

## The script list may replace demo.py

It may be safer to "bind" all scripts into a list before any are executed.  This would do away with the demo.p program counter entirely.  The new code will likely do this.

## Style sheets

**Note**: Helper methods will likely exist to alter this stylesheet more easily.

Presenters may alter the appearance of captions by using changing the
following stylesheet::

```css
    QPlainTextEdit#democaption {
        background-color: yellow;
        font-family: DejaVu Sans Mono;
        font-size: 18pt;
        font-weight: normal; /* normal,bold,100,..,900 */
        font-style: normal; /* normal,italic,oblique */
    }
```

You will find this stylesheet in the node @data
``qt-gui-plugin-style-sheet`` in leoSettings.leo or myLeoSettings.leo.

## Acknowledgements

This plugin was inspired by [demo-it](https://github.com/howardabrams/demo-it/blob/master/demo-it.org). Or perhaps demo-it was inspired by Leo's earlier screencast plugin.

