#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Lars Jørgen Solberg <supersolberg@gmail.com> 2013
#


from mwlib import wiki, parser, expander, nshandling
from mwlib.templ.magics import MagicResolver
from mwlib.templ.nodes import Node, Variable, Template, show
from mwlib.templ.parser import parse
from mwlib.templ.evaluate import flatten, Expander, ArgumentList
from mwlib.templ.marks import mark_start

import wcb

import codecs
import re
import argparse
import sys
import time

class TemplateNotFound(Exception):
    pass

mr = MagicResolver()

def replace_tags(txt):
    patt = re.compile(r"<!--.*?-->|<(nowiki|math|gallery|source|pre|timeline|poem|ref)>.*?</\1>", flags=re.DOTALL|re.UNICODE|re.IGNORECASE)

    return re.sub(patt, "\n", txt,)


def cleanup_name(title):
    title = env.wiki.nshandler.get_fqname(title, nshandling.NS_TEMPLATE)
    #does this template actually exist?
    page = env.wiki.get_page(title)
    if not page:
        raise TemplateNotFound('Could not find template "' + title + '"')
    #is it a redirect?
    if page.names[-1] != title:
        return cleanup_name(page.names[-1])
    else:
        return env.wiki.nshandler.splitname(title)[1]


def get_templates(title, used=dict()):
    parse_error = False
    raw = env.wiki.nuwiki.get_page(title)

    #exp = Expander('', wikidb=env.wiki)

    if raw is None:
        raw = env.wiki.nuwiki.get_page(title.encode("utf-8", "ignore"))
        # I dont know why this helps...

    if raw is None:
        sys.stderr.write("Could not find " + title.encode("ascii", "backslashreplace") + "\n")
        return used
    raw = raw.rawtext
    try:
        todo = [parse(raw, replace_tags=replace_tags)]
    except RuntimeError as excp:
        sys.stderr.write(title.encode("utf-8", "ignore") + ': ')
        sys.stderr.write(unicode(excp).encode("ascii", "backslashreplace") + "\n")
        Summary.parseerrors += 1
        return used
    while todo:
        n = todo.pop()
        if isinstance(n, basestring):
            continue

        if isinstance(n, Template) and isinstance(n[0], basestring):
            try:
                name = n[0]
                if name.startswith("/"):
                    name = title+name

                magic = False
                for i in name.split(":"):
                    if mr.has_magic(i):
                        magic = True
                        break
                if magic:
                    continue

                name = cleanup_name(name)
                if len(name) == 0:
                    continue

                res = []
                args = expander.get_template_args(n, exp)
                n.flatten(exp, args, res)

                for x in res:
                    if isinstance(x, mark_start):
                        # o_O mark.msg is a string in the form "u'foo'"
                        m = eval(x.msg)

                        m = cleanup_name(m)
                        if not m in used:
                            used[m] = [0, 0]
                        used[m][1] += 1
                        Summary.templates += 1

                if not name in used:
                    used[name] = [0, 0]
                used[name][0] += 1
            except TemplateNotFound as excp:
                sys.stderr.write(title.encode("utf-8", "ignore") + ': ')
                sys.stderr.write(unicode(excp).encode("ascii", "backslashreplace") + "\n")
                Summary.missing_templates += 1
            except Exception as excp:
                sys.stderr.write(title.encode("utf-8", "ignore") + ': ')
                sys.stderr.write(unicode(excp).encode("ascii", "backslashreplace") + "\n")
                parse_error = True



        todo.extend(n)
    Summary.articles += 1
    if parse_error:
        Summary.parseerrors += 1
    return used


def printres(result):
    l = list()
    for k in result.keys():
        l.append([result[k][0], result[k][1], k])

        l.sort(key=lambda x: x[0], reverse=True)

    if args.outfile:
        out = codecs.open(args.outfile, 'w', encoding='utf-8')
    else:
        out = sys.stdout

    out.write(unicode(Summary.articles) + u' articles\n')
    out.write('direct_total_name\n')
    for i in l:
        out.write(repr(i[0]) + '_')
        out.write(repr(i[1]) + '_')
        if args.outfile:
            out.write(i[2] + '\n')
        else:
            out.write(i[2].encode("utf-8", "ignore") + '\n')

    if args.outfile:
        out.close()

class Summary:
    starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    articles = 0
    redirects = 0
    templates = 0
    missing_templates = 0
    parseerrors = 0
    errors = 0

    def print_summary(self):
        print "Started: ".rjust(30) + self.starttime
        print "Done: ".rjust(30) + time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        print "Aricles: ".rjust(30) + str(self.articles)
        print "Redirects: ".rjust(30) + str(self.redirects)
        print "Missing templates: ".rjust(30) + str(self.missing_templates)
        print "Articles with parse errors: ".rjust(30) + str(self.parseerrors)
        print "Other errors: ".rjust(30) + str(self.errors)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Counts template inclusions')
    parser.add_argument('article', nargs='?', default=None)
    parser.add_argument('--outfile', '-o', default=None, type=str)
    parser.add_argument('--max', '-m', default=0, type=int,
                        help="don't examine more than MAX articles.")
    parser.add_argument('--all-namespaces', action='store_true', help="count inclusions from all namespaces (except Template:)")
    args =  parser.parse_args()

    env = wiki.makewiki(wcb.paths["wikiconf"])
    exp = Expander('', wikidb=env.wiki)


#just look at one article
    if args.article:
        templates = get_templates(args.article)

#all articles
    else:
        templates = dict()
        counter = 0

        if args.all_namespaces:
            titles = env.wiki.reader.iterkeys()
        else:
            titles = env.wiki.nuwiki.articles()

        for title in titles:
            namespace = env.wiki.nshandler.splitname(title)[0]
            if namespace == nshandling.NS_TEMPLATE:
                continue


            page = env.wiki.get_page(title)
            if not page:
                Summary.errors += 1
                sys.stderr.write(title.encode("utf-8", "ignore") + ': Broken redirect\n')
                continue
            if len(page.names) != 1:
                Summary.redirects += 1
                continue
            get_templates(title, templates)
            counter += 1
            if counter == args.max:
                break
            if counter % 25000 == 0:
                printres(templates)

    printres(templates)
    Summary().print_summary()
