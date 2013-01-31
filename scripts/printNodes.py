#!/usr/bin/env python
# -*- coding: utf-8 -*-


from mwlib import wiki, uparser
from mwlib.parser import nodes
from mwlib import advtree, parser
import argparse, codecs, sys
import util, paths

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='Prints the syntax tree of an article')
    argparser.add_argument('article', nargs='?', default=None, help="name of article")
    argparser.add_argument('--file', '-f', default=None, type=str, help="parse FILE")
    argparser.add_argument('--advanced', '-a', action='store_true', help="Convert to advtree")
    args = argparser.parse_args()

    env = wiki.makewiki(paths.paths["wikiconf"])

    if args.file:
        try:
            f = codecs.open(args.file, encoding='utf-8')
            raw = f.read()
        except Exception as excp:
            sys.exit(unicode(excp).encode("ascii", "backslashreplace") + "\n")
        tree = uparser.parseString(title='Nameless', raw=raw, wikidb=env.wiki, lang=env.wiki.siteinfo["general"]["lang"])
    elif args.article:
        tree = env.wiki.getParsedArticle(args.article)
    else:
        argparser.print_help()
        exit(-1)

    if tree: 
        if args.advanced:
            advtree.buildAdvancedTree(tree)   
        parser.show(sys.stdout, tree, 0)
    else:
        print 'Could not find article "' + args.article + '"'
