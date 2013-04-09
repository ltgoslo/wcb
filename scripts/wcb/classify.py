#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

import wcb
from wcb import srilm
from wcb.purify import *



class Preprocessor(Purifier):
    def __init__(self, env, templateactions, elementrules):    
        super(Preprocessor, self).__init__(env, templateactions, elementrules)


    def purify(self, tree):
        sections = super(Preprocessor, self).purify(tree)
        #create HTML-style headings, 
        for s in sections:
            if isinstance(s.tree, advtree.Section):
                s.heading = '<h' + str(s.tree.level) + '>' + s.title + '</h' + str(s.tree.level) + '>'
        return sections

    def _node2str(self, n):
        ret = u''
        next = None

        if not n.isVisible():
            return ret
        #dont do anything fancy with text nodes
        if isinstance(n, advtree.Text):
            return n.caption
        #special treatment for Section and Article
        elif isinstance(n, advtree.Article):
            ret = u'<h1>' + n.caption + u'</h1>\n'
            if n.children:
                for c in n.children:
                    ret += self._node2str(c)
        elif isinstance(n, advtree.AdvancedSection):
            ret = u'<h' + str(n.level) + '>'
            if n.children: #ehh emtpy section with no heading...
                ret += self._node2str(n.children[0])
            ret += u'</h' + str(n.level) + '>\n'
            if n.children:
                for c in n.children[1:]:
                    ret += self._node2str(c)
        else:
            ac = node.node_action(self.elementrules, n)
            if DEBUG:
                print "node_action(" + str(n) + ") == " + node.action_name(ac)
           # try:
            if ac == node.PURGE:
                return  u''
            elif ac == node.REPLACE:
                ret =  u'<' + n.tagname + ' />'
            elif ac == node.KEEP:
                if n.__class__.__name__ in node.noclose:
                    return u'<' + n.tagname + ' />\n'
                ret = u'<' + n.tagname + '>'
                txt = u''
                if n.children:
                    for c in n.children:
                        txt += self._node2str(c)
                else:
                    txt += getDisplayText(n)
                #ignore this tag if the children dont produce any text
                txt = txt.strip()
                if len(txt) > 0:
                    ret += txt
                    ret += u'</' + n.tagname + '>'
                else:
                    ret = u''
            else: #node.REMOVE
                if n.children:
                    for c in n.children:
                        ret += self._node2str(c)
                else:
                    #fixme, this never happens
                    ret += getDisplayText(n)

        #add a newline after blocks
        if n.isblocknode and len(ret) > 0:
            ret += u'\n'
        return ret


def classify(sections, clean_client=None, dirty_client=None, clean_port=5000, dirty_port=5001):
    if not clean_client:
        clean_server = srilm.Server(clean_port, wcb.paths["clean lm"])
        clean_client = srilm.Client(clean_server.port, clean_server.order)
    if not dirty_client:
        dirty_server = srilm.Server(dirty_port, wcb.paths["dirty lm"])
        dirty_client = srilm.Client(dirty_server.port, dirty_server.order)
        
    txt = [srilm.explode(s.string) for s in sections]
    clean = []
    dirty = []
    for i,score in enumerate(srilm.classify_bulk(txt, clean_client, dirty_client)):
        if score > 0:
            sections[i].clean = True
            clean.append(sections[i])
        else:
            sections[i].clean = False
            dirty.append(sections[i])
        if sections[i].isEmpty():
            sections[i].clean = False
    return clean,dirty
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', action='store_true')
    parser.add_argument('article')
    args = parser.parse_args()
    

    env = wiki.makewiki(wcb.paths["wikiconf"])
    act = template.create_actions(env, wcb.paths["templaterules"], wcb.paths["templatecache"])
    elementrules = node.read_rules(wcb.paths["noderules"])

    purifier = Preprocessor(env, act, elementrules)

    name = "Test"

    if args.file:
        name = args.article
        markup = util.file2s(args.article)
    else:
        page = env.wiki.get_page(args.article)
        raw = page.rawtext
        name = page.names[-1]
        markup =  act.handle_templates(raw, title=name)

    tree = myParseString.myParseString(title=name, raw=markup, wikidb=env.wiki, 
                                       lang=env.wiki.siteinfo["general"]["lang"], uniq=act.exp.uniquifier)
    advtree.buildAdvancedTree(tree)

    sections = purifier.purify(tree)
    for s in sections:
        print s
