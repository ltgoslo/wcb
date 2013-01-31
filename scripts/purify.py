#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

from mwlib import wiki, expander, uparser, advtree, utoken
from mwlib.templ import parser, nodes
from mwlib import parser, nshandling

import sys, locale, argparse, re, collections, string

import template, node, myParseString, myUniquifier, paths
import util, log


DEBUG = False


amap = {advtree.Text:"caption",
        advtree.Link:"target",
        advtree.URL:"caption",
        advtree.Math:"caption",
        #advtree.ImageLink:"caption",
        advtree.ArticleLink:"target",
        advtree.NamespaceLink:"target",
        advtree.Article:"caption",}


#modified version of mwlib.advtree.getAllDisplayText
def getDisplayText(n):
    "Return the text that is intended for display"
    access = amap.get(n.__class__, "")
    if access:
        return unicode(getattr(n, access))
    else:
        return u''


class Token:
    def __init__(self, node, start):
        self.node = node
        self.start = start
        
    def __repr__(self):
        return 'Token(' + self.node.__class__.__name__ + ', ' + repr(self.start) + ')'


def markup_sentences(purifier, puresection, sentences, escape_function=None):
    res = collections.deque([])
    
    puresection.build_tokens()
    #print repr(puresection.tokens) +  str(id(puresection.tokens))
    rules = purifier.elementrules
    
    token_off = 0
    token_frag = 0


    for sentence in sentences:
        assert isinstance(sentence, unicode)
        markup = u''

        sentence = sentence.strip()
        if not sentence:
            continue
        

        skip_until = None
        closing = False
        while token_off < len(puresection.tokens):
            t = puresection.tokens[token_off]
            

            if skip_until:
                if isinstance(t, Token) and skip_until == t.node:
                    skip_until = None

            elif t:
                if isinstance(t, basestring):
                    assert isinstance(t, unicode), t
                    if not t:
                        token_frag = 0
                        token_off += 1
                        continue
                    nodetext = t[token_frag:]
                    sentence_frag, node_frag = matchstring(sentence, nodetext)
                    markup += escape_function(sentence[:sentence_frag])
                    log.logger.debug('nodetext: "' + nodetext[:node_frag] + '"')
                    log.logger.debug('sentence: "' + sentence + '"')
                    sentence = sentence[sentence_frag:]
                    log.logger.debug('sentence: "' + sentence + '"')
                    if not sentence:
                        closing = True

                    if node_frag == len(nodetext):# and len(nodetext) != len(sentence):
                        token_frag = 0
                    else:
                        token_frag += node_frag
                        break
                        

                    
                else:
                    ac = rules.node_action(t.node)
                    if t.start and closing and ac != node.REPLACE and ac != node.PURGE:
                        break

                    #print node.action_name(ac)
                    if ac == node.REPLACE:
                        if t.start:
                            markup += rules.node_start(t.node)
                            skip_until = t.node

                    elif ac == node.PURGE:
                        if t.start:
                            skip_until = t.node
                    elif ac == node.KEEP:
                        if t.start:
                            markup += rules.node_start(t.node)
                        else:
                            markup += rules.node_params(t.node) + rules.node_end(t.node)
                    #elif ac == node.REMOVE: pass
                                   
            token_off += 1

        res.append(markup.replace('\n', ' ').strip())

    markup = u''
    while token_off < len(puresection.tokens):
        t = puresection.tokens[token_off]
        if not isinstance(t, basestring):
            ac = rules.node_action(t.node)
            if ac == node.REPLACE:
                if t.start:
                    markup += rules.node_start(t.node)
                    skip_until = t.node
            elif ac == node.PURGE:
                if t.start:
                    skip_until = t.node
            elif ac == node.KEEP:
                if t.start:
                    markup += rules.node_start(t.node)
                else:
                    markup += rules.node_params(t.node) + rules.node_end(t.node)
        token_off += 1
    if res:
        res[-1] = res[-1] + markup.replace('\n', ' ').strip()
            
    return res
            
class AlignmentException(Exception):
    pass

def matchstring(s1, s2):
    """
    mathces two strings ignoring whitespace
    returns a tuple with the no of characters mathced for each paramter
    """

    off1 = 0
    off2 = 0
    while off1 < len(s1) and off2 < len(s2):
        if s1[off1] == s2[off2]:
            off1 += 1
            off2 += 1
        elif s1[off1].isspace() or ord(s1[off1]) <= 32:
            off1 += 1
        elif s2[off2].isspace() or ord(s2[off2]) <= 32:
            off2 += 1
        else:
            #oh oh
            err = '\n' + s1 + '\n' + s2 + '\n' + \
            s1[:off1] + '[' + s1[off1] + ']' + s1[off1:] + '\n' + \
            s2[:off2] + '[' + s2[off2] + ']' + s2[off2:]  
            err = err.encode('ascii', 'ignore')
            raise AlignmentException(err)
    
    #skip remaining white spaces
    #while off1 < len(s1) and s1[off1] in string.whitespace:
    #    off1 += 1
    while off2 < len(s2) and s2[off2] in string.whitespace:
        off2 += 1


    log.logger.debug(s1 + ', ' + s2 + ' == > ' + str(off1) + ', ' + str(off2))
    return (off1, off2)


        


