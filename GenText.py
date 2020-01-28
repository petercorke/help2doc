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
debug_gen = False
debug_format = False



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
                        #print "SAME"
                        self.addTable(nextLine.col1(), nextLine.col2())
                    else:
                        #print "NOT SAME"
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
