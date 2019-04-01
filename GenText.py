# GenText module
#
# GenHelp superclass
# GenLatex  generate Latex format help
# GenHTML  generate HTML format help
#
# they provide numerous methods for formatting the text:
#
# g.transform(s, **args):
# g.emphFunction(s):
# g.emphVar(s):
#
# g.startModule(funcname, text, tag=None, titlebar=False, ismethod=False):
#      displays first line of file |FILE short description
# g.endModule():
#
# g.heading(text):
#      displays headings, as from lines ending with ::
#
# g.endMethod():
#
# g.startTable():
# g.addTable(col1, col2):
# g.endTable():
#
# g.startCode():
# g.addCode(text):
# g.endCode():
#
# g.startList():
# g.addList(text):
# g.endList():
#
# g.startPara():
# g.paragraph(text, **args):
# g.endPara():
#
# g.startAlso():
# g.addAlso(text):
# g.endAlso():
#

from functools import partial
import re
import os
from datetime import date
import sys
import parse

# debug options
debug_gen = True
debug_format = True



def addspace(s):
    return s.replace(',', ', ')


def trace(func):
    fname = func.func_name

    def echo_func(*args, **kwargs):
        if debug_gen:
            print "---------->", fname, args[1:], kwargs
        return func(*args, **kwargs)
    return echo_func


def changecaps(s):
    if s.isupper():
        return s.lower()
    else:
        return


def split_first_word(s):
    k = s.find(' ')
    if k < 0:
        return s
    else:
        return (changecaps(s[:k]), s[k:].lstrip(' '))




# =============================================================================
# GenHelp superclass
# =============================================================================

