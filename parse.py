import re
from datetime import date

# debug options
debug_chunk = False
debug_line = False

# these variables are left capitalized
nocaps = ['L', 'T', 'R', 'C', 'C2', 'H', 'E', 'J',
          'TR', 'T0', 'T1', 'R0', 'R1']

# states and their names
BLANKLINE = 1
HEADER = 2
TABLE = 3
LIST = 4
TEXT = 5
SEEALSO = 6
SUMMARY = 7
TABLESEP = 8
END = 9

statenames = ['BLANKLINE', 'HEADER', 'TABLE', 'LIST', 'TEXT',
              'SEEALSO', 'SUMMARY', 'TABLESEP', 'END']


# regular expressions for code parsing
#  \s is whitespace
#  \S is not whitespace
re_table = re.compile(r'\s*(?P<col1>\S[\s\S]+?)\s\s\s+(?P<col2>.+)')
re_tablesep = re.compile(r'-+')
re_bullet = re.compile(r'\s+-\s*(?P<text>.*)')
re_text = re.compile(r'\s*(?P<text>.*)')
re_header = re.compile(r'\s*(?P<text>[A-Z][^:]+)::$')
re_seealso = re.compile(r'\s*See also\s*(?P<text>.*?)\.$')
# re_code = re.compile(r' {8}\s*(?P<text>.+)')


class MATLABLine(object):
    def __init__(self, indent, type, text):
        self.indent = indent   # can be a list in case of table
        self.type = type
        self.textdata = text   # is a list, 2 elements in case of table [col1 col2]

    def __repr__(self):
        return 'indent=' + str(self.indent) + ' type=' + stateName(self.type) + ' text=' + self.textdata[0]


    def same(self, other):
        if self.type == TEXT and other.type == TEXT and self.indent > 8 and other.indent > 8:
            return True
        return self.type == other.type and self.indent == other.indent

    def text(self, indent=False):
        if indent:
            return ' ' * (self.indent - 6) + self.textdata[0].strip()
        else:
            return self.textdata[0].strip()

    def col1(self):
        return self.textdata[0].strip()

    def col2(self):
        return self.textdata[1].strip()


class MATLABLineEnd(Exception):
    pass

# p = Parser(mfile)
# l = p.nextLine()
# returns an object with properties: type, text, indent


class Parser(object):
    def __init__(self, doc):
        self.linenum = 0
        self.lines = doc.split('\n')

    def nextLine(self):

        # get comment line, classify it
        (text, indent, typ) = self.readline()

        if typ == TABLE:
            z = self.peekline()  # peek at next line
            if z[2] == TEXT and z[1] == indent[1]:
                # continuation line
                text[0] += ' ' + z[0][0]
                self.readline()  # consume that line

        elif typ == LIST:
            z = self.peekline()  # peek at next line
            if z[2] == TEXT and z[1] == indent:
                # continuation line
                text[0] += ' ' + z[0][0]
                self.readline()  # consume that line

        if debug_line:
            self.showline(indent, typ, text)

        if debug_chunk:
            self.showchunk(indent, typ, text)
        return MATLABLine(indent, typ, text)

    def readline(self):
        # return the next MATLAB comment line from the string
        # returns on the first non-comment line found
        try:
            line = self.lines.pop(0)
        except IndexError:
            return ('', 0, END)
        self.linenum += 1

        if line and line[0] != '%':
            return ('', 0, END)
        line = line.lstrip('%')
        line = line.rstrip()
        if debug_line:
            print '---|%s|' % line
        if self.linenum == 1:
            return ([line.strip()], 0, SUMMARY)
        else:
            return self.classify(line)

    def peekline(self, i=0):
        # return the next MATLAB comment line from the string
        # returns on the first non-comment line found
        try:
            line = self.lines[i]
        except IndexError:
            return ('', 0, END)

        if line and line[0] != '%':
            return ('', 0, END)
        line = line.lstrip('%')
        line = line.rstrip()
        return self.classify(line)

    def classify(self, line):

        if line == '':
            return ([''], 0, BLANKLINE)

        # TEXT::
        m = re_header.match(line)
        if m:
            indent = m.start('text')
            chunk = [m.group('text')]
            return (chunk, indent, HEADER)

        #  OPT   TEXT   at least 3 spaces between
        m = re_table.match(line)
        if m:
            # the two chunks of text are <opt>, <text>
            # if indent >= 8:
            #     # if opt is indented >= 8 this signals verbatim mode
            #     # ie. PARA with indent 8
            #     m2 = re_para.match(line)
            #     if m2:
            #         state = PARA
            #         indent = m2.start('text')
            #         curIndent = indent
            #         chunk = [m2.group('text')]
            #         return (chunk, indent, state)
            # otherwise a table line
            chunk = [m.group('col1'), m.group('col2')]
            if m.start('col1') < 8:
                return (chunk, [m.start('col1'), m.start('col2')], TABLE)

        # --
        m = re_tablesep.match(line)
        if m:
            return (None, 0, TABLESEP)

        #  - TEXT
        m = re_bullet.match(line)
        if m:
            indent = m.start('text')
            chunk = [m.group('text')]
            return (chunk, indent, LIST)

        # See also TEXT.
        m = re_seealso.match(line)
        if m:
            indent = m.start('text')
            chunk = [m.group('text')]
            return (chunk, indent, SEEALSO)

        m = re_text.match(line)
        if m:
            indent = m.start('text')
            chunk = [m.group(0)]
            return (chunk, indent, TEXT)

    def showchunk(self, indent, typ, text):
        print '<<< getchunk:%s' % stateName(typ),
        print ', indent=',
        print indent,

        print '{',
        print text,
        print '} >>>'

    def showline(self, indent, typ, text):
        print '<< getchunk:%s' % stateName(typ),
        print ', indent=',
        print indent,
        print '{',
        print text,
        print '} >>'


def stateName(c):
    if c:
        return statenames[c - 1]
    else:
        return 'NIL'
