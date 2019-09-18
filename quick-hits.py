#!/usr/bin/python3.5

# I don't believe in license.
# You can do whatever you want with this program.

import os
import sys
import re
import time
import random
import argparse
import requests
from urllib.parse import urlparse
from colored import fg, bg, attr
from multiprocessing.dummy import Pool


def testURL( url ):
    time.sleep( 1 )
    t_urlparse = urlparse(url)
    u = t_urlparse.scheme + '_' + t_urlparse.netloc
    if not u in t_exceptions:
        t_exceptions[u] = 0
    if t_exceptions[u] >= 5:
        return
    
    sys.stdout.write( 'progress: %d/%d\r' %  (t_multiproc['n_current'],t_multiproc['n_total']) )
    t_multiproc['n_current'] = t_multiproc['n_current'] + 1

    try:
        r = requests.get( url, timeout=2, verify=False, stream=True )
    except Exception as e:
        t_exceptions[u] = t_exceptions[u] + 1
        # sys.stdout.write( "%s[-] error occurred: %s%s\n" % (fg('red'),e,attr(0)) )
        return
    
    if 'Content-Type' in r.headers:
        content_type = r.headers['Content-Type']
    else:
        content_type = '-'
    
    output = '%sC=%d\t\tL=%d\t\tT=%s\n' %  (url.ljust(t_multiproc['u_max_length']),r.status_code,len(r.text),content_type)
    # sys.stdout.write( '%s' % output )

    fp = open( t_multiproc['f_output'], 'a+' )
    fp.write( output )
    fp.close()

    if str(r.status_code) in t_codes:
        sys.stdout.write( '%s' % output )
    
    if t_multiproc['_grabfiles']:
        saveFile( t_multiproc['d_output'], t_urlparse, r )


def saveFile( d_output, t_urlparse, r ):
    filename = t_urlparse.path.strip('/')
    filename = re.sub( '[^0-9a-zA-Z_\-\.]', '_', filename )
    d_output = d_output +  '/' + t_urlparse.netloc
    f_output = d_output + '/' + filename
    # print(f_output)
    
    if not os.path.isdir(d_output):
        try:
            os.makedirs( d_output )
        except Exception as e:
            sys.stdout.write( "%s[-] error occurred: %s%s\n" % (fg('red'),e,attr(0)) )
            return
    
    s_headers = 'HTTP/1.1 ' + str(r.status_code) + ' ' + r.reason + "\n"
    for k,v in r.headers.items():
        s_headers = s_headers + k + ': ' + v + "\n"

    # print(s_headers)
    content = s_headers + "\n" + r.text
    fp = open( f_output, 'w' )
    fp.write( content )
    fp.close()


# disable "InsecureRequestWarning: Unverified HTTPS request is being made."
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


parser = argparse.ArgumentParser()
parser.add_argument( "-f","--files",help="set file list (required)" )
parser.add_argument( "-g","--no-grab",help="disable file download", action="store_true" )
parser.add_argument( "-o","--hosts",help="set host list (required)" )
# parser.add_argument( "-k","--skip-resolve",help="skip host testing", action="store_true" )
# parser.add_argument( "-r","--redirect",help="follow redirection" )
parser.add_argument( "-s","--no-https",help="disable https", action="store_true" )
parser.add_argument( "-e","--code",help="display only status code separated by comma, default=none" )
parser.add_argument( "-u","--urls",help="set url list (required)" )
parser.add_argument( "-t","--threads",help="threads, default 10" )
parser.parse_args()
args = parser.parse_args()

if args.no_https:
    _https = False
else:
    _https = True

t_hosts = []
if args.hosts:
    if os.path.isfile(args.hosts):
        fp = open( args.hosts, 'r' )
        t_hosts = fp.readlines()
        fp.close()
    else:
        t_hosts.append( args.hosts )
    n_hosts = len(t_hosts)
    sys.stdout.write( '%s[+] %d hosts found: %s%s\n' % (fg('green'),n_hosts,args.urls,attr(0)) )

t_urls = []
if args.urls:
    if os.path.isfile(args.urls):
        fp = open( args.urls, 'r' )
        t_urls = fp.readlines()
        fp.close()
    else:
        t_urls.append( args.urls )
    n_urls = len(t_urls)
    sys.stdout.write( '%s[+] %d urls found: %s%s\n' % (fg('green'),n_urls,args.urls,attr(0)) )

if len(t_hosts) == 0 and len(t_urls) == 0:
    parser.error( 'hosts/urls list missing' )

if args.files:
    t_files = []
    if os.path.isfile(args.files):
        fp = open( args.files, 'r' )
        t_files = fp.readlines()
        fp.close()
    else:
        t_files.append( args.files )
    n_files = len(t_files)
    sys.stdout.write( '%s[+] %d files found: %s%s\n' % (fg('green'),n_files,args.files,attr(0)) )
else:
    parser.error( 'files list missing' )

if args.no_grab:
    _grabfiles = False
else:
    _grabfiles = True

if args.code:
    t_codes = args.code.split(',')
    t_codes_str = ','.join(t_codes)
else:
    t_codes = []
    t_codes_str = 'none'

if args.threads:
    _threads = int(args.threads)
else:
    _threads = 10

t_totest = []
u_max_length = 0
d_output =  os.getcwd()+'/quick-hits'
f_output = d_output + '/' + 'output'
if not os.path.isdir(d_output):
    try:
        os.makedirs( d_output )
    except Exception as e:
        sys.stdout.write( "%s[-] error occurred: %s%s\n" % (fg('red'),e,attr(0)) )
        exit()

sys.stdout.write( '%s[+] options are -> threads:%d, status_code:%s%s\n' % (fg('green'),_threads,t_codes_str,attr(0)) )
sys.stdout.write( '[+] computing url and host and file list...\n' )

# print(t_hosts)
# print(t_urls)
# print(t_files)

for url in t_urls:
    for file in t_files:
        u = url.strip().rstrip('/') + '/' + file.strip().lstrip('/')
        t_totest.append( u )
        l = len(u)
        if l > u_max_length:
            u_max_length = l

for host in t_hosts:
    for file in t_files:
        u = 'https' if _https else 'http'
        u = u + '://' + host.strip() + '/' + file.strip().lstrip('/')
        t_totest.append( u )
        l = len(u)
        if l > u_max_length:
            u_max_length = l

n_totest = len(t_totest)
sys.stdout.write( '%s[+] %d urls created.%s\n' % (fg('green'),n_totest,attr(0)) )
sys.stdout.write( '[+] testing...\n' )


random.shuffle(t_totest)
random.shuffle(t_totest)
# print("\n".join(t_totest))
# exit()

t_exceptions = {}
t_multiproc = {
    'n_current': 0,
    'n_total': n_totest,
    'u_max_length': u_max_length+10,
    'd_output': d_output,
    'f_output': f_output,
    '_grabfiles': _grabfiles
}

pool = Pool( _threads )
pool.map( testURL, t_totest )
pool.close()
pool.join()
