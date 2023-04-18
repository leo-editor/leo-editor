#@+leo-ver=5-thin
#@+node:ekr.20080708094444.1: * @file leoShadow.py
#@+<< leoShadow docstring >>
#@+node:ekr.20080708094444.78: ** << leoShadow docstring >>
"""
leoShadow.py

This code allows users to use Leo with files which contain no sentinels
and still have information flow in both directions between outlines and
derived files.

Private files contain sentinels: they live in the Leo-shadow subdirectory.
Public files contain no sentinels: they live in the parent (main) directory.

When Leo first reads an @shadow we create a file without sentinels in the regular directory.

The slightly hard thing to do is to pick up changes from the file without
sentinels, and put them into the file with sentinels.

Settings:
- @string shadow_subdir (default: .leo_shadow): name of the shadow directory.

- @string shadow_prefix (default: x): prefix of shadow files.
  This prefix allows the shadow file and the original file to have different names.
  This is useful for name-based tools like py.test.
"""
#@-<< leoShadow docstring >>
#@+<< leoShadow imports & annotations >>
#@+node:ekr.20080708094444.52: ** << leoShadow imports & annotations >>
from __future__ import annotations
import difflib
import os
import pprint
from typing import List, Optional, Tuple, TYPE_CHECKING
from leo.core import leoGlobals as g

if TYPE_CHECKING:  # pragma: no cover
    from leo.core.leoCommands import Commands as Cmdr
    from leo.core.leoNodes import Position
#@-<< leoShadow imports & annotations >>

