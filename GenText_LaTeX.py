from GenText import * # file parser and text rendering

# =============================================================================
# GenLatex subclass
# =============================================================================
class GenLaTeX(GenHelp):
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
            #print 'DEFINITION', definition

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