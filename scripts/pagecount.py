#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

from mwlib import wiki, nshandling

class namespace:
    def __init__(self, name):
        self.pages = 0
        self.redirects = 0
        self.name = name

    def __str__(self):
        return self.name + '\t' + str(self.pages)  + '\t' + str(self.redirects)

if __name__ == "__main__":
    env = wiki.makewiki(paths.paths["wikiconf"])
    rm = nshandling.get_redirect_matcher(env.wiki.siteinfo, env.wiki.nshandler)

    namespaces = {}
    for i in env.wiki.siteinfo["namespaces"]:
        if not "canonical" in env.wiki.siteinfo["namespaces"][i]:
            ns = namespace("")
        else:
            ns = namespace(env.wiki.siteinfo["namespaces"][i]["canonical"])
        namespaces[i] = ns

    counter = 0
    for name, raw in env.wiki.reader.iteritems():
        ns, _name, fullname = env.wiki.nshandler.splitname(name)
        ns = str(ns)
        if rm(raw):
            namespaces[ns].redirects += 1
        else:
            namespaces[ns].pages += 1


    print 'namespace\tpages\tredirects'
    for ns in namespaces.values():
        print ns
