#!/usr/bin/env python
# -*- coding: utf-8 -*-


from mwlib import wiki, uparser
from mwlib.parser import nodes
from mwlib import advtree, parser
import argparse, codecs, sys


def printTree(article, indent=""):
    if isinstance(article, nodes.Link):
        text = ": " + article.target
        if isinstance(article, nodes.ImageLink):
            if article.isInline():
                text = " (inline)" + text
            else:
                text = " (block)" + text
    elif isinstance(article, nodes.Section):
        text = ": (level " + str(article.level) + ") " + article.caption.strip()
    elif isinstance(article, nodes.Paragraph):
        text = ""
    else:
        text = ": " + article.caption.strip()
    text = indent + article.__class__.__name__ + text
    print text.encode("ascii", "backslashreplace")
    for child in article:
        printTree(child, "-" + indent)


def printAdvTree(article, ident=""):
    text = ident + article.__class__.__name__ + ":" + article.text
    print text
    for c in article.getAllChildren():
        printAdvTree(c, "-" + ident)
if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='Prints the syntax tree of an article')
    argparser.add_argument('wikiconf')
    argparser.add_argument('article', nargs='?', default=None, help="name of article")
    argparser.add_argument('--file', '-f', default=None, type=str, help="parse FILE")
    argparser.add_argument('--advanced', '-a', action='store_true', help="Convert to advtree")

    args =  argparser.parse_args()
    env = wiki.makewiki(args.wikiconf)

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
        parser.print_help()
        exit(-1)

    if tree: 
        if args.advanced:
            advtree.buildAdvancedTree(tree)   
        parser.show(sys.stdout, tree, 0)
    else:
        print 'Could not find article "' + args.article + '"'