class GenHelp(object):
    def __init__(self, filepath=None):
        if filepath:
            self.filepath = filepath
        else:
            self.filepath = '.'
        self.filelist = []

        # empty the buffer
        self.out = ''

        # set of extracted variables is empty
        self.vars = set()
        self.funcname = None

        # create compiled re's for later
        self.re_word = re.compile(r'''(?<![\\{A-Za-z])[a-zA-Z][a-zA-Z0-9_']*\b''')
        self.re_signature = re.compile(r"""
            \s*   # initial blank space
            (   # LHS
                (
                    (?P<lhs1>[a-zA-Z][a-zA-Z0-9]*)      # single output var
                    |
                    (
                        \[                              # list of output vars
                            (?P<lhs2>
                                ([a-zA-Z][a-zA-Z0-9]*)
                                (
                                    \s*,\s*
                                    ([a-zA-Z][a-zA-Z0-9]*)
                                )*
                            )
                        \]
                    )
                )
                \s*=\s*
            )?
            \s* # RHS
            (
                (
                    (?P<subject>[a-zA-Z][a-zA-Z0-9]*\.)?    # leading object and dot
                    (?P<method>[a-zA-Z][a-zA-Z0-9\._]*)     # method or function name
                        \(                                  # parameter list
                            (
                                (?P<rhs>                      # argument list
                                        ([a-zA-Z'][a-zA-Z0-9']*)      # first var
                                        (                             # remainder of var list
                                            (\s*,\s*)
                                            ([a-zA-Z'][a-zA-Z0-9']*)
                                        )*
                                )
                                |(\.\.\.)                      # ellipsis
                                |(\s*\[[^]]+\])
                            )?    # can be empty parenthesis
                        \)
                )
                |(?P<rhs1>[A-Za-z][A-Za-z0-9]*)\.(?P<rhs2>[A-Za-z][A-Za-z0-9]*)   # A.B
                |(?P<rhs3>[A-Za-z][A-Za-z0-9]*)\s*[.]?[+*/|^-]\s*(?P<rhs4>[A-Za-z][A-Za-z0-9]*)   # A*B
            )
            """, re.X)

        self.re_filename = re.compile(r'([a-zA-Z][a-zA-Z0-9_/]+\.(mlx|m))')


    def write(self, outfile, display=False):
        self.done()
        # dump it to a file
        out = open(outfile, 'w')
        out.write(self.out)
        out.close()

        # optionally open it for perusal
        if display:
            os.system('open %s' % outfile)

    def done(self):
        pass


    def findvars(self, s, classname=None):
        '''For a line of text look for a MATLAB code signature at the start of the line
        and split it out from the rest of the text.  All variables in that signature are
        added to the function's symbol table.
        '''
        m = self.re_signature.match(s)
        if m:
            e = m.end(0)
            signature = s[:e]
            para = s[e:]

            l = [];
            if m.group('lhs1'):
                l.append(m.group('lhs1'))
            if m.group('subject'):
                l.append(m.group('subject'))
            if m.group('lhs2'):
                l.extend([x.strip() for x in m.group('lhs2').split(',')])
            if m.group('rhs'):
                l.extend([x.strip() for x in m.group('rhs').split(',')])
            if m.group('rhs1'):
                l.append(m.group('rhs1'))
            if m.group('rhs2'):
                l.append(m.group('rhs2'))
            if m.group('rhs3'):
                l.append(m.group('rhs3'))
            if m.group('rhs4'):
                l.append(m.group('rhs4'))
            self.vars.update(l)
            #print '  findvars: set=', self.vars, ' definition:', signature
        else:
            para = s
            signature = ''
            #print '   findvars: NOTHING'
        return (signature, para)

    def subsvars(self, s, classname=None):
        '''For a line of text replace all instances of variables in the symbol table
        with emphasised text.
        '''
        def subfunc(m, funcname, sublist, classname):
            s = m.group(0)

            if classname:
                if s == funcname:
                    return self.emphFunction(s)
                if s == classname:
                    return self.emphFunction(s)
            else:
                if s.lower() == funcname:
                    return self.emphFunction(s.lower())

            if s in sublist:
                return self.emphVar(s)
            else:
                # no change
                return s

        # substitute any keywords
        s = self.re_word.sub(partial(subfunc,  funcname=self.funcname, sublist=self.vars, classname=classname), s)
        return s

    # Generate a help document for a structured comment block
    #
    #   gen is the doco generator object
    #   doc is the string
    #   funcname
    #
    # Repeatedly calls getchunk() to get the next logical chunk of text.
    def format(self, doc, funcname, titlebar=True, tag=None, classname=None):

        #print 'createDoco', funcname, titlebar, tag, classname
        if not doc:
            return

        parser = parse.Parser(doc)

        curLine = parser.nextLine()

        liststack = []

        while True:
            # ============================== LINE
            if curLine.type == parse.TEXT:
                if curLine.indent < 8:
                    # regular paragraph
                    self.startPara()

                    # parse out any code definition at start of paragraph
                    #para = curLine.text
                    #definition = ''
                    (definition, para) = self.findvars(curLine.text())

                    self.addPara(para,
                                 definition,
                                 classname=classname
                                 )

                    while True:
                        nextLine = parser.nextLine()
                        if nextLine.same(curLine):
                            self.addPara(nextLine.text(), '')
                        else:
                            break
                    self.endPara()
                else:
                    # literal code lines
                    self.startCode()
                    self.addCode(curLine.text(True))
                    while True:
                        nextLine = parser.nextLine()
                        if nextLine.same(curLine):
                            self.addCode(nextLine.text(True))
                        else:
                            # not a similar code line
                            if nextLine.type == parse.BLANKLINE:
                                self.addCode('')   # emit blank line
                                nextLine = parser.nextLine()
                                if nextLine.same(curLine):
                                    self.addCode(nextLine.text(True))
                                    continue
                            elif nextLine.type == parse.TABLE and nextLine.indent[0] == curLine.indent:
                                self.addCode(nextLine.text())
                            break

                    self.endCode()
                curLine = nextLine
                continue

            # ============================== TABLE
            elif curLine.type == parse.TABLE:
                self.startTable()
                self.addTable(curLine.col1(), curLine.col2())
                while True:
                    nextLine = parser.nextLine()
                    if nextLine.same(curLine):
                        print "SAME"
                        self.addTable(nextLine.col1(), nextLine.col2())
                    else:
                        print "NOT SAME"
                        # not a similar table line
                        if nextLine.type in (parse.TABLESEP, parse.BLANKLINE):
                            # blank line is a blank row in table
                            nextLine = parser.nextLine()
                            if nextLine.same(curLine):
                                self.addTable('', '')
                                self.addTable(nextLine.col1(), nextLine.col2())
                                continue
                        elif nextLine.type == parse.TEXT and nextLine.indent == curLine.indent[1]:
                            self.addTable('', nextLine.text())
                            continue
                        break
                self.endTable()
                curLine = nextLine
                continue

            # ============================== LIST
            elif curLine.type == parse.LIST:
                self.startList()
                self.addList(curLine.text())
                liststack = [];
                while True:
                    nextLine = parser.nextLine()
                    if nextLine.same(curLine):
                        self.addList(nextLine.text())
                    elif nextLine.type == parse.LIST:
                        # not a similar list line
                        if nextLine.indent > curLine.indent:
                            # nesting, start a new list
                            liststack.append(curLine)   # push the nesting
                            self.startList()
                            self.addList(nextLine.text())
                            curLine = nextLine
                        else:
                            # unnesting, return to a previous list
                            if nextLine.indent == liststack[-1].indent:
                                # matches previous list
                                self.endList()
                                curLine = liststack.pop()
                                self.addList(nextLine.text())
                            else:
                                print 'ERROR: lists not properly nested'
                    elif nextLine.type == parse.TEXT and nextLine.indent == curLine.indent:
                        self.addList(nextLine.text())
                    else:
                        break
                self.endList()
                for x in liststack:  # handle any nested loops that need ending
                    self.endList()
                curLine = nextLine
                continue

            # ============================== SEEALSO
            elif curLine.type == parse.SEEALSO:
                self.heading('See also')
                self.startAlso()
                out = ''
                for (i, func) in enumerate(curLine.text().split(',')):
                    func = func.strip()

                    # try to get the capitalization right
                    if '.' in func:
                        # if its CLASS.METHOD show as is
                        self.addAlso(func)
                    else:
                        func2 = self.findfile(func.strip())
                        if func2:
                            # if we find a matching file then use the
                            # capitalization of the file
                            self.addAlso(func2)
                        else:
                            # otherwise just make it lowercase
                            if not func.isupper() and not func.islower():
                                # the case is mixed, leave it that way
                                self.addAlso(func)
                            else:
                                self.addAlso(func.lower())
                self.endAlso()

            # ============================== HEADER
            elif curLine.type == parse.HEADER:
                self.heading(curLine.text())


            # ============================== SUMMARY
            elif curLine.type == parse.SUMMARY:
                if not classname:
                    ismethod = True
                elif classname == funcname:
                    ismethod = True
                else:
                    ismethod = False
                self.startModule(funcname, curLine.text(), tag=tag, titlebar=titlebar, ismethod=ismethod)


            # ============================== BLANKLINE
            elif curLine.type == parse.BLANKLINE:
                pass

            # ============================== END
            elif curLine.type == parse.END:
                break

            curLine = parser.nextLine()

    def findfile(self, filename):
        # lazy initialization of all .m file names
        if not self.filelist:
            for root, dirs, files in os.walk(self.filepath):
                for file in files:
                    #print filename, file
                    if os.path.splitext(file)[1] != '.m':
                        # skip non matlab files
                        continue
                    self.filelist.append(os.path.splitext(file)[0])

        # check if the named file exists, in either given case or
        # lower case.  Return the version that matches.
        if filename in self.filelist:
            return filename
        filename = filename.lower()
        if filename in self.filelist:
            return filename
        return None


    def transform(self, s, **args):

        s = self.substitutions(s)
        # substitute variables names
        if 'classname' in args:
            s = self.subsvars(s, classname=args['classname'])
        else:
            s = self.subsvars(s)

        # substitute filenames
        #  also substitutes inside of \url{...}
        #s = self.re_filename.sub(lambda m: self.emphPath(m.group(1)), s)

        return s

    # co-routine that returns the next logical chunk of the input string s
    #
    # yields with a tuple (text, indent, type) where type is one of:
    #
    #BLANKLINE
    # a blank line
    #
    #LIST
    # a chunk of text starting with a -
    #
    #TABLE
    # a line of text with two chunks, separated by at least 3 spaces
    #
    #HEADER
    # a documentation header line, ends with double colon
    #
    #SEEALSO
    # a line of text beginning with "See also"
    #
    #TEXT
    # a line of text 
    #
    #

    