class PureSection(object):
    #heading = None #<h1>Foo</h1>
    #title = None #Foo i.e. self.heading without the surrounding tags
    #content = None #string[:len(heading)]

    def __init__(self, string, tree, purifier):
        self.string = string
        self.tree = tree
        self.purifier = purifier
        self.tokens = None

        self.content = ''

        self.clean = True #untill further notice

        #print repr(tree)

        if isinstance(tree, advtree.Article):
            self.level = 1
            self.title = tree.caption
        else:
            self.level = tree.level
            if tree.children and len(tree.children) > 0:
                self.title = purifier._node2str(tree.children[0])
            else:
                self.title = u''
        self.heading = purifier.elementrules.node_start(tree) + self.title + purifier.elementrules.node_end(tree)
        
        #the content without <h2>heading</h2>
        self.content = string[len(self.heading) + 1:].strip()
        self.heading = self.heading.replace('\n', '')
        self.title = self.title.replace('\n', '')
        super(PureSection, self).__init__()

    def __str__(self):
        return self.string.encode("utf-8", "ignore")
        
    def __repr__(self):
        return repr(self.tree)

    def getNodesByClass(self, theclass):
        return self._getNodesByClass(self.tree, theclass)

    def _getNodesByClass(self, tree, theclass):
        res = []
        if tree.children:
            for c in tree.children:
                if not isinstance(c, advtree.Text):
                    if node.node_action(self.purifier.elementrules, c) != node.PURGE:
                        if isinstance(c, theclass):
                            if len(self.purifier._node2str(c)) > 0:
                                res.append(c)
                        res.extend(self._getNodesByClass(c, theclass))
        return res
    


    def build_tokens(self, tree=None):
        self._build_tokens(None)
        self._clean_tokens()

    def _clean_tokens(self):
        newtokens = collections.deque([])
        i = 0
        while i < len(self.tokens) - 1:
            t = self.tokens[i]
            u = self.tokens[i + 1]
            if isinstance(t, basestring) or isinstance(u, basestring) or t.node != u.node:
                newtokens.append(t)
                i += 1
            else:
                i += 2
        self.tokens = newtokens
                
            


    def _build_tokens(self, tree):

        if not tree:
            tree = self.tree
        if not self.tokens:
            self.tokens = collections.deque([])

        if not tree.isVisible():
            return
        if not isinstance(tree, basestring):
            self.tokens.append(Token(tree, True))

        #special treatment for article and section
        if isinstance(tree, advtree.Article):
            self.tokens.append(getDisplayText(tree))
            self.tokens.append(Token(tree, False))
        elif isinstance(tree, advtree.AdvancedSection):
            if tree.children and len(tree.children) > 0: 
                self._build_tokens(tree.children[0])
            self.tokens.append(Token(tree, False))
            for c in tree.children[1:]:
                self._build_tokens(c)
            self.tokens.append("")
            return
        #'regular' nodes
        if tree.children:
            for c in tree.children:
                self._build_tokens(c)
        else:
            text = getDisplayText(tree)
            if text:
                self.tokens.append(text)

        if not isinstance(tree, basestring):
            self.tokens.append(Token(tree, False))

    def isEmpty(self):
        #fixme, it makes more sense if a section is considered empty if it has no printable text
        return len(self.content) == 0


