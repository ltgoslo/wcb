#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Lars Jørgen Solberg <supersolberg@gmail.com> 2013
#
import argparse
import os
import random
import shutil
import multiprocessing
import Queue
import traceback

from mwlib import wiki, nshandling

import wcb
from wcb import classify
from wcb import template
from wcb import node
from wcb import log

from trainingdata import write_section


DEBUG = True
_chunk_size = 10000000 #write ~10M characters in each file

def worker(outdir, inqueue, outqueue, purifier):

    buf = ''
    num = 0

    while True:
        try:
            #get the name of the next article
            name = inqueue.get(True, 1)
            #purify it
            sections = purifier.parse_and_purify(name)
            if not sections:
                continue
            text = ''.join([s.string for s in sections])

            #add the result to our buffers and save them if they are big enough
            buf += text
            if len(buf) >= _chunk_size:
                write_section(outdir, buf, num)
                buf = ''
                num += 1
        except Queue.Empty as excp:
            #save the data we have
            if len(buf) > 0:
                write_section(outdir, buf, num)
            #tell the main process that we're shutting down
            outqueue.put(None)
        except Exception as excp:
            msg = name + u": " + unicode(excp)
            log.logger.error(msg.encode("utf-8", "ignore"))
            if DEBUG:
                log.logger.error(traceback.format_exc())



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Purifies and "explodes" all articles')

    parser.add_argument('outdir')
    parser.add_argument('--processes', '-p', type=int, default=1)
    parser.add_argument('--max', '-m', type=int, help="get no more than this many articles")
    args = parser.parse_args()



    env = wiki.makewiki(wcb.paths["wikiconf"])
    act = template.create_actions(env, wcb.paths["templaterules"], wcb.paths["templatecache"])
    elementrules = node.read_rules(wcb.paths["noderules"])

    purifier = classify.Preprocessor(env, act, elementrules)


    #prepare the output dir
    if os.path.exists(args.outdir):
        shutil.rmtree(args.outdir)
    os.mkdir(args.outdir)

    #add the page names to a queue
    i = 0
    l = []
    names = multiprocessing.Queue()
    for name in env.wiki.reader.keys():
        #make sure that its in the main namespace
        if env.wiki.nshandler.splitname(name)[0] == nshandling.NS_MAIN:
            l.append(name)
            i += 1
        if args.max and i == args.max:
            break
    random.shuffle(l)
    for n in l:
        names.put(n)



    #start worker processes
    ret = multiprocessing.Queue()
    log.logger.info("Starting workers")
    for i in range(0, args.processes):
        p = multiprocessing.Process(target=worker, name=str(i), args=(args.outdir, names, ret, purifier))
        p.daemon = True
        p.start()

    #collect the results
    curr_pcs = args.processes
    while curr_pcs > 0:
        r = ret.get()
        if not r:
            curr_pcs -= 1


    log.logger.info("Done")
