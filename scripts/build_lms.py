#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

from wcb import srilm

import argparse
import os
import glob

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('set_dir')
    parser.add_argument('lm_dir')
    args = parser.parse_args()

    order = ['2', '3', '4', '5', '10']
    pwd = os.getcwd()
    os.chdir(args.set_dir)
    train = [t[6:] for t in glob.iglob('clean_*.exploded')]
    print train
    os.chdir(pwd)

    pr_train = ['10', '20', '50', '100']
    smooth = ['-kndiscount', '-ukndiscount', '-cdiscount 1', '-addsmooth 1', '-wbdiscount']

    for o in order:
        for t in train:
            for s in smooth:
                for c in ('clean', 'dirty'):
                    lm = os.path.join(args.lm_dir, c + '_' + o + 'gram_' + t + '_' +  s[1:].replace(' ', '_') + '.lm')
                    if not os.path.exists(lm) and not os.path.exists(lm + '.gz'):
                        srilm.make_lm(lm=lm,
                                      trainset=os.path.join(args.set_dir, c + '_' + t),
                                      order=int(o),
                                      args=s.split())

    #only make 15 grams with cdiscount
    order = ['15']
    smooth = ['-cdiscount 1']
    for o in order:
        for t in train:
            for s in smooth:
                for c in ('clean', 'dirty'):
                    lm = os.path.join(args.lm_dir, c + '_' + o + 'gram_' + t + 'train_' +  s[1:].replace(' ', '_') + '.lm')
                    if not os.path.exists(lm) and not os.path.exists(lm + '.gz'):
                        srilm.make_lm(lm=lm,
                                      trainset=os.path.join(args.set_dir, c + '_' + t),
                                      order=int(o),
                                      args=s.split())
