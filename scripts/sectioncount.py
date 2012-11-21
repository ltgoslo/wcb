#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

import argparse, sys, time, multiprocessing, copy, logging, traceback, Queue
import paths, template, purify, node, myParseString, util
from mwlib import wiki, nshandling, advtree
from mwlib.templ import evaluate


DEBUG = False

def worker(q, names, templr, noder):
    env = templr.env
    purifier = purify.Purifier(env, templr, noder)
    rm = nshandling.get_redirect_matcher(env.wiki.siteinfo, env.wiki.nshandler)


    articles = 0
    skipped = 0
    
    while True:
        try:
            name = names.get(True, 1)
            #only examine pages in the main namespace
            if env.wiki.nshandler.splitname(name)[0] == nshandling.NS_MAIN:
                raw = env.wiki.reader[name]
                #ignore redirects
                if not rm(raw):
                    raw = templr.handle_templates(raw, title=name)
                    tree = myParseString.myParseString(title=name, raw=raw, wikidb=env.wiki, 
                                                       lang=env.wiki.siteinfo["general"]["lang"], 
                                                       uniq=templr.exp.uniquifier)
                    advtree.buildAdvancedTree(tree)
                    #for all sections in each article
                    for s in purifier.purify(tree):
                        q.put(Record(s.heading, len(s.content)))
                    articles += 1
                else:
                    #for skipping a redirect
                    skipped += 1
            else:
                #for skipping a page not in NS_MAIN
                skipped += 1
        except Queue.Empty as excp:
            logger.info("examined " + str(articles) + " articles, skipped " + str(skipped))                
            q.put(None)
            return
        except Exception as excp:
            msg = name + u": " + unicode(excp)
            logger.error(msg.encode("utf-8", "ignore"))
            if DEBUG:
                logger.error(traceback.format_exc())


class Record:
    name = None
    count = 1
    length = 0
    
    def __init__(self, name, length):
        name = name.replace('_', '-')
        self.name = name.replace('\n', ' ')
        self.length = length

    def __repr__(self):
        return 'Record(' + self.name.encode("utf-8", "ignore") + ', ' + str(self.length) + ')'
        
    
def printres(results):
    l = results.values()

    logger.info(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + ": Sorting " + str(len(l)) + " headings")
    l.sort(key=lambda x: x.count, reverse=True)
    
    print "name_count_avg length"
    for h in l:
        row = h.name.encode("utf-8", "ignore") + "_"
        row += str(h.count) + "_"
        row += str(h.length / h.count)
        print row

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--processes', '-p', type=int, default=1)
    parser.add_argument('--max', '-m', type=int, help="dont process more than this many pages")
    args = parser.parse_args()
    

    env = wiki.makewiki(paths.paths["wikiconf"])
    templr = template.create_actions(env, paths.paths["templaterules"], paths.paths["templatecache"])
    noder = node.read_rules(paths.paths["noderules"])

    logger = multiprocessing.log_to_stderr()
    logger.setLevel(logging.INFO)
    

    logger.info("Listing articles")
    names = multiprocessing.Queue()
    
    if not args.max:
        args.max = len(env.wiki.reader.keys())

    i = 0
    for n in env.wiki.reader.keys():
        if i < args.max:
            names.put(n)
            i += 1
        else:
            break

    #deepycopy(tempr) doesent work...
    templr.env = None
    templr.exp = None
    
    #start the worker processes
    q = multiprocessing.Queue()
    logger.info(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + ": Starting workers")
    for i in range(0, args.processes):
        newtemplr = copy.deepcopy(templr)
        newtemplr.env =  wiki.makewiki(paths.paths["wikiconf"])
        newtemplr.exp = evaluate.Expander('', wikidb=newtemplr.env.wiki)

        p = multiprocessing.Process(target=worker, args=(q, names, newtemplr, 
                                                         copy.deepcopy(noder)))
        p.daemon = True
        p.start()


    #collect the results
    count = 0
    curr_pcs = args.processes
    res = {}
    while curr_pcs > 0:
        r = q.get()
        if not r:
            curr_pcs -= 1
        else:
            if r.name in res:
                res[r.name].count += 1
                res[r.name].length += r.length
            else:
                res[r.name] = r
 
    logger.info(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + ": All workers are done")

    printres(res)
    logger.info(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + ": Done")
