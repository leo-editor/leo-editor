@q@@+leo-ver=5-thin@>
@q@@+node:ekr.20170401122024.7: * @@file C:/leo.repo/leo-editor/leo/test/unittest/input/cweave.w@>
@q@@@@language cweb@>
@ % This file is part of CWEB.
% This program by Silvio Levy and Donald E. Knuth
% is based on a program by Knuth.
% It is distributed WITHOUT ANY WARRANTY, express or implied.
% Version 3.61 --- July 2000
% (essentially the same as version 3.6, which added
%  recently introduced features of standard C++ to version 3.4)

% Copyright (C) 1987,1990,1993,2000 Silvio Levy and Donald E. Knuth

% Permission is granted to make and distribute verbatim copies of this
% document provided that the copyright notice and this permission notice
% are preserved on all copies.

% Permission is granted to copy and distribute modified versions of this
% document under the conditions for verbatim copying, provided that the
% entire resulting derived work is given a different name and distributed
% under the terms of a permission notice identical to this one.

% Here is TeX material that gets inserted after \input cwebmac
\def\hang{\hangindent 3em\indent\ignorespaces}
\def\pb{$\.|\ldots\.|$} % C brackets (|...|)
\def\v{\char'174} % vertical (|) in typewriter font
\def\dleft{[\![} \def\dright{]\!]} % double brackets
\mathchardef\RA="3221 % right arrow
\mathchardef\BA="3224 % double arrow
\def\({} % ) kludge for alphabetizing certain section names
\def\TeXxstring{\\{\TEX/\_string}}
\def\skipxTeX{\\{skip\_\TEX/}}
\def\copyxTeX{\\{copy\_\TEX/}}

\def\title{CWEAVE (Version 3.61)}
\def\topofcontents{\null\vfill
  \centerline{\titlefont The {\ttitlefont CWEAVE} processor}
  \vskip 15pt
  \centerline{(Version 3.61)}
  \vfill}
\def\botofcontents{\vfill
\noindent
Copyright \copyright\ 1987, 1990, 1993, 2000 Silvio Levy and Donald E. Knuth
\bigskip\noindent
Permission is granted to make and distribute verbatim copies of this
document provided that the copyright notice and this permission notice
are preserved on all copies.

\smallskip\noindent
Permission is granted to copy and distribute modified versions of this
document under the conditions for verbatim copying, provided that the
entire resulting derived work is given a different name and distributed
under the terms of a permission notice identical to this one.
}
\pageno=\contentspagenumber \advance\pageno by 1
\let\maybe=\iftrue
@s not_eq normal @q unreserve a C++ keyword @>@** Introduction. This is the \.{CWEAVE} program by Silvio Levy and Donald E. Knuth, based on \.{WEAVE} by Knuth. We are thankful to Steve Avery, Nelson Beebe, Hans-Hermann Bode (to whom the original \CPLUSPLUS/ adaptation is due), Klaus Guntermann, Norman Ramsey, Tomas Rokicki, Joachim Schnitter, Joachim Schrod, Lee Wittenberg, Saroj Mahapatra, Cesar Augusto Rorato Crusius, and others who have contributed improvements.  The ``banner line'' defined here should be changed whenever \.{CWEAVE} is modified.

@d banner "This is CWEAVE (Version 3.61)\n"

@c @<Include files@>@/
@h
@<Common code for \.{CWEAVE} and \.{CTANGLE}@>@/
@<Typedef declarations@>@/
@<Global variables@>@/
@<Predeclaration of procedures@>
@ We predeclare several standard system functions here instead of including their system header files, because the names of the header files are not as standard as the names of the functions. (For example, some \CEE/ environments have \.{<string.h>} where others have \.{<strings.h>}.)

@<Predeclaration of procedures@>=
extern int strlen(); /* length of string */
extern int strcmp(); /* compare strings lexicographically */
extern char* strcpy(); /* copy one string to another */
extern int strncmp(); /* compare up to $n$ string characters */
extern char* strncpy(); /* copy up to $n$ string characters */
@ \.{CWEAVE} has a fairly straightforward outline.  It operates in three phases: First it inputs the source file and stores cross-reference data, then it inputs the source once again and produces the \TEX/ output file, finally it sorts and outputs the index.  Please read the documentation for \.{common}, the set of routines common to \.{CTANGLE} and \.{CWEAVE}, before proceeding further.

@c
int main (ac, av)
int ac; /* argument count */
char **av; /* argument values */
{
  argc=ac; argv=av;
  program=cweave;
  make_xrefs=force_lines=1; /* controlled by command-line options */
  common_init();
  @<Set initial values@>;
  if (show_banner) printf(banner); /* print a ``banner line'' */
  @<Store all the reserved words@>;
  phase_one(); /* read all the user's text and store the cross-references */
  phase_two(); /* read all the text again and translate it to \TEX/ form */
  phase_three(); /* output the cross-reference index */
  return wrap_up(); /* and exit gracefully */
}@ We have to get \CEE/'s reserved words into the hash table, and the simplest way to do this is to insert them every time \.{CWEAVE} is run.  Fortunately there are relatively few reserved words. (Some of these are not strictly ``reserved,'' but are defined in header files of the ISO Standard \CEE/ Library.) @^reserved words@>

@<Store all the reserved words@>=
id_lookup("and",NULL,alfop);
id_lookup("and_eq",NULL,alfop);
id_lookup("asm",NULL,sizeof_like);
id_lookup("auto",NULL,int_like);
id_lookup("bitand",NULL,alfop);
id_lookup("bitor",NULL,alfop);
id_lookup("bool",NULL,raw_int);
id_lookup("break",NULL,case_like);
id_lookup("case",NULL,case_like);
id_lookup("catch",NULL,catch_like);
id_lookup("char",NULL,raw_int);
id_lookup("class",NULL,struct_like);
id_lookup("clock_t",NULL,raw_int);
id_lookup("compl",NULL,alfop);
id_lookup("const",NULL,const_like);
id_lookup("const_cast",NULL,raw_int);
id_lookup("continue",NULL,case_like);
id_lookup("default",NULL,case_like);
id_lookup("define",NULL,define_like);
id_lookup("defined",NULL,sizeof_like);
id_lookup("delete",NULL,delete_like);
id_lookup("div_t",NULL,raw_int);
id_lookup("do",NULL,do_like);
id_lookup("double",NULL,raw_int);
id_lookup("dynamic_cast",NULL,raw_int);
id_lookup("elif",NULL,if_like);
id_lookup("else",NULL,else_like);
id_lookup("endif",NULL,if_like);
id_lookup("enum",NULL,struct_like);
id_lookup("error",NULL,if_like);
id_lookup("explicit",NULL,int_like);
id_lookup("export",NULL,int_like);
id_lookup("extern",NULL,int_like);
id_lookup("FILE",NULL,raw_int);
id_lookup("float",NULL,raw_int);
id_lookup("for",NULL,for_like);
id_lookup("fpos_t",NULL,raw_int);
id_lookup("friend",NULL,int_like);
id_lookup("goto",NULL,case_like);
id_lookup("if",NULL,if_like);
id_lookup("ifdef",NULL,if_like);
id_lookup("ifndef",NULL,if_like);
id_lookup("include",NULL,if_like);
id_lookup("inline",NULL,int_like);
id_lookup("int",NULL,raw_int);
id_lookup("jmp_buf",NULL,raw_int);
id_lookup("ldiv_t",NULL,raw_int);
id_lookup("line",NULL,if_like);
id_lookup("long",NULL,raw_int);
id_lookup("mutable",NULL,int_like);
id_lookup("namespace",NULL,struct_like);
id_lookup("new",NULL,new_like);
id_lookup("not",NULL,alfop);
id_lookup("not_eq",NULL,alfop);
id_lookup("NULL",NULL,custom);
id_lookup("offsetof",NULL,raw_int);
id_lookup("operator",NULL,operator_like);
id_lookup("or",NULL,alfop);
id_lookup("or_eq",NULL,alfop);
id_lookup("pragma",NULL,if_like);
id_lookup("private",NULL,public_like);
id_lookup("protected",NULL,public_like);
id_lookup("ptrdiff_t",NULL,raw_int);
id_lookup("public",NULL,public_like);
id_lookup("register",NULL,int_like);
id_lookup("reinterpret_cast",NULL,raw_int);
id_lookup("return",NULL,case_like);
id_lookup("short",NULL,raw_int);
id_lookup("sig_atomic_t",NULL,raw_int);
id_lookup("signed",NULL,raw_int);
id_lookup("size_t",NULL,raw_int);
id_lookup("sizeof",NULL,sizeof_like);
id_lookup("static",NULL,int_like);
id_lookup("static_cast",NULL,raw_int);
id_lookup("struct",NULL,struct_like);
id_lookup("switch",NULL,for_like);
id_lookup("template",NULL,template_like);
id_lookup("this",NULL,custom);
id_lookup("throw",NULL,case_like);
id_lookup("time_t",NULL,raw_int);
id_lookup("try",NULL,else_like);
id_lookup("typedef",NULL,typedef_like);
id_lookup("typeid",NULL,raw_int);
id_lookup("typename",NULL,struct_like);
id_lookup("undef",NULL,if_like);
id_lookup("union",NULL,struct_like);
id_lookup("unsigned",NULL,raw_int);
id_lookup("using",NULL,int_like);
id_lookup("va_dcl",NULL,decl); /* Berkeley's variable-arg-list convention */
id_lookup("va_list",NULL,raw_int); /* ditto */
id_lookup("virtual",NULL,int_like);
id_lookup("void",NULL,raw_int);
id_lookup("volatile",NULL,const_like);
id_lookup("wchar_t",NULL,raw_int);
id_lookup("while",NULL,for_like);
id_lookup("xor",NULL,alfop);
id_lookup("xor_eq",NULL,alfop);
res_wd_end=name_ptr;
id_lookup("TeX",NULL,custom);
id_lookup("make_pair",NULL,func_template);
@ The following parameters were sufficient in the original \.{WEAVE} to handle \TEX/, so they should be sufficient for most applications of \.{CWEAVE}. If you change |max_bytes|, |max_names|, |hash_size|, or |buf_size| you have to change them also in the file |"common.w"|.

@d max_bytes 90000 /* the number of bytes in identifiers,
  index entries, and section names */
@d max_names 4000 /* number of identifiers, strings, section names;
  must be less than 10240; used in |"common.w"| */
@d max_sections 2000 /* greater than the total number of sections */
@d hash_size 353 /* should be prime */
@d buf_size 100 /* maximum length of input line, plus one */
@d longest_name 10000 /* section names and strings shouldn't be longer than this */
@d long_buf_size (buf_size+longest_name)
@d line_length 80 /* lines of \TEX/ output have at most this many characters;
  should be less than 256 */
@d max_refs 20000 /* number of cross-references; must be less than 65536 */
@d max_toks 20000 /* number of symbols in \CEE/ texts being parsed;
  must be less than 65536 */
@d max_texts 4000 /* number of phrases in \CEE/ texts being parsed;
  must be less than 10240 */
@d max_scraps 2000 /* number of tokens in \CEE/ texts being parsed */
@d stack_size 400 /* number of simultaneous output levels */

@ The next few sections contain stuff from the file |"common.w"| that must
be included in both |"ctangle.w"| and |"cweave.w"|. It appears in
file |"common.h"|, which needs to be updated when |"common.w"| changes.

@i common.h@* Data structures exclusive to {\tt CWEAVE}. As explained in \.{common.w}, the field of a |name_info| structure that contains the |rlink| of a section name is used for a completely different purpose in the case of identifiers.  It is then called the |ilk| of the identifier, and it is used to distinguish between various types of identifiers, as follows:  \yskip\hang |normal| and |func_template| identifiers are part of the \CEE/ program that will  appear in italic type (or in typewriter type if all uppercase).  \yskip\hang |custom| identifiers are part of the \CEE/ program that will be typeset in special ways.  \yskip\hang |roman| identifiers are index entries that appear after \.{@@\^} in the \.{CWEB} file.  \yskip\hang |wildcard| identifiers are index entries that appear after \.{@@:} in the \.{CWEB} file.  \yskip\hang |typewriter| identifiers are index entries that appear after \.{@@.} in the \.{CWEB} file.  \yskip\hang |alfop|, \dots, |template_like| identifiers are \CEE/ or \CPLUSPLUS/ reserved words whose |ilk| explains how they are to be treated when \CEE/ code is being formatted.

@d ilk dummy.Ilk
@d normal 0 /* ordinary identifiers have |normal| ilk */
@d roman 1 /* normal index entries have |roman| ilk */
@d wildcard 2 /* user-formatted index entries have |wildcard| ilk */
@d typewriter 3 /* `typewriter type' entries have |typewriter| ilk */
@d abnormal(a) (a->ilk>typewriter) /* tells if a name is special */
@d func_template 4 /* identifiers that can be followed by optional template */
@d custom 5 /* identifiers with user-given control sequence */
@d alfop 22 /* alphabetic operators like \&{and} or \&{not\_eq} */
@d else_like 26 /* \&{else} */
@d public_like 40 /* \&{public}, \&{private}, \&{protected} */
@d operator_like 41 /* \&{operator} */
@d new_like 42 /* \&{new} */
@d catch_like 43 /* \&{catch} */
@d for_like 45 /* \&{for}, \&{switch}, \&{while} */
@d do_like 46 /* \&{do} */
@d if_like 47 /* \&{if}, \&{ifdef}, \&{endif}, \&{pragma}, \dots */
@d delete_like 48 /* \&{delete} */
@d raw_ubin 49 /* `\.\&' or `\.*' when looking for \&{const} following */
@d const_like 50 /* \&{const}, \&{volatile} */
@d raw_int 51 /* \&{int}, \&{char}, \dots; also structure and class names  */
@d int_like 52 /* same, when not followed by left parenthesis or \DC\ */
@d case_like 53 /* \&{case}, \&{return}, \&{goto}, \&{break}, \&{continue} */
@d sizeof_like 54 /* \&{sizeof} */
@d struct_like 55 /* \&{struct}, \&{union}, \&{enum}, \&{class} */
@d typedef_like 56 /* \&{typedef} */
@d define_like 57 /* \&{define} */
@d template_like 58 /* \&{template} */
@ We keep track of the current section number in |section_count|, which is the total number of sections that have started.  Sections which have been altered by a change file entry have their |changed_section| flag turned on during the first phase.

@<Global variables@>=
boolean change_exists; /* has any section changed? */

@ The other large memory area in \.{CWEAVE} keeps the cross-reference data. All uses of the name |p| are recorded in a linked list beginning at |p->xref|, which points into the |xmem| array. The elements of |xmem| are structures consisting of an integer, |num|, and a pointer |xlink| to another element of |xmem|.  If |x=p->xref| is a pointer into |xmem|, the value of |x->num| is either a section number where |p| is used, or |cite_flag| plus a section number where |p| is mentioned, or |def_flag| plus a section number where |p| is defined; and |x->xlink| points to the next such cross-reference for |p|, if any. This list of cross-references is in decreasing order by section number. The next unused slot in |xmem| is |xref_ptr|. The linked list ends at |&xmem[0]|.  The global variable |xref_switch| is set either to |def_flag| or to zero, depending on whether the next cross-reference to an identifier is to be underlined or not in the index. This switch is set to |def_flag| when \.{@@!} or \.{@

@d} is scanned, and it is cleared to zero when
the next identifier or index entry cross-reference has been made.
Similarly, the global variable |section_xref_switch| is either
|def_flag| or |cite_flag| or zero, depending
on whether a section name is being defined, cited or used in \CEE/ text.

@<Typedef declarations@>=
typedef struct xref_info {
  sixteen_bits num; /* section number plus zero or |def_flag| */
  struct xref_info *xlink; /* pointer to the previous cross-reference */
} xref_info;
typedef xref_info *xref_pointer;

@ @<Global...@>=
xref_info xmem[max_refs]; /* contains cross-reference information */
xref_pointer xmem_end = xmem+max_refs-1;
xref_pointer xref_ptr; /* the largest occupied position in |xmem| */
sixteen_bits xref_switch,section_xref_switch; /* either zero or |def_flag| */

@ A section that is used for multi-file output (with the \.{@@(} feature) has a special first cross-reference whose |num| field is |file_flag|.

@d file_flag (3*cite_flag)
@d def_flag (2*cite_flag)
@d cite_flag 10240 /* must be strictly larger than |max_sections| */
@d xref equiv_or_xref

@<Set initial values@>=
xref_ptr=xmem; name_dir->xref=(char*)xmem; xref_switch=0; section_xref_switch=0;
xmem->num=0; /* sentinel value */@ A new cross-reference for an identifier is formed by calling |new_xref|, which discards duplicate entries and ignores non-underlined references to one-letter identifiers or \CEE/'s reserved words.  If the user has sent the |no_xref| flag (the \.{-x} option of the command line), it is unnecessary to keep track of cross-references for identifiers. If one were careful, one could probably make more changes around section 100 to avoid a lot of identifier looking up.

@d append_xref(c) if (xref_ptr==xmem_end) overflow("cross-reference");
  else (++xref_ptr)->num=c;
@d no_xref (flags['x']==0)
@d make_xrefs flags['x'] /* should cross references be output? */
@d is_tiny(p) ((p+1)->byte_start==(p)->byte_start+1)
@d unindexed(a) (a<res_wd_end && a->ilk>=custom)
      /* tells if uses of a name are to be indexed */

@c
void
new_xref(p)
name_pointer p;
{
  xref_pointer q; /* pointer to previous cross-reference */
  sixteen_bits m, n; /* new and previous cross-reference value */
  if (no_xref) return;
  if ((unindexed(p) || is_tiny(p)) && xref_switch==0) return;
  m=section_count+xref_switch; xref_switch=0; q=(xref_pointer)p->xref;
  if (q != xmem) {
    n=q->num;
    if (n==m || n==m+def_flag) return;
    else if (m==n+def_flag) {
        q->num=m; return;
    }
  }
  append_xref(m); xref_ptr->xlink=q; p->xref=(char*)xref_ptr;
}@ The cross-reference lists for section names are slightly different. Suppose that a section name is defined in sections $m_1$, \dots, $m_k$, cited in sections $n_1$, \dots, $n_l$, and used in sections $p_1$, \dots, $p_j$.  Then its list will contain $m_1+|def_flag|$, \dots, $m_k+|def_flag|$, $n_1+|cite_flag|$, \dots, $n_l+|cite_flag|$, $p_1$, \dots, $p_j$, in this order.  Although this method of storage takes quadratic time with respect to the length of the list, under foreseeable uses of \.{CWEAVE} this inefficiency is insignificant.

@c
void
new_section_xref(p)
name_pointer p;
{
  xref_pointer q,r; /* pointers to previous cross-references */
  q=(xref_pointer)p->xref; r=xmem;
  if (q>xmem)
        while (q->num>section_xref_switch) {r=q; q=q->xlink;}
  if (r->num==section_count+section_xref_switch)
        return; /* don't duplicate entries */
  append_xref(section_count+section_xref_switch);
  xref_ptr->xlink=q; section_xref_switch=0;
  if (r==xmem) p->xref=(char*)xref_ptr;
  else r->xlink=xref_ptr;
}@ The cross-reference list for a section name may also begin with |file_flag|. Here's how that flag gets put~in.

@c
void
set_file_flag(p)
name_pointer p;
{
  xref_pointer q;
  q=(xref_pointer)p->xref;
  if (q->num==file_flag) return;
  append_xref(file_flag);
  xref_ptr->xlink = q;
  p->xref = (char *)xref_ptr;
}@ A third large area of memory is used for sixteen-bit `tokens', which appear in short lists similar to the strings of characters in |byte_mem|. Token lists are used to contain the result of \CEE/ code translated into \TEX/ form; further details about them will be explained later. A |text_pointer| variable is an index into |tok_start|.

@<Typedef declarations@>=
typedef sixteen_bits token;
typedef token *token_pointer;
typedef token_pointer *text_pointer;

@ The first position of |tok_mem| that is unoccupied by replacement text is called |tok_ptr|, and the first unused location of |tok_start| is called |text_ptr|. Thus, we usually have |*text_ptr==tok_ptr|.

@<Global variables@>=
token tok_mem[max_toks]; /* tokens */
token_pointer tok_mem_end = tok_mem+max_toks-1; /* end of |tok_mem| */
token_pointer tok_start[max_texts]; /* directory into |tok_mem| */
token_pointer tok_ptr; /* first unused position in |tok_mem| */
text_pointer text_ptr; /* first unused position in |tok_start| */
text_pointer tok_start_end = tok_start+max_texts-1; /* end of |tok_start| */
token_pointer max_tok_ptr; /* largest value of |tok_ptr| */
text_pointer max_text_ptr; /* largest value of |text_ptr| */

@ @<Set init...@>=
tok_ptr=tok_mem+1; text_ptr=tok_start+1; tok_start[0]=tok_mem+1;
tok_start[1]=tok_mem+1;
max_tok_ptr=tok_mem+1; max_text_ptr=tok_start+1;@ Here are the three procedures needed to complete |id_lookup|:

@c
int names_match(p,first,l,t)
name_pointer p; /* points to the proposed match */
char *first; /* position of first character of string */
int l; /* length of identifier */
eight_bits t; /* desired ilk */
{
  if (length(p)!=l) return 0;
  if (p->ilk!=t && !(t==normal && abnormal(p))) return 0;
  return !strncmp(first,p->byte_start,l);
}

void
init_p(p,t)
name_pointer p;
eight_bits t;
{
  p->ilk=t; p->xref=(char*)xmem;
}

void
init_node(p)
name_pointer p;
{
  p->xref=(char*)xmem;
}@* Lexical scanning. Let us now consider the subroutines that read the \.{CWEB} source file and break it into meaningful units. There are four such procedures: One simply skips to the next `\.{@@\ }' or `\.{@

@*}' that begins a
section; another passes over the \TEX/ text at the beginning of a
section; the third passes over the \TEX/ text in a \CEE/ comment;
and the last, which is the most interesting, gets the next token of
a \CEE/ text.  They all use the pointers |limit| and |loc| into
the line of input currently being studied.@ Control codes in \.{CWEB}, which begin with `\.{@@}', are converted into a numeric code designed to simplify \.{CWEAVE}'s logic; for example, larger numbers are given to the control codes that denote more significant milestones, and the code of |new_section| should be the largest of all. Some of these numeric control codes take the place of |char| control codes that will not otherwise appear in the output of the scanning routines. @^ASCII code dependencies@>

@d ignore 00 /* control code of no interest to \.{CWEAVE} */
@d verbatim 02 /* takes the place of extended ASCII \.{\char2} */
@d begin_short_comment 03 /* \CPLUSPLUS/ short comment */
@d begin_comment '\t' /* tab marks will not appear */
@d underline '\n' /* this code will be intercepted without confusion */
@d noop 0177 /* takes the place of ASCII delete */
@d xref_roman 0203 /* control code for `\.{@@\^}' */
@d xref_wildcard 0204 /* control code for `\.{@@:}' */
@d xref_typewriter 0205 /* control code for `\.{@@.}' */
@d TeX_string 0206 /* control code for `\.{@@t}' */
@f TeX_string TeX
@d ord 0207 /* control code for `\.{@@'}' */
@d join 0210 /* control code for `\.{@@\&}' */
@d thin_space 0211 /* control code for `\.{@@,}' */
@d math_break 0212 /* control code for `\.{@@\v}' */
@d line_break 0213 /* control code for `\.{@@/}' */
@d big_line_break 0214 /* control code for `\.{@@\#}' */
@d no_line_break 0215 /* control code for `\.{@@+}' */
@d pseudo_semi 0216 /* control code for `\.{@@;}' */
@d macro_arg_open 0220 /* control code for `\.{@@[}' */
@d macro_arg_close 0221 /* control code for `\.{@@]}' */
@d trace 0222 /* control code for `\.{@@0}', `\.{@@1}' and `\.{@@2}' */
@d translit_code 0223 /* control code for `\.{@@l}' */
@d output_defs_code 0224 /* control code for `\.{@@h}' */
@d format_code 0225 /* control code for `\.{@@f}' and `\.{@@s}' */
@d definition 0226 /* control code for `\.{@@d}' */
@d begin_C 0227 /* control code for `\.{@@c}' */
@d section_name 0230 /* control code for `\.{@@<}' */
@d new_section 0231 /* control code for `\.{@@\ }' and `\.{@@*}' */

@ Control codes are converted to \.{CWEAVE}'s internal representation by means of the table |ccode|.

@<Global variables@>=
eight_bits ccode[256]; /* meaning of a char following \.{@@} */

@ @<Set ini...@>=
{int c; for (c=0; c<256; c++) ccode[c]=0;}
ccode[' ']=ccode['\t']=ccode['\n']=ccode['\v']=ccode['\r']=ccode['\f']
   =ccode['*']=new_section;
ccode['@@']='@@'; /* `quoted' at sign */
ccode['=']=verbatim;
ccode['d']=ccode['D']=definition;
ccode['f']=ccode['F']=ccode['s']=ccode['S']=format_code;
ccode['c']=ccode['C']=ccode['p']=ccode['P']=begin_C;
ccode['t']=ccode['T']=TeX_string;
ccode['l']=ccode['L']=translit_code;
ccode['q']=ccode['Q']=noop;
ccode['h']=ccode['H']=output_defs_code;
ccode['&']=join; ccode['<']=ccode['(']=section_name;
ccode['!']=underline; ccode['^']=xref_roman;
ccode[':']=xref_wildcard; ccode['.']=xref_typewriter; ccode[',']=thin_space;
ccode['|']=math_break; ccode['/']=line_break; ccode['#']=big_line_break;
ccode['+']=no_line_break; ccode[';']=pseudo_semi;
ccode['[']=macro_arg_open; ccode[']']=macro_arg_close;
ccode['\'']=ord;
@<Special control codes for debugging@>@;

@ Users can write \.{@@2}, \.{@@1}, and \.{@@0} to turn tracing fully on, partly on, and off, respectively.

@<Special control codes for debugging@>=
ccode['0']=ccode['1']=ccode['2']=trace;
@ The |skip_limbo| routine is used on the first pass to skip through portions of the input that are not in any sections, i.e., that precede the first section. After this procedure has been called, the value of |input_has_ended| will tell whether or not a section has actually been found.  There's a complication that we will postpone until later: If the \.{@@s} operation appears in limbo, we want to use it to adjust the default interpretation of identifiers.

@<Predeclaration of procedures@>=
void skip_limbo();

@ @c
void
skip_limbo() {
  while(1) {
    if (loc>limit && get_line()==0) return;
    *(limit+1)='@@';
    while (*loc!='@@') loc++; /* look for '@@', then skip two chars */
    if (loc++ <=limit) { int c=ccode[(eight_bits)*loc++];
      if (c==new_section) return;
      if (c==noop) skip_restricted();
      else if (c==format_code) @<Process simple format in limbo@>;
    }
  }
}
@ During the definition and \CEE/ parts of a section, cross-references are made for all identifiers except reserved words. However, the right identifier in a format definition is not referenced, and the left identifier is referenced only if it has been explicitly underlined (preceded by \.{@@!}). The \TEX/ code in comments is, of course, ignored, except for \CEE/ portions enclosed in \pb; the text of a section name is skipped entirely, even if it contains \pb\ constructions.  The variables |lhs| and |rhs| point to the respective identifiers involved in a format definition.

@<Global variables@>=
name_pointer lhs, rhs; /* pointers to |byte_start| for format identifiers */
name_pointer res_wd_end; /* pointer to the first nonreserved identifier */

@ A much simpler processing of format definitions occurs when the definition is found in limbo.

@<Process simple format in limbo@>=
{
  if (get_next()!=identifier)
    err_print("! Missing left identifier of @@s");
@.Missing left identifier...@>
  else {
    lhs=id_lookup(id_first,id_loc,normal);
    if (get_next()!=identifier)
      err_print("! Missing right identifier of @@s");
@.Missing right identifier...@>
    else {
      rhs=id_lookup(id_first,id_loc,normal);
      lhs->ilk=rhs->ilk;
    }
  }
}
@ The |skip_TeX| routine is used on the first pass to skip through the \TEX/ code at the beginning of a section. It returns the next control code or `\.{\v}' found in the input. A |new_section| is assumed to exist at the very end of the file.

@f skip_TeX TeX

@c
unsigned
skip_TeX() /* skip past pure \TEX/ code */
{
  while (1) {
    if (loc>limit && get_line()==0) return(new_section);
    *(limit+1)='@@';
    while (*loc!='@@' && *loc!='|') loc++;
    if (*loc++ =='|') return('|');
    if (loc<=limit) return(ccode[(eight_bits)*(loc++)]);
  }
}@*1 Inputting the next token. As stated above, \.{CWEAVE}'s most interesting lexical scanning routine is the |get_next| function that inputs the next token of \CEE/ input. However, |get_next| is not especially complicated.  The result of |get_next| is either a |char| code for some special character, or it is a special code representing a pair of characters (e.g., `\.{!=}'), or it is the numeric value computed by the |ccode| table, or it is one of the following special codes:  \yskip\hang |identifier|: In this case the global variables |id_first| and |id_loc| will have been set to the beginning and ending-plus-one locations in the buffer, as required by the |id_lookup| routine.  \yskip\hang |string|: The string will have been copied into the array |section_text|; |id_first| and |id_loc| are set as above (now they are pointers into |section_text|).  \yskip\hang |constant|: The constant is copied into |section_text|, with slight modifications; |id_first| and |id_loc| are set.  \yskip\noindent Furthermore, some of the control codes cause |get_next| to take additional actions:  \yskip\hang |xref_roman|, |xref_wildcard|, |xref_typewriter|, |TeX_string|, |verbatim|: The values of |id_first| and |id_loc| will have been set to the beginning and ending-plus-one locations in the buffer.  \yskip\hang |section_name|: In this case the global variable |cur_section| will point to the |byte_start| entry for the section name that has just been scanned. The value of |cur_section_char| will be |'('| if the section name was preceded by \.{@@(} instead of \.{@

@<}.

\yskip\noindent If |get_next| sees `\.{@@!}'
it sets |xref_switch| to |def_flag| and goes on to the next token.

@d constant 0200 /* \CEE/ constant */
@d string 0201 /* \CEE/ string */
@d identifier 0202 /* \CEE/ identifier or reserved word */

@<Global variables@>=
name_pointer cur_section; /* name of section just scanned */
char cur_section_char; /* the character just before that name */@ @<Include...@>=
#include <ctype.h> /* definition of |isalpha|, |isdigit| and so on */
#include <stdlib.h> /* definition of |exit| */
@ As one might expect, |get_next| consists mostly of a big switch that branches to the various special cases that can arise. \CEE/ allows underscores to appear in identifiers, and some \CEE/ compilers even allow the dollar sign.

@d isxalpha(c) ((c)=='_' || (c)=='$')
   /* non-alpha characters allowed in identifier */
@d ishigh(c) ((eight_bits)(c)>0177)
@^high-bit character handling@>

@<Predeclaration of procedures@>=
eight_bits get_next();
@ @c
eight_bits
get_next() /* produces the next input token */
{@+eight_bits c; /* the current character */
  while (1) {
    @<Check if we're at the end of a preprocessor command@>;
    if (loc>limit && get_line()==0) return(new_section);
    c=*(loc++);
    if (xisdigit(c) || c=='\\' || c=='.') @<Get a constant@>@;
    else if (c=='\'' || c=='"' || (c=='L'&&(*loc=='\'' || *loc=='"'))@|
           || (c=='<' && sharp_include_line==1))
        @<Get a string@>@;
    else if (xisalpha(c) || isxalpha(c) || ishigh(c))
      @<Get an identifier@>@;
    else if (c=='@@') @<Get control code and possible section name@>@;
    else if (xisspace(c)) continue; /* ignore spaces and tabs */
    if (c=='#' && loc==buffer+1) @<Raise preprocessor flag@>;
    mistake: @<Compress two-symbol operator@>@;
    return(c);
  }
}
@ Because preprocessor commands do not fit in with the rest of the syntax of \CEE/, we have to deal with them separately.  One solution is to enclose such commands between special markers.  Thus, when a \.\# is seen as the first character of a line, |get_next| returns a special code |left_preproc| and raises a flag |preprocessing|.  We can use the same internal code number for |left_preproc| as we do for |ord|, since |get_next| changes |ord| into a string.

@d left_preproc ord /* begins a preprocessor command */
@d right_preproc 0217 /* ends a preprocessor command */

@<Global variables@>=
boolean preprocessing=0; /* are we scanning a preprocessor command? */

@ @<Raise prep...@>= {
  preprocessing=1;
  @<Check if next token is |include|@>;
  return (left_preproc);
}
@ An additional complication is the freakish use of \.< and \.> to delimit a file name in lines that start with \.{\#include}.  We must treat this file name as a string.

@<Global variables@>=
boolean sharp_include_line=0; /* are we scanning a |#include| line? */

@ @<Check if next token is |include|@>=
while (loc<=buffer_end-7 && xisspace(*loc)) loc++;
if (loc<=buffer_end-6 && strncmp(loc,"include",7)==0) sharp_include_line=1;
@ When we get to the end of a preprocessor line, we lower the flag and send a code |right_preproc|, unless the last character was a \.\\.

@<Check if we're at the end of a preprocessor command@>=
  while (loc==limit-1 && preprocessing && *loc=='\\')
    if (get_line()==0) return(new_section); /* still in preprocessor mode */
  if (loc>=limit && preprocessing) {
    preprocessing=sharp_include_line=0;
    return(right_preproc);
  }
@ The following code assigns values to the combinations
\.{++}, \.{--}, \.{->}, \.{>=}, \.{<=}, \.{==}, \.{<<},
\.{>>}, \.{!=}, \.{\v\v}, and \.{\&\&}, and to the \CPLUSPLUS/ combinations \.{...}, \.{::}, \.{.*} and \.{->*}. The compound assignment operators (e.g., \.{+=}) are treated as separate tokens.

@d compress(c) if (loc++<=limit) return(c)

@<Compress two-symbol operator@>=
switch(c) {
  case '/': if (*loc=='*') {compress(begin_comment);}
    else if (*loc=='/') compress(begin_short_comment); break;
  case '+': if (*loc=='+') compress(plus_plus); break;
  case '-': if (*loc=='-') {compress(minus_minus);}
    else if (*loc=='>') if (*(loc+1)=='*') {loc++; compress(minus_gt_ast);}
                        else compress(minus_gt); break;
  case '.': if (*loc=='*') {compress(period_ast);}
            else if (*loc=='.' && *(loc+1)=='.') {
              loc++; compress(dot_dot_dot);
            }
            break;
  case ':': if (*loc==':') compress(colon_colon); break;
  case '=': if (*loc=='=') compress(eq_eq); break;
  case '>': if (*loc=='=') {compress(gt_eq);}
    else if (*loc=='>') compress(gt_gt); break;
  case '<': if (*loc=='=') {compress(lt_eq);}
    else if (*loc=='<') compress(lt_lt); break;
  case '&': if (*loc=='&') compress(and_and); break;
  case '|': if (*loc=='|') compress(or_or); break;
  case '!': if (*loc=='=') compress(not_eq); break;
}
@ @<Get an identifier@>= {
  id_first=--loc;
  while (isalpha(*++loc) || isdigit(*loc) || isxalpha(*loc) || ishigh(*loc));
  id_loc=loc; return(identifier);
}
@ Different conventions are followed by \TEX/ and \CEE/ to express octal and hexadecimal numbers; it is reasonable to stick to each convention within its realm.  Thus the \CEE/ part of a \.{CWEB} file has octals introduced by \.0 and hexadecimals by \.{0x}, but \.{CWEAVE} will print with \TeX/ macros that the user can redefine to fit the context. In order to simplify such macros, we replace some of the characters.  Notice that in this section and the next, |id_first| and |id_loc| are pointers into the array |section_text|, not into |buffer|.

@<Get a constant@>= {
  id_first=id_loc=section_text+1;
  if (*(loc-1)=='\\') {*id_loc++='~';
  while (xisdigit(*loc)) *id_loc++=*loc++;} /* octal constant */
  else if (*(loc-1)=='0') {
    if (*loc=='x' || *loc=='X') {*id_loc++='^'; loc++;
      while (xisxdigit(*loc)) *id_loc++=*loc++;} /* hex constant */
    else if (xisdigit(*loc)) {*id_loc++='~';
      while (xisdigit(*loc)) *id_loc++=*loc++;} /* octal constant */
    else goto dec; /* decimal constant */
  }
  else { /* decimal constant */
    if (*(loc-1)=='.' && !xisdigit(*loc)) goto mistake; /* not a constant */
    dec: *id_loc++=*(loc-1);
    while (xisdigit(*loc) || *loc=='.') *id_loc++=*loc++;
    if (*loc=='e' || *loc=='E') { /* float constant */
      *id_loc++='_'; loc++;
      if (*loc=='+' || *loc=='-') *id_loc++=*loc++;
      while (xisdigit(*loc)) *id_loc++=*loc++;
    }
  }
  while (*loc=='u' || *loc=='U' || *loc=='l' || *loc=='L'
         || *loc=='f' || *loc=='F') {
    *id_loc++='$'; *id_loc++=toupper(*loc); loc++;
  }
  return(constant);
}
@ \CEE/ strings and character constants, delimited by double and single quotes, respectively, can contain newlines or instances of their own delimiters if they are protected by a backslash.  We follow this convention, but do not allow the string to be longer than |longest_name|.

@<Get a string@>= {
  char delim = c; /* what started the string */
  id_first = section_text+1;
  id_loc = section_text;
  if (delim=='\'' && *(loc-2)=='@@') {*++id_loc='@@'; *++id_loc='@@';}
  *++id_loc=delim;
  if (delim=='L') { /* wide character constant */
    delim=*loc++; *++id_loc=delim;
  }
  if (delim=='<') delim='>'; /* for file names in |#include| lines */
  while (1) {
    if (loc>=limit) {
      if(*(limit-1)!='\\') {
        err_print("! String didn't end"); loc=limit; break;
@.String didn't end@>
      }
      if(get_line()==0) {
        err_print("! Input ended in middle of string"); loc=buffer; break;
@.Input ended in middle of string@>
      }
    }
    if ((c=*loc++)==delim) {
      if (++id_loc<=section_text_end) *id_loc=c;
      break;
    }
    if (c=='\\') if (loc>=limit) continue;
      else if (++id_loc<=section_text_end) {
        *id_loc = '\\'; c=*loc++;
      }
    if (++id_loc<=section_text_end) *id_loc=c;
  }
  if (id_loc>=section_text_end) {
    printf("\n! String too long: ");
@.String too long@>
    term_write(section_text+1,25);
    printf("..."); mark_error;
  }
  id_loc++;
  return(string);
}
@ After an \.{@@} sign has been scanned, the next character tells us whether there is more work to do.

@<Get control code and possible section name@>= {
  c=*loc++;
  switch(ccode[(eight_bits)c]) {
    case translit_code: err_print("! Use @@l in limbo only"); continue;
@.Use @@l in limbo...@>
    case underline: xref_switch=def_flag; continue;
    case trace: tracing=c-'0'; continue;
    case xref_roman: case xref_wildcard: case xref_typewriter:
    case noop: case TeX_string: c=ccode[c]; skip_restricted(); return(c);
    case section_name:
      @<Scan the section name and make |cur_section| point to it@>;
    case verbatim: @<Scan a verbatim string@>;
    case ord: @<Get a string@>;
    default: return(ccode[(eight_bits)c]);
  }
}
@ The occurrence of a section name sets |xref_switch| to zero, because the section name might (for example) follow \&{int}.

@<Scan the section name and make |cur_section| point to it@>= {
  char *k; /* pointer into |section_text| */
  cur_section_char=*(loc-1);
  @<Put section name into |section_text|@>;
  if (k-section_text>3 && strncmp(k-2,"...",3)==0)
        cur_section=section_lookup(section_text+1,k-3,1); /* 1 indicates a prefix */
  else cur_section=section_lookup(section_text+1,k,0);
  xref_switch=0; return(section_name);
}
@ At the present point in the program we have |*(loc-1)==verbatim|; we set |id_first| to the beginning of the string itself, and |id_loc| to its ending-plus-one location in the buffer.  We also set |loc| to the position just after the ending delimiter.

@<Scan a verbatim string@>= {
  id_first=loc++; *(limit+1)='@@'; *(limit+2)='>';
  while (*loc!='@@' || *(loc+1)!='>') loc++;
  if (loc>=limit) err_print("! Verbatim string didn't end");
@.Verbatim string didn't end@>
  id_loc=loc; loc+=2;
  return (verbatim);
}
@ Section names are placed into the |section_text| array with consecutive spaces, tabs, and carriage-returns replaced by single spaces. There will be no spaces at the beginning or the end. (We set |section_text[0]=' '| to facilitate this, since the |section_lookup| routine uses |section_text[1]| as the first character of the name.)

@<Set initial values@>=section_text[0]=' ';

@ @<Put section name...@>=
k=section_text;
while (1) {
  if (loc>limit && get_line()==0) {
    err_print("! Input ended in section name");
@.Input ended in section name@>
    loc=buffer+1; break;
  }
  c=*loc;
  @<If end of name or erroneous control code, |break|@>;
  loc++; if (k<section_text_end) k++;
  if (xisspace(c)) {
    c=' '; if (*(k-1)==' ') k--;
  }
*k=c;
}
if (k>=section_text_end) {
  printf("\n! Section name too long: ");
@.Section name too long@>
  term_write(section_text+1,25);
  printf("..."); mark_harmless;
}
if (*k==' ' && k>section_text) k--;
@ @<If end of name...@>=
if (c=='@@') {
  c=*(loc+1);
  if (c=='>') {
    loc+=2; break;
  }
  if (ccode[(eight_bits)c]==new_section) {
    err_print("! Section name didn't end"); break;
@.Section name didn't end@>
  }
  if (c!='@@') {
    err_print("! Control codes are forbidden in section name"); break;
@.Control codes are forbidden...@>
  }
  *(++k)='@@'; loc++; /* now |c==*loc| again */
}
@ This function skips over a restricted context at relatively high speed.

@<Predeclaration of procedures@>=
void skip_restricted();

@ @c
void
skip_restricted()
{
  id_first=loc; *(limit+1)='@@';
false_alarm:
  while (*loc!='@@') loc++;
  id_loc=loc;
  if (loc++>limit) {
    err_print("! Control text didn't end"); loc=limit;
@.Control text didn't end@>
  }
  else {
    if (*loc=='@@'&&loc<=limit) {loc++; goto false_alarm;}
    if (*loc++!='>')
      err_print("! Control codes are forbidden in control text");
@.Control codes are forbidden...@>
  }
}
@** Phase one processing. We now have accumulated enough subroutines to make it possible to carry out \.{CWEAVE}'s first pass over the source file. If everything works right, both phase one and phase two of \.{CWEAVE} will assign the same numbers to sections, and these numbers will agree with what \.{CTANGLE} does.  The global variable |next_control| often contains the most recent output of |get_next|; in interesting cases, this will be the control code that ended a section or part of a section.

@<Global variables@>=
eight_bits next_control; /* control code waiting to be acting upon */@ The overall processing strategy in phase one has the following straightforward outline.

@<Predeclaration of procedures@>=
void phase_one();

@ @c
void
phase_one() {
  phase=1; reset_input(); section_count=0;
  skip_limbo(); change_exists=0;
  while (!input_has_ended)
    @<Store cross-reference data for the current section@>;
  changed_section[section_count]=change_exists;
    /* the index changes if anything does */
  phase=2; /* prepare for second phase */
  @<Print error messages about unused or undefined section names@>;
}
@ @<Store cross-reference data...@>=
{
  if (++section_count==max_sections) overflow("section number");
  changed_section[section_count]=changing;
     /* it will become 1 if any line changes */
  if (*(loc-1)=='*' && show_progress) {
    printf("*%d",section_count);
    update_terminal; /* print a progress report */
  }
  @<Store cross-references in the \TEX/ part of a section@>;
  @<Store cross-references in the definition part of a section@>;
  @<Store cross-references in the \CEE/ part of a section@>;
  if (changed_section[section_count]) change_exists=1;
}
@ In the \TEX/ part of a section, cross-reference entries are made only for the identifiers in \CEE/ texts enclosed in \pb, or for control texts enclosed in \.{@@\^}$\,\ldots\,$\.{@@>} or \.{@@.}$\,\ldots\,$\.{@@>} or \.{@@:}$\,\ldots\,$\.{@@>}.

@<Store cross-references in the \TEX/ part of a section@>=
while (1) {
  switch (next_control=skip_TeX()) {
    case translit_code: err_print("! Use @@l in limbo only"); continue;
@.Use @@l in limbo...@>
    case underline: xref_switch=def_flag; continue;
    case trace: tracing=*(loc-1)-'0'; continue;
    case '|': C_xref(section_name); break;
    case xref_roman: case xref_wildcard: case xref_typewriter:
    case noop: case section_name:
      loc-=2; next_control=get_next(); /* scan to \.{@@>} */
      if (next_control>=xref_roman && next_control<=xref_typewriter) {
        @<Replace |"@@@@"| by |"@@"| @>@;
        new_xref(id_lookup(id_first, id_loc,next_control-identifier));
      }
      break;
  }
  if (next_control>=format_code) break;
}
@ @<Replace |"@@@@"| by |"@@"| @>=
{
  char *src=id_first,*dst=id_first;
  while(src<id_loc){
    if(*src=='@@') src++;
    *dst++=*src++;
  }
  id_loc=dst;
  while (dst<src) *dst++=' '; /* clean up in case of error message display */
}
@ When we get to the following code we have |next_control>=format_code|.

@<Store cross-references in the definition part of a section@>=
while (next_control<=definition) { /* |format_code| or |definition| */
  if (next_control==definition) {
    xref_switch=def_flag; /* implied \.{@@!} */
    next_control=get_next();
  } else @<Process a format definition@>;
  outer_xref();
}
@ Error messages for improper format definitions will be issued in phase two. Our job in phase one is to define the |ilk| of a properly formatted identifier, and to remove cross-references to identifiers that we now discover should be unindexed.

@<Process a format definition@>= {
  next_control=get_next();
  if (next_control==identifier) {
    lhs=id_lookup(id_first, id_loc,normal); lhs->ilk=normal;
    if (xref_switch) new_xref(lhs);
    next_control=get_next();
    if (next_control==identifier) {
      rhs=id_lookup(id_first, id_loc,normal);
      lhs->ilk=rhs->ilk;
      if (unindexed(lhs)) { /* retain only underlined entries */
        xref_pointer q,r=NULL;
        for (q=(xref_pointer)lhs->xref;q>xmem;q=q->xlink)
          if (q->num<def_flag)
            if (r) r->xlink=q->xlink;
            else lhs->xref=(char*)q->xlink;
          else r=q;
      }
      next_control=get_next();
    }
  }
}
@ Finally, when the \TEX/ and definition parts have been treated, we have |next_control>=begin_C|.

@<Store cross-references in the \CEE/ part of a section@>=
if (next_control<=section_name) {  /* |begin_C| or |section_name| */
  if (next_control==begin_C) section_xref_switch=0;
  else {
    section_xref_switch=def_flag;
    if(cur_section_char=='(' && cur_section!=name_dir)
      set_file_flag(cur_section);
  }
  do {
    if (next_control==section_name && cur_section!=name_dir)
      new_section_xref(cur_section);
    next_control=get_next(); outer_xref();
  } while ( next_control<=section_name);
}
@ @<Print error messages about un...@>=section_check(root)
@ The |C_xref| subroutine stores references to identifiers in \CEE/ text material beginning with the current value of |next_control| and continuing until |next_control| is `\.\{' or `\.{\v}', or until the next ``milestone'' is passed (i.e., |next_control>=format_code|). If |next_control>=format_code| when |C_xref| is called, nothing will happen; but if |next_control=='|'| upon entry, the procedure assumes that this is the `\.{\v}' preceding \CEE/ text that is to be processed.  The parameter |spec_ctrl| is used to change this behavior. In most cases |C_xref| is called with |spec_ctrl==ignore|, which triggers the default processing described above. If |spec_ctrl==section_name|, section names will be gobbled. This is used when \CEE/ text in the \TEX/ part or inside comments is parsed: It allows for section names to appear in \pb, but these strings will not be entered into the cross reference lists since they are not definitions of section names.  The program uses the fact that our internal code numbers satisfy the relations |xref_roman==identifier+roman| and |xref_wildcard==identifier +wildcard| and |xref_typewriter==identifier+typewriter|, as well as |normal==0|.

@<Predeclaration of procedures@>=
void C_xref();

@ @c
void
C_xref( spec_ctrl ) /* makes cross-references for \CEE/ identifiers */
  eight_bits spec_ctrl;
{
  name_pointer p; /* a referenced name */
  while (next_control<format_code || next_control==spec_ctrl) {
    if (next_control>=identifier && next_control<=xref_typewriter) {
      if (next_control>identifier) @<Replace |"@@@@"| by |"@@"| @>@;
      p=id_lookup(id_first, id_loc,next_control-identifier); new_xref(p);
    }
    if (next_control==section_name) {
      section_xref_switch=cite_flag;
      new_section_xref(cur_section);
    }
    next_control=get_next();
    if (next_control=='|' || next_control==begin_comment ||
        next_control==begin_short_comment) return;
  }
}
@ The |outer_xref| subroutine is like |C_xref| except that it begins with |next_control!='|'| and ends with |next_control>=format_code|. Thus, it handles \CEE/ text with embedded comments.

@<Predeclaration of procedures@>=
void outer_xref();

@ @c
void
outer_xref() /* extension of |C_xref| */
{
  int bal; /* brace level in comment */
  while (next_control<format_code)
    if (next_control!=begin_comment && next_control!=begin_short_comment)
      C_xref(ignore);
    else {
      boolean is_long_comment=(next_control==begin_comment);
      bal=copy_comment(is_long_comment,1); next_control='|';
      while (bal>0) {
        C_xref(section_name); /* do not reference section names in comments */
        if (next_control=='|') bal=copy_comment(is_long_comment,bal);
        else bal=0; /* an error message will occur in phase two */
      }
    }
}
@ After phase one has looked at everything, we want to check that each section name was both defined and used.  The variable |cur_xref| will point to cross-references for the current section name of interest.

@<Global variables@>=
xref_pointer cur_xref; /* temporary cross-reference pointer */
boolean an_output; /* did |file_flag| precede |cur_xref|? */

@ The following recursive procedure walks through the tree of section names and prints out anomalies. @^recursion@>

@<Predeclaration of procedures@>=
void section_check();

@ @c
void
section_check(p)
name_pointer p; /* print anomalies in subtree |p| */
{
  if (p) {
    section_check(p->llink);
    cur_xref=(xref_pointer)p->xref;
    if (cur_xref->num==file_flag) {an_output=1; cur_xref=cur_xref->xlink;}
    else an_output=0;
    if (cur_xref->num <def_flag) {
      printf("\n! Never defined: <"); print_section_name(p); putchar('>'); mark_harmless;
@.Never defined: <section name>@>
    }
    while (cur_xref->num >=cite_flag) cur_xref=cur_xref->xlink;
    if (cur_xref==xmem && !an_output) {
      printf("\n! Never used: <"); print_section_name(p); putchar('>'); mark_harmless;
@.Never used: <section name>@>
    }
    section_check(p->rlink);
  }
}
@* Low-level output routines. The \TEX/ output is supposed to appear in lines at most |line_length| characters long, so we place it into an output buffer. During the output process, |out_line| will hold the current line number of the line about to be output.

@<Global variables@>=
char out_buf[line_length+1]; /* assembled characters */
char *out_ptr; /* just after last character in |out_buf| */
char *out_buf_end = out_buf+line_length; /* end of |out_buf| */
int out_line; /* number of next line to be output */@ The |flush_buffer| routine empties the buffer up to a given breakpoint, and moves any remaining characters to the beginning of the next line. If the |per_cent| parameter is 1 a |'%'| is appended to the line that is being output; in this case the breakpoint |b| should be strictly less than |out_buf_end|. If the |per_cent| parameter is |0|, trailing blanks are suppressed. The characters emptied from the buffer form a new line of output; if the |carryover| parameter is true, a |"%"| in that line will be carried over to the next line (so that \TEX/ will ignore the completion of commented-out text).

@d c_line_write(c) fflush(active_file),fwrite(out_buf+1,sizeof(char),c,active_file)
@d tex_putc(c) putc(c,active_file)
@d tex_new_line putc('\n',active_file)
@d tex_printf(c) fprintf(active_file,c)

@c
void
flush_buffer(b,per_cent,carryover)
char *b;  /* outputs from |out_buf+1| to |b|,where |b<=out_ptr| */
boolean per_cent,carryover;
{
  char *j; j=b; /* pointer into |out_buf| */
  if (! per_cent) /* remove trailing blanks */
    while (j>out_buf && *j==' ') j--;
  c_line_write(j-out_buf);
  if (per_cent) tex_putc('%');
  tex_new_line; out_line++;
  if (carryover)
    while (j>out_buf)
      if (*j--=='%' && (j==out_buf || *j!='\\')) {
        *b--='%'; break;
      }
  if (b<out_ptr) strncpy(out_buf+1,b+1,out_ptr-b);
  out_ptr-=b-out_buf;
}@ When we are copying \TEX/ source material, we retain line breaks that occur in the input, except that an empty line is not output when the \TEX/ source line was nonempty. For example, a line of the \TEX/ file that contains only an index cross-reference entry will not be copied. The |finish_line| routine is called just before |get_line| inputs a new line, and just after a line break token has been emitted during the output of translated \CEE/ text.

@c
void
finish_line() /* do this at the end of a line */
{
  char *k; /* pointer into |buffer| */
  if (out_ptr>out_buf) flush_buffer(out_ptr,0,0);
  else {
    for (k=buffer; k<=limit; k++)
      if (!(xisspace(*k))) return;
    flush_buffer(out_buf,0,0);
  }
}@ In particular, the |finish_line| procedure is called near the very beginning of phase two. We initialize the output variables in a slightly tricky way so that the first line of the output file will be `\.{\\input cwebmac}'.

@<Set initial values@>=
out_ptr=out_buf+1; out_line=1; active_file=tex_file;
*out_ptr='c'; tex_printf("\\input cwebma");
@ When we wish to append one character |c| to the output buffer, we write `|out(c)|'; this will cause the buffer to be emptied if it was already full.  If we want to append more than one character at once, we say |out_str(s)|, where |s| is a string containing the characters.  A line break will occur at a space or after a single-nonletter \TEX/ control sequence.

@d out(c) {if (out_ptr>=out_buf_end) break_out(); *(++out_ptr)=c;}

@c
void
out_str(s) /* output characters from |s| to end of string */
char *s;
{
  while (*s) out(*s++);
}@ The |break_out| routine is called just before the output buffer is about to overflow. To make this routine a little faster, we initialize position 0 of the output buffer to `\.\\'; this character isn't really output.

@<Set initial values@>=
out_buf[0]='\\';

@ A long line is broken at a blank space or just before a backslash that isn't preceded by another backslash. In the latter case, a |'%'| is output at the break.

@<Predeclaration of procedures@>=
void break_out();

@ @c
void
break_out() /* finds a way to break the output line */
{
  char *k=out_ptr; /* pointer into |out_buf| */
  while (1) {
    if (k==out_buf) @<Print warning message, break the line, |return|@>;
    if (*k==' ') {
      flush_buffer(k,0,1); return;
    }
    if (*(k--)=='\\' && *k!='\\') { /* we've decreased |k| */
      flush_buffer(k,1,1); return;
    }
  }
}
@ We get to this section only in the unusual case that the entire output line consists of a string of backslashes followed by a string of nonblank non-backslashes. In such cases it is almost always safe to break the line by putting a |'%'| just before the last character.

@<Print warning message, break the line, |return|@>=
{
  printf("\n! Line had to be broken (output l. %d):\n",out_line);
@.Line had to be broken@>
  term_write(out_buf+1, out_ptr-out_buf-1);
  new_line; mark_harmless;
  flush_buffer(out_ptr-1,1,1); return;
}
@ Here is a macro that outputs a section number in decimal notation. The number to be converted by |out_section| is known to be less than |def_flag|, so it cannot have more than five decimal digits.  If the section is changed, we output `\.{\\*}' just after the number.

@c
void
out_section(n)
sixteen_bits n;
{
  char s[6];
  sprintf(s,"%d",n); out_str(s);
  if(changed_section[n]) out_str ("\\*");
@.\\*@>
}@ The |out_name| procedure is used to output an identifier or index entry, enclosing it in braces.

@c
void
out_name(p,quote_xalpha)
name_pointer p;
boolean quote_xalpha;
{
  char *k, *k_end=(p+1)->byte_start; /* pointers into |byte_mem| */
  out('{');
  for (k=p->byte_start; k<k_end; k++) {
    if (isxalpha(*k) && quote_xalpha) out('\\');
@.\\\$@>
@.\\\_@>
    out(*k);
  }
  out('}');
}@* Routines that copy \TEX/ material. During phase two, we use subroutines |copy_limbo|, |copy_TeX|, and |copy_comment| in place of the analogous |skip_limbo|, |skip_TeX|, and |skip_comment| that were used in phase one. (Well, |copy_comment| was actually written in such a way that it functions as |skip_comment| in phase one.)  The |copy_limbo| routine, for example, takes \TEX/ material that is not part of any section and transcribes it almost verbatim to the output file. The use of `\.{@@}' signs is severely restricted in such material: `\.{@@@@}' pairs are replaced by singletons; `\.{@@l}' and `\.{@@q}' and `\.{@@s}' are interpreted.

@c
void
copy_limbo()
{
  char c;
  while (1) {
    if (loc>limit && (finish_line(), get_line()==0)) return;
    *(limit+1)='@@';
    while (*loc!='@@') out(*(loc++));
    if (loc++<=limit) {
      c=*loc++;
      if (ccode[(eight_bits)c]==new_section) break;
      switch (ccode[(eight_bits)c]) {
        case translit_code: out_str("\\ATL"); break;
@.\\ATL@>
        case '@@': out('@@'); break;
        case noop: skip_restricted(); break;
        case format_code: if (get_next()==identifier) get_next();
          if (loc>=limit) get_line(); /* avoid blank lines in output */
          break; /* the operands of \.{@@s} are ignored on this pass */
        default: err_print("! Double @@ should be used in limbo");
@.Double @@ should be used...@>
        out('@@');
      }
    }
  }
}@ The |copy_TeX| routine processes the \TEX/ code at the beginning of a
section; for example, the words you are now reading were copied in this
way. It returns the next control code or `\.{\v}' found in the input.
We don't copy spaces or tab marks into the beginning of a line. This
makes the test for empty lines in |finish_line| work.

@ @f copy_TeX TeX
@c
eight_bits
copy_TeX()
{
  char c; /* current character being copied */
  while (1) {
    if (loc>limit && (finish_line(), get_line()==0)) return(new_section);
    *(limit+1)='@@';
    while ((c=*(loc++))!='|' && c!='@@') {
      out(c);
      if (out_ptr==out_buf+1 && (xisspace(c))) out_ptr--;
    }
    if (c=='|') return('|');
    if (loc<=limit) return(ccode[(eight_bits)*(loc++)]);
  }
}@ The |copy_comment| function issues a warning if more braces are opened than closed, and in the case of a more serious error it supplies enough braces to keep \TEX/ from complaining about unbalanced braces. Instead of copying the \TEX/ material into the output buffer, this function copies it into the token memory (in phase two only). The abbreviation |app_tok(t)| is used to append token |t| to the current token list, and it also makes sure that it is possible to append at least one further token without overflow.

@d app_tok(c) {if (tok_ptr+2>tok_mem_end) overflow("token"); *(tok_ptr++)=c;}

@<Predeclaration of procedures@>=
int copy_comment();

@ @c
int copy_comment(is_long_comment,bal) /* copies \TEX/ code in comments */
boolean is_long_comment; /* is this a traditional \CEE/ comment? */
int bal; /* brace balance */
{
  char c; /* current character being copied */
  while (1) {
    if (loc>limit) {
      if (is_long_comment) {
        if (get_line()==0) {
          err_print("! Input ended in mid-comment");
@.Input ended in mid-comment@>
          loc=buffer+1; goto done;
        }
      }
      else {
        if (bal>1) err_print("! Missing } in comment");
@.Missing \} in comment@>
        goto done;
      }
    }
    c=*(loc++);
    if (c=='|') return(bal);
    if (is_long_comment) @<Check for end of comment@>;
    if (phase==2) {
      if (ishigh(c)) app_tok(quoted_char);
      app_tok(c);
    }
    @<Copy special things when |c=='@@', '\\'|@>;
    if (c=='{') bal++;
    else if (c=='}') {
      if(bal>1) bal--;
      else {err_print("! Extra } in comment");
@.Extra \} in comment@>
        if (phase==2) tok_ptr--;
      }
    }
  }
done:@<Clear |bal| and |return|@>;
}
@ @<Check for end of comment@>=
if (c=='*' && *loc=='/') {
  loc++;
  if (bal>1) err_print("! Missing } in comment");
@.Missing \} in comment@>
  goto done;
}
@ @<Copy special things when |c=='@@'...@>=
if (c=='@@') {
  if (*(loc++)!='@@') {
    err_print("! Illegal use of @@ in comment");
@.Illegal use of @@...@>
    loc-=2; if (phase==2) *(tok_ptr-1)=' '; goto done;
  }
}
else if (c=='\\' && *loc!='@@')
  if (phase==2) app_tok(*(loc++)) else loc++;
@ We output enough right braces to keep \TEX/ happy.

@<Clear |bal| and |return|@>=
if (phase==2) while (bal-- >0) app_tok('}');
return(0);
@** Parsing.
The most intricate part of \.{CWEAVE} is its mechanism for converting
\CEE/-like code into \TEX/ code, and we might as well plunge into this
aspect of the program now. A ``bottom up'' approach is used to parse the
\CEE/-like material, since \.{CWEAVE} must deal with fragmentary
constructions whose overall ``part of speech'' is not known.

At the lowest level, the input is represented as a sequence of entities
that we shall call {\it scraps}, where each scrap of information consists
of two parts, its {\it category} and its {\it translation}. The category
is essentially a syntactic class, and the translation is a token list that
represents \TEX/ code. Rules of syntax and semantics tell us how to
combine adjacent scraps into larger ones, and if we are lucky an entire
\CEE/ text that starts out as hundreds of small scraps will join
together into one gigantic scrap whose translation is the desired \TEX/
code. If we are unlucky, we will be left with several scraps that don't
combine; their translations will simply be output, one by one.

The combination rules are given as context-sensitive productions that are
applied from left to right. Suppose that we are currently working on the
sequence of scraps $s_1\,s_2\ldots s_n$. We try first to find the longest
production that applies to an initial substring $s_1\,s_2\ldots\,$; but if
no such productions exist, we try to find the longest production
applicable to the next substring $s_2\,s_3\ldots\,$; and if that fails, we
try to match $s_3\,s_4\ldots\,$, etc.

A production applies if the category codes have a given pattern. For
example, one of the productions (see rule~3) is
$$\hbox{|exp| }\left\{\matrix{\hbox{|binop|}\cr\hbox{|ubinop|}}\right\}
\hbox{ |exp| }\RA\hbox{ |exp|}$$
and it means that three consecutive scraps whose respective categories are
|exp|, |binop| (or |ubinop|),
and |exp| are converted to one scrap whose category
is |exp|.  The translations of the original
scraps are simply concatenated.  The case of
$$\hbox{|exp| |comma| |exp| $\RA$ |exp|} \hskip4emE_1C\,\\{opt}9\,E_2$$
(rule 4) is only slightly more complicated:
Here the resulting |exp| translation
consists not only of the three original translations, but also of the
tokens |opt| and 9 between the translations of the
|comma| and the following |exp|.
In the \TEX/ file, this will specify an optional line break after the
comma, with penalty 90.

At each opportunity the longest possible production is applied.  For
example, if the current sequence of scraps is |int_like| |cast|
|lbrace|, rule 31 is applied; but if the sequence is |int_like| |cast|
followed by anything other than |lbrace|, rule 32 takes effect.

Translation rules such as `$E_1C\,\\{opt}9\,E_2$' above use subscripts
to distinguish between translations of scraps whose categories have the
same initial letter; these subscripts are assigned from left to right.@ Here is a list of the category codes that scraps can have. (A few others, like |int_like|, have already been defined; the |cat_name| array contains a complete list.)

@d exp 1 /* denotes an expression, including perhaps a single identifier */
@d unop 2 /* denotes a unary operator */
@d binop 3 /* denotes a binary operator */
@d ubinop 4
  /* denotes an operator that can be unary or binary, depending on context */
@d cast 5 /* denotes a cast */
@d question 6 /* denotes a question mark and possibly the expressions flanking it */
@d lbrace 7 /* denotes a left brace */
@d rbrace 8 /* denotes a right brace */
@d decl_head 9 /* denotes an incomplete declaration */
@d comma 10 /* denotes a comma */
@d lpar 11 /* denotes a left parenthesis or left bracket */
@d rpar 12 /* denotes a right parenthesis or right bracket */
@d prelangle 13 /* denotes `$<$' before we know what it is */
@d prerangle 14 /* denotes `$>$' before we know what it is */
@d langle 15 /* denotes `$<$' when it's used as angle bracket in a template */
@d colcol 18 /* denotes `::' */
@d base 19 /* denotes a colon that introduces a base specifier */
@d decl 20 /* denotes a complete declaration */
@d struct_head 21 /* denotes the beginning of a structure specifier */
@d stmt 23 /* denotes a complete statement */
@d function 24 /* denotes a complete function */
@d fn_decl 25 /* denotes a function declarator */
@d semi 27 /* denotes a semicolon */
@d colon 28 /* denotes a colon */
@d tag 29 /* denotes a statement label */
@d if_head 30 /* denotes the beginning of a compound conditional */
@d else_head 31 /* denotes a prefix for a compound statement */
@d if_clause 32 /* pending \.{if} together with a condition */
@d lproc 35 /* begins a preprocessor command */
@d rproc 36 /* ends a preprocessor command */
@d insert 37 /* a scrap that gets combined with its neighbor */
@d section_scrap 38 /* section name */
@d dead 39 /* scrap that won't combine */
@d ftemplate 59 /* \\{make\_pair} */
@d new_exp 60 /* \&{new} and a following type identifier */
@d begin_arg 61 /* \.{@@[} */
@d end_arg 62 /* \.{@@]} */

@<Global variables@>=
char cat_name[256][12];
eight_bits cat_index;

@ @<Set in...@>=
    for (cat_index=0;cat_index<255;cat_index++)
      strcpy(cat_name[cat_index],"UNKNOWN");
@.UNKNOWN@>
    strcpy(cat_name[exp],"exp");
    strcpy(cat_name[unop],"unop");
    strcpy(cat_name[binop],"binop");
    strcpy(cat_name[ubinop],"ubinop");
    strcpy(cat_name[cast],"cast");
    strcpy(cat_name[question],"?");
    strcpy(cat_name[lbrace],"{"@q}@>);
    strcpy(cat_name[rbrace],@q{@>"}");
    strcpy(cat_name[decl_head],"decl_head");
    strcpy(cat_name[comma],",");
    strcpy(cat_name[lpar],"(");
    strcpy(cat_name[rpar],")");
    strcpy(cat_name[prelangle],"<");
    strcpy(cat_name[prerangle],">");
    strcpy(cat_name[langle],"\\<");
    strcpy(cat_name[colcol],"::");
    strcpy(cat_name[base],"\\:");
    strcpy(cat_name[decl],"decl");
    strcpy(cat_name[struct_head],"struct_head");
    strcpy(cat_name[alfop],"alfop");
    strcpy(cat_name[stmt],"stmt");
    strcpy(cat_name[function],"function");
    strcpy(cat_name[fn_decl],"fn_decl");
    strcpy(cat_name[else_like],"else_like");
    strcpy(cat_name[semi],";");
    strcpy(cat_name[colon],":");
    strcpy(cat_name[tag],"tag");
    strcpy(cat_name[if_head],"if_head");
    strcpy(cat_name[else_head],"else_head");
    strcpy(cat_name[if_clause],"if()");
    strcpy(cat_name[lproc],"#{"@q}@>);
    strcpy(cat_name[rproc],@q{@>"#}");
    strcpy(cat_name[insert],"insert");
    strcpy(cat_name[section_scrap],"section");
    strcpy(cat_name[dead],"@@d");
    strcpy(cat_name[public_like],"public");
    strcpy(cat_name[operator_like],"operator");
    strcpy(cat_name[new_like],"new");
    strcpy(cat_name[catch_like],"catch");
    strcpy(cat_name[for_like],"for");
    strcpy(cat_name[do_like],"do");
    strcpy(cat_name[if_like],"if");
    strcpy(cat_name[delete_like],"delete");
    strcpy(cat_name[raw_ubin],"ubinop?");
    strcpy(cat_name[const_like],"const");
    strcpy(cat_name[raw_int],"raw");
    strcpy(cat_name[int_like],"int");
    strcpy(cat_name[case_like],"case");
    strcpy(cat_name[sizeof_like],"sizeof");
    strcpy(cat_name[struct_like],"struct");
    strcpy(cat_name[typedef_like],"typedef");
    strcpy(cat_name[define_like],"define");
    strcpy(cat_name[template_like],"template");
    strcpy(cat_name[ftemplate],"ftemplate");
    strcpy(cat_name[new_exp],"new_exp");
    strcpy(cat_name[begin_arg],"@@["@q]@>);
    strcpy(cat_name[end_arg],@q[@>"@@]");
    strcpy(cat_name[0],"zero");
@ This code allows \.{CWEAVE} to display its parsing steps.

@c
void
print_cat(c) /* symbolic printout of a category */
eight_bits c;
{
  printf(cat_name[c]);
}@ The token lists for translated \TEX/ output contain some special control symbols as well as ordinary characters. These control symbols are interpreted by \.{CWEAVE} before they are written to the output file.  \yskip\hang |break_space| denotes an optional line break or an en space;  \yskip\hang |force| denotes a line break;  \yskip\hang |big_force| denotes a line break with additional vertical space;  \yskip\hang |preproc_line| denotes that the line will be printed flush left;  \yskip\hang |opt| denotes an optional line break (with the continuation line indented two ems with respect to the normal starting position)---this code is followed by an integer |n|, and the break will occur with penalty $10n$;  \yskip\hang |backup| denotes a backspace of one em;  \yskip\hang |cancel| obliterates any |break_space|, |opt|, |force|, or |big_force| tokens that immediately precede or follow it and also cancels any |backup| tokens that follow it;  \yskip\hang |indent| causes future lines to be indented one more em;  \yskip\hang |outdent| causes future lines to be indented one less em.  \yskip\noindent All of these tokens are removed from the \TEX/ output that comes from \CEE/ text between \pb\ signs; |break_space| and |force| and |big_force| become single spaces in this mode. The translation of other \CEE/ texts results in \TEX/ control sequences \.{\\1}, \.{\\2}, \.{\\3}, \.{\\4}, \.{\\5}, \.{\\6}, \.{\\7}, \.{\\8} corresponding respectively to |indent|, |outdent|, |opt|, |backup|, |break_space|, |force|, |big_force| and |preproc_line|. However, a sequence of consecutive `\.\ ', |break_space|, |force|, and/or |big_force| tokens is first replaced by a single token (the maximum of the given ones).  The token |math_rel| will be translated into \.{\\MRL\{}, and it will get a matching \.\} later. Other control sequences in the \TEX/ output will be `\.{\\\\\{}$\,\ldots\,$\.\}' surrounding identifiers, `\.{\\\&\{}$\,\ldots\,$\.\}' surrounding reserved words, `\.{\\.\{}$\,\ldots\,$\.\}' surrounding strings, `\.{\\C\{}$\,\ldots\,$\.\}$\,$|force|' surrounding comments, and `\.{\\X$n$:}$\,\ldots\,$\.{\\X}' surrounding section names, where |n| is the section number.

@d math_rel 0206
@d big_cancel 0210 /* like |cancel|, also overrides spaces */
@d cancel 0211 /* overrides |backup|, |break_space|, |force|, |big_force| */
@d indent 0212 /* one more tab (\.{\\1}) */
@d outdent 0213 /* one less tab (\.{\\2}) */
@d opt 0214 /* optional break in mid-statement (\.{\\3}) */
@d backup 0215 /* stick out one unit to the left (\.{\\4}) */
@d break_space 0216 /* optional break between statements (\.{\\5}) */
@d force 0217 /* forced break between statements (\.{\\6}) */
@d big_force 0220 /* forced break with additional space (\.{\\7}) */
@d preproc_line 0221 /* begin line without indentation (\.{\\8}) */
@^high-bit character handling@>

@d quoted_char 0222
        /* introduces a character token in the range |0200|--|0377| */
@d end_translation 0223 /* special sentinel token at end of list */
@d inserted 0224 /* sentinel to mark translations of inserts */
@d qualifier 0225 /* introduces an explicit namespace qualifier */
@ The raw input is converted into scraps according to the following table, which gives category codes followed by the translations. \def\stars {\.{**}}% The symbol `\stars' stands for `\.{\\\&\{{\rm identifier}\}}', i.e., the identifier itself treated as a reserved word. The right-hand column is the so-called |mathness|, which is explained further below.  An identifier |c| of length 1 is translated as \.{\\\v c} instead of as \.{\\\\\{c\}}. An identifier \.{CAPS} in all caps is translated as \.{\\.\{CAPS\}} instead of as \.{\\\\\{CAPS\}}. An identifier that has become a reserved word via |typedef| is translated with \.{\\\&} replacing \.{\\\\} and |raw_int| replacing |exp|.  A string of length greater than 20 is broken into pieces of size at most~20 with discretionary breaks in between.  \yskip\halign{\quad#\hfil&\quad#\hfil&\quad\hfil#\hfil\cr \.{!=}&|binop|: \.{\\I}&yes\cr \.{<=}&|binop|: \.{\\Z}&yes\cr \.{>=}&|binop|: \.{\\G}&yes\cr \.{==}&|binop|: \.{\\E}&yes\cr \.{\&\&}&|binop|: \.{\\W}&yes\cr \.{\v\v}&|binop|: \.{\\V}&yes\cr \.{++}&|unop|: \.{\\PP}&yes\cr \.{--}&|unop|: \.{\\MM}&yes\cr \.{->}&|binop|: \.{\\MG}&yes\cr \.{>>}&|binop|: \.{\\GG}&yes\cr \.{<<}&|binop|: \.{\\LL}&yes\cr \.{::}&|colcol|: \.{\\DC}&maybe\cr \.{.*}&|binop|: \.{\\PA}&yes\cr \.{->*}&|binop|: \.{\\MGA}&yes\cr \.{...}&|raw_int|: \.{\\,\\ldots\\,}&yes\cr \."string\."&|exp|: \.{\\.\{}string with special characters quoted\.\}&maybe\cr \.{@@=}string\.{@@>}&|exp|: \.{\\vb\{}string with special characters   quoted\.\}&maybe\cr \.{@@'7'}&|exp|: \.{\\.\{@@'7'\}}&maybe\cr \.{077} or \.{\\77}&|exp|: \.{\\T\{\\\~77\}}&maybe\cr \.{0x7f}&|exp|: \.{\\T\{\\\^7f\}}&maybe\cr \.{77}&|exp|: \.{\\T\{77\}}&maybe\cr \.{77L}&|exp|: \.{\\T\{77\\\$L\}}&maybe\cr \.{0.1E5}&|exp|: \.{\\T\{0.1\\\_5\}}&maybe\cr \.+&|ubinop|: \.+&yes\cr \.-&|ubinop|: \.-&yes\cr \.*&|raw_ubin|: \.*&yes\cr \./&|binop|: \./&yes\cr \.<&|prelangle|: \.{\\langle}&yes\cr \.=&|binop|: \.{\\K}&yes\cr \.>&|prerangle|: \.{\\rangle}&yes\cr \..&|binop|: \..&yes\cr \.{\v}&|binop|: \.{\\OR}&yes\cr \.\^&|binop|: \.{\\XOR}&yes\cr \.\%&|binop|: \.{\\MOD}&yes\cr \.?&|question|: \.{\\?}&yes\cr \.!&|unop|: \.{\\R}&yes\cr \.\~&|unop|: \.{\\CM}&yes\cr \.\&&|raw_ubin|: \.{\\AND}&yes\cr \.(&|lpar|: \.(&maybe\cr \.[&|lpar|: \.[&maybe\cr \.)&|rpar|: \.)&maybe\cr \.]&|rpar|: \.]&maybe\cr \.\{&|lbrace|: \.\{&yes\cr \.\}&|lbrace|: \.\}&yes\cr \.,&|comma|: \.,&yes\cr \.;&|semi|: \.;&maybe\cr \.:&|colon|: \.:&no\cr \.\# (within line)&|ubinop|: \.{\\\#}&yes\cr \.\# (at beginning)&|lproc|:  |force| |preproc_line| \.{\\\#}&no\cr end of \.\# line&|rproc|:  |force|&no\cr identifier&|exp|: \.{\\\\\{}identifier with underlines and              dollar signs quoted\.\}&maybe\cr \.{and}&|alfop|: \stars&yes\cr \.{and\_eq}&|alfop|: \stars&yes\cr \.{asm}&|sizeof_like|: \stars&maybe\cr \.{auto}&|int_like|: \stars&maybe\cr \.{bitand}&|alfop|: \stars&yes\cr \.{bitor}&|alfop|: \stars&yes\cr \.{bool}&|raw_int|: \stars&maybe\cr \.{break}&|case_like|: \stars&maybe\cr \.{case}&|case_like|: \stars&maybe\cr \.{catch}&|catch_like|: \stars&maybe\cr \.{char}&|raw_int|: \stars&maybe\cr \.{class}&|struct_like|: \stars&maybe\cr \.{clock\_t}&|raw_int|: \stars&maybe\cr \.{compl}&|alfop|: \stars&yes\cr \.{const}&|const_like|: \stars&maybe\cr \.{const\_cast}&|raw_int|: \stars&maybe\cr \.{continue}&|case_like|: \stars&maybe\cr \.{default}&|case_like|: \stars&maybe\cr \.{define}&|define_like|: \stars&maybe\cr \.{defined}&|sizeof_like|: \stars&maybe\cr \.{delete}&|delete_like|: \stars&maybe\cr \.{div\_t}&|raw_int|: \stars&maybe\cr \.{do}&|do_like|: \stars&maybe\cr \.{double}&|raw_int|: \stars&maybe\cr \.{dynamic\_cast}&|raw_int|: \stars&maybe\cr \.{elif}&|if_like|: \stars&maybe\cr \.{else}&|else_like|: \stars&maybe\cr \.{endif}&|if_like|: \stars&maybe\cr \.{enum}&|struct_like|: \stars&maybe\cr \.{error}&|if_like|: \stars&maybe\cr \.{explicit}&|int_like|: \stars&maybe\cr \.{export}&|int_like|: \stars&maybe\cr \.{extern}&|int_like|: \stars&maybe\cr \.{FILE}&|raw_int|: \stars&maybe\cr \.{float}&|raw_int|: \stars&maybe\cr \.{for}&|for_like|: \stars&maybe\cr \.{fpos\_t}&|raw_int|: \stars&maybe\cr \.{friend}&|int_like|: \stars&maybe\cr \.{goto}&|case_like|: \stars&maybe\cr \.{if}&|if_like|: \stars&maybe\cr \.{ifdef}&|if_like|: \stars&maybe\cr \.{ifndef}&|if_like|: \stars&maybe\cr \.{include}&|if_like|: \stars&maybe\cr \.{inline}&|int_like|: \stars&maybe\cr \.{int}&|raw_int|: \stars&maybe\cr \.{jmp\_buf}&|raw_int|: \stars&maybe\cr \.{ldiv\_t}&|raw_int|: \stars&maybe\cr \.{line}&|if_like|: \stars&maybe\cr \.{long}&|raw_int|: \stars&maybe\cr \.{make\_pair}&|ftemplate|: \.{\\\\\{make\\\_pair\}}&maybe\cr \.{mutable}&|int_like|: \stars&maybe\cr \.{namespace}&|struct_like|: \stars&maybe\cr \.{new}&|new_like|: \stars&maybe\cr \.{not}&|alfop|: \stars&yes\cr \.{not\_eq}&|alfop|: \stars&yes\cr \.{NULL}&|exp|: \.{\\NULL}&yes\cr \.{offsetof}&|raw_int|: \stars&maybe\cr \.{operator}&|operator_like|: \stars&maybe\cr \.{or}&|alfop|: \stars&yes\cr \.{or\_eq}&|alfop|: \stars&yes\cr \.{pragma}&|if_like|: \stars&maybe\cr \.{private}&|public_like|: \stars&maybe\cr \.{protected}&|public_like|: \stars&maybe\cr \.{ptrdiff\_t}&|raw_int|: \stars&maybe\cr \.{public}&|public_like|: \stars&maybe\cr \.{register}&|int_like|: \stars&maybe\cr \.{reinterpret\_cast}&|raw_int|: \stars&maybe\cr \.{return}&|case_like|: \stars&maybe\cr \.{short}&|raw_int|: \stars&maybe\cr \.{sig\_atomic\_t}&|raw_int|: \stars&maybe\cr \.{signed}&|raw_int|: \stars&maybe\cr \.{size\_t}&|raw_int|: \stars&maybe\cr \.{sizeof}&|sizeof_like|: \stars&maybe\cr \.{static}&|int_like|: \stars&maybe\cr \.{static\_cast}&|raw_int|: \stars&maybe\cr \.{struct}&|struct_like|: \stars&maybe\cr \.{switch}&|for_like|: \stars&maybe\cr \.{template}&|template_like|: \stars&maybe\cr \.{TeX}&|exp|: \.{\\TeX}&yes\cr \.{this}&|exp|: \.{\\this}&yes\cr \.{throw}&|case_like|: \stars&maybe\cr \.{time\_t}&|raw_int|: \stars&maybe\cr \.{try}&|else_like|: \stars&maybe\cr \.{typedef}&|typedef_like|: \stars&maybe\cr \.{typeid}&|raw_int|: \stars&maybe\cr \.{typename}&|struct_like|: \stars&maybe\cr \.{undef}&|if_like|: \stars&maybe\cr \.{union}&|struct_like|: \stars&maybe\cr \.{unsigned}&|raw_int|: \stars&maybe\cr \.{using}&|int_like|: \stars&maybe\cr \.{va\_dcl}&|decl|: \stars&maybe\cr \.{va\_list}&|raw_int|: \stars&maybe\cr \.{virtual}&|int_like|: \stars&maybe\cr \.{void}&|raw_int|: \stars&maybe\cr \.{volatile}&|const_like|: \stars&maybe\cr \.{wchar\_t}&|raw_int|: \stars&maybe\cr \.{while}&|for_like|: \stars&maybe\cr \.{xor}&|alfop|: \stars&yes\cr \.{xor\_eq}&|alfop|: \stars&yes\cr \.{@@,}&|insert|: \.{\\,}&maybe\cr \.{@@\v}&|insert|:  |opt| \.0&maybe\cr \.{@@/}&|insert|:  |force|&no\cr \.{@@\#}&|insert|:  |big_force|&no\cr \.{@@+}&|insert|:  |big_cancel| \.{\{\}} |break_space|   \.{\{\}} |big_cancel|&no\cr \.{@@;}&|semi|: &maybe\cr \.{@@[@q]@>}&|begin_arg|: &maybe\cr \.{@q[@>@@]}&|end_arg|: &maybe\cr \.{@@\&}&|insert|: \.{\\J}&maybe\cr \.{@@h}&|insert|: |force| \.{\\ATH} |force|&no\cr \.{@

@<}\thinspace section name\thinspace\.{@@>}&|section_scrap|:
 \.{\\X}$n$\.:translated section name\.{\\X}&maybe\cr
\.{@@(@q)@>}\thinspace section name\thinspace\.{@@>}&|section_scrap|:
 \.{\\X}$n$\.{:\\.\{}section name with special characters
      quoted\.{\ \}\\X}&maybe\cr
\.{/*}comment\.{*/}&|insert|: |cancel|
      \.{\\C\{}translated comment\.\} |force|&no\cr
\.{//}comment&|insert|: |cancel|
      \.{\\SHC\{}translated comment\.\} |force|&no\cr
}

\smallskip
The construction \.{@@t}\thinspace stuff\/\thinspace\.{@@>} contributes
\.{\\hbox\{}\thinspace  stuff\/\thinspace\.\} to the following scrap.

@i prod.w
@* Implementing the productions. More specifically, a scrap is a structure consisting of a category |cat| and a |text_pointer| |trans|, which points to the translation in |tok_start|.  When \CEE/ text is to be processed with the grammar above, we form an array |scrap_info| containing the initial scraps. Our production rules have the nice property that the right-hand side is never longer than the left-hand side. Therefore it is convenient to use sequential allocation for the current sequence of scraps. Five pointers are used to manage the parsing:  \yskip\hang |pp| is a pointer into |scrap_info|.  We will try to match the category codes |pp->cat,@,@,(pp+1)->cat|$,\,\,\ldots\,$ to the left-hand sides of productions.  \yskip\hang |scrap_base|, |lo_ptr|, |hi_ptr|, and |scrap_ptr| are such that the current sequence of scraps appears in positions |scrap_base| through |lo_ptr| and |hi_ptr| through |scrap_ptr|, inclusive, in the |cat| and |trans| arrays. Scraps located between |scrap_base| and |lo_ptr| have been examined, while those in positions |>=hi_ptr| have not yet been looked at by the parsing process.  \yskip\noindent Initially |scrap_ptr| is set to the position of the final scrap to be parsed, and it doesn't change its value. The parsing process makes sure that |lo_ptr>=pp+3|, since productions have as many as four terms, by moving scraps from |hi_ptr| to |lo_ptr|. If there are fewer than |pp+3| scraps left, the positions up to |pp+3| are filled with blanks that will not match in any productions. Parsing stops when |pp==lo_ptr+1| and |hi_ptr==scrap_ptr+1|.  Since the |scrap| structure will later be used for other purposes, we declare its second element as a union.

@<Typedef declarations@>=
typedef struct {
  eight_bits cat;
  eight_bits mathness;
  union {
    text_pointer Trans;
    @<Rest of |trans_plus| union@>@;
  } trans_plus;
} scrap;
typedef scrap *scrap_pointer;@ @d trans trans_plus.Trans /* translation texts of scraps */

@<Global variables@>=
scrap scrap_info[max_scraps]; /* memory array for scraps */
scrap_pointer scrap_info_end=scrap_info+max_scraps -1; /* end of |scrap_info| */
scrap_pointer pp; /* current position for reducing productions */
scrap_pointer scrap_base; /* beginning of the current scrap sequence */
scrap_pointer scrap_ptr; /* ending of the current scrap sequence */
scrap_pointer lo_ptr; /* last scrap that has been examined */
scrap_pointer hi_ptr; /* first scrap that has not been examined */
scrap_pointer max_scr_ptr; /* largest value assumed by |scrap_ptr| */

@ @<Set init...@>=
scrap_base=scrap_info+1;
max_scr_ptr=scrap_ptr=scrap_info;
@ Token lists in |@!tok_mem| are composed of the following kinds of items for \TEX/ output.  \yskip\item{$\bullet$}Character codes and special codes like |force| and |math_rel| represent themselves;  \item{$\bullet$}|id_flag+p| represents \.{\\\\\{{\rm identifier $p$}\}};  \item{$\bullet$}|res_flag+p| represents \.{\\\&\{{\rm identifier $p$}\}};  \item{$\bullet$}|section_flag+p| represents section name |p|;  \item{$\bullet$}|tok_flag+p| represents token list number |p|;  \item{$\bullet$}|inner_tok_flag+p| represents token list number |p|, to be translated without line-break controls.

@d id_flag 10240 /* signifies an identifier */
@d res_flag 2*id_flag /* signifies a reserved word */
@d section_flag 3*id_flag /* signifies a section name */
@d tok_flag 4*id_flag /* signifies a token list */
@d inner_tok_flag 5*id_flag /* signifies a token list in `\pb' */

@c
void
print_text(p) /* prints a token list for debugging; not used in |main| */
text_pointer p;
{
  token_pointer j; /* index into |tok_mem| */
  sixteen_bits r; /* remainder of token after the flag has been stripped off */
  if (p>=text_ptr) printf("BAD");
  else for (j=*p; j<*(p+1); j++) {
    r=*j%id_flag;
    switch (*j/id_flag) {
      case 1: printf("\\\\{"@q}@>); print_id((name_dir+r)); printf(@q{@>"}");
        break; /* |id_flag| */
      case 2: printf("\\&{"@q}@>); print_id((name_dir+r)); printf(@q{@>"}");
        break; /* |res_flag| */
      case 3: printf("<"); print_section_name((name_dir+r)); printf(">");
        break; /* |section_flag| */
      case 4: printf("[[%d]]",r); break; /* |tok_flag| */
      case 5: printf("|[[%d]]|",r); break; /* |inner_tok_flag| */
      default: @<Print token |r| in symbolic form@>;
    }
  }
  fflush(stdout);
}@ @<Print token |r|...@>=
switch (r) {
  case math_rel: printf("\\mathrel{"@q}@>); break;
  case big_cancel: printf("[ccancel]"); break;
  case cancel: printf("[cancel]"); break;
  case indent: printf("[indent]"); break;
  case outdent: printf("[outdent]"); break;
  case backup: printf("[backup]"); break;
  case opt: printf("[opt]"); break;
  case break_space: printf("[break]"); break;
  case force: printf("[force]"); break;
  case big_force: printf("[fforce]"); break;
  case preproc_line: printf("[preproc]"); break;
  case quoted_char: j++; printf("[%o]",(unsigned)*j); break;
  case end_translation: printf("[quit]"); break;
  case inserted: printf("[inserted]"); break;
  default: putxchar(r);
}
@ The production rules listed above are embedded directly into \.{CWEAVE}, since it is easier to do this than to write an interpretive system that would handle production systems in general. Several macros are defined here so that the program for each production is fairly short.  All of our productions conform to the general notion that some |k| consecutive scraps starting at some position |j| are to be replaced by a single scrap of some category |c| whose translation is composed from the translations of the disappearing scraps. After this production has been applied, the production pointer |pp| should change by an amount |d|. Such a production can be represented by the quadruple |(j,k,c,d)|. For example, the production `|exp@,comma@,exp| $\RA$ |exp|' would be represented by `|(pp,3,exp,-2)|'; in this case the pointer |pp| should decrease by 2 after the production has been applied, because some productions with |exp| in their second or third positions might now match, but no productions have |exp| in the fourth position of their left-hand sides. Note that the value of |d| is determined by the whole collection of productions, not by an individual one. The determination of |d| has been done by hand in each case, based on the full set of productions but not on the grammar of \CEE/ or on the rules for constructing the initial scraps.  We also attach a serial number to each production, so that additional information is available when debugging. For example, the program below contains the statement `|reduce(pp,3,exp,-2,4)|' when it implements the production just mentioned.  Before calling |reduce|, the program should have appended the tokens of the new translation to the |tok_mem| array. We commonly want to append copies of several existing translations, and macros are defined to simplify these common cases. For example, \\{app2}|(pp)| will append the translations of two consecutive scraps, |pp->trans| and |(pp+1)->trans|, to the current token list. If the entire new translation is formed in this way, we write `|squash(j,k,c,d,n)|' instead of `|reduce(j,k,c,d,n)|'. For example, `|squash(pp,3,exp,-2,3)|' is an abbreviation for `\\{app3}|(pp); reduce(pp,3,exp,-2,3)|'.  A couple more words of explanation: Both |big_app| and |app| append a token (while |big_app1| to |big_app4| append the specified number of scrap translations) to the current token list. The difference between |big_app| and |app| is simply that |big_app| checks whether there can be a conflict between math and non-math tokens, and intercalates a `\.{\$}' token if necessary.  When in doubt what to use, use |big_app|.  The |mathness| is an attribute of scraps that says whether they are to be printed in a math mode context or not.  It is separate from the ``part of speech'' (the |cat|) because to make each |cat| have a fixed |mathness| (as in the original \.{WEAVE}) would multiply the number of necessary production rules.  The low two bits (i.e. |mathness % 4|) control the left boundary. (We need two bits because we allow cases |yes_math|, |no_math| and |maybe_math|, which can go either way.) The next two bits (i.e. |mathness / 4|) control the right boundary. If we combine two scraps and the right boundary of the first has a different mathness from the left boundary of the second, we insert a \.{\$} in between.  Similarly, if at printing time some irreducible scrap has a |yes_math| boundary the scrap gets preceded or followed by a \.{\$}. The left boundary is |maybe_math| if and only if the right boundary is.  The code below is an exact translation of the production rules into \CEE/, using such macros, and the reader should have no difficulty understanding the format by comparing the code with the symbolic productions as they were listed earlier.

