#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars Jrgen Solberg <larsso@conan.megalol.be> 2012
#
from mwlib import wiki, nshandling, expander, uniq
from mwlib.templ import parser, nodes, evaluate
from mwlib.templ import marks, evaluate, magics

from myTemplate import MyTemplate, mark_argument  # a replacement for mwlib.templ.nodes.Template
import myUniquifier, myMagic, paths, log

import csv, sys, re, unicodedata, os, copy
from collections import deque, Sequence

EXPAND = 0
REMOVE = 1
KEEP = 2

#delimiter = unicodedata.lookup("REPLACEMENT CHARACTER")
delimiter = u"+"
delimiter_start = u"{("
delimiter_end = u")}"

_action_map = {"expand": 0, "remove": 1, "keep": 2}

logger = log.getLogger(__name__)

def action_code(action):
    """
    Returns EXPAND, REMOVE or KEEP
    """
    
    if isinstance(action, int):
        return action
    else:
        return _action_map[action.strip().lower()]

        


#template action
class TemplateActions:

    def __init__(self, env):
        self.env = env
        self.exp = evaluate.Expander('', wikidb=env.wiki)
        self.exp.uniquifier = myUniquifier.MyUniquifier()

        self.default_action = EXPAND
        self.cc_mode = False # if true, dont follow redirects, first letter is case sensetive

        self.removes = {}
        self.expands = {}
        self.keeps = {}

        
        

    def __str__(self):
        s = ""
        for t in self.removes.keys():
            s = s + "{{" + t.encode("utf-8", "ignore") + "}} -> remove\n"
        for t in self.keeps.keys():
            s = s + "{{" + t.encode("utf-8", "ignore") + "}} -> keep\n"
        for t in self.expands.keys():
            s = s + "{{" + t.encode("utf-8", "ignore") + "}} -> expand\n"

        return s

    def get_action(self, name):
        """
        Returns the approrpiate action for {{name}}
        """
        

        #try to follow redirects and get the right namespace
        name = self.env.wiki.nshandler.get_fqname(name, nshandling.NS_TEMPLATE)
        #this occasionaly raise a typeerror...
        try:
            page = self.env.wiki.get_page(name)
        except TypeError as excp:
            sys.stderr.write("got TypeError: " + str(excp) + " when looking for " + name.encode("utf-8", "ignore") + 
                             ", name is a " + name.__class__.__name__ + "\n")
            page = None
                             
        if page:
            name = page.names[-1]
        else:
            #remove templates we cant find
            return REMOVE
        

        if name in self.removes:
            return REMOVE
        elif name in self.keeps:
            return KEEP
        elif name in self.expands:
            return EXPAND
        else:
            ns = self.env.wiki.nshandler.splitname(name)[0]
            #dont include pages from the main namespace
            if ns == nshandling.NS_MAIN:
                return REMOVE
            else:
                return self.default_action

        
    def set_action(self, name, action):
        """
        Sets the action for {{name}}
        """

        if self.cc_mode and not 'Template:' in name:
            name = 'Template:' + name
        else:

        #try to follow redirects and get the right namespace
            name = self.env.wiki.nshandler.get_fqname(name, nshandling.NS_TEMPLATE)
            page = self.env.wiki.get_page(name)
            if page:
                name = page.names[-1]
            else:
            #get_action returns remove for these
                return

        #if a template occurs more than once, the first action takes
        #precedence
        if name in self.keeps or name in self.removes or name in self.expands:
            return

        ac = action_code(action)
        if ac == KEEP:
            self.keeps[name] = True
        elif ac == REMOVE:
            self.removes[name] = True
        elif ac == EXPAND:
            self.expands[name] = True


    def _update_expander(self, pagename):
        self.exp.resolver = magics.MagicResolver(pagename=pagename)
        self.exp.resolver.siteinfo = self.env.wiki.siteinfo
        self.exp.resolver.nshandler = self.env.wiki.nshandler 
        self.exp.resolver.wikidb = self.env.wiki
        #self.exp.resolver.local_values = local_values
        #self.exp.resolver.source = source



    def handle_templates(self, raw, title="Unnamed"):
        """
        Returns a copy of raw where templates are either expanded, removed or kept
        """
        self._update_expander(title)

        parsed = parser.parse(raw, included=False, replace_tags=self.exp.uniquifier.replace_tags)
        m = []
        for i in parsed:
            logger.debug(repr(i))
            if isinstance(i, nodes.Template):
                #t = MyTemplate(self, i)
                t = i
                res = []
                t.flatten(self.exp, expander.get_template_args(t, self.exp), res)

                m.extend(res)

            else:
                m.append(i)
        ret = []
        self._handle_marks(m, ret)
        logger.debug('cache size: ' + str(len(self.exp.parsedTemplateCache)))
        
        return  self._expand(ret)


    def _expand(self, parsed):
        markup = u''

        for token in parsed:
            if isinstance(token, MyTemplate):
                args = expander.get_template_args(token, self.exp)
                m = ["\n"]
                token.flatten(self.exp, args, m)
                m[0] = u''
                m = u''.join(m)
                markup += m
            elif isinstance(token, basestring):
                markup += token
            elif isinstance(token, Sequence):
                for e in token:
                    markup += self._expand(e)
        return markup


    def _handle_marks(self, m, res):
        i = 0

        while i < len(m):
            logger.debug(repr(m[i]))
            if isinstance(m[i], marks.mark_start):
                a = self.get_action(eval(m[i].msg))
                if a == EXPAND:
                    res.append(m[i])
                    i += 1
                elif a == REMOVE:
                    i += self._remove(m[i:], res)
                else: #KEEP
                    i += self._keep(m[i:], res)
            elif not isinstance(m[i], mark_argument):
                res.append(m[i])
                i += 1
            else:
                i += 1

        evaluate._insert_implicit_newlines(res)


    def _remove(self, m, res):
        if len(m) == 0:
            return 0
        assert isinstance(m[0], marks.mark_start)
        i = 0
        name = eval(m[0].msg)
        for n in m:
            logger.debug(repr(n))
            if isinstance(n, marks.mark_end) and eval(n.msg) == name:
                #self._handle_marks(m[i + 1:], res)
                return i + 1
            i += 1
                
            
    def _keep(self, m, res):
        if len(m) == 0:
            return 0
        assert isinstance(m[0], marks.mark_start)
        #use the canonical template name//
        name = self.env.wiki.nshandler.get_fqname(eval(m[0].msg), nshandling.NS_TEMPLATE)
        name = self.env.wiki.get_page(name).names[-1]
        name = self.env.wiki.nshandler.splitname(name)[1]
        res.append(delimiter_start + name)

        #the mark_end will have the same msg as the mark_start
        name = eval(m[0].msg)

        args = []
        i = 1

        newline_start = False

        for n in m[1:]: #skip mark_start
            #get the arguments
            if isinstance(n, mark_argument):
                args.append(eval(n.msg))
            else:
                if not isinstance(n, marks.mark):
                    if n[:2] == '{|':
                        newline_start = True
                break
            i += 1

        offset = i

      
        if len(args) > 0:
            res.append(delimiter)
        if newline_start:
            res.append(u'\n')

        i = 0
        for n in m:
            logger.debug(repr(n))
            #were done with this template, add the arguments and call _handle_marks
            if isinstance(n, marks.mark_end) and eval(n.msg) == name:
                res.append(n)
                res.append(delimiter)
                res.extend(delimiter.join(args))
                res.append(delimiter_end)
                return i + 1
            # weed out argument marks
            if not isinstance(n, mark_argument):
                res.append(n)
            i += 1

