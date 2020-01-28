from GenText import * # file parser and text rendering

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
            out.write('</body></html>\n')# =============================================================================
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

    @trace
    def heading(self, text):
        self.out += '### %s\n' % text

    @trace
    def startTable(self):
        self.out += '| | |\n|---|---|\n'

    @trace
    def addTable(self, col1, col2):
        self.out += '| `%s` | %s |\n' % (col1, col2)

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
                 f.write("|[`%s`](index_%s.html) | %s |\n" % (func, os.path.join(prefix,func), all[func]))

        with open('TOC.md', 'w') as f:
            if jekyll:
                f.write('---\n---\n')
            f.write('# Function indices\n\n')
            f.write(" * [All functions](%s)\n" % (os.path.join(prefix,'index_alpha.html'),))
            f.write(" * By tag:\n")
            for tag in sorted(bytag.keys()):
                f.write("   - [%s related](%s)\n" % (tag, os.path.join(prefix, tag+'.html')))