# =============================================================================
# GenLatex subclass
# =============================================================================
class GenLatex(GenHelp):
    def __init__(self, include=True, **kwargs):
        super(GenLatex, self).__init__(**kwargs)

        self.re_squote = re.compile(r"(\A|\s)'(.*?)'(\Z|[^a-zA-Z])")
        self.re_dquote = re.compile(r'"(.*?)"')
        self.re_dims2 = re.compile(r'\b([0-9A-Z]+([+-][A-Z0-9]+)?)x([0-9A-Z]+([+-][A-Z0-9]+)?)\b')
        self.re_dims3 = re.compile(r'\b([0-9A-Z]+([+-][A-Z0-9]+)?)x([0-9A-Z]+([+-][A-Z0-9]+)?)x([0-9A-Z]+([+-][A-Z0-9]+)?)\b')
        self.re_exp0 = re.compile(r'([RP])\^([0-9a-zA-Z]+)')
        self.re_exp1 = re.compile(r'\^([0-9a-zA-Z]+)')
        self.re_exp2 = re.compile(r'[^{}]\^[^{}]')
        #self.re_exp2 = re.compile(r'[^}]?\^[^{}]')
        #self.re_exp = re.compile(r'([a-zA-Z]\w*)\^([0-9a-zA-Z]+)')
        #self.re_exp = re.compile(r'\b([a-zA-Z]\w*)\^([0-9]+)\b')
        self.re_pi = re.compile(r'(?<![A-Za-z\\])pi(?![A-Za-z])')
        self.include = include
        self.re_url = re.compile(r'(https?://[a-zA-Z0-9/._?=-]+)')
        self.re_firstcircumflex = re.compile(r'\A\s*\^')

        if not self.include:
            self.out += r'''\documentclass[a4paper]{article}
\setlength{\parindent}{0mm}
\usepackage{parskip}
\usepackage{color}
\usepackage{amsfonts}  % mathbb font
\usepackage{hyperref}
\usepackage{longtable}
\usepackage{sectsty}
\usepackage{textcomp}     % access \textquotesingle
\allsectionsfont{\sffamily}
\makeatletter
\renewcommand\section{%
\@startsection{section}{1}{\z@}%
  {-3.5ex \@plus -1ex \@minus -.2ex}%
  {2.3ex \@plus.2ex}%
  {\color{red}\sffamily\huge\bfseries}}
\makeatother

\usepackage{fancyvrb}
\fvset{formatcom=\color{blue},fontseries=c,fontfamily=courier,xleftmargin=4mm,commentchar=!}

\DefineVerbatimEnvironment{Code}{Verbatim}{formatcom=\color{blue},fontseries=c,fontfamily=courier,fontsize=\footnotesize,xleftmargin=4mm,commentchar=!}

\begin{document}
'''; 

    def done(self):
        if not self.include:
            self.out += '\\end{document}\n'


    def substitutions(self, s):
        # LaTeX specific fixups

        # braces
        s = s.replace('{', '$\\{$')
        s = s.replace('}', '$\\}$')

        # 'string' -> `string'
        #s = self.re_squote.sub(r"\1`\2'\3", s)
        #s = self.re_squote.sub(r"\1`\2'\3", s)
        s = s.replace("'", r'\textquotesingle ')

        # "string" -> ``string''
        s = self.re_dquote.sub(r"``\1''", s)

        # NxM -> $N \times M$
        s = self.re_dims2.sub(r'$\1 \\times \3$', s)
        # NxMxK -> $N \times M \times K$
        s = self.re_dims3.sub(r'$\1 \\times \3 \\times \5$', s)

        # circumflex
        s = s.replace('^^^^', r'\textasciicircum\textasciicircum\textasciicircum\textasciicircum ')
        s = s.replace('^^^', r'\textasciicircum\textasciicircum\textasciicircum ')
        s = s.replace('^^', r'\textasciicircum\textasciicircum ')
        s = self.re_firstcircumflex.sub(r'\\textasciicircum ', s)

        # A^2 -> $A^2$
        s = self.re_exp0.sub(r'$\mathbb{\1}^{\2}$', s)
        # A^2 -> $A^2$
        s = self.re_exp1.sub(r'${}^{\1}$', s)
        s = self.re_exp2.sub(r'\\textasciicircum ', s)

        # ^N -> \textasciicircum N
        s = self.re_exp2.sub(r'\\textasciicircum ', s)

        # group notation
        s = s.replace('SO(2)', r'$\mbox{SO}(2)$')
        s = s.replace('SE(2)', r'$\mbox{SE}(2)$')
        s = s.replace('SO(3)', r'$\mbox{SO}(3)$')
        s = s.replace('SE(3)', r'$\mbox{SE}(3)$')
        
        # ^ -> \textasciicircum
        #s = s.replace('^', '\\textasciicircum ')

        # % -> \%
        s = s.replace('%', '\\%')
        # # -> \#
        s = s.replace('#', '\\#')

        # ~= -> ne
        s = s.replace('~=', '$\\ne$')
  
        # N'th -> N^{th}
        s = s.replace("'th", '${}^{\mbox{th}}$')

        # & -> \&
        s = s.replace('&', '\\&')
        # < -> $<$
        s = s.replace('<', '$<$')
        s = s.replace('>', '$>$')
        # ~ -> $\approx$
        s = s.replace(' ~ ', '$\\approx$')

        # _ -> \_
        #  do this last, otherwise function names with underscore become unrecognizable
        #  for function name substitutions
        s = s.replace('_', '\\_')

        s = s.replace('2pi', r'$2\pi$')
        s = s.replace('pi/2', r'$\pi/2$')
        s = s.replace('[-pi,pi)', r'$[-\pi, \pi)$')
        s = self.re_pi.sub(r'$\pi$', s)

        s = self.re_url.sub(r'\url{\1}', s)

        return s

    def emphFunction(self, s):
        return '\\textbf{\\color{red} %s}' % s

    def emphVar(self, s):
        return "\\texttt{%s}" % s

    def emphPath(self, s):
        return "\\texttt{%s}" % s

    @trace
    def startModule(self, funcname, text, tag=None, titlebar=False, ismethod=False):
        self.vars = set()
        #print 'startMod', funcname, self.transform(funcname), self.vars
        # _ -> \_
        funcname = funcname.replace('_', '\\_')
        self.out += '\n%%---------------------- %s\n' % funcname
        self.out += '\\hypertarget{%s}{\\section*{%s}}\n' % (funcname,funcname)
        self.out += '\\subsection*{%s}\n' % self.transform((split_first_word(text)[1]))
        if ismethod:
            self.out += '\\addcontentsline{toc}{section}{%s}\n' % funcname
        else:
            self.out += '\\addcontentsline{tom}{section}{%s}\n' % funcname
    @trace
    def endModule(self):
        self.out += '\\vspace{1.5ex}\\rule{\\textwidth}{1mm}\n'

    @trace
    def endMethod(self):
        self.out += '\\vspace{1.5ex}\\hrule\n'

    @trace
    def heading(self, text):
        self.out += '\n\\subsection*{%s}\n' % self.transform(text)

    @trace
    def startTable(self):
        self.out += '\\begin{longtable}{lp{120mm}}\n'

    @trace
    def addTable(self, col1, col2):
        col1 = col1.replace('~=', r'$\sim=$')
        col1 = col1.replace('*', r'\textasteriskcentered ')
        col1 = col1.replace('^', r'\textasciicircum ')
        col1 = col1.replace('_', r'\_')
        col1 = col1.replace("'", r'\textquotesingle ')
        self.out += '%s & %s\\\\ \n' % (col1, self.transform(col2))

    @trace
    def addTableSep(self):
        self.out += '\\hline\n'

    @trace
    def endTable(self):
        self.out += '\\end{longtable}\\vspace{1ex}\n'

    @trace
    def startCode(self):
        self.out += '\\begin{Code}\n'

    @trace
    def addCode(self, text):
        self.out += '%s\n' % text

    @trace
    def endCode(self):
        self.out += '\\end{Code}\n'

    @trace
    def startList(self):
        self.out += '\\begin{itemize}\n'

    @trace
    def addList(self, text):
        self.out += '  \\item %s\n' % self.transform(text)
        # HACK self.out += '  \\item %s\n' % self.transform(text, tolower=True)

    @trace
    def endList(self):
        self.out += '\\end{itemize}\n'

    @trace
    def startPara(self):
        self.out += '\n\n'

    @trace
    def addPara(self, text, definition, **args):  # MD version
        if definition:
            definition = definition.replace('_', r'\_')
            definition = definition.replace('^', r'\textasciicircum ')
            self.out += "\\texttt{" + definition + "}"
            print 'DEFINITION', definition

        self.out += self.transform(text, **args) + '\n'

    @trace
    def endPara(self):
        self.out += '\n'

    @trace
    def startAlso(self):
        self.alsoCount = 0
        self.startPara()

    @trace
    def addAlso(self, text):
        if self.alsoCount > 0:
            self.out += ', '
        # _ -> \_
        text2 = text.replace('_', '\\_')
        self.out += '\hyperlink{%s}{\\color{blue} %s}' % (text, text2)
        self.alsoCount += 1

    @trace
    def endAlso(self):
        self.out += '\n\n'


