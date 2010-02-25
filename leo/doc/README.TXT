Leo 4.7.1 final                    February 26, 2010

Leo 4.7.1 final is now available at:
http://sourceforge.net/project/showfiles.php?group_id=3458&package_id=29106

Leo 4.7.1 fixes a dangerous bug in Leo 4.7. When converting file-like sentinels
to thin-like sentinels in an external file, Leo now issues a warning and sets
the corresponding @file node dirty. This ensures that Leo will write the
converted external file and .leo file together, making it impossible to lose
data.

Leo is a text editor, data organizer, project manager and much more. See:
http://webpages.charter.net/edreamleo/intro.html

The highlights of Leo 4.7:
--------------------------

- Leo now uses the simplest possible internal data model.
  This is the so-called "one-node" world.
- Leo supports Python 3.x.
- Leo requires Python 2.6 or above.
- Several important improvements in file handling.
    - Leo converts @file nodes to @thin nodes automatically.
    - Leo creates a 'Recovered Nodes' node to hold data that
      otherwise might be lost due to clone conflicts.
    - @auto-rst now works much more reliably reliably.
    - Leo no longer supports @noref trees.  Such trees are not
      reliable in cooperative environments.
- A new Windows installer.
- Many other features, including new command line options and new plugins.
- Dozens of bug fixes.

Links:
------
Leo:      http://webpages.charter.net/edreamleo/front.html
Forum:    http://groups.google.com/group/leo-editor
Download: http://sourceforge.net/project/showfiles.php?group_id=3458
Bzr:      http://code.launchpad.net/leo-editor/
Quotes:   http://webpages.charter.net/edreamleo/testimonials.html