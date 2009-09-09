Leo 4.7 beta 1                          September 9, 2009

Leo 4.7 beta 1 is now available at:
http://sourceforge.net/project/showfiles.php?group_id=3458&package_id=29106

Leo is a text editor, data organizer, project manager and much more. See:
http://webpages.charter.net/edreamleo/intro.html

This version of Leo is labeled a beta version because it contains some new,
relatively untested plugins.  However, Leo's core should be quite reliable.

In particular, Leo 4.7 beta 1 fixes a bug that caused Leo 4.6 releases to crash
if .leoID.txt did not exist. Usually this file does exist, but Leo will prompt
for the contents of this file (a user id) the very first time somebody uses Leo.
Alas, an unfortunate reversion of code caused Leo to crash. Not exactly the best
introduction to Leo!

The highlights of Leo 4.7:
--------------------------

- A major simplification of internal data model: the so-called
  one-node world. Note: this is **disabled** in the beta 1 release.
- A new executable Windows installer, whose manifest is created from
  the files that bzr actively manages.
- Leo no longer adds directories to sys.path on startup.
- New plugins.
- The usual assortment of bug fixes.

Links:
------
Leo:      http://webpages.charter.net/edreamleo/front.html
Forum:    http://groups.google.com/group/leo-editor
Download: http://sourceforge.net/project/showfiles.php?group_id=3458
Bzr:      http://code.launchpad.net/leo-editor/
Quotes:   http://webpages.charter.net/edreamleo/testimonials.html