@d no_math 2 /* should be in horizontal mode */
@d yes_math 1 /* should be in math mode */
@d maybe_math 0 /* works in either horizontal or math mode */
@d big_app2(a) big_app1(a);big_app1(a+1)
@d big_app3(a) big_app2(a);big_app1(a+2)
@d big_app4(a) big_app3(a);big_app1(a+3)
@d app(a) *(tok_ptr++)=a
@d app1(a) *(tok_ptr++)=tok_flag+(int)((a)->trans-tok_start)

@<Global variables@>=
int cur_mathness, init_mathness;
@ @c
void
app_str(s)
char *s;
{
  while (*s) app_tok(*(s++));
}

void
big_app(a)
token a;
{
        if (a==' ' || (a>=big_cancel && a<=big_force)) /* non-math token */ {
                if (cur_mathness==maybe_math) init_mathness=no_math;
                else if (cur_mathness==yes_math) app_str("{}$");
                cur_mathness=no_math;
        }
        else {
                if (cur_mathness==maybe_math) init_mathness=yes_math;
                else if (cur_mathness==no_math) app_str("${}");
                cur_mathness=yes_math;
        }
        app(a);
}

void
big_app1(a)
scrap_pointer a;
{
  switch (a->mathness % 4) { /* left boundary */
  case (no_math):
    if (cur_mathness==maybe_math) init_mathness=no_math;
    else if (cur_mathness==yes_math) app_str("{}$");
    cur_mathness=a->mathness / 4; /* right boundary */
    break;
  case (yes_math):
    if (cur_mathness==maybe_math) init_mathness=yes_math;
    else if (cur_mathness==no_math) app_str("${}");
    cur_mathness=a->mathness / 4; /* right boundary */
    break;
  case (maybe_math): /* no changes */ break;
  }
  app(tok_flag+(int)((a)->trans-tok_start));
}
@ In \CEE/, new specifier names can be defined via |typedef|, and we want to make the parser recognize future occurrences of the identifier thus defined as specifiers.  This is done by the procedure |make_reserved|, which changes the |ilk| of the relevant identifier.  We first need a procedure to recursively seek the first identifier in a token list, because the identifier might be enclosed in parentheses, as when one defines a function returning a pointer.  If the first identifier found is a keyword like `\&{case}', we return the special value |case_found|; this prevents underlining of identifiers in case labels.  If the first identifier is the keyword `\&{operator}', we give up; users who want to index definitions of overloaded \CPLUSPLUS/ operators should say, for example, `\.{@@!@@\^\\\&\{operator\} \$+\{=\}\$@@>}' (or, more properly alphebetized, `\.{@@!@@:operator+=\}\{\\\&\{operator\} \$+\{=\}\$@@>}').

@d no_ident_found (token_pointer)0 /* distinct from any identifier token */
@d case_found (token_pointer)1 /* likewise */
@d operator_found (token_pointer)2 /* likewise */

@c
token_pointer
find_first_ident(p)
text_pointer p;
{
  token_pointer q; /* token to be returned */
  token_pointer j; /* token being looked at */
  sixteen_bits r; /* remainder of token after the flag has been stripped off */
  if (p>=text_ptr) confusion("find_first_ident");
  for (j=*p; j<*(p+1); j++) {
    r=*j%id_flag;
    switch (*j/id_flag) {
      case 2: /* |res_flag| */
        if (name_dir[r].ilk==case_like) return case_found;
        if (name_dir[r].ilk==operator_like) return operator_found;
        if (name_dir[r].ilk!=raw_int) break;
      case 1: return j;
      case 4: case 5: /* |tok_flag| or |inner_tok_flag| */
        if ((q=find_first_ident(tok_start+r))!=no_ident_found)
          return q;
      default: ; /* char, |section_flag|, fall thru: move on to next token */
        if (*j==inserted) return no_ident_found; /* ignore inserts */
        else if (*j==qualifier) j++; /* bypass namespace qualifier */
    }
  }
  return no_ident_found;
}@ The scraps currently being parsed must be inspected for any occurrence of the identifier that we're making reserved; hence the |for| loop below.

@c
void
make_reserved(p) /* make the first identifier in |p->trans| like |int| */
scrap_pointer p;
{
  sixteen_bits tok_value; /* the name of this identifier, plus its flag*/
  token_pointer tok_loc; /* pointer to |tok_value| */
  if ((tok_loc=find_first_ident(p->trans))<=operator_found)
    return; /* this should not happen */
  tok_value=*tok_loc;
  for (;p<=scrap_ptr; p==lo_ptr? p=hi_ptr: p++) {
    if (p->cat==exp) {
      if (**(p->trans)==tok_value) {
        p->cat=raw_int;
        **(p->trans)=tok_value%id_flag+res_flag;
      }
    }
  }
  (name_dir+(sixteen_bits)(tok_value%id_flag))->ilk=raw_int;
  *tok_loc=tok_value%id_flag+res_flag;
}@ In the following situations we want to mark the occurrence of an identifier as a definition: when |make_reserved| is just about to be used; after a specifier, as in |char **argv|; before a colon, as in \\{found}:; and in the declaration of a function, as in \\{main}()$\{\ldots;\}$.  This is accomplished by the invocation of |make_underlined| at appropriate times.  Notice that, in the declaration of a function, we find out that the identifier is being defined only after it has been swallowed up by an |exp|.

@c
void
make_underlined(p)
/* underline the entry for the first identifier in |p->trans| */
scrap_pointer p;
{
  token_pointer tok_loc; /* where the first identifier appears */
  if ((tok_loc=find_first_ident(p->trans))<=operator_found)
    return; /* this happens, for example, in |case found:| */
  xref_switch=def_flag;
  underline_xref(*tok_loc%id_flag+name_dir);
}@ We cannot use |new_xref| to underline a cross-reference at this point because this would just make a new cross-reference at the end of the list. We actually have to search through the list for the existing cross-reference.

@<Predeclaration of procedures@>=
void  underline_xref();

@ @c
void
underline_xref(p)
name_pointer p;
{
  xref_pointer q=(xref_pointer)p->xref; /* pointer to cross-reference being examined */
  xref_pointer r; /* temporary pointer for permuting cross-references */
  sixteen_bits m; /* cross-reference value to be installed */
  sixteen_bits n; /* cross-reference value being examined */
  if (no_xref) return;
  m=section_count+xref_switch;
  while (q != xmem) {
    n=q->num;
    if (n==m) return;
    else if (m==n+def_flag) {
        q->num=m; return;
    }
    else if (n>=def_flag && n<m) break;
    q=q->xlink;
  }
  @<Insert new cross-reference at |q|, not at beginning of list@>;
}
@ We get to this section only when the identifier is one letter long, so it didn't get a non-underlined entry during phase one.  But it may have got some explicitly underlined entries in later sections, so in order to preserve the numerical order of the entries in the index, we have to insert the new cross-reference not at the beginning of the list (namely, at |p->xref|), but rather right before |q|.

@<Insert new cross-reference at |q|, not at beginning of list@>=
  append_xref(0); /* this number doesn't matter */
  xref_ptr->xlink=(xref_pointer)p->xref; r=xref_ptr;
  p->xref=(char*)xref_ptr;
  while (r->xlink!=q) {r->num=r->xlink->num; r=r->xlink;}
  r->num=m; /* everything from |q| on is left undisturbed */
@ Now here's the |reduce| procedure used in our code for productions.  The `|freeze_text|' macro is used to give official status to a token list. Before saying |freeze_text|, items are appended to the current token list, and we know that the eventual number of this token list will be the current value of |text_ptr|. But no list of that number really exists as yet, because no ending point for the current list has been stored in the |tok_start| array. After saying |freeze_text|, the old current token list becomes legitimate, and its number is the current value of |text_ptr-1| since |text_ptr| has been increased. The new current token list is empty and ready to be appended to. Note that |freeze_text| does not check to see that |text_ptr| hasn't gotten too large, since it is assumed that this test was done beforehand.

@d freeze_text *(++text_ptr)=tok_ptr

@c
void
reduce(j,k,c,d,n)
scrap_pointer j;
eight_bits c;
short k, d, n;
{
  scrap_pointer i, i1; /* pointers into scrap memory */
  j->cat=c; j->trans=text_ptr;
  j->mathness=4*cur_mathness+init_mathness;
  freeze_text;
  if (k>1) {
    for (i=j+k, i1=j+1; i<=lo_ptr; i++, i1++) {
      i1->cat=i->cat; i1->trans=i->trans;
      i1->mathness=i->mathness;
    }
    lo_ptr=lo_ptr-k+1;
  }
  pp=(pp+d<scrap_base? scrap_base: pp+d);
  @<Print a snapshot of the scrap list if debugging @>;
  pp--; /* we next say |pp++| */
}@ Here's the |squash| procedure, which takes advantage of the simplification that occurs when |k==1|.

@c
void
squash(j,k,c,d,n)
scrap_pointer j;
eight_bits c;
short k, d, n;
{
  scrap_pointer i; /* pointers into scrap memory */
  if (k==1) {
    j->cat=c; pp=(pp+d<scrap_base? scrap_base: pp+d);
    @<Print a snapshot...@>;
    pp--; /* we next say |pp++| */
    return;
  }
  for (i=j; i<j+k; i++) big_app1(i);
  reduce(j,k,c,d,n);
}@ If \.{CWEAVE} is being run in debugging mode, the production numbers and current stack categories will be printed out when |tracing| is set to 2; a sequence of two or more irreducible scraps will be printed out when |tracing| is set to 1.

@<Global variables@>=
int tracing; /* can be used to show parsing details */

@ @<Print a snapsh...@>=
{ scrap_pointer k; /* pointer into |scrap_info| */
  if (tracing==2) {
    printf("\n%d:",n);
    for (k=scrap_base; k<=lo_ptr; k++) {
      if (k==pp) putxchar('*'); else putxchar(' ');
      if (k->mathness %4 ==  yes_math) putchar('+');
      else if (k->mathness %4 ==  no_math) putchar('-');
      print_cat(k->cat);
      if (k->mathness /4 ==  yes_math) putchar('+');
      else if (k->mathness /4 ==  no_math) putchar('-');
    }
    if (hi_ptr<=scrap_ptr) printf("..."); /* indicate that more is coming */
  }
}
@ The |translate| function assumes that scraps have been stored in positions |scrap_base| through |scrap_ptr| of |cat| and |trans|. It applies productions as much as possible. The result is a token list containing the translation of the given sequence of scraps.  After calling |translate|, we will have |text_ptr+3<=max_texts| and |tok_ptr+6<=max_toks|, so it will be possible to create up to three token lists with up to six tokens without checking for overflow. Before calling |translate|, we should have |text_ptr<max_texts| and |scrap_ptr<max_scraps|, since |translate| might add a new text and a new scrap before it checks for overflow.

@c
text_pointer
translate() /* converts a sequence of scraps */
{
  scrap_pointer i, /* index into |cat| */
  j; /* runs through final scraps */
  pp=scrap_base; lo_ptr=pp-1; hi_ptr=pp;
  @<If tracing, print an indication of where we are@>;
  @<Reduce the scraps...@>;
  @<Combine the irreducible scraps that remain@>;
}@ @<If tracing,...@>=
if (tracing==2) {
  printf("\nTracing after l. %d:\n",cur_line); mark_harmless;
@.Tracing after...@>
  if (loc>buffer+50) {
    printf("...");
    term_write(loc-51,51);
  }
  else term_write(buffer,loc-buffer);
}
@ And here now is the code that applies productions as long as possible. Before applying the production mechanism, we must make sure it has good input (at least four scraps, the length of the lhs of the longest rules), and that there is enough room in the memory arrays to hold the appended tokens and texts.  Here we use a very conservative test; it's more important to make sure the program will still work if we change the production rules (within reason) than to squeeze the last bit of space from the memory arrays.

@d safe_tok_incr 20
@d safe_text_incr 10
@d safe_scrap_incr 10

@<Reduce the scraps using the productions until no more rules apply@>=
while (1) {
  @<Make sure the entries |pp| through |pp+3| of |cat| are defined@>;
  if (tok_ptr+safe_tok_incr>tok_mem_end) {
    if (tok_ptr>max_tok_ptr) max_tok_ptr=tok_ptr;
    overflow("token");
  }
  if (text_ptr+safe_text_incr>tok_start_end) {
    if (text_ptr>max_text_ptr) max_text_ptr=text_ptr;
    overflow("text");
  }
  if (pp>lo_ptr) break;
  init_mathness=cur_mathness=maybe_math;
  @<Match a production...@>;
}
@ If we get to the end of the scrap list, category codes equal to zero are stored, since zero does not match anything in a production.

@<Make sure the entries |pp| through |pp+3| of |cat| are defined@>=
if (lo_ptr<pp+3) {
  while (hi_ptr<=scrap_ptr && lo_ptr!=pp+3) {
    (++lo_ptr)->cat=hi_ptr->cat; lo_ptr->mathness=(hi_ptr)->mathness;
    lo_ptr->trans=(hi_ptr++)->trans;
  }
  for (i=lo_ptr+1;i<=pp+3;i++) i->cat=0;
}
@ Let us consider the big switch for productions now, before looking at its context. We want to design the program so that this switch works, so we might as well not keep ourselves in suspense about exactly what code needs to be provided with a proper environment.

@d cat1 (pp+1)->cat
@d cat2 (pp+2)->cat
@d cat3 (pp+3)->cat
@d lhs_not_simple (pp->cat!=public_like
        && pp->cat!=semi
        && pp->cat!=prelangle
        && pp->cat!=prerangle
        && pp->cat!=template_like
        && pp->cat!=new_like
        && pp->cat!=new_exp
        && pp->cat!=ftemplate
        && pp->cat!=raw_ubin
        && pp->cat!=const_like
        && pp->cat!=raw_int
        && pp->cat!=operator_like)
 /* not a production with left side length 1 */

@<Match a production at |pp|, or increase |pp| if there is no match@>= {
  if (cat1==end_arg && lhs_not_simple)
    if (pp->cat==begin_arg) squash(pp,2,exp,-2,124);
    else squash(pp,2,end_arg,-1,125);
  else if (cat1==insert) squash(pp,2,pp->cat,-2,0);
  else if (cat2==insert) squash(pp+1,2,(pp+1)->cat,-1,0);
  else if (cat3==insert) squash(pp+2,2,(pp+2)->cat,0,0);
  else
  switch (pp->cat) {
    case exp: @<Cases for |exp|@>; @+break;
    case lpar: @<Cases for |lpar|@>; @+break;
    case unop: @<Cases for |unop|@>; @+break;
    case ubinop: @<Cases for |ubinop|@>; @+break;
    case binop: @<Cases for |binop|@>; @+break;
    case cast: @<Cases for |cast|@>; @+break;
    case sizeof_like: @<Cases for |sizeof_like|@>; @+break;
    case int_like: @<Cases for |int_like|@>; @+break;
    case public_like: @<Cases for |public_like|@>; @+break;
    case colcol: @<Cases for |colcol|@>; @+break;
    case decl_head: @<Cases for |decl_head|@>; @+break;
    case decl: @<Cases for |decl|@>; @+break;
    case base: @<Cases for |base|@>; @+break;
    case struct_like: @<Cases for |struct_like|@>; @+break;
    case struct_head: @<Cases for |struct_head|@>; @+break;
    case fn_decl: @<Cases for |fn_decl|@>; @+break;
    case function: @<Cases for |function|@>; @+break;
    case lbrace: @<Cases for |lbrace|@>; @+break;
    case if_like: @<Cases for |if_like|@>; @+break;
    case else_like: @<Cases for |else_like|@>; @+break;
    case else_head: @<Cases for |else_head|@>; @+break;
    case if_clause: @<Cases for |if_clause|@>; @+break;
    case if_head: @<Cases for |if_head|@>; @+break;
    case do_like: @<Cases for |do_like|@>; @+break;
    case case_like: @<Cases for |case_like|@>; @+break;
    case catch_like: @<Cases for |catch_like|@>; @+break;
    case tag: @<Cases for |tag|@>; @+break;
    case stmt: @<Cases for |stmt|@>; @+break;
    case semi: @<Cases for |semi|@>; @+break;
    case lproc: @<Cases for |lproc|@>; @+break;
    case section_scrap: @<Cases for |section_scrap|@>; @+break;
    case insert: @<Cases for |insert|@>; @+break;
    case prelangle: @<Cases for |prelangle|@>; @+break;
    case prerangle: @<Cases for |prerangle|@>; @+break;
    case langle: @<Cases for |langle|@>; @+break;
    case template_like: @<Cases for |template_like|@>; @+break;
    case new_like: @<Cases for |new_like|@>; @+break;
    case new_exp: @<Cases for |new_exp|@>; @+break;
    case ftemplate: @<Cases for |ftemplate|@>; @+break;
    case for_like: @<Cases for |for_like|@>; @+break;
    case raw_ubin: @<Cases for |raw_ubin|@>; @+break;
    case const_like: @<Cases for |const_like|@>; @+break;
    case raw_int: @<Cases for |raw_int|@>; @+break;
    case operator_like: @<Cases for |operator_like|@>; @+break;
    case typedef_like: @<Cases for |typedef_like|@>; @+break;
    case delete_like: @<Cases for |delete_like|@>; @+break;
    case question: @<Cases for |question|@>; @+break;
  }
  pp++; /* if no match was found, we move to the right */
}
@ Now comes the code that tries to match each production starting with a particular type of scrap. Whenever a match is discovered, the |squash| or |reduce| macro will cause the appropriate action to be performed, followed by |goto found|.

@<Cases for |exp|@>=
if (cat1==lbrace || cat1==int_like || cat1==decl) {
  make_underlined(pp); big_app1(pp); big_app(indent); app(indent);
  reduce(pp,1,fn_decl,0,1);
}
else if (cat1==unop) squash(pp,2,exp,-2,2);
else if ((cat1==binop || cat1==ubinop) && cat2==exp)
        squash(pp,3,exp,-2,3);
else if (cat1==comma && cat2==exp) {
  big_app2(pp);
  app(opt); app('9'); big_app1(pp+2); reduce(pp,3,exp,-2,4);
}
else if (cat1==lpar && cat2==rpar && cat3==colon) squash(pp+3,1,base,0,5);
else if (cat1==cast && cat2==colon) squash(pp+2,1,base,0,5);
else if (cat1==semi) squash(pp,2,stmt,-1,6);
else if (cat1==colon) {
  make_underlined (pp);  squash(pp,2,tag,-1,7);
}
else if (cat1==rbrace) squash(pp,1,stmt,-1,8);
else if (cat1==lpar && cat2==rpar && (cat3==const_like || cat3==case_like)) {
  big_app1(pp+2); big_app(' '); big_app1(pp+3); reduce(pp+2,2,rpar,0,9);
}
else if (cat1==cast && (cat2==const_like || cat2==case_like)) {
  big_app1(pp+1); big_app(' '); big_app1(pp+2); reduce(pp+1,2,cast,0,9);
}
else if (cat1==exp || cat1==cast) squash(pp,2,exp,-2,10);
@ @<Cases for |lpar|@>=
if ((cat1==exp||cat1==ubinop) && cat2==rpar) squash(pp,3,exp,-2,11);
else if (cat1==rpar) {
  big_app1(pp); app('\\'); app(','); big_app1(pp+1);
@.\\,@>
  reduce(pp,2,exp,-2,12);
}
else if ((cat1==decl_head || cat1==int_like || cat1==cast) && cat2==rpar)
 squash(pp,3,cast,-2,13);
else if ((cat1==decl_head || cat1==int_like || cat1==exp) && cat2==comma) {
  big_app3(pp); app(opt); app('9'); reduce(pp,3,lpar,-1,14);
}
else if (cat1==stmt || cat1==decl) {
  big_app2(pp); big_app(' '); reduce(pp,2,lpar,-1,15);
}
@ @<Cases for |unop|@>=
if (cat1==exp || cat1==int_like) squash(pp,2,exp,-2,16);
@ @<Cases for |ubinop|@>=
if (cat1==cast && cat2==rpar) {
  big_app('{'); big_app1(pp); big_app('}'); big_app1(pp+1);
  reduce(pp,2,cast,-2,17);
}
else if (cat1==exp || cat1==int_like) {
  big_app('{'); big_app1(pp); big_app('}'); big_app1(pp+1);
  reduce(pp,2,cat1,-2,18);
}
else if (cat1==binop) {
  big_app(math_rel); big_app1(pp); big_app('{'); big_app1(pp+1); big_app('}');
  big_app('}'); reduce(pp,2,binop,-1,19);
}
@ @<Cases for |binop|@>=
if (cat1==binop) {
  big_app(math_rel); big_app('{'); big_app1(pp); big_app('}');
  big_app('{'); big_app1(pp+1); big_app('}');
  big_app('}'); reduce(pp,2,binop,-1,20);
}
@ @<Cases for |cast|@>=
if (cat1==lpar) squash(pp,2,lpar,-1,21);
else if (cat1==exp) {
  big_app1(pp); big_app(' '); big_app1(pp+1); reduce(pp,2,exp,-2,21);
}
else if (cat1==semi) squash(pp,1,exp,-2,22);
@ @<Cases for |sizeof_like|@>=
if (cat1==cast) squash(pp,2,exp,-2,23);
else if (cat1==exp) {
  big_app1(pp); big_app(' '); big_app1(pp+1); reduce(pp,2,exp,-2,24);
}
@ @<Cases for |int_like|@>=
if (cat1==int_like|| cat1==struct_like) {
  big_app1(pp); big_app(' '); big_app1(pp+1); reduce(pp,2,cat1,-2,25);
}
else if (cat1==exp && (cat2==raw_int||cat2==struct_like))
  squash(pp,2,int_like,-2,26);
else if (cat1==exp || cat1==ubinop || cat1==colon) {
  big_app1(pp); big_app(' '); reduce(pp,1,decl_head,-1,27);
}
else if (cat1==semi || cat1==binop) squash(pp,1,decl_head,0,28);
@ @<Cases for |public_like|@>=
if (cat1==colon) squash(pp,2,tag,-1,29);
else squash(pp,1,int_like,-2,30);
@ @<Cases for |colcol|@>=
if (cat1==exp||cat1==int_like) {
  app(qualifier); squash(pp,2,cat1,-2,31);
}@+else if (cat1==colcol) squash(pp,2,colcol,-1,32);
@ @<Cases for |decl_head|@>=
if (cat1==comma) {
  big_app2(pp); big_app(' '); reduce(pp,2,decl_head,-1,33);
}
else if (cat1==ubinop) {
  big_app1(pp); big_app('{'); big_app1(pp+1); big_app('}');
  reduce(pp,2,decl_head,-1,34);
}
else if (cat1==exp && cat2!=lpar && cat2!=exp && cat2!=cast) {
  make_underlined(pp+1); squash(pp,2,decl_head,-1,35);
}
else if ((cat1==binop||cat1==colon) && cat2==exp && (cat3==comma ||
    cat3==semi || cat3==rpar))
  squash(pp,3,decl_head,-1,36);
else if (cat1==cast) squash(pp,2,decl_head,-1,37);
else if (cat1==lbrace || cat1==int_like || cat1==decl) {
  big_app1(pp); big_app(indent); app(indent); reduce(pp,1,fn_decl,0,38);
}
else if (cat1==semi) squash(pp,2,decl,-1,39);
@ @<Cases for |decl|@>=
if (cat1==decl) {
  big_app1(pp); big_app(force); big_app1(pp+1);
  reduce(pp,2,decl,-1,40);
}
else if (cat1==stmt || cat1==function) {
  big_app1(pp); big_app(big_force);
  big_app1(pp+1); reduce(pp,2,cat1,-1,41);
}
@ @<Cases for |base|@>=
if (cat1==int_like || cat1==exp) {
  if (cat2==comma) {
    big_app1(pp); big_app(' '); big_app2(pp+1);
    app(opt); app('9'); reduce(pp,3,base,0,42);
  }
  else if (cat2==lbrace) {
    big_app1(pp); big_app(' '); big_app1(pp+1); big_app(' '); big_app1(pp+2);
    reduce(pp,3,lbrace,-2,43);
  }
}
@ @<Cases for |struct_like|@>=
if (cat1==lbrace) {
  big_app1(pp); big_app(' '); big_app1(pp+1); reduce(pp,2,struct_head,0,44);
}
else if (cat1==exp||cat1==int_like) {
  if (cat2==lbrace || cat2==semi) {
    make_underlined(pp+1); make_reserved(pp+1);
    big_app1(pp); big_app(' '); big_app1(pp+1);
    if (cat2==semi) reduce(pp,2,decl_head,0,45);
    else {
      big_app(' '); big_app1(pp+2);reduce(pp,3,struct_head,0,46);
    }
  }
  else if (cat2==colon) squash(pp+2,1,base,2,47);
  else if (cat2!=base) {
    big_app1(pp); big_app(' '); big_app1(pp+1); reduce(pp,2,int_like,-2,48);
  }
}
@ @<Cases for |struct_head|@>=
if ((cat1==decl || cat1==stmt || cat1==function) && cat2==rbrace) {
  big_app1(pp); big_app(indent); big_app(force); big_app1(pp+1);
  big_app(outdent); big_app(force);  big_app1(pp+2);
  reduce(pp,3,int_like,-2,49);
}
else if (cat1==rbrace) {
  big_app1(pp); app_str("\\,"); big_app1(pp+1);
@.\\,@>
  reduce(pp,2,int_like,-2,50);
}
@ @<Cases for |fn_decl|@>=
if (cat1==decl) {
  big_app1(pp); big_app(force); big_app1(pp+1); reduce(pp,2,fn_decl,0,51);
}
else if (cat1==stmt) {
  big_app1(pp); app(outdent); app(outdent); big_app(force);
  big_app1(pp+1); reduce(pp,2,function,-1,52);
}
@ @<Cases for |function|@>=
if (cat1==function || cat1==decl || cat1==stmt) {
  big_app1(pp); big_app(big_force); big_app1(pp+1); reduce(pp,2,cat1,-1,53);
}
@ @<Cases for |lbrace|@>=
if (cat1==rbrace) {
  big_app1(pp); app('\\'); app(','); big_app1(pp+1);
@.\\,@>
  reduce(pp,2,stmt,-1,54);
}
else if ((cat1==stmt||cat1==decl||cat1==function) && cat2==rbrace) {
  big_app(force); big_app1(pp);  big_app(indent); big_app(force);
  big_app1(pp+1); big_app(force); big_app(backup);  big_app1(pp+2);
  big_app(outdent); big_app(force); reduce(pp,3,stmt,-1,55);
}
else if (cat1==exp) {
  if (cat2==rbrace) squash(pp,3,exp,-2,56);
  else if (cat2==comma && cat3==rbrace) squash(pp,4,exp,-2,56);
}
@ @<Cases for |if_like|@>=
if (cat1==exp) {
  big_app1(pp); big_app(' '); big_app1(pp+1); reduce(pp,2,if_clause,0,57);
}
@ @<Cases for |else_like|@>=
if (cat1==colon) squash(pp+1,1,base,1,58);
else if (cat1==lbrace) squash(pp,1,else_head,0,59);
else if (cat1==stmt) {
  big_app(force); big_app1(pp); big_app(indent); big_app(break_space);
  big_app1(pp+1); big_app(outdent); big_app(force);
  reduce(pp,2,stmt,-1,60);
}
@ @<Cases for |else_head|@>=
if (cat1==stmt || cat1==exp) {
  big_app(force); big_app1(pp); big_app(break_space); app(noop);
  big_app(cancel); big_app1(pp+1); big_app(force);
  reduce(pp,2,stmt,-1,61);
}
@ @<Cases for |if_clause|@>=
if (cat1==lbrace) squash(pp,1,if_head,0,62);
else if (cat1==stmt) {
  if (cat2==else_like) {
    big_app(force); big_app1(pp); big_app(indent); big_app(break_space);
    big_app1(pp+1); big_app(outdent); big_app(force); big_app1(pp+2);
    if (cat3==if_like) {
      big_app(' '); big_app1(pp+3); reduce(pp,4,if_like,0,63);
    }@+else reduce(pp,3,else_like,0,64);
  }
  else squash(pp,1,else_like,0,65);
}
@ @<Cases for |if_head|@>=
if (cat1==stmt || cat1==exp) {
  if (cat2==else_like) {
    big_app(force); big_app1(pp); big_app(break_space); app(noop);
    big_app(cancel); big_app1(pp+1); big_app(force); big_app1(pp+2);
    if (cat3==if_like) {
      big_app(' '); big_app1(pp+3); reduce(pp,4,if_like,0,66);
    }@+else reduce(pp,3,else_like,0,67);
  }
  else squash(pp,1,else_head,0,68);
}
@ @<Cases for |do_like|@>=
if (cat1==stmt && cat2==else_like && cat3==semi) {
  big_app1(pp); big_app(break_space); app(noop); big_app(cancel);
  big_app1(pp+1); big_app(cancel); app(noop); big_app(break_space);
  big_app2(pp+2); reduce(pp,4,stmt,-1,69);
}
@ @<Cases for |case_like|@>=
if (cat1==semi) squash(pp,2,stmt,-1,70);
else if (cat1==colon) squash(pp,2,tag,-1,71);
else if (cat1==exp) {
  big_app1(pp); big_app(' ');  big_app1(pp+1);  reduce(pp,2,exp,-2,72);
}
@ @<Cases for |catch_like|@>=
if (cat1==cast || cat1==exp) {
  big_app2(pp); big_app(indent); big_app(indent); reduce(pp,2,fn_decl,0,73);
}
@ @<Cases for |tag|@>=
if (cat1==tag) {
  big_app1(pp); big_app(break_space); big_app1(pp+1); reduce(pp,2,tag,-1,74);
}
else if (cat1==stmt||cat1==decl||cat1==function) {
  big_app(force); big_app(backup); big_app1(pp); big_app(break_space);
  big_app1(pp+1); reduce(pp,2,cat1,-1,75);
}
@ The user can decide at run-time whether short statements should be grouped together on the same line.

@d force_lines flags['f'] /* should each statement be on its own line? */
@<Cases for |stmt|@>=
if (cat1==stmt||cat1==decl||cat1==function) {
  big_app1(pp);
  if (cat1==function) big_app(big_force);
  else if (cat1==decl) big_app(big_force);
  else if (force_lines) big_app(force);
  else big_app(break_space);
  big_app1(pp+1); reduce(pp,2,cat1,-1,76);
}
@ @<Cases for |semi|@>=
big_app(' '); big_app1(pp); reduce(pp,1,stmt,-1,77);
@ @<Cases for |lproc|@>=
if (cat1==define_like) make_underlined(pp+2);
if (cat1==else_like || cat1==if_like ||cat1==define_like)
  squash(pp,2,lproc,0,78);
else if (cat1==rproc) {
  app(inserted); big_app2(pp); reduce(pp,2,insert,-1,79);
} else if (cat1==exp || cat1==function) {
  if (cat2==rproc) {
    app(inserted); big_app1(pp); big_app(' '); big_app2(pp+1);
    reduce(pp,3,insert,-1,80);
  }
  else if (cat2==exp && cat3==rproc && cat1==exp) {
    app(inserted); big_app1(pp); big_app(' '); big_app1(pp+1); app_str(" \\5");
@.\\5@>
    big_app2(pp+2); reduce(pp,4,insert,-1,80);
  }
}
@ @<Cases for |section_scrap|@>=
if (cat1==semi) {
  big_app2(pp); big_app(force); reduce(pp,2,stmt,-2,81);
}
else squash(pp,1,exp,-2,82);
@ @<Cases for |insert|@>=
if (cat1)
  squash(pp,2,cat1,0,83);
@ @<Cases for |prelangle|@>=
init_mathness=cur_mathness=yes_math;
app('<'); reduce(pp,1,binop,-2,84);
@ @<Cases for |prerangle|@>=
init_mathness=cur_mathness=yes_math;
app('>'); reduce(pp,1,binop,-2,85);
@ @<Cases for |langle|@>=
if (cat1==prerangle) {
  big_app1(pp); app('\\'); app(','); big_app1(pp+1);
@.\\,@>
  reduce(pp,2,cast,-1,86);
}
else if (cat1==decl_head || cat1==int_like || cat1==exp) {
  if (cat2==prerangle) squash(pp,3,cast,-1,87);
  else if (cat2==comma) {
    big_app3(pp); app(opt); app('9'); reduce(pp,3,langle,0,88);
  }
}
@ @<Cases for |template_like|@>=
if (cat1==exp && cat2==prelangle) squash(pp+2,1,langle,2,89);
else if (cat1==exp || cat1==raw_int) {
  big_app1(pp); big_app(' '); big_app1(pp+1); reduce(pp,2,cat1,-2,90);
}@+ else squash(pp,1,raw_int,0,91);
@ @<Cases for |new_like|@>=
if (cat1==lpar && cat2==exp && cat3==rpar) squash(pp,4,new_like,0,92);
else if (cat1==cast) {
  big_app1(pp); big_app(' '); big_app1(pp+1); reduce(pp,2,exp,-2,93);
}
else if (cat1!=lpar) squash(pp,1,new_exp,0,94);
@ @<Cases for |new_exp|@>=
if (cat1==int_like || cat1==const_like) {
  big_app1(pp); big_app(' '); big_app1(pp+1); reduce(pp,2,new_exp,0,95);
}
else if (cat1==struct_like && (cat2==exp || cat2==int_like)) {
  big_app1(pp); big_app(' '); big_app1(pp+1); big_app(' ');
  big_app1(pp+2); reduce(pp,3,new_exp,0,96);
}
else if (cat1==raw_ubin) {
  big_app1(pp); big_app('{'); big_app1(pp+1); big_app('}');
  reduce(pp,2,new_exp,0,97);
}
else if (cat1==lpar) squash(pp,1,exp,-2,98);
else if (cat1==exp) {
  big_app1(pp); big_app(' '); reduce(pp,1,exp,-2,98);
}
else if (cat1!=raw_int && cat1!=struct_like && cat1!=colcol)
  squash(pp,1,exp,-2,99);
@ @<Cases for |ftemplate|@>=
if (cat1==prelangle) squash(pp+1,1,langle,1,100);
else squash(pp,1,exp,-2,101);
@ @<Cases for |for_like|@>=
if (cat1==exp) {
  big_app1(pp); big_app(' '); big_app1(pp+1); reduce(pp,2,else_like,-2,102);
}
@ @<Cases for |raw_ubin|@>=
if (cat1==const_like) {
  big_app2(pp); app_str("\\ "); reduce(pp,2,raw_ubin,0,103);
@.\\\ @>
} else squash(pp,1,ubinop,-2,104);
@ @<Cases for |const_like|@>=
squash(pp,1,int_like,-2,105);
@ @<Cases for |raw_int|@>=
if (cat1==prelangle) squash(pp+1,1,langle,1,106);
else if (cat1==colcol) squash(pp,2,colcol,-1,107);
else if (cat1==cast) squash(pp,2,raw_int,0,108);
else if (cat1==lpar) squash(pp,1,exp,-2,109);
else if (cat1!=langle) squash(pp,1,int_like,-3,110);
@ @<Cases for |operator_like|@>=
if (cat1==binop || cat1==unop || cat1==ubinop) {
  if (cat2==binop) break;
  big_app1(pp); big_app('{'); big_app1(pp+1); big_app('}');
  reduce(pp,2,exp,-2,111);
}
else if (cat1==new_like || cat1==delete_like) {
  big_app1(pp); big_app(' '); big_app1(pp+1); reduce(pp,2,exp,-2,112);
}
else if (cat1==comma) squash(pp,2,exp,-2,113);
else if (cat1!=raw_ubin) squash(pp,1,new_exp,0,114);
@ @<Cases for |typedef_like|@>=
if ((cat1==int_like || cat1==cast) && (cat2==comma || cat2==semi))
  squash(pp+1,1,exp,-1,115);
else if (cat1==int_like) {
  big_app1(pp); big_app(' '); big_app1(pp+1); reduce(pp,2,typedef_like,0,116);
}
else if (cat1==exp && cat2!=lpar && cat2!=exp && cat2!=cast) {
  make_underlined(pp+1); make_reserved(pp+1);
  big_app1(pp); big_app(' '); big_app1(pp+1); reduce(pp,2,typedef_like,0,117);
}
else if (cat1==comma) {
  big_app2(pp); big_app(' '); reduce(pp,2,typedef_like,0,118);
}
else if (cat1==semi) squash(pp,2,decl,-1,119);
else if (cat1==ubinop && (cat2==ubinop || cat2==cast)) {
  big_app('{'); big_app1(pp+1); big_app('}'); big_app1(pp+2);
  reduce(pp+1,2,cat2,0,120);
}
@ @<Cases for |delete_like|@>=
if (cat1==lpar && cat2==rpar) {
  big_app2(pp); app('\\'); app(','); big_app1(pp+2);
@.\\,@>
  reduce(pp,3,delete_like,0,121);
}
else if (cat1==exp) {
  big_app1(pp); big_app(' '); big_app1(pp+1); reduce(pp,2,exp,-2,122);
}
@ @<Cases for |question|@>=
if (cat1==exp && (cat2==colon || cat2==base)) {
  (pp+2)->mathness=5*yes_math; /* this colon should be in math mode */
  squash(pp,3,binop,-2,123);
}
@ If the initial sequence of scraps does not reduce to a single scrap, we concatenate the translations of all remaining scraps, separated by blank spaces, with dollar signs surrounding the translations of scraps where appropriate.

@<Combine the irreducible scraps that remain@>= {
  @<If semi-tracing, show the irreducible scraps@>;
  for (j=scrap_base; j<=lo_ptr; j++) {
    if (j!=scrap_base) app(' ');
    if (j->mathness % 4 == yes_math) app('$');
    app1(j);
    if (j->mathness / 4 == yes_math) app('$');
    if (tok_ptr+6>tok_mem_end) overflow("token");
  }
  freeze_text; return(text_ptr-1);
}
@ @<If semi-tracing, show the irreducible scraps@>=
if (lo_ptr>scrap_base && tracing==1) {
  printf("\nIrreducible scrap sequence in section %d:",section_count);
@.Irreducible scrap sequence...@>
  mark_harmless;
  for (j=scrap_base; j<=lo_ptr; j++) {
    printf(" "); print_cat(j->cat);
  }
}
@* Initializing the scraps. If we are going to use the powerful production mechanism just developed, we must get the scraps set up in the first place, given a \CEE/ text. A table of the initial scraps corresponding to \CEE/ tokens appeared above in the section on parsing; our goal now is to implement that table. We shall do this by implementing a subroutine called |C_parse| that is analogous to the |C_xref| routine used during phase one.  Like |C_xref|, the |C_parse| procedure starts with the current value of |next_control| and it uses the operation |next_control=get_next()| repeatedly to read \CEE/ text until encountering the next `\.{\v}' or `\.{/*}', or until |next_control>=format_code|. The scraps corresponding to what it reads are appended into the |cat| and |trans| arrays, and |scrap_ptr| is advanced.

@c
void
C_parse(spec_ctrl) /* creates scraps from \CEE/ tokens */
  eight_bits spec_ctrl;
{
  int count; /* characters remaining before string break */
  while (next_control<format_code || next_control==spec_ctrl) {
    @<Append the scrap appropriate to |next_control|@>;
    next_control=get_next();
    if (next_control=='|' || next_control==begin_comment ||
        next_control==begin_short_comment) return;
  }
}@ The following macro is used to append a scrap whose tokens have just been appended:

@d app_scrap(c,b) {
  (++scrap_ptr)->cat=(c); scrap_ptr->trans=text_ptr;
  scrap_ptr->mathness=5*(b); /* no no, yes yes, or maybe maybe */
  freeze_text;
}
@ @<Append the scr...@>=
@<Make sure that there is room for the new scraps, tokens, and texts@>;
switch (next_control) {
  case section_name:
    app(section_flag+(int)(cur_section-name_dir));
    app_scrap(section_scrap,maybe_math);
    app_scrap(exp,yes_math);@+break;
  case string: case constant: case verbatim: @<Append a string or constant@>;
   @+break;
  case identifier: app_cur_id(1);@+break;
  case TeX_string: @<Append a \TEX/ string, without forming a scrap@>;@+break;
  case '/': case '.':
    app(next_control); app_scrap(binop,yes_math);@+break;
  case '<': app_str("\\langle");@+app_scrap(prelangle,yes_math);@+break;
@.\\langle@>
  case '>': app_str("\\rangle");@+app_scrap(prerangle,yes_math);@+break;
@.\\rangle@>
  case '=': app_str("\\K"); app_scrap(binop,yes_math);@+break;
@.\\K@>
  case '|': app_str("\\OR"); app_scrap(binop,yes_math);@+break;
@.\\OR@>
  case '^': app_str("\\XOR"); app_scrap(binop,yes_math);@+break;
@.\\XOR@>
  case '%': app_str("\\MOD"); app_scrap(binop,yes_math);@+break;
@.\\MOD@>
  case '!': app_str("\\R"); app_scrap(unop,yes_math);@+break;
@.\\R@>
  case '~': app_str("\\CM"); app_scrap(unop,yes_math);@+break;
@.\\CM@>
  case '+': case '-': app(next_control); app_scrap(ubinop,yes_math);@+break;
  case '*': app(next_control); app_scrap(raw_ubin,yes_math);@+break;
  case '&': app_str("\\AND"); app_scrap(raw_ubin,yes_math);@+break;
@.\\AND@>
  case '?': app_str("\\?"); app_scrap(question,yes_math);@+break;
@.\\?@>
  case '#': app_str("\\#"); app_scrap(ubinop,yes_math);@+break;
@.\\\#@>
  case ignore: case xref_roman: case xref_wildcard:
  case xref_typewriter: case noop:@+break;
  case '(': case '[': app(next_control); app_scrap(lpar,maybe_math);@+break;
  case ')': case ']': app(next_control); app_scrap(rpar,maybe_math);@+break;
  case '{': app_str("\\{"@q}@>); app_scrap(lbrace,yes_math);@+break;
@.\\\{@>@q}@>
  case '}': app_str(@q{@>"\\}"); app_scrap(rbrace,yes_math);@+break;
@q{@>@.\\\}@>
  case ',': app(','); app_scrap(comma,yes_math);@+break;
  case ';': app(';'); app_scrap(semi,maybe_math);@+break;
  case ':': app(':'); app_scrap(colon,no_math);@+break;@/
  @t\4@>  @<Cases involving nonstandard characters@>@;
  case thin_space: app_str("\\,"); app_scrap(insert,maybe_math);@+break;
@.\\,@>
  case math_break: app(opt); app_str("0");
    app_scrap(insert,maybe_math);@+break;
  case line_break: app(force); app_scrap(insert,no_math);@+break;
  case left_preproc: app(force); app(preproc_line);
    app_str("\\#"); app_scrap(lproc,no_math);@+break;
@.\\\#@>
  case right_preproc: app(force); app_scrap(rproc,no_math);@+break;
  case big_line_break: app(big_force); app_scrap(insert,no_math);@+break;
  case no_line_break: app(big_cancel); app(noop); app(break_space);
    app(noop); app(big_cancel);
    app_scrap(insert,no_math);@+break;
  case pseudo_semi: app_scrap(semi,maybe_math);@+break;
  case macro_arg_open: app_scrap(begin_arg,maybe_math);@+break;
  case macro_arg_close: app_scrap(end_arg,maybe_math);@+break;
  case join: app_str("\\J"); app_scrap(insert,no_math);@+break;
@.\\J@>
  case output_defs_code: app(force); app_str("\\ATH"); app(force);
    app_scrap(insert,no_math);@+break;
@.\\ATH@>
  default: app(inserted); app(next_control);
    app_scrap(insert,maybe_math);@+break;
}
@ @<Make sure that there is room for the new...@>=
if (scrap_ptr+safe_scrap_incr>scrap_info_end ||
  tok_ptr+safe_tok_incr>tok_mem_end @| ||
  text_ptr+safe_text_incr>tok_start_end) {
  if (scrap_ptr>max_scr_ptr) max_scr_ptr=scrap_ptr;
  if (tok_ptr>max_tok_ptr) max_tok_ptr=tok_ptr;
  if (text_ptr>max_text_ptr) max_text_ptr=text_ptr;
  overflow("scrap/token/text");
}
@ Some nonstandard characters may have entered \.{CWEAVE} by means of standard ones. They are converted to \TEX/ control sequences so that it is possible to keep \.{CWEAVE} from outputting unusual |char| codes.

@<Cases involving nonstandard characters@>=
case not_eq: app_str("\\I");@+app_scrap(binop,yes_math);@+break;
@.\\I@>
case lt_eq: app_str("\\Z");@+app_scrap(binop,yes_math);@+break;
@.\\Z@>
case gt_eq: app_str("\\G");@+app_scrap(binop,yes_math);@+break;
@.\\G@>
case eq_eq: app_str("\\E");@+app_scrap(binop,yes_math);@+break;
@.\\E@>
case and_and: app_str("\\W");@+app_scrap(binop,yes_math);@+break;
@.\\W@>
case or_or: app_str("\\V");@+app_scrap(binop,yes_math);@+break;
@.\\V@>
case plus_plus: app_str("\\PP");@+app_scrap(unop,yes_math);@+break;
@.\\PP@>
case minus_minus: app_str("\\MM");@+app_scrap(unop,yes_math);@+break;
@.\\MM@>
case minus_gt: app_str("\\MG");@+app_scrap(binop,yes_math);@+break;
@.\\MG@>
case gt_gt: app_str("\\GG");@+app_scrap(binop,yes_math);@+break;
@.\\GG@>
case lt_lt: app_str("\\LL");@+app_scrap(binop,yes_math);@+break;
@.\\LL@>
case dot_dot_dot: app_str("\\,\\ldots\\,");@+app_scrap(raw_int,yes_math);
  @+break;
@.\\,@>
@.\\ldots@>
case colon_colon: app_str("\\DC");@+app_scrap(colcol,maybe_math);@+break;
@.\\DC@>
case period_ast: app_str("\\PA");@+app_scrap(binop,yes_math);@+break;
@.\\PA@>
case minus_gt_ast: app_str("\\MGA");@+app_scrap(binop,yes_math);@+break;
@.\\MGA@>
@ The following code must use |app_tok| instead of |app| in order to protect against overflow. Note that |tok_ptr+1<=max_toks| after |app_tok| has been used, so another |app| is legitimate before testing again.  Many of the special characters in a string must be prefixed by `\.\\' so that \TEX/ will print them properly. @^special string characters@>

@<Append a string or constant@>=
count= -1;
if (next_control==constant) app_str("\\T{"@q}@>);
@.\\T@>
else if (next_control==string) {
  count=20; app_str("\\.{"@q}@>);
}
@.\\.@>
else app_str("\\vb{"@q}@>);
@.\\vb@>
while (id_first<id_loc) {
  if (count==0) { /* insert a discretionary break in a long string */
     app_str(@q(@>@q{@>"}\\)\\.{"@q}@>); count=20;
@q(@>@.\\)@>
  }
@^high-bit character handling@>
  if((eight_bits)(*id_first)>0177) {
    app_tok(quoted_char);
    app_tok((eight_bits)(*id_first++));
  }
  else {
    switch (*id_first) {
      case  ' ':case '\\':case '#':case '%':case '$':case '^':
      case '{': case '}': case '~': case '&': case '_': app('\\'); break;
@.\\\ @>
@.\\\\@>
@.\\\#@>
@.\\\%@>
@.\\\$@>
@.\\\^@>
@.\\\{@>@q}@>
@q{@>@.\\\}@>
@.\\\~@>
@.\\\&@>
@.\\\_@>
      case '@@': if (*(id_first+1)=='@@') id_first++;
        else err_print("! Double @@ should be used in strings");
@.Double @@ should be used...@>
    }
    app_tok(*id_first++);
  }
  count--;
}
app(@q{@>'}');
app_scrap(exp,maybe_math);
@ We do not make the \TEX/ string into a scrap, because there is no telling what the user will be putting into it; instead we leave it open, to be picked up by the next scrap. If it comes at the end of a section, it will be made into a scrap when |finish_C| is called.  There's a known bug here, in cases where an adjacent scrap is |prelangle| or |prerangle|. Then the \TEX/ string can disappear when the \.{\\langle} or \.{\\rangle} becomes \.{<} or \.{>}. For example, if the user writes \.{\v x<@@ty@@>\v}, the \TEX/ string \.{\\hbox\{y\}} eventually becomes part of an |insert| scrap, which is combined with a |prelangle| scrap and eventually lost. The best way to work around this bug is probably to enclose the \.{@@t...@@>} in \.{@@[...@@]} so that the \TEX/ string is treated as an expression. @^bug, known@>

@<Append a \TEX/ string, without forming a scrap@>=
app_str("\\hbox{"@q}@>);
@^high-bit character handling@>
while (id_first<id_loc)
  if((eight_bits)(*id_first)>0177) {
    app_tok(quoted_char);
    app_tok((eight_bits)(*id_first++));
  }
  else {
    if (*id_first=='@@') id_first++;
    app_tok(*id_first++);
  }
app(@q{@>'}');
@ The function |app_cur_id| appends the current identifier to the token list; it also builds a new scrap if |scrapping==1|.

@<Predeclaration of procedures@>=
void app_cur_id();

@ @c
void
app_cur_id(scrapping)
boolean scrapping; /* are we making this into a scrap? */
{
  name_pointer p=id_lookup(id_first,id_loc,normal);
  if (p->ilk<=custom) { /* not a reserved word */
    app(id_flag+(int)(p-name_dir));
    if (scrapping) app_scrap(p->ilk==func_template? ftemplate: exp,
                             p->ilk==custom? yes_math: maybe_math);
@.\\NULL@>
  } else {
    app(res_flag+(int)(p-name_dir));
    if (scrapping) {
      if (p->ilk==alfop) app_scrap(ubinop,yes_math)@;
      else app_scrap(p->ilk,maybe_math);
    }
  }
}
@ When the `\.{\v}' that introduces \CEE/ text is sensed, a call on |C_translate| will return a pointer to the \TEX/ translation of that text. If scraps exist in |scrap_info|, they are unaffected by this translation process.

@c
text_pointer
C_translate()
{
  text_pointer p; /* points to the translation */
  scrap_pointer save_base; /* holds original value of |scrap_base| */
  save_base=scrap_base; scrap_base=scrap_ptr+1;
  C_parse(section_name); /* get the scraps together */
  if (next_control!='|') err_print("! Missing '|' after C text");
@.Missing '|'...@>
  app_tok(cancel); app_scrap(insert,maybe_math);
        /* place a |cancel| token as a final ``comment'' */
  p=translate(); /* make the translation */
  if (scrap_ptr>max_scr_ptr) max_scr_ptr=scrap_ptr;
  scrap_ptr=scrap_base-1; scrap_base=save_base; /* scrap the scraps */
  return(p);
}@ The |outer_parse| routine is to |C_parse| as |outer_xref| is to |C_xref|: It constructs a sequence of scraps for \CEE/ text until |next_control>=format_code|. Thus, it takes care of embedded comments.  The token list created from within `\pb' brackets is output as an argument to \.{\\PB}, if the user has invoked \.{CWEAVE} with the \.{+e} flag. Although \.{cwebmac} ignores \.{\\PB}, other macro packages might use it to localize the special meaning of the macros that mark up program text.

@d make_pb flags['e']

@c
void
outer_parse() /* makes scraps from \CEE/ tokens and comments */
{
  int bal; /* brace level in comment */
  text_pointer p, q; /* partial comments */
  while (next_control<format_code)
    if (next_control!=begin_comment && next_control!=begin_short_comment)
      C_parse(ignore);
    else {
      boolean is_long_comment=(next_control==begin_comment);
      @<Make sure that there is room for the new...@>;
      app(cancel); app(inserted);
      if (is_long_comment) app_str("\\C{"@q}@>);
@.\\C@>
      else app_str("\\SHC{"@q}@>);
@.\\SHC@>
      bal=copy_comment(is_long_comment,1); next_control=ignore;
      while (bal>0) {
        p=text_ptr; freeze_text; q=C_translate();
         /* at this point we have |tok_ptr+6<=max_toks| */
        app(tok_flag+(int)(p-tok_start));
        if (make_pb) app_str("\\PB{");
@.\\PB@>
        app(inner_tok_flag+(int)(q-tok_start));
        if (make_pb)  app_tok('}');
        if (next_control=='|') {
          bal=copy_comment(is_long_comment,bal);
          next_control=ignore;
        }
        else bal=0; /* an error has been reported */
      }
      app(force); app_scrap(insert,no_math);
        /* the full comment becomes a scrap */
    }
}@* Output of tokens.
So far our programs have only built up multi-layered token lists in
\.{CWEAVE}'s internal memory; we have to figure out how to get them into
the desired final form. The job of converting token lists to characters in
the \TEX/ output file is not difficult, although it is an implicitly
recursive process. Four main considerations had to be kept in mind when
this part of \.{CWEAVE} was designed.  (a) There are two modes of output:
|outer| mode, which translates tokens like |force| into line-breaking
control sequences, and |inner| mode, which ignores them except that blank
spaces take the place of line breaks. (b) The |cancel| instruction applies
to adjacent token or tokens that are output, and this cuts across levels
of recursion since `|cancel|' occurs at the beginning or end of a token
list on one level. (c) The \TEX/ output file will be semi-readable if line
breaks are inserted after the result of tokens like |break_space| and
|force|.  (d) The final line break should be suppressed, and there should
be no |force| token output immediately after `\.{\\Y\\B}'.@ The output process uses a stack to keep track of what is going on at different ``levels'' as the token lists are being written out. Entries on this stack have three parts:  \yskip\hang |end_field| is the |tok_mem| location where the token list of a particular level will end;  \yskip\hang |tok_field| is the |tok_mem| location from which the next token on a particular level will be read;  \yskip\hang |mode_field| is the current mode, either |inner| or |outer|.  \yskip\noindent The current values of these quantities are referred to quite frequently, so they are stored in a separate place instead of in the |stack| array. We call the current values |cur_end|, |cur_tok|, and |cur_mode|.  The global variable |stack_ptr| tells how many levels of output are currently in progress. The end of output occurs when an |end_translation| token is found, so the stack is never empty except when we first begin the output process.

@d inner 0 /* value of |mode| for \CEE/ texts within \TEX/ texts */
@d outer 1 /* value of |mode| for \CEE/ texts in sections */

@<Typedef declarations@>= typedef int mode;
typedef struct {
  token_pointer end_field; /* ending location of token list */
  token_pointer tok_field; /* present location within token list */
  boolean mode_field; /* interpretation of control tokens */
} output_state;
typedef output_state *stack_pointer;

@ @d cur_end cur_state.end_field /* current ending location in |tok_mem| */
@d cur_tok cur_state.tok_field /* location of next output token in |tok_mem| */
@d cur_mode cur_state.mode_field /* current mode of interpretation */
@d init_stack stack_ptr=stack;cur_mode=outer /* initialize the stack */

@<Global variables@>=
output_state cur_state; /* |cur_end|, |cur_tok|, |cur_mode| */
output_state stack[stack_size]; /* info for non-current levels */
stack_pointer stack_ptr; /* first unused location in the output state stack */
stack_pointer stack_end=stack+stack_size-1; /* end of |stack| */
stack_pointer max_stack_ptr; /* largest value assumed by |stack_ptr| */

@ @<Set init...@>=
max_stack_ptr=stack;
@ To insert token-list |p| into the output, the |push_level| subroutine is called; it saves the old level of output and gets a new one going. The value of |cur_mode| is not changed.

@c
void
push_level(p) /* suspends the current level */
text_pointer p;
{
  if (stack_ptr==stack_end) overflow("stack");
  if (stack_ptr>stack) { /* save current state */
    stack_ptr->end_field=cur_end;
    stack_ptr->tok_field=cur_tok;
    stack_ptr->mode_field=cur_mode;
  }
  stack_ptr++;
  if (stack_ptr>max_stack_ptr) max_stack_ptr=stack_ptr;
  cur_tok=*p; cur_end=*(p+1);
}@ Conversely, the |pop_level| routine restores the conditions that were in force when the current level was begun. This subroutine will never be called when |stack_ptr==1|.

@c
void
pop_level()
{
  cur_end=(--stack_ptr)->end_field;
  cur_tok=stack_ptr->tok_field; cur_mode=stack_ptr->mode_field;
}@ The |get_output| function returns the next byte of output that is not a reference to a token list. It returns the values |identifier| or |res_word| or |section_code| if the next token is to be an identifier (typeset in italics), a reserved word (typeset in boldface), or a section name (typeset by a complex routine that might generate additional levels of output). In these cases |cur_name| points to the identifier or section name in question.

@<Global variables@>=
name_pointer cur_name;

@ @d res_word 0201 /* returned by |get_output| for reserved words */
@d section_code 0200 /* returned by |get_output| for section names */

@c
eight_bits
get_output() /* returns the next token of output */
{
  sixteen_bits a; /* current item read from |tok_mem| */
  restart: while (cur_tok==cur_end) pop_level();
  a=*(cur_tok++);
  if (a>=0400) {
    cur_name=a % id_flag + name_dir;
    switch (a / id_flag) {
      case 2: return(res_word); /* |a==res_flag+cur_name| */
      case 3: return(section_code); /* |a==section_flag+cur_name| */
      case 4: push_level(a % id_flag + tok_start); goto restart;
        /* |a==tok_flag+cur_name| */
      case 5: push_level(a % id_flag + tok_start); cur_mode=inner; goto restart;
        /* |a==inner_tok_flag+cur_name| */
      default: return(identifier); /* |a==id_flag+cur_name| */
    }
  }
  return(a);
}@ The real work associated with token output is done by |make_output|. This procedure appends an |end_translation| token to the current token list, and then it repeatedly calls |get_output| and feeds characters to the output buffer until reaching the |end_translation| sentinel. It is possible for |make_output| to be called recursively, since a section name may include embedded \CEE/ text; however, the depth of recursion never exceeds one level, since section names cannot be inside of section names.  A procedure called |output_C| does the scanning, translation, and output of \CEE/ text within `\pb' brackets, and this procedure uses |make_output| to output the current token list. Thus, the recursive call of |make_output| actually occurs when |make_output| calls |output_C| while outputting the name of a section. @^recursion@>

@c
void
output_C() /* outputs the current token list */
{
  token_pointer save_tok_ptr;
  text_pointer save_text_ptr;
  sixteen_bits save_next_control; /* values to be restored */
  text_pointer p; /* translation of the \CEE/ text */
  save_tok_ptr=tok_ptr; save_text_ptr=text_ptr;
  save_next_control=next_control; next_control=ignore; p=C_translate();
  app(inner_tok_flag+(int)(p-tok_start));
  if (make_pb) {
    out_str("\\PB{"); make_output(); out('}');
@.\\PB@>
  }@+else make_output(); /* output the list */
  if (text_ptr>max_text_ptr) max_text_ptr=text_ptr;
  if (tok_ptr>max_tok_ptr) max_tok_ptr=tok_ptr;
  text_ptr=save_text_ptr; tok_ptr=save_tok_ptr; /* forget the tokens */
  next_control=save_next_control; /* restore |next_control| to original state */
}@ Here is \.{CWEAVE}'s major output handler.

@<Predeclaration of procedures@>=
void make_output();

@ @c
void
make_output() /* outputs the equivalents of tokens */
{
  eight_bits a, /* current output byte */
  b; /* next output byte */
  int c; /* count of |indent| and |outdent| tokens */
  char scratch[longest_name]; /* scratch area for section names */
  char *k, *k_limit; /* indices into |scratch| */
  char *j; /* index into |buffer| */
  char *p; /* index into |byte_mem| */
  char delim; /* first and last character of string being copied */
  char *save_loc, *save_limit; /* |loc| and |limit| to be restored */
  name_pointer cur_section_name; /* name of section being output */
  boolean save_mode; /* value of |cur_mode| before a sequence of breaks */
  app(end_translation); /* append a sentinel */
  freeze_text; push_level(text_ptr-1);
  while (1) {
    a=get_output();
    reswitch: switch(a) {
      case end_translation: return;
      case identifier: case res_word: @<Output an identifier@>; break;
      case section_code: @<Output a section name@>; break;
      case math_rel: out_str("\\MRL{"@q}@>);
@.\\MRL@>
      case noop: case inserted: break;
      case cancel: case big_cancel: c=0; b=a;
        while (1) {
          a=get_output();
          if (a==inserted) continue;
          if ((a<indent && !(b==big_cancel&&a==' ')) || a>big_force) break;
          if (a==indent) c++; else if (a==outdent) c--;
          else if (a==opt) a=get_output();
        }
        @<Output saved |indent| or |outdent| tokens@>;
        goto reswitch;
      case indent: case outdent: case opt: case backup: case break_space:
      case force: case big_force: case preproc_line:
	  	@<Output a control,look ahead in case of line breaks, possibly |goto reswitch|@>; break;
      case quoted_char: out(*(cur_tok++));
      case qualifier: break;
      default: out(a); /* otherwise |a| is an ordinary character */
    }
  }
}
@ @<Output saved...@>=
  for (;c>0;c--) out_str("\\1");
@.\\1@>
  for (;c<0;c++) out_str("\\2");
@.\\2@>
@ The current mode does not affect the behavior of \.{CWEAVE}'s output routine except when we are outputting control tokens.

@<Output a control...@>=
if (a<break_space || a==preproc_line) {
  if (cur_mode==outer) {
    out('\\'); out(a-cancel+'0');
@.\\1@>
@.\\2@>
@.\\3@>
@.\\4@>
@.\\8@>
    if (a==opt) {
      b=get_output(); /* |opt| is followed by a digit */
      if (b!='0' || force_lines==0) out(b)@;
      else out_str("{-1}"); /* |force_lines| encourages more \.{@@\v} breaks */
    }
  } else if (a==opt) b=get_output(); /* ignore digit following |opt| */
  }
else @<Look ahead for strongest line break, |goto reswitch|@>
@ If several of the tokens |break_space|, |force|, |big_force| occur in a row, possibly mixed with blank spaces (which are ignored), the largest one is used. A line break also occurs in the output file, except at the very end of the translation. The very first line break is suppressed (i.e., a line break that follows `\.{\\Y\\B}').

@<Look ahead for strongest line break, |goto reswitch|@>= {
  b=a; save_mode=cur_mode; c=0;
  while (1) {
    a=get_output();
    if (a==inserted) continue;
    if (a==cancel || a==big_cancel) {
      @<Output saved |indent| or |outdent| tokens@>;
      goto reswitch; /* |cancel| overrides everything */
    }
    if ((a!=' ' && a<indent) || a==backup || a>big_force) {
      if (save_mode==outer) {
        if (out_ptr>out_buf+3 && strncmp(out_ptr-3,"\\Y\\B",4)==0)
          goto reswitch;
        @<Output saved |indent| or |outdent| tokens@>;
        out('\\'); out(b-cancel+'0');
@.\\5@>
@.\\6@>
@.\\7@>
        if (a!=end_translation) finish_line();
      }
      else if (a!=end_translation && cur_mode==inner) out(' ');
      goto reswitch;
    }
    if (a==indent) c++;
    else if (a==outdent) c--;
    else if (a==opt) a=get_output();
    else if (a>b) b=a; /* if |a==' '| we have |a<b| */
  }
}
@ An identifier of length one does not have to be enclosed in braces, and it looks slightly better if set in a math-italic font instead of a (slightly narrower) text-italic font. Thus we output `\.{\\\v}\.{a}' but `\.{\\\\\{aa\}}'.

@<Output an identifier@>=
out('\\');
if (a==identifier) {
  if (cur_name->ilk==custom && !doing_format) {
 custom_out:
    for (p=cur_name->byte_start;p<(cur_name+1)->byte_start;p++)
      out(*p=='_'? 'x': *p=='$'? 'X': *p);
    break;
  } else if (is_tiny(cur_name)) out('|')@;
@.\\|@>
  else { delim='.';
    for (p=cur_name->byte_start;p<(cur_name+1)->byte_start;p++)
      if (xislower(*p)) { /* not entirely uppercase */
         delim='\\'; break;
      }
  out(delim);
  }
@.\\\\@>
@.\\.@>
}@+else if (cur_name->ilk==alfop) {
  out('X');
  goto custom_out;
}@+else out('&'); /* |a==res_word| */
@.\\\&@>
if (is_tiny(cur_name)) {
  if (isxalpha((cur_name->byte_start)[0]))
    out('\\');
  out((cur_name->byte_start)[0]);
}
else out_name(cur_name,1);
@ The remaining part of |make_output| is somewhat more complicated. When we output a section name, we may need to enter the parsing and translation routines, since the name may contain \CEE/ code embedded in \pb\ constructions. This \CEE/ code is placed at the end of the active input buffer and the translation process uses the end of the active |tok_mem| area.

@<Output a section name@>= {
  out_str("\\X");
@.\\X@>
  cur_xref=(xref_pointer)cur_name->xref;
  if (cur_xref->num==file_flag) {an_output=1; cur_xref=cur_xref->xlink;}
  else an_output=0;
  if (cur_xref->num>=def_flag) {
    out_section(cur_xref->num-def_flag);
    if (phase==3) {
      cur_xref=cur_xref->xlink;
      while (cur_xref->num>=def_flag) {
        out_str(", ");
        out_section(cur_xref->num-def_flag);
      cur_xref=cur_xref->xlink;
      }
    }
  }
  else out('0'); /* output the section number, or zero if it was undefined */
  out(':');
  if (an_output) out_str("\\.{"@q}@>);
@.\\.@>
  @<Output the text of the section name@>;
  if (an_output) out_str(@q{@>" }");
  out_str("\\X");
}
@ @<Output the text...@>=
sprint_section_name(scratch,cur_name);
k=scratch;
k_limit=scratch+strlen(scratch);
cur_section_name=cur_name;
while (k<k_limit) {
  b=*(k++);
  if (b=='@@') @<Skip next character, give error if not `\.{@@}'@>;
  if (an_output)
    switch (b) {
 case  ' ':case '\\':case '#':case '%':case '$':case '^':
 case '{': case '}': case '~': case '&': case '_':
    out('\\'); /* falls through */
@.\\\ @>
@.\\\\@>
@.\\\#@>
@.\\\%@>
@.\\\$@>
@.\\\^@>
@.\\\{@>@q}@>
@q{@>@.\\\}@>
@.\\\~@>
@.\\\&@>
@.\\\_@>
 default: out(b);
    }
  else if (b!='|') out(b)
  else {
    @<Copy the \CEE/ text into the |buffer| array@>;
    save_loc=loc; save_limit=limit; loc=limit+2; limit=j+1;
    *limit='|'; output_C();
    loc=save_loc; limit=save_limit;
  }
}
@ @<Skip next char...@>=
if (*k++!='@@') {
  printf("\n! Illegal control code in section name: <");
@.Illegal control code...@>
  print_section_name(cur_section_name); printf("> "); mark_error;
}
@ The \CEE/ text enclosed in \pb\ should not contain `\.{\v}' characters, except within strings. We put a `\.{\v}' at the front of the buffer, so that an error message that displays the whole buffer will look a little bit sensible. The variable |delim| is zero outside of strings, otherwise it equals the delimiter that began the string being copied.

@<Copy the \CEE/ text into the |buffer| array@>=
j=limit+1; *j='|'; delim=0;
while (1) {
  if (k>=k_limit) {
    printf("\n! C text in section name didn't end: <");
@.C text...didn't end@>
    print_section_name(cur_section_name); printf("> "); mark_error; break;
  }
  b=*(k++);
  if (b=='@@' || (b=='\\' && delim!=0))
     @<Copy a quoted character into the buffer@>
  else {
    if (b=='\'' || b=='"')
      if (delim==0) delim=b;
      else if (delim==b) delim=0;
    if (b!='|' || delim!=0) {
      if (j>buffer+long_buf_size-3) overflow("buffer");
      *(++j)=b;
    }
    else break;
  }
}
@ @<Copy a quoted char...@>= {
  if (j>buffer+long_buf_size-4) overflow("buffer");
  *(++j)=b; *(++j)=*(k++);
}
@** Phase two processing. We have assembled enough pieces of the puzzle in order to be ready to specify the processing in \.{CWEAVE}'s main pass over the source file. Phase two is analogous to phase one, except that more work is involved because we must actually output the \TEX/ material instead of merely looking at the \.{CWEB} specifications.
@<Predeclaration of procedures@>=
void phase_two();

@ @c
void
phase_two() {
reset_input(); if (show_progress) printf("\nWriting the output file...");
@.Writing the output file...@>
section_count=0; format_visible=1; copy_limbo();
finish_line(); flush_buffer(out_buf,0,0); /* insert a blank line, it looks nice */
while (!input_has_ended) @<Translate the current section@>;
}
@ The output file will contain the control sequence \.{\\Y} between non-null sections of a section, e.g., between the \TEX/ and definition parts if both are nonempty. This puts a little white space between the parts when they are printed. However, we don't want \.{\\Y} to occur between two definitions within a single section. The variables |out_line| or |out_ptr| will change if a section is non-null, so the following macros `|save_position|' and `|emit_space_if_needed|' are able to handle the situation:

@d save_position save_line=out_line; save_place=out_ptr
@d emit_space_if_needed if (save_line!=out_line || save_place!=out_ptr)
  out_str("\\Y");
  space_checked=1
@.\\Y@>

@<Global variables@>=
int save_line; /* former value of |out_line| */
char *save_place; /* former value of |out_ptr| */
int sec_depth; /* the integer, if any, following \.{@@*} */
boolean space_checked; /* have we done |emit_space_if_needed|? */
boolean format_visible; /* should the next format declaration be output? */
boolean doing_format=0; /* are we outputting a format declaration? */
boolean group_found=0; /* has a starred section occurred? */

@ @<Translate the current section@>= {
  section_count++;
  @<Output the code for the beginning of a new section@>;
  save_position;
  @<Translate the \TEX/ part of the current section@>;
  @<Translate the definition part of the current section@>;
  @<Translate the \CEE/ part of the current section@>;
  @<Show cross-references to this section@>;
  @<Output the code for the end of a section@>;
}
@ Sections beginning with the \.{CWEB} control sequence `\.{@@\ }' start in the output with the \TEX/ control sequence `\.{\\M}', followed by the section number. Similarly, `\.{@

@*}' sections lead to the control sequence `\.{\\N}'. In this case there's an additional parameter, representing one plus the specified depth, immediately after the \.{\\N}. If the section has changed, we put \.{\\*} just after the section number.

@<Output the code for the beginning of a new section@>=
if (*(loc-1)!='*') out_str("\\M");
@.\\M@>
else {
  while (*loc == ' ') loc++;
  if (*loc=='*') { /* ``top'' level */
    sec_depth = -1;
    loc++;
  }
  else {
    for (sec_depth=0; xisdigit(*loc);loc++)
      sec_depth = sec_depth*10 + (*loc) -'0';
  }
  while (*loc == ' ') loc++; /* remove spaces before group title */
  group_found=1;
  out_str("\\N");
@.\\N@>
  {@+ char s[32];@+sprintf(s,"{%d}",sec_depth+1);@+out_str(s);@+}
  if (show_progress)
  printf("*%d",section_count); update_terminal; /* print a progress report */
}
out_str("{");out_section(section_count); out_str("}");
@ In the \TEX/ part of a section, we simply copy the source text, except that index entries are not copied and \CEE/ text within \pb\ is translated.

@<Translate the \TEX/ part of the current section@>= do {
  next_control=copy_TeX();
  switch (next_control) {
    case '|': init_stack; output_C(); break;
    case '@@': out('@@'); break;
    case TeX_string: case noop:
    case xref_roman: case xref_wildcard: case xref_typewriter:
    case section_name: loc-=2; next_control=get_next(); /* skip to \.{@@>} */
      if (next_control==TeX_string)
        err_print("! TeX string should be in C text only"); break;
@.TeX string should be...@>
    case thin_space: case math_break: case ord:
    case line_break: case big_line_break: case no_line_break: case join:
    case pseudo_semi: case macro_arg_open: case macro_arg_close:
    case output_defs_code:
        err_print("! You can't do that in TeX text"); break;
@.You can't do that...@>
  }
} while (next_control<format_code);
@ When we get to the following code we have |next_control>=format_code|, and the token memory is in its initial empty state.

@<Translate the definition part of the current section@>=
space_checked=0;
while (next_control<=definition) { /* |format_code| or |definition| */
  init_stack;
  if (next_control==definition) @<Start a macro definition@>@;
  else @<Start a format definition@>;
  outer_parse(); finish_C(format_visible); format_visible=1;
  doing_format=0;
}
@ Keeping in line with the conventions of the \CEE/ preprocessor (and otherwise contrary to the rules of \.{CWEB}) we distinguish here between the case that `\.(' immediately follows an identifier and the case that the two are separated by a space.  In the latter case, and if the identifier is not followed by `\.(' at all, the replacement text starts immediately after the identifier.  In the former case, it starts after we scan the matching `\.)'.

@<Start a macro definition@>= {
  if (save_line!=out_line || save_place!=out_ptr || space_checked) app(backup);
  if(!space_checked){emit_space_if_needed;save_position;}
  app_str("\\D"); /* this will produce `\&{define }' */
@.\\D@>
  if ((next_control=get_next())!=identifier)
    err_print("! Improper macro definition");
@.Improper macro definition@>
  else {
    app('$'); app_cur_id(0);
    if (*loc=='(')
  reswitch: switch (next_control=get_next()) {
      case '(': case ',': app(next_control); goto reswitch;
      case identifier: app_cur_id(0); goto reswitch;
      case ')': app(next_control); next_control=get_next(); break;
      default: err_print("! Improper macro definition"); break;
    }
    else next_control=get_next();
    app_str("$ "); app(break_space);
    app_scrap(dead,no_math); /* scrap won't take part in the parsing */
  }
}
@ @<Start a format...@>= {
  doing_format=1;
  if(*(loc-1)=='s' || *(loc-1)=='S') format_visible=0;
  if(!space_checked){emit_space_if_needed;save_position;}
  app_str("\\F"); /* this will produce `\&{format }' */
@.\\F@>
  next_control=get_next();
  if (next_control==identifier) {
    app(id_flag+(int)(id_lookup(id_first, id_loc,normal)-name_dir));
    app(' ');
    app(break_space); /* this is syntactically separate from what follows */
    next_control=get_next();
    if (next_control==identifier) {
      app(id_flag+(int)(id_lookup(id_first, id_loc,normal)-name_dir));
      app_scrap(exp,maybe_math); app_scrap(semi,maybe_math);
      next_control=get_next();
    }
  }
  if (scrap_ptr!=scrap_info+2) err_print("! Improper format definition");
@.Improper format definition@>
}
@ Finally, when the \TEX/ and definition parts have been treated, we have |next_control>=begin_C|. We will make the global variable |this_section| point to the current section name, if it has a name.

@<Global variables@>=
name_pointer this_section; /* the current section name, or zero */

@ @<Translate the \CEE/...@>=
this_section=name_dir;
if (next_control<=section_name) {
  emit_space_if_needed; init_stack;
  if (next_control==begin_C) next_control=get_next();
  else {
    this_section=cur_section;
    @<Check that '=' or '==' follows this section name, and emit the scraps to start the section definition@>;
  }
  while  (next_control<=section_name) {
    outer_parse();
    @<Emit the scrap for a section name if present@>;
  }
  finish_C(1);
}
@ The title of the section and an $\E$ or $\mathrel+\E$ are made into a scrap that should not take part in the parsing.

@<Check that '='...@>=
do next_control=get_next();
  while (next_control=='+'); /* allow optional `\.{+=}' */
if (next_control!='=' && next_control!=eq_eq)
  err_print("! You need an = sign after the section name");
@.You need an = sign...@>
  else next_control=get_next();
if (out_ptr>out_buf+1 && *out_ptr=='Y' && *(out_ptr-1)=='\\') app(backup);
    /* the section name will be flush left */
@.\\Y@>
app(section_flag+(int)(this_section-name_dir));
cur_xref=(xref_pointer)this_section->xref;
if(cur_xref->num==file_flag) cur_xref=cur_xref->xlink;
app_str("${}");
if (cur_xref->num!=section_count+def_flag) {
  app_str("\\mathrel+"); /*section name is multiply defined*/
  this_section=name_dir; /*so we won't give cross-reference info here*/
}
app_str("\\E"); /* output an equivalence sign */
@.\\E@>
app_str("{}$");
app(force); app_scrap(dead,no_math);
        /* this forces a line break unless `\.{@@+}' follows */
@ @<Emit the scrap...@>=
if (next_control<section_name) {
  err_print("! You can't do that in C text");
@.You can't do that...@>
  next_control=get_next();
}
else if (next_control==section_name) {
  app(section_flag+(int)(cur_section-name_dir));
  app_scrap(section_scrap,maybe_math);
  next_control=get_next();
}
@ Cross references relating to a named section are given after the section ends.

@<Show cross-references to this section@>=
if (this_section>name_dir) {
  cur_xref=(xref_pointer)this_section->xref;
  if (cur_xref->num==file_flag){an_output=1;cur_xref=cur_xref->xlink;}
  else an_output=0;
  if (cur_xref->num>def_flag)
    cur_xref=cur_xref->xlink; /* bypass current section number */
  footnote(def_flag); footnote(cite_flag); footnote(0);
}
@ @<Output the code for the end of a section@>=
out_str("\\fi"); finish_line();
@.\\fi@>
flush_buffer(out_buf,0,0); /* insert a blank line, it looks nice */
@ The |footnote| procedure gives cross-reference information about multiply defined section names (if the |flag| parameter is |def_flag|), or about references to a section name (if |flag==cite_flag|), or to its uses (if |flag==0|). It assumes that |cur_xref| points to the first cross-reference entry of interest, and it leaves |cur_xref| pointing to the first element not printed.  Typical outputs: `\.{\\A101.}'; `\.{\\Us 370\\ET1009.}'; `\.{\\As 8, 27\\*\\ETs64.}'.  Note that the output of \.{CWEAVE} is not English-specific; users may supply new definitions for the macros \.{\\A}, \.{\\As}, etc.

@<Predeclaration of procedures@>=
void footnote();

@ @c
void
footnote(flag) /* outputs section cross-references */
sixteen_bits flag;
{
  xref_pointer q; /* cross-reference pointer variable */
  if (cur_xref->num<=flag) return;
  finish_line(); out('\\');
@.\\A@>
@.\\Q@>
@.\\U@>
  out(flag==0? 'U': flag==cite_flag? 'Q': 'A');
  @<Output all the section numbers on the reference list |cur_xref|@>;
  out('.');
}
@ The following code distinguishes three cases, according as the number of cross-references is one, two, or more than two. Variable |q| points to the first cross-reference, and the last link is a zero.

@<Output all the section numbers on the reference list |cur_xref|@>=
q=cur_xref; if (q->xlink->num>flag) out('s'); /* plural */
while (1) {
  out_section(cur_xref->num-flag);
  cur_xref=cur_xref->xlink; /* point to the next cross-reference to output */
  if (cur_xref->num<=flag) break;
  if (cur_xref->xlink->num>flag) out_str(", "); /* not the last */
  else {out_str("\\ET"); /* the last */
@.\\ET@>
  if (cur_xref != q->xlink) out('s'); /* the last of more than two */
  }
}
@ The |finish_C| procedure outputs the translation of the current scraps, preceded by the control sequence `\.{\\B}' and followed by the control sequence `\.{\\par}'. It also restores the token and scrap memories to their initial empty state.  A |force| token is appended to the current scraps before translation takes place, so that the translation will normally end with \.{\\6} or \.{\\7} (the \TEX/ macros for |force| and |big_force|). This \.{\\6} or \.{\\7} is replaced by the concluding \.{\\par} or by \.{\\Y\\par}.

@<Predeclaration of procedures@>=
void finish_C();

@ @c
void
finish_C(visible) /* finishes a definition or a \CEE/ part */
  boolean visible; /* nonzero if we should produce \TEX/ output */
{
  text_pointer p; /* translation of the scraps */
  if (visible) {
    out_str("\\B"); app_tok(force); app_scrap(insert,no_math);
    p=translate();
@.\\B@>
    app(tok_flag+(int)(p-tok_start)); make_output(); /* output the list */
    if (out_ptr>out_buf+1)
      if (*(out_ptr-1)=='\\')
@.\\6@>
@.\\7@>
@.\\Y@>
        if (*out_ptr=='6') out_ptr-=2;
        else if (*out_ptr=='7') *out_ptr='Y';
    out_str("\\par"); finish_line();
  }
  if (text_ptr>max_text_ptr) max_text_ptr=text_ptr;
  if (tok_ptr>max_tok_ptr) max_tok_ptr=tok_ptr;
  if (scrap_ptr>max_scr_ptr) max_scr_ptr=scrap_ptr;
  tok_ptr=tok_mem+1; text_ptr=tok_start+1; scrap_ptr=scrap_info;
    /* forget the tokens and the scraps */
}
@** Phase three processing. We are nearly finished! \.{CWEAVE}'s only remaining task is to write out the index, after sorting the identifiers and index entries.  If the user has set the |no_xref| flag (the \.{-x} option on the command line), just finish off the page, omitting the index, section name list, and table of contents.

@<Predeclaration of procedures@>=
void phase_three();@ @c
void
phase_three() {
if (no_xref) {
  finish_line();
  out_str("\\end");
@.\\end@>
  finish_line();
}
else {
  phase=3; if (show_progress) printf("\nWriting the index...");
@.Writing the index...@>
  finish_line();
  if ((idx_file=fopen(idx_file_name,"w"))==NULL)
    fatal("! Cannot open index file ",idx_file_name);
@.Cannot open index file@>
  if (change_exists) {
    @<Tell about changed sections@>; finish_line(); finish_line();
  }
  out_str("\\inx"); finish_line();
@.\\inx@>
  active_file=idx_file; /* change active file to the index file */
  @<Do the first pass of sorting@>;
  @<Sort and output the index@>;
  finish_line(); fclose(active_file); /* finished with |idx_file| */
  active_file=tex_file; /* switch back to |tex_file| for a tic */
  out_str("\\fin"); finish_line();
@.\\fin@>
  if ((scn_file=fopen(scn_file_name,"w"))==NULL)
    fatal("! Cannot open section file ",scn_file_name);
@.Cannot open section file@>
  active_file=scn_file; /* change active file to section listing file */
  @<Output all the section names@>;
  finish_line(); fclose(active_file); /* finished with |scn_file| */
  active_file=tex_file;
  if (group_found) out_str("\\con");@+else out_str("\\end");
@.\\con@>
@.\\end@>
  finish_line();
  fclose(active_file);
}
if (show_happiness) printf("\nDone.");
check_complete(); /* was all of the change file used? */
}
@ Just before the index comes a list of all the changed sections, including the index section itself.

@<Global variables@>=
sixteen_bits k_section; /* runs through the sections */

@ @<Tell about changed sections@>= {
  /* remember that the index is already marked as changed */
  k_section=0;
  while (!changed_section[++k_section]);
  out_str("\\ch ");
@.\\ch@>
  out_section(k_section);
  while (k_section<section_count) {
    while (!changed_section[++k_section]);
    out_str(", "); out_section(k_section);
  }
  out('.');
}
@ A left-to-right radix sorting method is used, since this makes it easy to adjust the collating sequence and since the running time will be at worst proportional to the total length of all entries in the index. We put the identifiers into 102 different lists based on their first characters. (Uppercase letters are put into the same list as the corresponding lowercase letters, since we want to have `$t<\\{TeX}<\&{to}$'.) The list for character |c| begins at location |bucket[c]| and continues through the |blink| array.

@<Global variables@>=
name_pointer bucket[256];
name_pointer next_name; /* successor of |cur_name| when sorting */
name_pointer blink[max_names]; /* links in the buckets */

@ To begin the sorting, we go through all the hash lists and put each entry having a nonempty cross-reference list into the proper bucket.

@<Do the first pass of sorting@>= {
int c;
for (c=0; c<=255; c++) bucket[c]=NULL;
for (h=hash; h<=hash_end; h++) {
  next_name=*h;
  while (next_name) {
    cur_name=next_name; next_name=cur_name->link;
    if (cur_name->xref!=(char*)xmem) {
      c=(eight_bits)((cur_name->byte_start)[0]);
      if (xisupper(c)) c=tolower(c);
      blink[cur_name-name_dir]=bucket[c]; bucket[c]=cur_name;
    }
  }
}
}
@ During the sorting phase we shall use the |cat| and |trans| arrays from
\.{CWEAVE}'s parsing algorithm and rename them |depth| and |head|. They now
represent a stack of identifier lists for all the index entries that have
not yet been output. The variable |sort_ptr| tells how many such lists are
present; the lists are output in reverse order (first |sort_ptr|, then
|sort_ptr-1|, etc.). The |j|th list starts at |head[j]|, and if the first
|k| characters of all entries on this list are known to be equal we have
|depth[j]==k|.

@ @<Rest of |trans_plus| union@>=
name_pointer Head;

@ @d depth cat /* reclaims memory that is no longer needed for parsing */
@d head trans_plus.Head /* ditto */
@f sort_pointer int
@d sort_pointer scrap_pointer /* ditto */
@d sort_ptr scrap_ptr /* ditto */
@d max_sorts max_scraps /* ditto */

@<Global variables@>=
eight_bits cur_depth; /* depth of current buckets */
char *cur_byte; /* index into |byte_mem| */
sixteen_bits cur_val; /* current cross-reference number */
sort_pointer max_sort_ptr; /* largest value of |sort_ptr| */

@ @<Set init...@>=
max_sort_ptr=scrap_info;

@ The desired alphabetic order is specified by the |collate| array; namely, $|collate|[0]<|collate|[1]<\cdots<|collate|[100]$.

@<Global variables@>=
eight_bits collate[102+128]; /* collation order */
@^high-bit character handling@>

@ We use the order $\hbox{null}<\.\ <\hbox{other characters}<{}$\.\_${}< \.A=\.a<\cdots<\.Z=\.z<\.0<\cdots<\.9.$ Warning: The collation mapping needs to be changed if ASCII code is not being used. @^ASCII code dependencies@> @^high-bit character handling@>  We initialize |collate| by copying a few characters at a time, because some \CEE/ compilers choke on long strings.

@<Set initial values@>=
collate[0]=0;
strcpy(collate+1," \1\2\3\4\5\6\7\10\11\12\13\14\15\16\17");
/* 16 characters + 1 = 17 */
strcpy(collate+17,"\20\21\22\23\24\25\26\27\30\31\32\33\34\35\36\37");
/* 16 characters + 17 = 33 */
strcpy(collate+33,"!\42#$%&'()*+,-./:;<=>?@@[\\]^`{|}~_");
/* 32 characters + 33 = 65 */
strcpy(collate+65,"abcdefghijklmnopqrstuvwxyz0123456789");
/* (26 + 10) characters + 65 = 101 */
strcpy(collate+101,"\200\201\202\203\204\205\206\207\210\211\212\213\214\215\216\217");
/* 16 characters + 101 = 117 */
strcpy(collate+117,"\220\221\222\223\224\225\226\227\230\231\232\233\234\235\236\237");
/* 16 characters + 117 = 133 */
strcpy(collate+133,"\240\241\242\243\244\245\246\247\250\251\252\253\254\255\256\257");
/* 16 characters + 133 = 149 */
strcpy(collate+149,"\260\261\262\263\264\265\266\267\270\271\272\273\274\275\276\277");
/* 16 characters + 149 = 165 */
strcpy(collate+165,"\300\301\302\303\304\305\306\307\310\311\312\313\314\315\316\317");
/* 16 characters + 165 = 181 */
strcpy(collate+181,"\320\321\322\323\324\325\326\327\330\331\332\333\334\335\336\337");
/* 16 characters + 181 = 197 */
strcpy(collate+197,"\340\341\342\343\344\345\346\347\350\351\352\353\354\355\356\357");
/* 16 characters + 197 = 213 */
strcpy(collate+213,"\360\361\362\363\364\365\366\367\370\371\372\373\374\375\376\377");
/* 16 characters + 213 = 229 */

@ @<Sort and output...@>=
sort_ptr=scrap_info; unbucket(1);
while (sort_ptr>scrap_info) {
  cur_depth=sort_ptr->depth;
  if (blink[sort_ptr->head-name_dir]==0 || cur_depth==infinity)
    @<Output index entries for the list at |sort_ptr|@>@;
  else @<Split the list at |sort_ptr| into further lists@>;
}
@ @<Split the list...@>= {
  eight_bits c;
  next_name=sort_ptr->head;
  do {
    cur_name=next_name; next_name=blink[cur_name-name_dir];
    cur_byte=cur_name->byte_start+cur_depth;
    if (cur_byte==(cur_name+1)->byte_start) c=0; /* hit end of the name */
    else {
      c=(eight_bits) *cur_byte;
      if (xisupper(c)) c=tolower(c);
    }
  blink[cur_name-name_dir]=bucket[c]; bucket[c]=cur_name;
  } while (next_name);
  --sort_ptr; unbucket(cur_depth+1);
}
@ @<Output index...@>= {
  cur_name=sort_ptr->head;
  do {
    out_str("\\I");
@.\\I@>
    @<Output the name at |cur_name|@>;
    @<Output the cross-references at |cur_name|@>;
    cur_name=blink[cur_name-name_dir];
  } while (cur_name);
  --sort_ptr;
}
@ @<Output the name...@>=
switch (cur_name->ilk) {
  case normal: case func_template: if (is_tiny(cur_name)) out_str("\\|");
    else {char *j;
      for (j=cur_name->byte_start;j<(cur_name+1)->byte_start;j++)
        if (xislower(*j)) goto lowcase;
      out_str("\\."); break;
lowcase: out_str("\\\\");
    }
  break;
@.\\|@>
@.\\.@>
@.\\\\@>
  case wildcard: out_str("\\9");@+ goto not_an_identifier;
@.\\9@>
  case typewriter: out_str("\\.");
@.\\.@>
  case roman: not_an_identifier: out_name(cur_name,0); goto name_done;
  case custom: {char *j; out_str("$\\");
    for (j=cur_name->byte_start;j<(cur_name+1)->byte_start;j++)
      out(*j=='_'? 'x': *j=='$'? 'X': *j);
    out('$');
    goto name_done;
    }
  default: out_str("\\&");
@.\\\&@>
}
out_name(cur_name,1);
name_done:@;
@ Section numbers that are to be underlined are enclosed in `\.{\\[}$\,\ldots\,$\.]'.

@<Output the cross-references at |cur_name|@>=
@<Invert the cross-reference list at |cur_name|, making |cur_xref| the head@>;
do {
  out_str(", "); cur_val=cur_xref->num;
  if (cur_val<def_flag) out_section(cur_val);
  else {out_str("\\["); out_section(cur_val-def_flag); out(']');}
@.\\[@>
  cur_xref=cur_xref->xlink;
} while (cur_xref!=xmem);
out('.'); finish_line();
@ List inversion is best thought of as popping elements off one stack and pushing them onto another. In this case |cur_xref| will be the head of the stack that we push things onto.

@<Global variables@>=
xref_pointer next_xref, this_xref;
  /* pointer variables for rearranging a list */

@ @<Invert the cross-reference list at |cur_name|, making |cur_xref| the head@>=
this_xref=(xref_pointer)cur_name->xref; cur_xref=xmem;
do {
  next_xref=this_xref->xlink; this_xref->xlink=cur_xref;
  cur_xref=this_xref; this_xref=next_xref;
} while (this_xref!=xmem);
@ @<Output all the section names@>=section_print(root)
@ Procedure |unbucket| goes through the buckets and adds nonempty lists to the stack, using the collating sequence specified in the |collate| array. The parameter to |unbucket| tells the current depth in the buckets. Any two sequences that agree in their first 255 character positions are regarded as identical.

@d infinity 255 /* $\infty$ (approximately) */

@<Predeclaration of procedures@>=
void  unbucket();

@ @c
void
unbucket(d) /* empties buckets having depth |d| */
eight_bits d;
{
  int c;  /* index into |bucket|; cannot be a simple |char| because of sign
    comparison below*/
  for (c=100+128; c>= 0; c--) if (bucket[collate[c]]) {
@^high-bit character handling@>
    if (sort_ptr>=scrap_info_end) overflow("sorting");
    sort_ptr++;
    if (sort_ptr>max_sort_ptr) max_sort_ptr=sort_ptr;
    if (c==0) sort_ptr->depth=infinity;
    else sort_ptr->depth=d;
    sort_ptr->head=bucket[collate[c]]; bucket[collate[c]]=NULL;
  }
}
@ The following recursive procedure walks through the tree of section names and prints them. @^recursion@>

@<Predeclaration of procedures@>=
void section_print();

@ @c
void
section_print(p) /* print all section names in subtree |p| */
name_pointer p;
{
  if (p) {
    section_print(p->llink); out_str("\\I");
@.\\I@>
    tok_ptr=tok_mem+1; text_ptr=tok_start+1; scrap_ptr=scrap_info; init_stack;
    app(p-name_dir+section_flag); make_output();
    footnote(cite_flag);
    footnote(0); /* |cur_xref| was set by |make_output| */
    finish_line();@/
    section_print(p->rlink);
  }
}
@ Because on some systems the difference between two pointers is a |long| rather than an |int|, we use \.{\%ld} to print these quantities.

@c
void
print_stats() {
  printf("\nMemory usage statistics:\n");
@.Memory usage statistics:@>
  printf("%ld names (out of %ld)\n",
            (long)(name_ptr-name_dir),(long)max_names);
  printf("%ld cross-references (out of %ld)\n",
            (long)(xref_ptr-xmem),(long)max_refs);
  printf("%ld bytes (out of %ld)\n",
            (long)(byte_ptr-byte_mem),(long)max_bytes);
  printf("Parsing:\n");
  printf("%ld scraps (out of %ld)\n",
            (long)(max_scr_ptr-scrap_info),(long)max_scraps);
  printf("%ld texts (out of %ld)\n",
            (long)(max_text_ptr-tok_start),(long)max_texts);
  printf("%ld tokens (out of %ld)\n",
            (long)(max_tok_ptr-tok_mem),(long)max_toks);
  printf("%ld levels (out of %ld)\n",
            (long)(max_stack_ptr-stack),(long)stack_size);
  printf("Sorting:\n");
  printf("%ld levels (out of %ld)\n",
            (long)(max_sort_ptr-scrap_info),(long)max_scraps);
}@** Index.
If you have read and understood the code for Phase III above, you know what
is in this index and how it got here. All sections in which an identifier is
used are listed with that identifier, except that reserved words are
indexed only when they appear in format definitions, and the appearances
of identifiers in section names are not indexed. Underlined entries
correspond to where the identifier was declared. Error messages, control
sequences put into the output, and a few
other things like ``recursion'' are indexed here too.
@q@@-leo@>
