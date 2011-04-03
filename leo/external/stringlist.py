#@+leo-ver=4-thin
#@+node:ville.20090720135131.1484:@thin stringlist.py

#@<< imports >>
#@+node:ville.20090720135131.1640:<< imports >>
import re
import subprocess
#@nonl
#@-node:ville.20090720135131.1640:<< imports >>
#@nl
#@+others
#@+node:ville.20090720135131.1493:class SList
class SList(list):
    """List derivative with a special access attributes.

    These are normal string lists, but with the special attributes:

        .l: value as list (the list itself).
        .n: value as a string, joined on newlines.
        .s: value as a string, joined on spaces.

    """

    #@    @+others
    #@+node:ville.20090720135131.1494:get_list
    def get_list(self):
        return self

    #@-node:ville.20090720135131.1494:get_list
    #@+node:ville.20090720135131.1495:get_spstr
    def get_spstr(self):
        self.__spstr = ' '.join(self)
        return self.__spstr

    #@-node:ville.20090720135131.1495:get_spstr
    #@+node:ville.20090720135131.1496:get_nlstr
    def get_nlstr(self):
        self.__nlstr = '\n'.join(self)
        return self.__nlstr

    #@-node:ville.20090720135131.1496:get_nlstr
    #@+node:ville.20090720135131.1501:property accessors
    l = property(get_list)
    s = property(get_spstr)
    n = property(get_nlstr)
    #@nonl
    #@-node:ville.20090720135131.1501:property accessors
    #@+node:ville.20090720135131.1498:grep
    def grep(self, pattern, prune = False, field = None):
        """ Return all strings matching 'pattern' (a regex or callable)

        This is case-insensitive. If prune is true, return all items
        NOT matching the pattern.

        If field is specified, the match must occur in the specified
        whitespace-separated field.

        Examples::

            a.grep( lambda x: x.startswith('C') )
            a.grep('Cha.*log', prune=1)
            a.grep('chm', field=-1)
        """

        def match_target(s):
            if field is None:
                return s
            parts = s.split()
            try:
                tgt = parts[field]
                return tgt
            except IndexError:
                return ""

        if isinstance(pattern, basestring):
            pred = lambda x : re.search(pattern, x, re.IGNORECASE)
        else:
            pred = pattern
        if not prune:
            return SList([el for el in self if pred(match_target(el))])
        else:
            return SList([el for el in self if not pred(match_target(el))])
    #@-node:ville.20090720135131.1498:grep
    #@+node:ville.20090720135131.1499:fields
    def fields(self, *fields):
        """ Collect whitespace-separated fields from string list

        Allows quick awk-like usage of string lists.

        Example data (in var a, created by 'a = !ls -l')::
            -rwxrwxrwx  1 ville None      18 Dec 14  2006 ChangeLog
            drwxrwxrwx+ 6 ville None       0 Oct 24 18:05 IPython

        a.fields(0) is ['-rwxrwxrwx', 'drwxrwxrwx+']
        a.fields(1,0) is ['1 -rwxrwxrwx', '6 drwxrwxrwx+']
        (note the joining by space).
        a.fields(-1) is ['ChangeLog', 'IPython']

        IndexErrors are ignored.

        Without args, fields() just split()'s the strings.
        """
        if len(fields) == 0:
            return [el.split() for el in self]

        res = SList()
        for el in [f.split() for f in self]:
            lineparts = []

            for fd in fields:
                try:
                    lineparts.append(el[fd])
                except IndexError:
                    pass
            if lineparts:
                res.append(" ".join(lineparts))

        return res
    #@-node:ville.20090720135131.1499:fields
    #@+node:ville.20090720135131.1500:sort
    def sort(self,field= None,  nums = False):
        """ sort by specified fields (see fields())

        Example::
            a.sort(1, nums = True)

        Sorts a by second field, in numerical order (so that 21 > 3)

        """

        #decorate, sort, undecorate
        if field is not None:
            dsu = [[SList([line]).fields(field),  line] for line in self]
        else:
            dsu = [[line,  line] for line in self]
        if nums:
            for i in range(len(dsu)):
                numstr = "".join([ch for ch in dsu[i][0] if ch.isdigit()])
                try:
                    n = int(numstr)
                except ValueError:
                    n = 0;
                dsu[i][0] = n


        dsu.sort()
        return SList([t[1] for t in dsu])

    #@-node:ville.20090720135131.1500:sort
    #@-others
#@-node:ville.20090720135131.1493:class SList
#@+node:ville.20090720134348.1860:shcmd
def shcmd(cmd):
    """ Execute shell command, capture output to string list """

    out = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]

    sl = SList(out.split('\n'))
    return sl
#@-node:ville.20090720134348.1860:shcmd
#@-others
#@-node:ville.20090720135131.1484:@thin stringlist.py
#@-leo
