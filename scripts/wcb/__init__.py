#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Lars Jørgen Solberg <supersolberg@gmail.com> 2013
#
import os

from mwlib import nuwiki, wiki

# read the config, its location is given by the PATHSFILE enirionment variable
paths = {}
def read_paths(filename):
    dirname = os.path.dirname(filename)
    f = open(filename)
    for l in f:
        pair = l.split('#', 2)[0]
        if '=' in pair:
            pair = pair.split('=')
            paths[pair[0].strip()] = os.path.join(dirname, pair[1].strip())
    #make sure that the tmp directory exists
    if not os.path.isdir(paths['tmp']):
        os.makedirs(paths['tmp'])
    f.close()

if 'PATHSFILE' in os.environ:
    read_paths(os.environ['PATHSFILE'])
else:
    print("PATHSFILE not set")


# cdb is no longer supported by mwlib, we use the third party module mwlib.cdb instead
def wiki_nucdb(path=None, lang="en", **kwargs):
    from mwlib.cdb import cdbwiki
    path = os.path.expanduser(path)
    db = cdbwiki.WikiDB(path, lang=lang)
    return nuwiki.adapt(db)
wiki.dispatch = dict(wiki=dict(nucdb=wiki_nucdb))

# workaround for a bug in mwlib, we don't care about images anyway
def normalize_and_get_image_path(x, *args):
    pass
nuwiki.adapt.normalize_and_get_image_path = normalize_and_get_image_path

#if "siteinfo" is set in the pathsfile, use it
def load_siteinfo(lang="en"):
    from mwlib import siteinfo
    try:
        import simplejson as json
    except ImportError:
        import json

    if "siteinfo" in paths:
        if not  os.path.exists(paths["siteinfo"]):
            logger.error("Can't find " + os.path.exists(paths["siteinfo"]))
        else:
            siteinfo._cache[lang] = json.load(open(paths["siteinfo"], "rb"))["query"]
load_siteinfo()

if __name__ == "__main__":
    print paths
