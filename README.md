This package provides some tools to support a simple MATLAB markup that is subtle enough to ensure that the help documentation is still readable using the command line `help` function. All documentation is kept with the code in a single text file which means that many software development tools (like sed, awk, diff) can be applied and revisions tracked easily using GitHub.

In contrast, MATLAB _Live Functions_ are zip files that contain many files are not easy to edit or compare outside of the MATLAB environment.

There are two tools in this package:

* [help2doc](#help2doc)
* [showtags](#showtags)

# help2doc

Process MATLAB source files (functions and class definitions) and produce LaTex, HTML or MarkDown documentation.


## Usage

```
help2doc options <list of m files>
```

The options are:

| Switch           |    Purpose |
--- | ---
-h, --help            | show this help message and exit
-w, --web             | format pages for online web viewing
-M, --doc             | format pages for matlab help browser
-l, --latex           | format pages for creation with LaTeX
-m, --markdown        | format pages for creation with MarkDown
--mvtb                | format pages for MVTB
--rtb                 | format pages for RTB
-p PATH, --path=PATH  | path to toolbox root
--include             | LaTeX document is for inclusion, not standalone (no preamble)
-c, --code            | create html form of code
-d, --display         | display in web browser
-v, --verbose         | display in web browser
--exclude=EXCLUDE_FILES | exclude files
--index               | create index files


## MATLAB markup


### Placing the markup comment blocks

### H1 line
The H1 line is the first line in the file and gives the function name and a brief synopsis.

```matlab
%PLOT_RIBBON Draw a wide curved 3D arrow
```

### Additional comments
Following the H1 line, but in the same comment block, describe the function (or the class).

```matlab
%PLOT_RIBBON Draw a wide curved 3D arrow
%
% plot_ribbon() adds a 3D curved arrow "ribbon" to the current plot.  The ribbon by
% default is about the z-axis at the origin.
%
% Options::
% 'radius',R     radius of the ribbon (default 0.25)
% 'N',N          number of points along the ribbon (default 100)
%
% 'd',D          ratio of shaft length to total  (default 0.9)
% 'w1',W         width of shaft (default 0.2)
% 'w2',W         width of head (default 0.4)
% 'phi',P        length of ribbon as fraction of circle (default 0.8)
% 'phase',P      rotate the arrow about its axis (radians, default 0)
%
% 'color',C      color as MATLAB ColorSpec (default 'r')
% 'specular',S   specularity of surface (default 0.2)
% 'diffuse',D    diffusivity of surface (default 0.8)
%
% 'nice'         adjust the phase for nicely phased arrow 
```

Documentation ends at the first non-comment line in the file.

### Class methods

In addition to the comment block starting at the top of the file which describes the class, document each method by a comment block below the function declaration for the method.  

```matlab
       function t = SE3(obj)
            %SE2.SE3 Lift to 3D
            %
            % Q = P.SE3() is an SE3 object formed by lifting the rigid-body motion
            % described by the SE2 object P from 2D to 3D.  The rotation is about the
            % z-axis, and the translation is within the xy-plane.
            %
            % See also SE3.
```

Methods for the class are listed alphabetically, except for the constructor which is always listed first.  The class name is highlighted.

### Markup format

#### Headings

A heading is indicated by a double colon on the end of a standalone text line

```matlab
%
% A heading::
%
```

#### Paragraph

A sequence of lines with the same indent and no blank lines in between.  The first part of the paragraph is parsed to find any MATLAB code and any variables are added to a symbol table for this M-file.  Any instances of that symbol in later text are escaped in an output format specific way.

```matlab
%
% X = FUNC(A,B) returns a matrix that is a function of A and B.  If A is a matrix then so is X.
%
```
will result in:

`X = FUNC(A,B)` returns a matrix that is a function of `A` and `B`.  If `A` is a matrix then so is `X`.

The MATLAB code parser is implemented using regexp and supports the following patterns:
```
VLIST := VAR | VAR, <VLIST> | <EMPTY> | ...
LHS := F | F(<VLIST>) | OBJ.METHOD | OBJ.METHOD(<VLIST>)
RHS := VAR | [<VLIST>]
EXPR := <LHS> | <RHS> = <LHS>
```


#### Lists
A list item begins with a hyphen.
```matlab
%
% - First list item.
% - Second list item.
% - Very long list item which wraps
%   around to the next line.
%
```
Lists may also be indented.
```matlab
%
% - First list item.
%   - First line of indented list
%   - Second line of indented list
% - Second line of original list
%
```

#### Table
Only two column tables are supported.  The columns are separated by at least 3 white spaces.
```matlab
%
% A    first row
% B    second row
% AA   third row
% BB   very long table text which wraps
%      around to the next line.
%
```
Tables cannot be nested.  There is no header row.

In MarkDown output format it is mandatory to have a header row, so the first row of a table is empty.

#### Literal

Any code that is indented by at least 8 blanks is treated as a literal

```matlab
%          for i=1:100
%             do_a_thing();
%          end
```

#### See also

A comma separated list of functions is transformed into hyperlinked text.

```matlab
% See also function1, function2, function3.
```

## Tags and indices

If the `--index` command option is given, then indices are compiled and extra output files are created.

A comment line like

```matlab
%## tag1 tag2 ...
```
will cause the containing file to be added to various indices:

* the alphabetic index called `index_alpha` with an extension that depends on the output language.
* one or more per tag index files with names of the form `index_tag` with an extension that depends on the output language.

# showtags
A command line utility that will show a formatted list of all functions and their tags, for example

```matlab
% showtags *m
           t2r.m: 2d 3d homogeneous
   tb_optparse.m: utility
     tr2angvec.m: 3d homogeneous rotation
      tr2delta.m: 3d differential homogeneous
        tr2eul.m: 3d homogeneous rotation
        tr2jac.m: 3d differential homogeneous
        tr2rpy.m: 3d homogeneous rotation
         tr2rt.m: 2d 3d homogeneous rotation translation
```

The tags are listed alphabetically, and unknown tags are displayed inside angle brackets.

# TODO

* `--rtb` and `--mvtb` add specific footer and copyright notices to the output documentation.  This needs to be generalized.
* the MATLAB file parser still needs work
* I think the HTML output generator is broken now...
* Need to handle tags for classes
* Need to create index generator code for other languages than MarkDown
* Probably need to split `GenText.py` into per language files, it's too big
