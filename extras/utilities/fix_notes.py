#!/usr/bin/python

from lxml import etree
from copy import deepcopy
import sys

"""This script is intended to move the content of inline notes to the end of the document
inside a <div type="notes">. The inline note tags will then contain ref attributes
corresponding to the ids of the note contents at the end of the file"""

for file in sys.argv[1:]:
    fd = open(file)
    print >> sys.stderr, "reading ", file
    text_string = fd.read()
    root = etree.fromstring(text_string)    
    for el in root.getiterator():
        try:
            if el.tag.startswith("{"):
                old_tag = el.tag
                el.tag = el.tag.rsplit('}', 1)[-1]
        except AttributeError:
            pass
    note_div = etree.Element("div", type="notes")
    note_div.text = "\n"
    note_count = 1
    for el in root.iter('note'):
        new_id = "philo_note_%d" % note_count
        new_note = deepcopy(el)
        for attr in new_note.attrib:
            del new_note.attrib[attr]
        new_note.attrib['id'] = new_id
        new_note.attrib['n'] = str(note_count)
        new_note.tail = "\n"
        el.tag = "ptr"
        for child in el:
            el.remove(child)
        el.text = ""
        note_div.append(new_note)
        el.attrib["target"] = "#%s" % new_id
        note_count += 1
    root[-1].append(note_div)
    new_file = file + ".notes_fixed"
    print >> sys.stderr, "writing ", new_file
    new_fd = open(new_file,"w")
    new_fd.write("<?xml version='1.0' encoding='utf-8'?>")
    tree = etree.ElementTree(root)
    new_fd.write(etree.tostring(tree,encoding="utf-8"))
    new_fd.close()