# =============================================================================
# GenHTML subclass
# =============================================================================

class GenHTML(GenHelp):

    def __init__(self, matlab=False, toolbox=None, **kwargs):
        super(GenHTML, self).__init__(**kwargs)
        self.matlab = matlab

        if toolbox == 'rtb':
            self.toolboxname = "Robotics Toolbox for MATLAB"
            self.toolboxurl = "http://www.petercorke.com/robot"
        elif toolbox == 'mvtb':
            self.toolboxname = "Machine Vision Toolbox for MATLAB"
            self.toolboxurl = "http://www.petercorke.com/vision"

    def done(self):
        pass

    def substitutions(self, s):
        # HTML specific fixups
        s = s.replace('<', '&lt;')
        s = s.replace('>', '&gt;')
        s = s.replace('&', '&amp;')
        s = s.replace('^', '&circ;')

        return s

    def emphFunction(self, s):
        return '<span style="color:red">%s</span>' % s

    def emphVar(self, s):
        return '<strong>%s</strong>' % s

    def emphPath(self, s):
        return '<strong>%s</strong>' % s

    @trace
    def startModule(self, funcname, text, tag=None, titlebar=False, ismethod=False):
        def gen_titlebar(funcname):
            if self.matlab:
                out = '''<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <link rel="stylesheet" href="http://www.petercorke.com/RVC/common/toolboxhelp.css">
    <title>M-File Help: %(function)s</title>
  </head>
  <body>
  <table border="0" cellspacing="0" width="100%%">
    <tr class="subheader">
      <td class="headertitle">M-File Help: %(function)s</td>
      <td class="subheader-left"><a href="matlab:open %(function)s">View code for %(function)s</a></td>
    </tr>
  </table>
''' % {'function' : funcname}

            else:
                out = '''<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <link rel="stylesheet" href="http://www.petercorke.com/RVC/common/toolboxhelp.css">
    <title>%(function)s</title>
  </head>
  <body>
''' % {'function' : funcname}

            return out

        # create HTML header block + title bar
        if titlebar:
            self.out += gen_titlebar(funcname)
        if tag:
            self.out += '<a name="%s">' % tag
        self.out += '<h1>%s</h1>' % funcname
        if tag:
            self.out += '</a>\n'
        #out += '<p><span class="helptopic">%s</span>  %s</p>' % (funcname, split_first_word(text[0])[1])
        self.out += '<p><span class="helptopic">%s</span></p>' % (split_first_word(text[0])[1])
        self.vars = set()

    def endModule(self):
        self.out += '<hr>\n'
        today = date.today()
        out = '<address style="text-align:right">Generated %s by <strong><a href="xx">%s</a></strong> &copy; 2014 Peter Corke</address>\n' % (today.isoformat(), sys.argv[0])
        if self.matlab:
            self.out += '''
<table border="0" width="100%" cellpadding="0" cellspacing="0">
  <tr class="subheader" valign="top"><td>&nbsp;</td></tr></table>
<p class="copy">&copy; 1990-2014 Peter Corke.</p>
</body></html>'''
        else:
            self.out += '''
<p class="copy"><a href="%s">%s</a> &copy; 1990-2014 Peter Corke.</p>
</body></html>''' % (self.toolboxurl, self.toolboxname)

    @trace
    def endMethod(self):
        self.out += '<hr>\n'

    @trace
    def heading(self, text):
        self.out += '<h2>%s</h2>\n' % text

    @trace
    def startTable(self):
        self.out += '<table class="list">\n'

    @trace
    def addTable(self, col1, col2):
        self.out += '  <tr><td style="white-space: nowrap;" class="col1">%s</td> <td>%s</td></tr>\n' % (col1, col2)

    @trace
    def addTableSep(self):
        self.out += '  <tr></tr>\n  <tr></tr>'

    @trace
    def endTable(self):
        self.out += '</table>\n'

    @trace
    def startCode(self):
        self.out += '<pre style="width: 90%%;" class="examples">\n'

    @trace
    def addCode(self, text):
        self.out += '%s\n' % text.replace(' ', '&nbsp;')

    @trace
    def endCode(self):
        self.out += '</pre>\n'

    @trace
    def startList(self):
        self.out += '<ul>\n'

    @trace
    def addList(self, text):
        self.out += '  <li>%s</li>\n' % text

    @trace
    def endList(self):
        self.out += '</ul>\n'

    @trace
    def startPara(self):
        self.out += '<p>\n'

    @trace
    def addPara(self, text, **args):
        self.startPara()
        self.findvars(text, classname=args['classname'])
        s =  self.transform(text, **args)
        self.out += s + '\n\n'
        self.endPara()

    @trace
    def endPara(self):
        self.out += '</p>\n'

    @trace
    def startAlso(self):
        self.alsoCount = 0
        self.startPara()

    @trace
    def addAlso(self, text):
        if self.alsoCount > 0:
            self.out += ', '
        if self.matlab:
            self.out += '<a href="%s.html">%s</a>' % (text,text)
        else:
            self.out += '<a href="%s.html">%s</a>' % (text,text)
        self.alsoCount += 1

    @trace
    def endAlso(self):
        self.endPara()

    # Generate code document for a regular m-file
    def format_code(self, filename, pname=None):

        def fixspace(s):
            return s.replace(' ', '&nbsp;')

        re_comment = re.compile(r'(%.*)$')

        # open the output file
        outfile = os.path.splitext(filename.lstrip('@'))[0]+'_code.html'
        out = open(outfile, 'w')

        funcname = os.path.splitext(os.path.basename(filename))[0]

        out.write('''<html>
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <link rel="stylesheet" href="http://www.petercorke.com/RVC/common/book.css">
        <title>M-File Help: %(function)s</title>
      </head>
      <body>
    ''' % {'function' : funcname})

        with open(filename, 'r') as f:
            out.write('<h1>%s</h1>' % funcname)
            out.write('<table class="codelistingtable">')

            for (num,line) in enumerate(f):
                line = line.replace(' ', '&nbsp;')
                line = re_comment.sub('<span style="color:blue">\\1</span>', line)
                out.write('<tr><td class="codelistingnum">%d</td><td><pre class="codelistingcode">%s</pre></td></tr>\n' % (num+1, line))

            out.write('</table>\n')
            today = date.today()
            out.write('<hr><address style="text-align:right">Generated %s by <strong><a href="xx">%s</a></strong> &copy; 2014 Peter Corke</address>\n' % (today.isoformat(), pname))
            out.write('</body></html>\n')