def expand_rules(env, rules):
    """
    Constructs a TemplateActions from a list of template names/patterns
    """    
    act = TemplateActions(env)
    all = []
    for n in env.wiki.reader.iterkeys():
        [ns, name, fullname] = env.wiki.nshandler.splitname(n)
        if ns == nshandling.NS_TEMPLATE:
            page = env.wiki.get_page("Template:" + name)
            if page:
                name = page.names[-1][9:]
                all.append(name)
            #else this is a broken redirect, not much to do about it
                
    for r in rules:
        #regexp
        if r[0][0] == "/" and r[0][-1] == "/":
            n = r[0][1:-1]
            for t in all:
                if re.search(n, t, re.U | re.I):
                    act.set_action(t, r[1])
        else:
            page = env.wiki.get_page("Template:" + r[0])
            if page:
                act.set_action(page.names[-1], r[1])
            else:
                act.set_action('Template:' + r[0], r[1])
                logger.warn("Could not find {{" +  r[0].encode("utf-8", "ignore") + "}}")
    return act

def expand_cached_rules(env, rules):
    """
    Constructs a TemplateActions object from a list of _only_ template names.
    """
    act = TemplateActions(env)
    for name, action in rules:
        ac = action_code(action)
        if  ac == KEEP:
            act.keeps[name] = True
        elif ac == REMOVE:
            act.removes[name] = True
        elif ac == EXPAND:
            act.expands[name] = True
        
    return act