class Purifier(object):

    def __init__(self, env, templateactions, elementrules):
        self.env = env
        self.templateactions = templateactions
        self.elementrules = elementrules
        self.rm = nshandling.get_redirect_matcher(env.wiki.siteinfo, env.wiki.nshandler)

        self.keep_empty = False # shoud we keep sections with no content?
        self.extra_newlines = False # should we include newlines as hints for a sentence segmentor?

    
        super(Purifier, self).__init__()


    def parse_and_purify(self, title, follow_redirects=False):
        """
        parses the named article and returns it as a list of PureSections, returns None for redirects
        """
        title = title.decode('utf-8')
        raw = self.env.wiki.reader[title]

        #check for redirect
        target = self.rm(raw) 
        if target:
            if follow_redirects:
                log.logger.info(title + ' redirects to ' + target)
                return self.parse_and_purify(target)
            else:
                return None

        else:    
            markup = self.templateactions.handle_templates(raw, title=title)
            tree = myParseString.myParseString(title=title, raw=markup, wikidb=self.env.wiki, 
                                               lang=self.env.wiki.siteinfo["general"]["lang"], 
                                               uniq=self.templateactions.exp.uniquifier)
            advtree.buildAdvancedTree(tree)
            return self.purify(tree)

    def purify_string(self, string, title='__no_name__'):
        """
        parses the string and returns it as a list of PureSections
        """
        markup = self.templateactions.handle_templates(string, title=title)
        tree = myParseString.myParseString(title=title, raw=markup, wikidb=self.env.wiki, 
                                           lang=self.env.wiki.siteinfo["general"]["lang"], 
                                           uniq=self.templateactions.exp.uniquifier)
        advtree.buildAdvancedTree(tree)
        return self.purify(tree)        
        

    def purify(self, tree):
        """
        destructively purifies 'tree' and returns it as a list of sections.
        """
        
        sections = []
        self._set_tagnames(tree) # in retrospect, using the _tag attribute might have been a better strategy
        self._collect_sections(tree, sections)
        self._split_sections(tree)

        pure_sections = []
        for s in sections:
            section_string = self._node2str(s)
            ps = PureSection(section_string, s, self)
            #if self.keep_empty or not ps.isEmpty():
            pure_sections.append(ps)


        return pure_sections

    def _set_tagnames(self, tree):
        if not isinstance(tree, advtree.Text):
            if not tree.tagname:
            #first, check rawtagname
                if tree.rawtagname:
                    tree.tagname = tree.rawtagname
            #then, set it to captions for generic nodes
                elif tree.caption and tree.__class__.__name__ == "TagNode":
                    tree.tagname = tree.caption
            #else set it to classname
                else:
                    tree.tagname = tree.__class__.__name__
        if tree.children:
            for c in tree.children:
                self._set_tagnames(c)

    def _collect_sections(self, tree, sections):
        #if this is a section add it to the list
        if isinstance(tree, advtree.Article) or isinstance(tree, advtree.AdvancedSection):
            sections.append(tree)
         #examine the children
        if tree.children:
            for c in tree.children:
                self._collect_sections(c, sections)
    
    #split each section into a separate subtree
    def _split_sections(self, tree):
        if tree.children:
            for c in list(tree.children):
                self._split_sections(c)
                if isinstance(c, advtree.AdvancedSection):
                    tree.removeChild(c)
                

                        
    def _purify(self, tree):
        res = self._node2str(tree) 
        if tree.children:
            for c in tree.children:
                res += self._purify(c)

        return res

    def node2str(self, n):
        return self._node2str(n)

    def _node2str(self, n):
        ret = u''
        next = None

        if not n.isVisible():
            return ret

        #dont do anything fancy with text nodes
        if isinstance(n, advtree.Text):
            return n.caption
        
#special treatment for Section and Aricle
        ac = node.node_action(self.elementrules, n)
        if isinstance(n, advtree.Article):
            if ac != node.PURGE:
                ret = self.elementrules.node_start(n) + n.caption + self.elementrules.node_end(n) + '\n'
            if n.children:
                for c in n.children:
                    ret += self._node2str(c)
        elif isinstance(n, advtree.AdvancedSection):
            if ac != node.PURGE:
                ret = self.elementrules.node_start(n)
                if ac != node.REPLACE:
                    if n.children: 
                        ret += self._node2str(n.children[0])
                ret += self.elementrules.node_end(n) + '\n'                
            
                if n.children:
                    for c in n.children[1:]:
                        ret += self._node2str(c)
        else:

            if ac == node.PURGE:
                if self.extra_newlines and n.isblocknode:
                    return u'\n'
                else:
                    return  u' '
            elif ac == node.REPLACE:
                ret = self.elementrules.node_start(n)
            elif ac == node.KEEP:
                if n.__class__.__name__ in node.noclose:
                    return self.elementrules.node_start(n)
                ret = self.elementrules.node_start(n)
                txt = u''
                if n.children:
                    for c in n.children:
                        txt += self._node2str(c)
                else:
                    txt += getDisplayText(n)
                #ignore this tag if the children dont produce any text
                if len(txt.strip()) > 0:
                    ret += txt
                    ret += self.elementrules.node_params(n) + self.elementrules.node_end(n)
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
            if self.extra_newlines:
                ret = u'\n' + ret
            ret += u'\n'
        

        return ret
            
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', action='store_true')
    parser.add_argument('--extra-newlines', action='store_true')
    parser.add_argument('--keep-empty', action='store_true')
    parser.add_argument('article')
    args = parser.parse_args()
    

    env = wiki.makewiki(paths.paths["wikiconf"])
    act = template.create_actions(env, paths.paths["templaterules"], paths.paths["templatecache"])
    elementrules = node.read_rules(paths.paths["noderules"])

    purifier = Purifier(env, act, elementrules)
    purifier.extra_newlines = args.extra_newlines
    purifier.keep_empty = args.keep_empty
   
    
    raw = """
This text is above all the headings
== Template tests ==
Pagename: {{PAGENAME}}

"Coor title dm" expands to "Coor dm" should be kept<br />
{{coor title dm|11|22|33|N|44|55|E|:city}}
"Fact" should be removed<br />
{{Fact}}

"Harvtxt" is a redirect to "Harvard citation"<br />
{{Harv|Smith|2006| p=25}} 

"Cleanup" expands to "Asbox" that should be removed<br />
{{Cleanup}}

<h2>Markup tests</h2>
I wonder what happens to the heading above...
== Wiki style header ==
As opposed to this one


 """
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