# =============================================================================
# GenMD subclass to create MarkDown output
# =============================================================================

class GenMarkDown(GenHelp):

    def __init__(self, matlab=False, toolbox=None, **kwargs):
        super(GenMarkDown, self).__init__(**kwargs)
        self.matlab = matlab
        self.re_dims2 = re.compile(r'(\b[0-9A-Z]+)x([0-9A-Z]+)\b')
        self.re_dims3 = re.compile(r'(\b[0-9A-Z]+)x([0-9A-Z]+)x([0-9A-Z]+)\b')
        self.re_exp = re.compile(r'\^([0-9a-zA-Z-]+)')
        self.re_exp2 = re.compile(r'[^{}]\^[^{}]')

        if toolbox == 'rtb':
            self.toolboxname = "Robotics Toolbox for MATLAB"
            self.toolboxurl = "http://www.petercorke.com/robot"
        elif toolbox == 'mvtb':
            self.toolboxname = "Machine Vision Toolbox for MATLAB"
            self.toolboxurl = "http://www.petercorke.com/vision"

    def done(self):
        pass

    def substitutions(self, s):
        # MarkDown specific fixups
        # NxM -> N &times; M
        s = self.re_dims2.sub(r'\1&times;\2', s)

        # NxMxK -> N &times; M &times; K
        s = self.re_dims3.sub(r'\1&times;\2&times; \3', s)

        # A^2 -> A<sup>2</sup>
        s = self.re_exp.sub(r'<sup>\1</sup>', s)

        s = s.replace('\n', ' ')

        return s

    def emphFunction(self, s):
        return '**%s**' % s

    def emphVar(self, s):
        return '`%s`' % s

    def emphPath(self, s):
        return '`%s`' % s

    @trace
    def startModule(self, funcname, text, tag=None, titlebar=False, ismethod=False):

        self.out += '# %s\n' % funcname

        self.out += '_%s_\n' % (split_first_word(text)[1])
        self.vars = set()


    def endModule(self):
            pass

    @trace
    def endMethod(self):
        self.out += '<hr>\n\n'

    @trace
    def heading(self, text):
        self.out += '### %s\n' % text

    @trace
    def startTable(self):
        self.out += '| | |\n|-|-|\n'

    @trace
    def addTable(self, col1, col2):
        self.out += '  | `%s` | %s |\n' % (col1, col2)

    @trace
    def addTableSep(self):
        self.out += ''

    @trace
    def endTable(self):
        self.out += '\n\n'

    @trace
    def startCode(self):
        print '  start code'
        self.out += '```matlab\n'

    @trace
    def addCode(self, text):
        print '  add code'
        self.out += '%s\n' % text

    @trace
    def endCode(self):
        print '  end code'
        self.out += '```\n'

    @trace
    def startList(self):
        self.out += ''

    @trace
    def addList(self, text):
        self.out += '* %s\n' % self.transform(text)

    @trace
    def endList(self):
        self.out += '\n'

    @trace
    def startPara(self):
        self.out += '\n'

    @trace
    def addPara(self, text, definition, **args):
        print "  add to para", text, definition

        self.startPara()
        if definition:
            self.out += "```" + definition + "```"

        s =  self.transform(text, **args)
        self.out += s

    @trace
    def endPara(self):
        self.out += '\n'

    @trace
    def startAlso(self):
        self.alsoCount = 0
        self.startPara()

    @trace
    def addAlso(self, text):
        if self.alsoCount > 0:
            self.out += ', '
        self.out += '[%s](%s.md)' % (text,text)
        self.alsoCount += 1

    @trace
    def endAlso(self):
        self.endPara()

    # Generate code document for a regular m-file
    def format_code(self, filename, pname=None):

        # open the output file
        outfile = os.path.splitext(filename.lstrip('@'))[0]+'_code.md'
        out = open(outfile, 'w')

        funcname = os.path.splitext(os.path.basename(filename))[0]

        out.write('''
        ## M-File Help: %(function)s
    ''' % {'function' : funcname})

        with open(filename, 'r') as f:
            out.write('# %s\n' % funcname)
            out.write('```matlab\n')

            for (num,line) in enumerate(f):
                out.write(line+'\n')

            out.write('```\n')
            today = date.today()
            out.write('---\nGenerated %s by *%s &copy; 2019 Peter Corke\n' % (today.isoformat(), pname))

