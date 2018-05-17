#!/usr/bin/env python

import os
from wsgiref.handlers import CGIHandler

import simplejson
from philologic.runtime import get_start_end_date as start_end_date
from philologic.DB import DB

import sys
sys.path.append("..")
import custom_functions
try:
     from custom_functions import WebConfig
except ImportError:
     from philologic.runtime import WebConfig
try:
     from custom_functions import WSGIHandler
except ImportError:
     from philologic.runtime import WSGIHandler


def get_start_end_date(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=UTF-8'), ("Access-Control-Allow-Origin", "*")]
    start_response(status, headers)
    config = WebConfig(os.path.abspath(os.path.dirname(__file__)).replace('scripts', ''))
    db = DB(config.db_path + '/data/')
    request = WSGIHandler(environ, config)
    start_date, end_date = start_end_date(db, config, start_date=request.start_date, end_date=request.end_date)
    request.metadata["year"] = "{}-{}".format(start_date, end_date)
    request["start_date"] = ""
    request["end_date"] = ""
    hits = db.query(request["q"], request["method"], request["arg"], **request.metadata)
    total_results = 0
    hits.finish()
    total_results = len(hits)
    yield simplejson.dumps({"start_date": start_date, "end_date": end_date, "total_results": total_results})


if __name__ == "__main__":
    CGIHandler().run(get_start_end_date)
