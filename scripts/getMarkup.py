#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Lars Jørgen Solberg <supersolberg@gmail.com> 2013
#


from mwlib import wiki, parser

import argparse

import wcb
from wcb import log

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('article')
    args =  parser.parse_args()

    env = wiki.makewiki(wcb.paths["wikiconf"])

    logger = log.getLogger(__name__)

    args.article = unicode(args.article, 'utf-8')


    if env:
        markup = env.wiki.nuwiki.get_page(args.article)
    if markup:
        print markup.rawtext
    else:
        logger.error('could not find article in dump (using ' + wcb.paths["wikiconf"] + ')')
