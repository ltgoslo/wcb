#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Lars Jørgen Solberg <supersolberg@gmail.com> 2013
#


from mwlib import wiki, uparser
from mwlib import advtree, parser

import argparse
import codecs
import sys

import wcb

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='Prints the syntax tree of an article')
    argparser.add_argument('--advanced', '-a', action='store_true', help="Convert to advtree")
    argparser.add_argument('article')
    argparser.add_argument('--file', '-f', action='store_true', help="read article from FILE")
    args = argparser.parse_args()

    env = wiki.makewiki(wcb.paths["wikiconf"])

    if args.file:
        try:
            f = codecs.open(args.article, encoding='utf-8')
            raw = f.read()
        except ValueError as excp:
            sys.exit(unicode(excp).encode("ascii", "backslashreplace") + "\n")
        tree = uparser.parseString(title='Nameless', raw=raw, wikidb=env.wiki, lang=env.wiki.siteinfo["general"]["lang"])
    else:
        tree = env.wiki.getParsedArticle(args.article)

    if tree:
        if args.advanced:
            advtree.buildAdvancedTree(tree)
        parser.show(sys.stdout, tree, 0)
    else:
        print 'Could not find article "' + args.article + '"'
