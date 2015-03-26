Leo 5.1 b1: March 27, 2015

Leo 5.1 b1 is now available at: http://sourceforge.net/projects/leo/files/Leo/

This release features @clean trees, one of the most important developments
in Leo's history.

Leo is a PIM, an IDE and an outliner.
Video tutorials: http://leoeditor.com/screencasts.html
Text tutorials: http://leoeditor.com/tutorial.html

The highlights of Leo 5.1
--------------------------

@clean nodes create external files without sentinel comments, yet Leo can
update @clean trees from changes made to the corresponding external files,
something long thought impossible. @clean trees preserve clone links and
user attributes (uA's). Reading @clean trees is faster than reading @auto
or @shadow trees.
    
The Mulder/Ream algorithm updates @clean trees from changes made in the
corresponding external files. This is a completely rewritten and much
simpler version of Bernhard Mulder's original @shadow update algorithm.
http://leoeditor.com/appendices.html#the-mulder-ream-update-algorithm

Here is what one of Leo's users has to say about @clean:

I just want to provide my own thoughts about the importance of @clean. I
look at the posts in this group a fair amount because I find the discussion
interesting but I had abandoned leo as a day-to-day tool principally
because of the sentinels in @file nodes. Even for solo projects, I just
found them visually unappealing and beyond that occasionally confusing when
I went to edit files with external editors. I would sometimes start a
project in leo, particularly if it was based on code I developed in the
past using leo, and then would use the old @nosent to save a version of the
code without sentinels and then use my external editor of choice and not
use leo at all. I missed many of the features of leo but just couldn't get
over the sentinel issue.

@clean really seems to solve all the issues that I had. In particular--and
somehow this point doesn't seem to me to have been emphasized enough--it
seems to fully support organizer nodes. They are one of the great things
about leo--it's happy to guess initially at what the structure of your
program is but it's completely up to you to determine the structure and the
ability to do things like break up long methods, group like methods, group
menu actions in GUI code, etc etc is one of the very cool things about leo.
My limited but growing experience with @clean's handling of external
changes has been mainly with incremental (as opposed to more sweeping) code
changes, and the assignment of new lines is reasonable and you can always
fix them it quickly if you don't like how external changes have been
handled.

There have been some posts about the recovered nodes, comparing the old and
new nodes where there were external changes. I think it's genius. As
opposed to hoping that leo has correctly incorporated external changes,
it's all there in case you want to take a closer look. Without this, I
would just not have the confidence that external changes were being applied
correctly and while you can always do a git diff, I am not looking to do
that every time I change a file externally especially if I am not at the
point where I am about to do a commit.

There has been some discussion of @auto v. @clean. Preference is obviously
a matter of taste. I will say that for me the fact that node headlines are
unaffected by external file changes is a feature not a problem since I
place notes in the headlines that I want preserved when I edit files
externally. Yes, if the node headlines are the method names then they won't
be updated if an external edit changes a method name but this was true of
@file as well.

The ability to work on projects with people who don't have leo is obvious;
one perhaps slightly less obvious benefit of no sentinels is that I suspect
that the likelihood that someone will clone a git repository is reduced
when that repository's code is riddled with leo sentinels (unless the
potential cloner is a leo loyalist). The one downside to no
sentinels--there is no evidence that leo is being used but I think that
raises the broader question of marketing leo, which I certainly believe
will be aided significantly by being able to take advantage of leo without
sentinels in external files.--- Steve Zatz

And a few more features:
 
* A new web page, http://leoeditor.com/load-leo.html, displays .leo files
  in the browser.
  
* Added command history to Leo's minibuffer.

* A new IdleTime class greatly simplifies idle-time handling.

* Leo now honors @language inside @doc parts

* @data nodes can be composed of their descendant nodes.

* @int qt-cursor-width = 5 is great for geriatric eyes.

* @shadow is now deprecated. @clean is superior to @shadow in all respects.
Leo will support all flavors of @auto indefinitely.

Links:
------
Leo:       http://leoeditor.com
Docs:      http://leoeditor.com/leo_toc.html
Tutorials: http://leoeditor.com/tutorial.html
Videos:    http://leoeditor.com/screencasts.html
Forum:     http://groups.google.com/group/leo-editor
Download:  http://sourceforge.net/projects/leo/files/
Github:    https://github.com/leo-editor/leo-editor
Quotes:    http://leoeditor.com/testimonials.html
Viewer:    http://leoeditor.com/load-leo.html
