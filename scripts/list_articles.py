#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

from mwlib import wiki, nshandling
import paths, log, util
import argparse, random, os, codecs


def articles():
    env = wiki.makewiki(paths.paths["wikiconf"])
    rm = nshandling.get_redirect_matcher(env.wiki.siteinfo, env.wiki.nshandler)    


    if os.path.exists(os.path.join(paths.paths["tmp"], 'articles.list')):
        log.logger.info("reading names from " + os.path.join(paths.paths["tmp"], 'articles.list'))
        f = codecs.open(os.path.join(paths.paths["tmp"], 'articles.list'), 'r', 'utf-8')
        names = [l.strip() for l in f]
        f.close()
    else:
        log.logger.info("empty cache, this will take a while")
        names = [k for k in env.wiki.reader.keys() if env.wiki.nshandler.splitname(k)[0] == nshandling.NS_MAIN]
        log.logger.info("writing names to " + os.path.join(paths.paths["tmp"], 'articles.list'))
        f = codecs.open(os.path.join(paths.paths["tmp"], 'articles.list'), 'w', 'utf-8')
        for n in names:
            raw = env.wiki.reader[n]
            if not rm(raw):
                f.write(n + '\n')
        f.close()
    return names
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--number', '-n', type=int)
    parser.add_argument('--randomise', '-r', action='store_true')

    args = parser.parse_args()
    

    names = articles()
        
    if not args.number:
        args.number = len(names)
    
    if args.randomise:
        random.shuffle(names)

    for n in names[:args.number]:
        print n.encode('utf-8')
