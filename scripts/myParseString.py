#!/usr/bin/env python
# -*- coding: utf-8 -*-


from mwlib import nshandling, metabook
from mwlib import expander
from mwlib.log import Log
from mwlib.refine import core, compat
from mwlib.utoken import token as T

import log
import re, collections

#Taken from uparser.py in mwlib
#added one extra argument uniq
#it does not try to expand templates
def myParseString(
    title=None,
    raw=None,
    wikidb=None,
    revision=None,
    lang=None,
    magicwords=None,
    uniq=None,
    orig_raw=None,
):
    """parse article with title from raw mediawiki text"""

    uniquifier = None
    siteinfo = None
    assert title is not None, 'no title given'
    if raw is None:
        page = wikidb.normalize_and_get_page(title, 0)
        if page:
            raw = page.rawtext
        else:
            raw = None
        
        assert raw is not None, "cannot get article %r" % (title,)
    if wikidb:
        te = None
#te = expander.Expander(raw, pagename=title, wikidb=wikidb)
        #input = te.expandTemplates(True)
        input = raw
        uniquifier = uniq

        if hasattr(wikidb, 'get_siteinfo'):
            siteinfo = wikidb.get_siteinfo()

        src = None 
        if hasattr(wikidb, 'getSource'):
            src = wikidb.getSource(title, revision=revision)
            assert not isinstance(src, dict)
            
        if not src:
            src=metabook.source()
            
        if lang is None:
            lang = src.language
        if magicwords is None:
            if siteinfo is not None and 'magicwords' in siteinfo:
                magicwords = siteinfo['magicwords']
            else:
                magicwords = src.get('magicwords')
    else:
        input = raw
        te = None
        
    if siteinfo is None:
        nshandler = nshandling.get_nshandler_for_lang(lang)
    else:
        nshandler = nshandling.nshandler(siteinfo)
    a = compat.parse_txt(input, title=title, wikidb=wikidb, nshandler=nshandler, lang=lang, magicwords=magicwords, uniquifier=uniq, expander=te)
    #fix_start(wikidb, a, title, orig_raw)
    #if log.DEBUG:
    #    rec_deb(a)

    a.caption = title
    if te and te.magic_displaytitle:
        a.caption = te.magic_displaytitle
        
    from mwlib.old_uparser import postprocessors
    for x in postprocessors:
        x(a, title=title, revision=revision, wikidb=wikidb, lang=lang)
    
    return a


def fix_start(wiki, tokens, title, raw=None):
    """
    set Token.start to the correct character offset
    """
    if not raw:
        raw = wiki.nuwiki.get_page(title)
        if not raw:
        #dont do anything drastic if we cant find the original markup
            log.logger.warn("Couldn't find " + str(title))
            return
        raw = raw.rawtext
    
    t_list = []
    iron_tree(tokens, t_list)

    missing = collections.deque([]) #indecies for tokens where we couldnt find the offset
    for i in xrange(0, len(t_list)):
        t = t_list[i]
        t.start_bak = t.start
        t.start = None

        txt = None
        if t.text:
            txt = t.text
        elif t.caption:
            txt = t.caption
        elif t.target:
            txt = t.target
        if txt:
            t.text = txt

        if txt:
     
            matches = [m for m in re.finditer(re.escape(txt), raw)]
            if matches and len(matches) == 1:
                t.start = matches[0].start()
                t.source = raw
                t.len = len(txt)
            else:
                if len(matches) > 1 and len(txt) > 2:
                    missing.append(i) 
    
    
    old_missing = None
    new_missing = missing
    while new_missing != old_missing:
        log.logger.debug(repr(old_missing) + ' ' + repr(new_missing))
        old_missing = new_missing
        new_missing = collections.deque([])
        for i in old_missing:
            t = t_list[i]
            if not t.text:
                continue
            
            start_off = None
            end_off = None
            j = i

            while j > 0:
                j -= 1
                if hasattr(t_list[j], 'start') and t_list[j].start >= 0 and hasattr(t_list[j], 'text'):
                    start_off = t_list[j].start
                    start_off += len(t_list[j].text)
                    break
            j = i
            while j < len(t_list):
                j += 1
                if hasattr(t_list[j], 'start') and t_list[j].start >= 0:
                    end_off = t_list[j].start
                    break
            if end_off > start_off and start_off != None:
                matches = [m for m in re.finditer(re.escape(t.text), raw[start_off:end_off])]
                if matches and len(matches) == 1:
                    t.start = matches[0].start() + start_off
                    t.source = raw
                    log.logger.debug(str(i) + ' ' + repr(t))
                else:
                    new_missing.append(i)
    return
        
                
                

def iron_tree(tree, res):
    """
    think household chore, not metal

    traverses the tree and adds the nodes to the list res
    """
    
    res.append(tree)
    if tree.children:
        for c in tree.children:
            iron_tree(c, res)
                              

def parse_txt(env, raw, **kwargs):
    sub = core.parse_txt(raw, **kwargs)

    article = T(type=T.t_complex_article, start=0, len=0, children=sub)
    compat._change_classes(article)
    rec_deb(article)

    return article


def rec_deb(t): 
    log.logger.debug('repr: ' + repr(t))
    log.logger.debug('rawtagname: ' + str(t.rawtagname))
    if isinstance(t.source, basestring):
        log.logger.debug('source: ' + t.source[:30])
    log.logger.debug('start: ' + str(t.start))
    log.logger.debug('text: ' + str(t.text))
    log.logger.debug('--------------------------')

    if t.children:
        for c in t.children:
            rec_deb(c)
   
