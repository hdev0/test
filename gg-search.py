#!/usr/bin/python3

import os
import sys
import json
import argparse
from goop import goop
from multiprocessing.dummy import Pool


parser = argparse.ArgumentParser()
parser.add_argument( "-t","--term",help="search term", action="append" )
parser.add_argument( "-e","--endpage",help="search end page, default 100" )
parser.add_argument( "-s","--startpage",help="search start page, default 0" )
parser.add_argument( "-f","--fbcookie",help="your facebook cookie" )

parser.parse_args()
args = parser.parse_args()

if args.startpage:
    start_page = int(args.startpage)
else:
    start_page = 0

if args.endpage:
    end_page = int(args.endpage)
else:
    end_page = 100

if args.fbcookie:
    fb_cookie = args.fbcookie
else:
    parser.error( 'facebook cookie is missing' )

if args.term:
    t_terms = args.term
else:
    parser.error( 'term is missing' )


def doMultiSearch( page ):
    zero_result = 0
    for i in range(page-5,page-1):
        if i != page and i in gg_history and gg_history[i] == 0:
            zero_result = zero_result + 1

    if zero_result < 3:
        s_results = goop.search( gg_search, fb_cookie, page=page )
        # sys.stdout.write( '[+] grabbing page %d/%d... (%d)\n' %  (page,end_page,len(s_results)) )
        gg_history[page] = len(s_results)
        # print(s_results)
        for i in s_results:
            print( s_results[i]['url'] )
        # t_results.append( s_results )
    else:
        for i in range(page,end_page):
            gg_history[i] = 0


s_results = []
t_results = []
t_history = []
gg_history = {}


for term in t_terms:
    gg_search = term
    pool = Pool( 5 )
    pool.map( doMultiSearch, range(start_page,end_page) )
    pool.close()
    pool.join()
