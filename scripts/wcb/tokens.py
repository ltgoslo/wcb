#!/usr/bin/env python
# -*- coding: utf-8 -*-


from mwlib import wiki, parser
from mwlib.templ.scanner import symbols, tokenize

import argparse
import codecs


parser = argparse.ArgumentParser(description='Prints the tokens generated in the template expansion phase')
parser.add_argument('wikiconf')
parser.add_argument('article')
args =  parser.parse_args()

env = wiki.makewiki(args.wikiconf)

try:
    args.article =  unicode(args.article)
except UnicodeError as ex:
    print "warning: ",
    print ex
    args.article = unicode(args.article,errors="ignore")

if env:
    markup = env.wiki.nuwiki.get_page(args.article)
if markup:
    for t in tokenize(markup.rawtext, included=False):
        print t
else:
    print 'Could not find article "' + args.article + '"'

