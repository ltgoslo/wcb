#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#


import util, log, srilm
import argparse, os, collections, codecs

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('sets')
    parser.add_argument('taint') 
    args = parser.parse_args()


    tainted_sections = collections.deque([s.strip() for s in  util.sections(args.taint)])
    for filename in os.listdir(args.sets):
        log.logger.info(filename)
        sections = collections.deque(util.sections(filename))
        with codecs.open(filename, 'w', 'utf-8') as f:
            for s in sections:
                if s.strip() not in tainted_sections:
                    f.write(s)
                else:
                    log.logger.info('removing ' + srilm.unexplode(s))
                    tainted_sections.remove(s.strip())