#@+others
#@+node:ekr.20080708094444.80: ** class ShadowController
class ShadowController:
    """A class to manage @shadow files"""
    #@+others
    #@+node:ekr.20080708094444.79: *3*  x.ctor & x.reloadSettings
    def __init__(self, c: Cmdr, trace: bool = False, trace_writers: bool = False) -> None:
        """Ctor for ShadowController class."""
        self.c = c
        # Opcode dispatch dict.
        self.dispatch_dict = {
            'delete': self.op_delete,
            'equal': self.op_equal,
            'insert': self.op_insert,
            'replace': self.op_replace,
        }
        self.encoding: str = c.config.default_derived_file_encoding
        self.errors = 0
        self.results: List[str] = []
        self.shadow_subdir: str = None
        self.shadow_prefix: str = None
        self.shadow_in_home_dir: bool = None
        # Support for goto-line.
        self.reloadSettings()

    def reloadSettings(self) -> None:
        """ShadowController.reloadSettings."""
        c = self.c
        self.shadow_subdir = c.config.getString('shadow-subdir') or '.leo_shadow'
        self.shadow_prefix = c.config.getString('shadow-prefix') or ''
        self.shadow_in_home_dir = c.config.getBool('shadow-in-home-dir', default=False)
        self.shadow_subdir = g.os_path_normpath(self.shadow_subdir)
    #@+node:ekr.20080711063656.1: *3* x.File utils
    #@+node:ekr.20080711063656.7: *4* x.baseDirName
    def baseDirName(self) -> Optional[str]:
        c = self.c
        filename = c.fileName()
        if filename:
            return g.os_path_dirname(g.finalize(filename))
        print('')
        self.error('Can not compute shadow path: .leo file has not been saved')
        return None
    #@+node:ekr.20080711063656.4: *4* x.dirName and pathName
    def dirName(self, filename: str) -> str:
        """Return the directory for filename."""
        x = self
        return g.os_path_dirname(x.pathName(filename))

    def pathName(self, filename: str) -> str:
        """Return the full path name of filename."""
        x = self
        theDir = x.baseDirName()
        return g.finalize_join(theDir, filename) if theDir else ''
    #@+node:ekr.20080712080505.3: *4* x.isSignificantPublicFile
    def isSignificantPublicFile(self, fn: str) -> bool:
        """
        This tells the AtFile.read logic whether to import a public file
        or use an existing public file.
        """
        return bool(
            g.os_path_exists(fn) and
            g.os_path_isfile(fn) and
            g.os_path_getsize(fn) > 10
        )
    #@+node:ekr.20080710082231.19: *4* x.makeShadowDirectory
    def makeShadowDirectory(self, fn: str) -> bool:
        """Make a shadow directory for the **public** fn."""
        x = self
        path = x.shadowDirName(fn)
        if not g.os_path_exists(path):
            # Force the creation of the directories.
            g.makeAllNonExistentDirectories(path)
        return g.os_path_exists(path) and g.os_path_isdir(path)
    #@+node:ekr.20080713091247.1: *4* x.replaceFileWithString
    def replaceFileWithString(self, encoding: str, fileName: str, s: str) -> bool:
        """
        Replace the file with s if s is different from theFile's contents.

        Return True if theFile was changed.
        """
        x, c = self, self.c
        exists = g.os_path_exists(fileName)
        if exists:
            # Read the file.  Return if it is the same.
            s2, e = g.readFileIntoString(fileName)
            if s2 is None:
                return False
            if s == s2:
                report = c.config.getBool('report-unchanged-files', default=True)
                if report and not g.unitTesting:
                    g.es('unchanged:', fileName)
                return False
        # Issue warning if directory does not exist.
        theDir = g.os_path_dirname(fileName)
        if theDir and not g.os_path_exists(theDir):
            if not g.unitTesting:
                x.error(f"not written: {fileName} directory not found")
            return False
        # Replace the file.
        try:
            with open(fileName, 'wb') as f:
                # Fix bug 1243847: unicode error when saving @shadow nodes.
                f.write(g.toEncodedString(s, encoding=encoding))
            c.setFileTimeStamp(fileName)  # Fix #1053.  This is an *ancient* bug.
            if not g.unitTesting:
                kind = 'wrote' if exists else 'created'
                g.es(f"{kind:>6}: {fileName}")
            return True
        except IOError:
            x.error(f"unexpected exception writing file: {fileName}")
            g.es_exception()
            return False
    #@+node:ekr.20080711063656.6: *4* x.shadowDirName and shadowPathName
    def shadowDirName(self, filename: str) -> str:
        """Return the directory for the shadow file corresponding to filename."""
        x = self
        return g.os_path_dirname(x.shadowPathName(filename))

    def shadowPathName(self, filename: str) -> str:
        """Return the full path name of filename, resolved using c.fileName()"""
        x = self
        c = x.c
        baseDir = x.baseDirName()
        fileDir = g.os_path_dirname(filename)
        # 2011/01/26: bogomil: redirect shadow dir
        if self.shadow_in_home_dir:
            # Each .leo file has a separate shadow_cache in base dir
            fname = "_".join(
                [os.path.splitext(os.path.basename(c.mFileName))[0], "shadow_cache"])
            # On Windows incorporate the drive letter to the private file path
            if os.name == "nt":
                fileDir = fileDir.replace(':', '%')
            # build the cache path as a subdir of the base dir
            fileDir = "/".join([baseDir, fname, fileDir])
        return baseDir and g.finalize_join(
                baseDir,
                fileDir,  # Bug fix: honor any directories specified in filename.
                x.shadow_subdir,
                x.shadow_prefix + g.shortFileName(filename))
    #@+node:ekr.20080708192807.1: *3* x.Propagation
    #@+node:ekr.20080708094444.35: *4* x.check_output
    def check_output(self) -> bool:
        """Check that we produced a valid output."""
        x = self
        lines1 = x.b
        junk, sents1 = x.separate_sentinels(x.old_sent_lines, x.marker)
        lines2, sents2 = x.separate_sentinels(x.results, x.marker)
        ok = lines1 == lines2 and sents1 == sents2
        if g.unitTesting:
            # The unit test will report the error.
            return ok
        if lines1 != lines2:
            g.trace()
            d = difflib.Differ()
            aList = list(d.compare(lines2, x.b))
            pprint.pprint(aList)
        if sents1 != sents2:
            x.show_error(
                lines1=sents1,
                lines2=sents2,
                message="Sentinels not preserved!",
                lines1_message="old sentinels",
                lines2_message="new sentinels")
        return ok
    #@+node:ekr.20080708094444.38: *4* x.propagate_changed_lines (main algorithm) & helpers
    def propagate_changed_lines(self,
        new_public_lines: List[str],
        old_private_lines: List[str],
        marker: "Marker",
        p: Position = None,
    ) -> List[str]:
        #@+<< docstring >>
        #@+node:ekr.20150207044400.9: *5*  << docstring >>
        """
        The Mulder update algorithm, revised by EKR.

        Use the diff between the old and new public lines to insperse sentinels
        from old_private_lines into the result.

        The algorithm never deletes or rearranges sentinels. However, verbatim
        sentinels may be inserted or deleted as needed.
        """
        #@-<< docstring >>
        x = self
        x.init_ivars(new_public_lines, old_private_lines, marker)
        sm = difflib.SequenceMatcher(None, x.a, x.b)
        # Ensure leading sentinels are put first.
        x.put_sentinels(0)
        x.sentinels[0] = []
        for tag, ai, aj, bi, bj in sm.get_opcodes():
            f = x.dispatch_dict.get(tag, x.op_bad)
            f(tag, ai, aj, bi, bj)
        # Put the trailing sentinels & check the result.
        x.results.extend(x.trailing_sentinels)
        # check_output is likely to be more buggy than the code under test.
        # x.check_output()
        return x.results
    #@+node:ekr.20150207111757.180: *5* x.dump_args
    def dump_args(self) -> None:
        """Dump the argument lines."""
        x = self
        table = (
            (x.old_sent_lines, 'old private lines'),
            (x.a, 'old public lines'),
            (x.b, 'new public lines'),
        )
        for lines, title in table:
            x.dump_lines(lines, title)
        g.pr()
    #@+node:ekr.20150207111757.178: *5* x.dump_lines
    def dump_lines(self, lines: List[str], title: str) -> None:
        """Dump the given lines."""
        print(f"\n{title}...\n")
        for i, line in enumerate(lines):
            g.pr(f"{i:4} {line!r}")
    #@+node:ekr.20150209044257.6: *5* x.init_data
    def init_data(self) -> List[str]:
        """
        Init x.sentinels and x.trailing_sentinels arrays.
        Return the list of non-sentinel lines in x.old_sent_lines.
        """
        x = self
        lines = x.old_sent_lines
        # The sentinels preceding each non-sentinel line,
        # not including @verbatim sentinels.
        sentinels: List[str] = []
        # A list of all non-sentinel lines found.  Should match x.a.
        new_lines: List[str] = []
        # A list of lists of sentinels preceding each line.
        x.sentinels = []
        i = 0
        while i < len(lines):
            line = lines[i]
            i += 1
            if x.marker.isVerbatimSentinel(line):
                # Do *not* include the @verbatim sentinel.
                if i < len(lines):
                    line = lines[i]
                    i += 1
                    x.sentinels.append(sentinels)
                    sentinels = []
                    new_lines.append(line)
                else:
                    x.verbatim_error()
            elif x.marker.isSentinel(line):
                sentinels.append(line)
            else:
                x.sentinels.append(sentinels)
                sentinels = []
                new_lines.append(line)
        x.trailing_sentinels = sentinels
        return new_lines
    #@+node:ekr.20080708094444.40: *5* x.init_ivars
    def init_ivars(self,
        new_public_lines: List[str],
        old_private_lines: List[str],
        marker: "Marker",
    ) -> None:
        """Init all ivars used by propagate_changed_lines & its helpers."""
        x = self
        x.delim1, x.delim2 = marker.getDelims()
        x.marker = marker
        x.old_sent_lines = old_private_lines
        x.results = []
        x.verbatim_line = f"{x.delim1}@verbatim{x.delim2}\n"
        old_public_lines = x.init_data()
        x.b = x.preprocess(new_public_lines)
        x.a = x.preprocess(old_public_lines)
    #@+node:ekr.20150207044400.16: *5* x.op_bad
    def op_bad(self, tag: str, ai: int, aj: int, bi: int, bj: int) -> None:
        """Report an unexpected opcode."""
        x = self
        x.error(f"unknown SequenceMatcher opcode: {tag!r}")
    #@+node:ekr.20150207044400.12: *5* x.op_delete
    def op_delete(self, tag: str, ai: int, aj: int, bi: int, bj: int) -> None:
        """Handle the 'delete' opcode."""
        x = self
        for i in range(ai, aj):
            x.put_sentinels(i)
    #@+node:ekr.20150207044400.13: *5* x.op_equal
    def op_equal(self, tag: str, ai: int, aj: int, bi: int, bj: int) -> None:
        """Handle the 'equal' opcode."""
        x = self
        assert aj - ai == bj - bi and x.a[ai:aj] == x.b[bi:bj]
        for i in range(ai, aj):
            x.put_sentinels(i)
            # works because x.lines[ai:aj] == x.lines[bi:bj]
            x.put_plain_line(x.a[i])
    #@+node:ekr.20150207044400.14: *5* x.op_insert
    def op_insert(self, tag: str, ai: int, aj: int, bi: int, bj: int) -> None:
        """Handle the 'insert' opcode."""
        x = self
        for i in range(bi, bj):
            x.put_plain_line(x.b[i])
        # Prefer to put sentinels after inserted nodes.
        # Requires a call to x.put_sentinels(0) before the main loop.
    #@+node:ekr.20150207044400.15: *5* x.op_replace
    def op_replace(self, tag: str, ai: int, aj: int, bi: int, bj: int) -> None:
        """Handle the 'replace' opcode."""
        x = self
        if 1:
            # Intersperse sentinels and lines.
            b_lines = x.b[bi:bj]
            for i in range(ai, aj):
                x.put_sentinels(i)
                if b_lines:
                    x.put_plain_line(b_lines.pop(0))
            # Put any trailing lines.
            while b_lines:
                x.put_plain_line(b_lines.pop(0))
        else:
            # Feasible. Causes the present unit tests to fail.
            for i in range(ai, aj):
                x.put_sentinels(i)
            for i in range(bi, bj):
                x.put_plain_line(x.b[i])
    #@+node:ekr.20150208060128.7: *5* x.preprocess
    def preprocess(self, lines: List[str]) -> List[str]:
        """
        Preprocess public lines, adding newlines as needed.
        This happens before the diff.
        """
        result = []
        for line in lines:
            if not line.endswith('\n'):
                line = line + '\n'
            result.append(line)
        return result
    #@+node:ekr.20150208223018.4: *5* x.put_plain_line
    def put_plain_line(self, line: str) -> None:
        """Put a plain line to x.results, inserting verbatim lines if necessary."""
        x = self
        if x.marker.isSentinel(line):
            x.results.append(x.verbatim_line)
        x.results.append(line)
    #@+node:ekr.20150209044257.8: *5* x.put_sentinels
    def put_sentinels(self, i: int) -> None:
        """Put all the sentinels to the results"""
        x = self
        if 0 <= i < len(x.sentinels):
            sentinels = x.sentinels[i]
            x.results.extend(sentinels)
    #@+node:ekr.20080708094444.36: *4* x.propagate_changes
    def propagate_changes(self, old_public_file: str, old_private_file: str) -> bool:
        """
        Propagate the changes from the public file (without_sentinels)
        to the private file (with_sentinels)
        """
        x, at = self, self.c.atFileCommands
        at.errors = 0
        self.encoding = at.encoding
        s = at.readFileToUnicode(old_private_file)  # Sets at.encoding and inits at.readLines.
        old_private_lines = g.splitLines(s or '')  # #1466.
        s = at.readFileToUnicode(old_public_file)
        if at.encoding != self.encoding:
            g.trace(f"can not happen: encoding mismatch: {at.encoding} {self.encoding}")
            at.encoding = self.encoding
        old_public_lines = g.splitLines(s)
        if 0:
            g.trace(f"\nprivate lines...{old_private_file}")
            for s in old_private_lines:
                g.trace(type(s), isinstance(s, str), repr(s))
            g.trace(f"\npublic lines...{old_public_file}")
            for s in old_public_lines:
                g.trace(type(s), isinstance(s, str), repr(s))
        marker = x.markerFromFileLines(old_private_lines, old_private_file)
        new_private_lines = x.propagate_changed_lines(
            old_public_lines, old_private_lines, marker)
        # Never create the private file here!
        fn = old_private_file
        exists = g.os_path_exists(fn)
        different = new_private_lines != old_private_lines
        copy = exists and different
        # 2010/01/07: check at.errors also.
        if copy and x.errors == 0 and at.errors == 0:
            s = ''.join(new_private_lines)
            x.replaceFileWithString(at.encoding, fn, s)
        return copy
    #@+node:bwmulder.20041231170726: *4* x.updatePublicAndPrivateFiles
    def updatePublicAndPrivateFiles(self, root: Position, fn: str, shadow_fn: str) -> None:
        """handle crucial @shadow read logic.

        This will be called only if the public and private files both exist."""
        x = self
        if x.isSignificantPublicFile(fn):
            # Update the private shadow file from the public file.
            written = x.propagate_changes(fn, shadow_fn)
            if written:
                x.message(f"updated private {shadow_fn} from public {fn}")
        else:
            pass
            # Don't write *anything*.
            # if 0: # This causes considerable problems.
                # # Create the public file from the private shadow file.
                # x.copy_file_removing_sentinels(shadow_fn,fn)
                # x.message("created public %s from private %s " % (fn, shadow_fn))
    #@+node:ekr.20080708094444.89: *3* x.Utils...
    #@+node:ekr.20080708094444.85: *4* x.error & message & verbatim_error
    def error(self, s: str, silent: bool = False) -> None:
        x = self
        if not silent:
            g.error(s)
        # For unit testing.
        x.errors += 1

    def message(self, s: str) -> None:
        g.es_print(s, color='orange')

    def verbatim_error(self) -> None:
        x = self
        x.error('file syntax error: nothing follows verbatim sentinel')
        g.trace(g.callers())
    #@+node:ekr.20090529125512.6122: *4* x.markerFromFileLines & helper
    def markerFromFileLines(self, lines: List[str], fn: str) -> "Marker":
        """Return the sentinel delimiter comment to be used for filename."""
        at, x = self.c.atFileCommands, self
        s = x.findLeoLine(lines)
        ok, junk, start, end, junk = at.parseLeoSentinel(s)
        if end:
            delims = '', start, end
        else:
            delims = start, '', ''
        return x.Marker(delims)
    #@+node:ekr.20090529125512.6125: *5* x.findLeoLine
    def findLeoLine(self, lines: List[str]) -> str:
        """Return the @+leo line, or ''."""
        for line in lines:
            i = line.find('@+leo')
            if i != -1:
                return line
        return ''
    #@+node:ekr.20080708094444.9: *4* x.markerFromFileName
    def markerFromFileName(self, filename: str) -> "Marker":
        """Return the sentinel delimiter comment to be used for filename."""
        x = self
        if not filename:
            return None
        root, ext = g.os_path_splitext(filename)
        if ext == '.tmp':
            root, ext = os.path.splitext(root)
        delims = g.comment_delims_from_extension(filename)
        marker = x.Marker(delims)
        return marker
    #@+node:ekr.20080708094444.29: *4* x.separate_sentinels
    def separate_sentinels(self, lines: List[str], marker: "Marker") -> Tuple[List[str], List[str]]:
        """
        Separates regular lines from sentinel lines.
        Do not return @verbatim sentinels.

        Returns (regular_lines, sentinel_lines)
        """
        x = self
        regular_lines = []
        sentinel_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if marker.isVerbatimSentinel(line):
                # Add the plain line that *looks* like a sentinel,
                # but *not* the preceding @verbatim sentinel itself.
                # Adding the actual sentinel would spoil the sentinel test when
                # the user adds or deletes a line requiring an @verbatim line.
                i += 1
                if i < len(lines):
                    line = lines[i]
                    regular_lines.append(line)
                else:
                    x.verbatim_error()
            elif marker.isSentinel(line):
                sentinel_lines.append(line)
            else:
                regular_lines.append(line)
            i += 1
        return regular_lines, sentinel_lines
    #@+node:ekr.20080708094444.33: *4* x.show_error & helper
    def show_error(self,
        lines1: List[str],
        lines2: List[str],
        message: str,
        lines1_message: str,
        lines2_message: str,
    ) -> None:
        x = self
        banner1 = '=' * 30
        banner2 = '-' * 30
        g.es_print(f"{banner1}\n{message}\n{banner1}\n{lines1_message}\n{banner2}")
        x.show_error_lines(lines1, 'shadow_errors.tmp1')
        g.es_print(f"\n{banner1}\n{lines2_message}\n{banner1}")
        x.show_error_lines(lines2, 'shadow_errors.tmp2')
        g.es_print('\n@shadow did not pick up the external changes correctly')
    #@+node:ekr.20080822065427.4: *5* x.show_error_lines
    def show_error_lines(self, lines: List[str], fileName: str) -> None:
        for i, line in enumerate(lines):
            g.es_print(f"{i:3} {line!r}")
    #@+node:ekr.20090529061522.5727: *3* class x.Marker
    class Marker:
        """A class representing comment delims in @shadow files."""
        #@+others
        #@+node:ekr.20090529061522.6257: *4* ctor & repr
        def __init__(self, delims: Tuple[str, str, str]) -> None:
            """Ctor for Marker class."""
            delim1, delim2, delim3 = delims
            self.delim1 = delim1  # Single-line comment delim.
            self.delim2 = delim2  # Block comment starting delim.
            self.delim3 = delim3  # Block comment ending delim.
            if not delim1 and not delim2:
                self.delim1 = g.app.language_delims_dict.get('unknown_language')

        def __repr__(self) -> str:
            if self.delim1:
                delims = self.delim1
            else:
                delims = f"{self.delim2} {self.delim3}"
            return f"<Marker: delims: {delims!r}>"
        #@+node:ekr.20090529061522.6258: *4* getDelims
        def getDelims(self) -> Tuple[str, str]:
            """Return the pair of delims to be used in sentinel lines."""
            if self.delim1:
                return self.delim1, ''
            return self.delim2, self.delim3
        #@+node:ekr.20090529061522.6259: *4* isSentinel
        def isSentinel(self, s: str, suffix: str = '') -> bool:
            """Return True is line s contains a valid sentinel comment."""
            s = s.strip()
            if self.delim1 and s.startswith(self.delim1):
                return s.startswith(self.delim1 + '@' + suffix)
            if self.delim2:
                return s.startswith(
                    self.delim2 + '@' + suffix) and s.endswith(self.delim3)
            return False
        #@+node:ekr.20090529061522.6260: *4* isVerbatimSentinel
        def isVerbatimSentinel(self, s: str) -> bool:
            """Return True if s is an @verbatim sentinel."""
            return self.isSentinel(s, suffix='verbatim')
        #@-others
    #@-others
#@-others
#@@language python
#@@tabwidth -4
#@@pagewidth 70
#@-leo
