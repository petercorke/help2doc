Process MATLAB source files (functions and class definitions) and produce LaTex, HTML or MarkDown documentation.

# Usage

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


# MATLAB markup

The markup is simple and subtle enough to ensure that the help documentation is still readable.

## Placing the markup comment blocks

## H1 line
The H1 line is the first line in the file and gives the function name and a brief synopsis.

```matlab
%PLOT_RIBBON Draw a wide curved 3D arrow
```

## Additional comments
Following the H1 line, but in the same comment block.

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

Documetation ends at the first non-comment line in the file.

## Class methods

Place the comments below the function declaration for the method

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


## Markup format

### Headings

A heading is indicated by a double colon on the end of a standalone text line

```matlab
%
% A heading::
%
```

### Tables
```matlab
%
% A heading::
```

### Lists
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

### Table
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
Tables cannot be nested.

### Literal

Any code that is indented by at least 8 blanks is treated as a literal

```matlab
%          for i=1:100
%             do_a_thing();
%          end
```

### See also

A comma separated list of functions is transformed into hyperlinked text.

```matlab
% See also function1, function2, function3.
```
