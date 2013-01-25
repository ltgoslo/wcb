#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

# reads paths from a file...


import os, argparse
import log

paths = {}

def read_paths(filename):
    global paths
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
    log.logger.warning("PATHSFILE not set")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('pathsfile')
    args = parser.parse_args()

    read_paths(args.pathsfile)
    print paths
