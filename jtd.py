#! /usr/bin/env python3

import os
import os.path
import glob
import json

# load the index data
with open("TOC.json", "r") as toc:
    funcIndex_tag, funcIndex_all = json.load(toc)


funcIndex_tag['ALL'] = funcIndex_all.keys()

# create the set of folders
for (tag,functions) in funcIndex_tag.items():
    if os.path.exists(tag):
        if os.path.isdir(tag):
            # folder exists, empty it
            for file in glob.glob(os.path.join(tag, "*.md")):
                os.remove(file)
    else:
        # create the folder
        os.mkdir(tag)

# copy files into folders
for (tag,functions) in funcIndex_tag.items():
    for function in functions:
        with open(function+".md", "r") as src, open(os.path.join(tag, function+".md"), "w") as dst:
            dst.write("---\nlayout: default\nparent: %s functions\n---\n" % tag)
            dst.write(src.read())

# update the TOC files
for tag in funcIndex_tag.keys():
    with open("TOC_%s.md" % tag, "r") as src:
        data = src.read()
    with open("TOC_%s.md" % tag, "w") as dst:
        if tag == "ALL":
            nav_order = 100
        else:
            nav_order = 10
        dst.write("---\nlayout: default\nhas_children: true\nhas_to: false\nnav_order: %d\n---\n" % nav_order)
        dst.write(data)

# cleanup all non-TOC files
print(funcIndex_all)

for function in funcIndex_all.keys():
    os.remove(function+".md")