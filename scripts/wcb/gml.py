#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Lars Jørgen Solberg <supersolberg@gmail.com> 2013
#

import wcb
from wcb import log
from wcb import purify
from wcb import template
from wcb import classify
from wcb import node
from wcb import senseg

import argparse
import re

from mwlib import wiki, advtree

re_empty = re.compile(ur'⌊(.)[ \t\r\f\v]*\1⌋', re.U)
re_par = re.compile(ur'___NL___$', re.U)

logger = log.getLogger(__name__)


def arrow(text):
    text = text.group(1)
    return text.replace('\n', ' ')


re_template = None
arrows = None
def postprocess(text):
    global re_template
    global arrows
    if not re_template:
        re_template = re.compile(re.escape(template.delimiter_start) + r'.+?' +
                                 re.escape(template.delimiter) + r'.+?' +
                                 re.escape(template.delimiter_end),
                                 re.U|re.S)
        arrows = re.compile(r'<___(.*?)___>', re.U|re.S)
        re_fix_enum = re.compile(r'^(\d+\.)[ \t]*\n', re.U|re.M)


    res = text
    n = True
    while n:
        res, n = arrows.subn(arrow, res)

    n = True
    while n:
        res,n = re_empty.subn('', res)


    return re_template.sub(rewrite_template, res)

delimiter = re.compile(re.escape(template.delimiter), re.U|re.S)
def rewrite_template(template_text):
    parts = template_text.group(0)
    parts = parts[len(template.delimiter_start):-len(template.delimiter_start)]
    parts = delimiter.split(parts)
    res = u'⌊λ' + parts[1]
    params = u'¦'.join(parts[2:])
    if params:
        res += u'¦' + params
    res += u'¦' + parts[0] + u'λ⌋'

    logger.debug(template_text.group(0) + ' ==> ' + res)
    return res

fix_templates = postprocess

re_magicchars = re.compile(u'([⌊⌋¦])', re.U)
def escape(text):
    return re_magicchars.sub(u'⌊\1⌋', text)


def filter_sections(sections):
    sprint = 0
    for s in reversed(sections):
        if s.isEmpty():
            s.clean = False
            s.sprint = False
        else:
            s.sprint = s.clean

        if s.clean:
            sprint = s.level
        elif s.level < sprint:
            s.sprint = True
            sprint = s.level

        if isinstance(s.tree, advtree.Article):
            if sprint:
                s.sprint = True
            sprint = 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('article')
    parser.add_argument('--senseg', '-s', action='store_true')
    parser.add_argument('--clean-port', default='5000')
    parser.add_argument('--dirty-port', default='5001')
    args = parser.parse_args()

    env = wiki.makewiki(wcb.paths["wikiconf"])
    act = template.create_actions(env, wcb.paths["templaterules"], wcb.paths["templatecache"])

    #classifiy sections
    preprocessor = classify.Preprocessor(env, act, node.read_rules(wcb.paths["noderules"]))
    sections = preprocessor.parse_and_purify(args.article, follow_redirects=True)
    clean,dirty = classify.classify(sections, clean_port=args.clean_port, dirty_port=args.dirty_port)
    filter_sections(sections)

    logger.debug('clean sections: ' + ', '.join([s.title for s in clean]))
    logger.debug('dirty sections: ' + ', '.join([s.title for s in dirty]))

    #gml
    gml_purifier = purify.Purifier(env, act, node.read_rules(wcb.paths["noderules_gml"]))


    if args.senseg:
    #senseg
        senseg_purifier = purify.Purifier(env, act, node.read_rules(wcb.paths["noderules_senseg"]))
        senseg_purifier.extra_newlines = True

        for s in senseg.senseg_sections(senseg_purifier, gml_purifier, clean, escape):
            gml_s = fix_templates(s).encode('utf-8')
            if gml_s and gml_s.strip():
                for line in gml_s.splitlines():
                    line = re_par.sub('\n', line)
                    print line.replace('___NL___', '') #only insert line breaks at the end of a sentence

    else:
        for s in clean:
            print fix_templates(gml_purifier.node2str(s.tree)).encode('utf-8').replace('___NL___', '')
