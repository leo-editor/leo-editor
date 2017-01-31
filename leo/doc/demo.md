#Leo's demo.py plugin

The demo.py plugin helps presenters run dynamic demos from Leo files.

- [Overview](../doc/demo.md#overview)
- [Helper methods](../doc/demo.md#helper-methods)
    - [Images and focus](../doc/demo.md#images-and-focus)
    - [Menus](../doc/demo.md#menus)
    - [Starting and ending](../doc/demo.md#starting-and-ending)
    - [Typing](../doc/demo.md#typing)
- [Undo](../doc/demo.md#undo)
- [Style sheets](../doc/demo.md#style-sheets)
- [Acknowledgements](../doc/demo.md#acknowledgements)

#Overview

A **script tree**, a tree of **demo scripts**, controls the demo. Demo scripts free the presenter from having to type correctly or remember sequences of desired actions.

The **demo-next** command executes the next demo script.  The plugin ends the presentation just after executing the last demo script. The **demo-end** command ends the demo early.

To start a demo, presenters run a **top-level script**. Top-level scripts instantiate the Demo class, and then call demo.start(p), where p is the root of the script tree. For example:
```python
import leo.plugins.demo as demo

class Demo_1(demo.Demo):
    
    def setup(self, p):
        fn = 'c:/demos/demo1.leo'
        demo.user_dict['c'] = g.openWithFileName(fn, old_c=c)
        
    def teardown():
        c = demo.user_dict.get('c')
        if c: c.close()

Demo_1(c).start(g.findNodeInTree(c, p, 'demo1-commands'))
```

**Notes**:

- The **demo.user_dict** ivar is a Python dictionary that demo scripts may freely use.

- Subclasses of Demo may define **setup** and **teardown** methods. The demo class calls demo.setup(p) just before the first demo script, and calls demo.teardown() just after the last demo script.

- **Important**: The Demo class executes demo scripts *in the present outline*. As shown above, demo scripts may create new outlines, thereby changing the meaning of c. It is up to the demo scripts themselves to handle such complications.

#Helper methods

Demo scripts have access to c, g and p as usual.  Demo scripts also have access to the predefined **demo** variable, bound to the Demo instance. This allows demo scripts to use all the **helper methods** in the Demo class. These methods can:

- Simulate typing in headlines, body text, the minibuffer, or anywhere else.
- Overlay a scaled image on the screen.
- Open any Leo menu, selecting particular menu items.
- [Coming soon] Scale font sizes.

For example, this demo script executes the insert-node command!

```python
    demo.single_key('Alt-X')
    demo.plain_keys('ins\\tno\\t\\n')
```

The following sections describe all public helper methods of the Demo class.

##Images and focus

In the following methods, the valid values for the `pane` arguments are "body", "log" and "tree".

**demo.caption(s, pane)**

Creates a caption with text s in the indicated pane. A **caption** is a text area that overlays part of Leo's screen. By default, captions have a distinctive yellow background. The appearance of captions can be changed using Qt stylesheets. See below.

**demo.image(pane,fn,center=None,height=None,width=None)**

Overlays an image in a pane.

- `pane`: Valid values are 'body', 'log' or 'tree'.
- `fn`: The path to the image file, relative to the leo/Icons directory for relative paths.
- `height`: Scales the image so it has the given height.
- `width`: Scales the image i so it has the given width.
- `center`: If True, centers the image horizontally in the given pane.

**demo.focus(pane)**

Forces focus to the given pane. Valid values are 'body', 'log' or 'tree'.

##Menus

**demo.open_menu(menu_name)**

Opens the menu whose name is given, ignoring case and any non-alpha characters in menu_name. This method shows all parent menus, so demo.open_menu('cursorback') suffices to show the `Cmds\:Cursor/Selection\:Cursor Back...` menu.

**demo.dismiss_menubar()**

Dismisses the menu opened with demo.open_menu.

##Starting and ending

**demo.setup(p)**

May be overridden in subclasses. Called before executing the first demo script.

**demo.start(p)**

Starts a demo. p is the root of demo script tree. 

**demo.end()**

Ends the demo and calls the teardown script. The demo automatically ends after executing the last demo script.

**demo.teardown(p)**

May be overridden in subclasses. Called whenever the demo ends.

##Typing

The **demo.n1** and **demo.n2** ivars determine the speed of the simulated typing provided by the following methods. Demo scripts may change either at any time. If both are given, each character is followed by a wait of betwen n1 and n2 seconds. If n2 is None, the wait is exactly n1. The default values are 0.02 and 0.175 seconds, respectively. 

**demo.body_keys(s)**

Simulates typing the string s in the body pane. This method supports undo.

**demo.head_keys(s)**

Simulates typing the string s in the body pane. This method supports undo.

**demo.keys(s)**

Simulates typing the string s in the present widget. This method support undo

**demo.key(setting)**

Types a single key in the present widget. This method does not support undo. Examples:
```python
   demo.key('Alt-X') # Activate the minibuffer
   demo.key('Ctrl-F') # Execute Leo's Find command
```

#Undo

The demo plugin does not change Leo's key-handling in any way.  As a result, presenters may undo/redo the *actions* of demo scripts. Some limitations:

- Demo scripts can not be undone/redone in a single step, unless each demo script makes *itself* undoable.

- Leo's undo command is limited to the presently selected outline. If a demo script opens another outline, there is no *automatic* way of selecting the previous outline.

These limitations are unlikely to be a nuisance in practice.

#Style sheets & magnification

**demo.set_magnification(multiplier)**

Magnifies text by the given multiplier, a number between 0.0 and 1.0.

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

#Acknowledgements

Edward K. Ream started this plugin on January 29, 2017, based on Leo's screencast plugin.

The [demo-it](https://github.com/howardabrams/demo-it/blob/master/demo-it.org) inspired this plugin. Or perhaps it was the other way around. demo-it may have been inspired by the screencast plugin.

