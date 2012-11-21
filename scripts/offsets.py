#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

import purify, util, log, paths, template, node
from mwlib import wiki, advtree
import argparse

def source(tree):
    ret = tree.__class__.__name__ + ' '
    if tree.start:
        ret += str(tree.start)
        if tree.len:
            ret += ':' + str(tree.len)
    else:
        ret += '?:?'
    ret += ' | ' + purify.getDisplayText(tree) + '\n'
    if tree.children:
        for c in tree.children:
            ret += source(c)
    return ret

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('article')
    args = parser.parse_args()
    
    env = wiki.makewiki(paths.paths["wikiconf"])
    act = template.create_actions(env, paths.paths["templaterules"], paths.paths["templatecache"])
    elementrules = node.read_rules(paths.paths["noderules"])

    purifier = purify.Purifier(env, act, elementrules)
    purifier.keep_empty = True
    purifier.extra_newlines = True

    sections = purifier.parse_and_purify(args.article)
    #sections = purifier.parse_and_purify('Algorithm')
    for s in sections:
        print '#####'
        print source(s.tree)
        #print purify.subtrees('A partial formalization of the concept began with attempts to solve the ', s)

