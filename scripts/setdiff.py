#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Lars Jørgen Solberg <supersolberg@gmail.com> 2013
#


from wcb import util
from wcb import log
from wcb import srilm


import argparse
import os
import collections
import codecs

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('sets')
    parser.add_argument('unwanted')
    args = parser.parse_args()


    unwanted_sections = collections.deque([s.strip() for s in  util.sections(args.unwanted)])
    mathces = 0
    for filename in os.listdir(args.sets):
        log.logger.info(filename)
        sections = collections.deque(util.sections(filename))
        with codecs.open(filename, 'w', 'utf-8') as f:
            for s in sections:
                if s.strip() not in unwanted_sections:
                    f.write(s)
                else:
                    mathces += 1
                    log.logger.info('removing ' + srilm.unexplode(s))
                    unwanted_sections.remove(s.strip())
    log.logger.info('Removed ' + mathces + ' sections')
