#!/usr/bin/env python
# -*- coding: utf-8 -*-


from mwlib import wiki, parser
import argparse
import codecs
import log, paths, util

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('article')
    args =  parser.parse_args()

    env = wiki.makewiki(paths.paths["wikiconf"])

    args.article = unicode(args.article, 'utf-8')
    

    if env:
        markup = env.wiki.nuwiki.get_page(args.article)
    if markup:
        print markup.rawtext
    else:
        log.logger.error('could not find article in dump (using ' + paths.paths["wikiconf"] + ')')

