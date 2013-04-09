#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

import re, cPickle, os, argparse

from wcb import log, util
from wcb.purify import *

_offset = ord('a')


def enc_base25(n):
    res = ''
    while n > 0:
        res = chr((n % 25) + _offset) + res
        n /= 25
    if res == '':
        res = 'a'
    return res

def dec_base25(s):
    res = 0
    for char in s:
        res *= 25
        res += ord(char) - _offset
    return res



class Masker(object):

    def __init__(self, pattern=re.compile('{\(.*?\)}', re.U)):
        self.pattern = pattern
        super(Masker, self).__init__()
        self.start = u'zzzz'
        self.end = u'zzzz'
        self.mask_pattern = None
        self.id = 0
        self.items = []

    def store_item(self, item):
        self.items.append(item.group(0))
        mask = self.start + enc_base25(self.id) + self.end
        self.id += 1
        return mask

    def store_string(self, string):
        if self.start in string:
            raise Exception('Masks are nesting!! ' + string)
        self.items.append(string)
        mask = self.start + enc_base25(self.id) + self.end
        self.id += 1
        return mask

    def retrieve_item(self, mask):
        mask = mask.group(0)
        log.logger.debug('mask: ' + mask)
        try:
            return self.items[dec_base25(mask[len(self.start):-len(self.end)])]
        except Exception as e:
            log.logger.error(str(e) + ' ' + mask)
            return mask

    def mask(self, text):
        return self.pattern.sub(self.store_item, text)

    def unmask(self, text):
        if not isinstance(text, unicode):
            text = text.decode('utf-8')
        if not self.mask_pattern:
            self.mask_pattern = re.compile(re.escape(self.start) + u'([a-y]+?)' + re.escape(self.end), re.U)
        return self.mask_pattern.sub(self.retrieve_item, text)


def load_masks(masker, masks_file):
    log.logger.debug('loading from ' + masks_file)
    if os.path.exists(masks_file):
        f = open(masks_file, 'r')
        masker.items = cPickle.load(f)
        f.close()

def save_masks(masker, masks_file):
    log.logger.debug('saving to ' + masks_file)
    f = open(masks_file, 'w')
    cPickle.dump(masker.items, f)
    f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('masks')
    parser.add_argument('--load', '-l', action='store_true')
    parser.add_argument('--regexp', '-r')
    args = parser.parse_args()

    if args.regexp:
        masker = Masker(re.compile(args.regexp, re.U|re.I))
    else:
        masker = Masker()

    text = util.file2s(args.file)
    if args.load:
        load_masks(masker, args.masks)
        print masker.unmask(text)
    else:
        text = masker.mask(text)
        save_masks(masker, args.masks)
        util.s2file(text, args.file)
