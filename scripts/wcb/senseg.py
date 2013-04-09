#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Lars Jørgen Solberg <supersolberg@gmail.com> 2013
#

from wcb import util
from wcb import log
from wcb import purify
from wcb import template
from wcb import classify
from wcb import node

import argparse
import collections
import re

from mwlib import wiki

re_fix_enum = re.compile(r'^((\d+\.)|(\w\.))[ \t]*\n', re.U|re.M)
re_fix_period = re.compile(r'\n\s*(\.+)\s*\n', re.U|re.M)

def senseg(string):
    out, err = util.cmd('tokenizer -L en-u8 -W -P -S -n', string)
    if len(err) > 0:
        log.logger.error(err)
    out = out.replace('<EOS />', ' ')

    # fix false positives like "1.\nFoo\n2.\Bar
    out = re_fix_enum.sub(r'\1 ', out)
    # fix lone periods
    #out = re_fix_period.sub(r'\n\1 ', out)

    return out



def senseg_sections(senseg_purifier, ml_purifier, sections, escape_funtion=lambda x:x):
    res = collections.deque([])
    for s in sections:
        text = senseg(senseg_purifier.node2str(s.tree))
        res.extend(purify.markup_sentences(ml_purifier, s, re.split('\n+', text), escape_funtion))
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('article')
    args = parser.parse_args()


    env = wiki.makewiki(wcb.paths["wikiconf"])
    act = template.create_actions(env, wcb.paths["templaterules"], wcb.paths["templatecache"])

    #classifiy sections
    preprocessor = classify.Preprocessor(env, act, node.read_rules(wcb.paths["noderules"]))
    sections = preprocessor.parse_and_purify(args.article)
    clean,dirty = classify.classify(sections)

    log.logger.debug('clean sections: ' + ', '.join([s.title for s in clean]))
    log.logger.debug('dirty sections: ' + ', '.join([s.title for s in dirty]))

    #senseg
    senseg_purifier = purify.Purifier(env, act, node.read_rules(wcb.paths["noderules_senseg"]))
    senseg_purifier.extra_newlines = True

    #gml
    gml_purifier = purify.Purifier(env, act, node.read_rules(wcb.paths["noderules_gml"]))

    for s in senseg_sections(senseg_purifier, gml_purifier, clean):
        print s
