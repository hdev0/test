#!/usr/bin/python3.5

# I don't believe in license.
# You can do whatever you want with this program.

def doWork():
    while True:
        host = q.get()
        resolve( host )
        q.task_done()


def resolve( host ):
    if t_multiproc['n_current']%5000 == 0:
        save()
    
    sys.stdout.write( 'progress: %d/%d\r' %  (t_multiproc['n_current'],t_multiproc['n_total']) )
    t_multiproc['n_current'] = t_multiproc['n_current'] + 1

    try:
        ip = socket.gethostbyname( host )
        t_alive[host] = ip
        # print(ip)
    except Exception as e:
        t_dead.append( host )
        # sys.stdout.write( "%s[-] error occurred: %s (%s)%s\n" % (fg('red'),e,host,attr(0)) )


def save(alts):
    if alts:
        fp = open( 'h_alts', 'w' )
        for h in t_alts:
            if len(h):
                fp.write( "%s\n" % h )
        fp.close()

    fp = open( 'h_alive', 'w' )
    for h in sorted(t_alive.keys()):
        if len(h):
            fp.write( "%s:%s\n" % (h,t_alive[h]) )
    fp.close()

    fp = open( 'h_dead', 'w' )
    for h in t_dead:
        if len(h):
            fp.write( "%s\n" % h )
    fp.close()



def occalts( t_array ):
    t_occ = []
    l = len(t_array)
    # print(l)

    for i in range(0,l):
        for j in range(0,l):
            if i == j:
                continue
            maxmax = t_array[i]
            for nn in range(0,maxmax+1):
                t_array2 = t_array.copy()
                t_array2[i] = nn
                max = t_array[j]
                print(max)
                for n in range(0,max+1):
                    for pad in range(1,2):
                        print(pad)
                        t_array3 = t_array2.copy()
                        t_array3[j] = str(n).rjust(pad,'0')
                        print(t_array3)
                        # print(t_array2)
                        t_occ.append( t_array3 )
        # break
    print(t_occ)
    print(len(t_occ))
    return t_occ


def generateAlts( host, current ):
    index = 0
    matches = re.compile( '[0-9]+' ).finditer( host )
    temp = list(matches)
    n_matches = len(temp)
    matches = iter(temp)
    # print("\nhost %s" % host)
    # print("CURRENT %d" % current)
    # print("n_matches %d" % n_matches)

    t_alts.append( host )

    for m in matches:
        # print("INDEX %d" % index)
        # print(m.group())
        if index > current:
            # print("index != current NO SKIP")
            n_start = 0
            n_end = int( int(m.group()) * N_MULTI )
            if n_end < N_MIN:
                n_end = N_MIN
            # n_end = int(m.group())
            n_end = n_end
            # print(n_end)

            p_start = m.start()
            p_end = m.end()
            p_len = p_end - p_start
            s_prefix = host[0:p_start]
            s_suffix = host[p_end:]

            for i in range(n_start,n_end):
                new_h = s_prefix + str(i) + s_suffix
                generateAlts( new_h, index )
        # else:
            # if not host in t_alts:
            # print("index = current SKIP")

        index = index + 1


def getAlts( host ):
    sys.stdout.write( 'progress: %d/%d\r' %  (t_multiproc['n_current'],t_multiproc['n_total']) )
    t_multiproc['n_current'] = t_multiproc['n_current'] + 1

    # for host in t_hosts:
    generateAlts( host, -1 )
        # print(sorted(t_alts))
    # print( len(t_alts) )
        # exit()

import os
import sys
import re
import socket
import argparse
from functools import partial
from colored import fg, bg, attr
from threading import Thread
from queue import Queue
from multiprocessing.dummy import Pool

N_MIN = 20
N_MULTI = 1.2

parser = argparse.ArgumentParser()
parser.add_argument( "-o","--host",help="set hosts file list" )
parser.add_argument( "-t","--threads",help="threads, default 10" )
parser.parse_args()
args = parser.parse_args()

if args.threads:
    _threads = int(args.threads)
else:
    _threads = 10

t_hosts = []
if args.host:
    if os.path.isfile(args.host):
        fp = open( args.host, 'r' )
        t_hosts = fp.read().strip().split("\n")
        fp.close()

n_host = len(t_hosts)

if not n_host:
    parser.error( 'hosts list missing' )

sys.stdout.write( '%s[+] %d hosts loaded: %s%s\n' % (fg('green'),n_host,args.host,attr(0)) )
sys.stdout.write( '[+] generating alts...\n' )



t_alts = []
t_multiproc = {
    'n_current': 0,
    'n_total': n_host
}

pool = Pool( 20 )
pool.map( getAlts, t_hosts )
pool.close()
pool.join()

# getAlts( t_hosts )
n_alt = len(t_alts)
save(True)
sys.stdout.write( '%s[+] %d alts generated%s\n' % (fg('green'),n_alt,attr(0)) )
sys.stdout.write( '[+] resolving...\n' )



t_alive = {}
t_dead = []
t_multiproc = {
    'n_current': 0,
    'n_total': n_alt
}

q = Queue( _threads*2 )

for i in range(_threads):
    t = Thread( target=doWork )
    t.daemon = True
    t.start()

try:
    for host in t_alts:
        q.put( host )
    q.join()
except KeyboardInterrupt:
    sys.exit(1)


# print( t_alive)
# print( t_dead)
sys.stdout.write( '%s[+] %d hosts alive, %d dead hosts%s\n' % (fg('green'),len(t_alive),len(t_dead),attr(0)) )
save(False)


exit()

