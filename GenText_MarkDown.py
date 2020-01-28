from GenText import * # file parser and text rendering

# =============================================================================
# GenMD subclass to create MarkDown output
# =============================================================================

class GenMarkDown(GenHelp):

    def __init__(self, matlab=False, toolbox=None, jekyll=False, **kwargs):
        super(GenMarkDown, self).__init__(**kwargs)
        self.matlab = matlab
        self.re_dims2 = re.compile(r'(\b[0-9A-Z]+)x([0-9A-Z]+)\b')
        self.re_dims3 = re.compile(r'(\b[0-9A-Z]+)x([0-9A-Z]+)x([0-9A-Z]+)\b')
        self.re_exp = re.compile(r'\^([0-9a-zA-Z-]+)')
        self.re_exp2 = re.compile(r'[^{}]\^[^{}]')
        self.jekyll = jekyll

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

        # pipe character confuses GH markdown
        s = s.replace('|', '&vert;')

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

    #-------------------- MODULE
    @trace
    def startModule(self, funcname, text, tag=None, titlebar=False, ismethod=False):

        # for Jekyll static page generator need to add special header, simple version here
        if self.jekyll:
            self.out += '---\n---\n'
        self.out += '# %s\n' % funcname

        self.out += '_%s_\n' % (split_first_word(text)[1])
        self.vars = set()


    def endModule(self):
            pass

    @trace
    def endMethod(self):
        self.out += '<hr>\n\n'

    #-------------------- TABLE
    @trace
    def startTable(self):
        self.out += '\n| | |\n|---|---|\n'  # for GitHub need a blank line first

    @trace
    def addTable(self, col1, col2):
        self.out += '| `%s` | %s |\n' % (col1, col2)

    @trace
    def addTableSep(self):
        self.out += ''

    @trace
    def endTable(self):
        self.out += '\n\n'

    #-------------------- CODE
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
        self.out = self.out[0:-2]  # remove previous newline
        self.out += '```\n'

    #-------------------- LIST
    @trace
    def startList(self):
        self.out += ''

    @trace
    def addList(self, text):
        self.out += '* %s\n' % self.transform(text)

    @trace
    def endList(self):
        self.out += '\n'

    #-------------------- PARA
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

    #-------------------- SEE ALSO
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

    #-------------------- HEADING
    @trace
    def heading(self, text):
        self.out += '### %s\n' % text


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

    def write_indices(self, all, bytag, prefix='', jekyll=False):
        # make the alphabetic list
        print all
        funcs = sorted(all.keys())
        with open('TOC_alpha.md', 'w') as f:
            if jekyll:
                f.write('---\n---\n')
            f.write('# Alphabetic list of functions\n')
            f.write('\n| Function | Description|\n|---|---|\n')
            for func in funcs:
                f.write("|[`%s`](%s.html) | %s |\n" % (func, os.path.join(prefix,func), all[func]))

        # make the per tag indices
        for tag in bytag.keys():
            funcs = sorted(bytag[tag])
            with open('TOC_%s.md' % (tag,), 'w') as f:
                if jekyll:
                    f.write('---\n---\n')
                f.write('# List of %s functions\n' % (tag,))
                f.write('\n| Function | Description|\n|---|---|\n')
                for func in funcs:
                 f.write("|[`%s`](TOC_%s.html) | %s |\n" % (func, os.path.join(prefix,func), all[func]))

        with open('TOC.md', 'w') as f:
            if jekyll:
                f.write('---\n---\n')
            f.write('# Function indices\n\n')
            f.write(" * [All functions](%s)\n" % (os.path.join(prefix,'index_alpha.html'),))
            f.write(" * By tag:\n")
            for tag in sorted(bytag.keys()):
                f.write("   - [%s related](%s)\n" % (tag, os.path.join(prefix, tag+'.html')))