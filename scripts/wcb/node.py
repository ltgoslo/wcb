#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

import argparse, csv, sys, codecs
from mwlib import advtree
import log


logger = log.getLogger(__name__)

KEEP = 0
REMOVE = 1
PURGE = 2
REPLACE = 3

_code_map = {"keep": KEEP, "remove": REMOVE, "purge": PURGE, "replace": REPLACE}
_name_map = ("keep", "remove", "purge", "replace")

#elements that never have a closing tag
noclose = {"BreakingReturn": True, "HorizontalRule": True}

#not strictly necessary as lookups are done on tagnames in a pinch, but it
#removes a lot of noise from advtree.fixTagNodes()
class Hieroglyphs(advtree.TagNode, advtree.AdvancedNode):
    _tag = "hiero"
    isblocknode = True
    tagname = "hiero"
advtree._tagNodeMap[Hieroglyphs._tag] = Hieroglyphs

class Poem(advtree.TagNode, advtree.AdvancedNode):
    _tag = "poem"
    isblocknode = True
    tagname = "poem"
advtree._tagNodeMap[Poem._tag] = Poem


class Rules:
    def __init__(self):
        self.actions = dict()
        self.start = dict()
        self.end = dict()
        self.seperator = dict()
        self.parameters = dict()

    def node_start(self, node):
        return self._get_prop(node, self.start, '')

    def node_action(self, node):
        #imagelinks are special cases, they are purged if they are blocks
        if node.__class__ == advtree.ImageLink:
            if node.isblocknode:
                return PURGE

        ret =  self._get_prop(node, self.actions, KEEP)
        return ret
    
    def node_end(self, node):
        return self._get_prop(node, self.end, '')

    def node_params(self, node):
        sep = self._get_prop(node, self.seperator, default = '')
        params = self._get_prop(node, self.parameters, default = [])
        if not params:
            return ''
        attrs = node.getAttributes()
        values = []
        for p in params:
           try:
               if p in attrs:
                   values.append(str(attrs[p]))
               else:
                   values.append(str(getattr(node, p)))
           except AttributeError:
               pass
        #log.logger.info(sep + sep.join(values))
        return sep + sep.join(values)

    def _get_prop(self, node, prop, default=None):
        #log.logger.debug(repr(node) + ' ' + prop.__class__.__name__)
        try:
            if node.__class__.__name__.strip().lower() in prop:
                r = prop[node.__class__.__name__.strip().lower()]
            elif node.rawtagname and node.rawtagname in prop:
                r = prop[node.rawtagname]
            else:
                r = prop[node.caption]
        except KeyError:
            logger.error('Unknown property: ' + repr(prop) + '(' + repr(node) + ')')        
            r = default
        #log.logger.debug(repr(r))
        return r

    def __str__(self):
        return  'Actions: ' + repr(self.actions) + '\n\n' + 'Start: ' + repr(self.start) + '\n\n' + \
            'End: ' + repr(self.end) + '\n\n' + 'Parameters: ' + repr(self.parameters)

def action_code(name):
    return _code_map[name.strip().lower()]

def action_name(code):
    return  _name_map[code]

#this is here for historic reasons
def node_action(rules, node):
    return rules.node_action(node)


def read_rules(rules_file):
    """
    Reads a cvs file with rules for markup elements, returs a dict with the 
    node names as keys.
    """
    rules = Rules()
    #always remove 'Node'
    rules.actions['node'] = REMOVE
    rules.actions['text'] = REMOVE

    f = open(rules_file, 'rb')
    reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
    reader.next() #skip headings
    for r in reader:
        #skip emtpy rules
        if len(r) < 2 or "" == r[0] or "" == r[1]:
            continue
        name = r[0].strip().lower()
        rules.actions[name] = action_code(r[1])
        if len(r) > 2 and r[2]:
            rules.start[name] = r[2].strip().decode('utf-8')
        else:
            if rules.actions[name] == KEEP:
                rules.start[name] = '<' + r[0] + '>'
                rules.end[name] = '</' + r[0] + '>'
            elif rules.actions[name] == REPLACE:
                rules.start[name] = '<' + r[0] + ' />'
                rules.end[name] = ''
            elif rules.actions[name] == REMOVE:
                rules.start[name] = ''
                rules.end[name] = ''

        if len(r) > 3 and r[3]:
            rules.end[name] = r[3].strip().decode('utf-8')
        if len(r) > 4 and r[4]:
            rules.seperator[name] = r[4].strip().decode('utf-8')
        else:
            rules.seperator[name] = ''
        i = 5
        params = []
        while i < len(r):
            if r[i]:
                params.append(r[i])
            i += 1
        rules.parameters[name] = params
            
    f.close()
    return rules


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Rules for markup elements')
    parser.add_argument('rulesfile')
    args =  parser.parse_args()

    
    r = read_rules(args.rulesfile)
    print r
