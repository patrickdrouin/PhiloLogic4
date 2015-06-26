#!/usr/bin/env python

import os
import sys
sys.path.append('..')
from functions.wsgi_handler import WSGIHandler
from wsgiref.handlers import CGIHandler
from philologic.DB import DB
from philologic.HitWrapper import ObjectWrapper
from lxml import etree
import functions as f
import reports as r
import re
import subprocess
import json
from bisect import bisect_left

header_name = 'teiHeader'  ## Not sure if this should be configurable

def get_note_link_back(environ, start_response):
    config = f.WebConfig()
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(db, environ)
    
    # Get byte offset of hash
    path = config.db_path
    philo_id = request.doc_id + ' 0 0 0 0 0 0'
    obj = ObjectWrapper(philo_id.split(), db)
    filename = path + '/data/TEXT/' + obj.filename
    proc = subprocess.Popen(['grep', '-o', '--byte-offset', request.note_id, filename], stdout=subprocess.PIPE)
    output = proc.communicate()[0]
    first_hit = output.split('\n')[0]
    note_offset = int(first_hit.split(':')[0].strip())
    
    # Get all div1s in document
    c = db.dbh.cursor()
    doc_id =  int(request.doc_id)
    next_doc_id = doc_id + 1
    # find the starting rowid for this doc
    c.execute('select rowid from toms where philo_id="%d 0 0 0 0 0 0"' % doc_id)
    start_rowid = c.fetchone()[0]
    # find the starting rowid for the next doc
    c.execute('select rowid from toms where philo_id="%d 0 0 0 0 0 0"' % next_doc_id)
    try:
        end_rowid = c.fetchone()[0]
    except TypeError: # if this is the last doc, just get the last rowid in the table.
        c.execute('select max(rowid) from toms;')
        end_rowid = c.fetchone()[0]
    
    c.execute('select byte_start, philo_id from toms where rowid >= ? and rowid <=? and philo_type="div2"', (start_rowid, end_rowid))
    results = [(i['byte_start'], i['philo_id']) for i in c.fetchall()]
    closest_byte = takeClosest([i[0] for i in results], note_offset)
    result_id = dict(results)[closest_byte]
    link = 'navigate/' + '/'.join(result_id.split()[:2]) + '#%s-link-back' % request.note_id.replace('#', '')
    status = '200 OK'
    headers = [('Content-type', 'application/json; charset=UTF-8'),("Access-Control-Allow-Origin","*")]
    start_response(status,headers)
    yield json.dumps({'link': link, "h": result_id})


def takeClosest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
       return after
    else:
       return before
        
if __name__ == "__main__":
    CGIHandler().run(get_note_link_back)