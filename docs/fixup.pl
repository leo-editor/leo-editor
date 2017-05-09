#!/usr/bin/perl
while(<>) {
    if (/Chapter 1:/) {
	$seen_chapter_one = 1;
    }
    if (!$seen_chapter_one) {
        if (/^
            \s* \\
	    (chapter|(sub)?section)
            \s* {
            (.*)
            } \s*
            $
            /x) {
	    next if ($3 eq 'Front Matter');
            print "\\$1*{$3}\n";
            print "\\addcontentsline{toc}{$1}{$3}\n" unless $2 eq 'sub';
        } elsif (/^\s*Contents:\s*$/) {
		next;
        } else {
		print;
	}
    } else {
        if (/^
            \s* \\ chapter \s* { \s*
            Chapter \s* [0-9]+ \s* : \s*
            ( .* )
            } \s* $
            /x) {
               print "\\chapter{$1}\n";
        } else {
	    print;
        }
    }
}
