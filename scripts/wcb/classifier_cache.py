#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#
import log

import collections
import os

def write_cache(lm_dir, label, set_name, results):
    if not is_cached(lm_dir, label, set_name):
        log.logger.info("caching results in "  + filename(lm_dir, label, set_name))
        if not os.path.exists(os.path.join(lm_dir, 'cache')):
            os.mkdir(os.path.join(lm_dir, 'cache'))
        with open(filename(lm_dir, label, set_name), 'w') as f:
            for r in results:
                f.write(repr(r) + '\n')


def read_cache(lm_dir, label, set_name):
    results = collections.deque([])
    if is_cached(lm_dir, label, set_name):
        log.logger.info("using cached results from "  + filename(lm_dir, label, set_name))
        with open(filename(lm_dir, label, set_name), 'r') as f:
            for r in f:
                results.append(float(r))

    return results



def filename(lm_dir, label, set_name):
    return os.path.join(lm_dir, 'cache', label + '_' + set_name)


def is_cached(lm_dir, label, set_name):
    return os.path.exists(filename(lm_dir, label, set_name))