#uses cached rules if possible, creates cache if not                       
def create_actions(env, rules, cache):
    if os.path.exists(cache) and os.stat(cache).st_mtime > os.stat(rules).st_mtime:
        logger.info("reading cached rules from: " + cache)
        act = expand_cached_rules(env, read_rules(cache))
    else:
        logger.info("reading rules from: " + rules)
        act = expand_rules(env, read_rules(rules))
        logger.info("creating cache-file: " + cache)
        write_rules(cache, act)
    
    return act


def read_rules(rules_file):
    """
    Reads a cvs file with template rules and returns them as
    a list in the form [(pattern, action), ...]
    """
    rows = []
    f = open(rules_file, 'rb')
    reader = csv.reader(f, delimiter='_', quoting=csv.QUOTE_NONE)
    reader.next() #skip headings
    for r in reader:
        #skip emtpy rules
        if "" == r[0] or "" == r[1]:
            continue
        rows.append((r[0], r[1]))
    f.close()
    return rows

def write_rules(rules_file, actions):
    """
    Saves rules to a file that can be read by read_rules()
    """
    f = open(rules_file, 'w')
    f.write("template_action_comment\n")
    for t in actions.removes.keys():
            f.write(t.encode("utf-8", "ignore") + "_remove\n")
    for t in actions.keeps.keys():
            f.write(t.encode("utf-8", "ignore") + "_keep\n")
    for t in actions.expands.keys():
            f.write(t.encode("utf-8", "ignore") + "_expand\n")
    f.close()

if __name__ == "__main__":
    env = wiki.makewiki(paths.paths["wikiconf"])
    rules = create_actions(env, paths.paths["templaterules"], paths.paths["templatecache"])

    markup = env.wiki.nuwiki.get_page('Albert Einstein').rawtext

    print rules.handle_templates('\n\n{{flag|China}}\n\n', 'Demo')
    

    #print "{{Harvard citation text}} -> ",
    #print rules.get_action("Harvard citation text")
    #print "{{harvtxt}} -> ",
    #print rules.get_action("harvtxt")
    #print "{{Harvtxt}} -> ",
    #print rules.get_action("Harvtxt")
    #print "{{doesnotexist}} -> ",
    #print rules.get_action("doesnotexist")
    #print "{{End}} -> ",
    #print rules.get_action("End")
    #print "{{IPA}} -> ",
    #print rules.get_action("IPA")
    #print "{{IPA notice}} -> ",
    #print rules.get_action("IPA notice")
    
    
