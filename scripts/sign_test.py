#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Lars Jørgen Solberg <supersolberg@gmail.com> 2013
#

import argparse
import time
import os

from wcb import util
from wcb import srilm
from wcb import log
from wcb import classifier_cache

import scipy.stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('clean_set')
    parser.add_argument('dirty_set')
    parser.add_argument('lm_dir')
    parser.add_argument('clean_port')
    parser.add_argument('dirty_port')
    parser.add_argument('clean_lm')
    parser.add_argument('dirty_lm')
    parser.add_argument('--articles', '-a', action='store_true', default=False)
    args = parser.parse_args()


    log.logger.debug("loading sets")
    if args.articles:
        clean_sections = [srilm.explode(util.file2s(os.path.join(args.clean_set, f))) for f in os.listdir(args.clean_set)]
        dirty_sections = [srilm.explode(util.file2s(os.path.join(args.dirty_set, f))) for f in os.listdir(args.dirty_set)]
    else:
        clean_sections = [s for s in util.sections(args.clean_set)]
        dirty_sections = [s for s in util.sections(args.dirty_set)]

    log.logger.info(str(len(clean_sections)) + " + " + str(len(dirty_sections)) + " sections")
    #classifiers = [('test', 'clean_2gram_10train_cdiscount_1.lm', 'dirty_2gram_10train_cdiscount_1.lm', 2)]
    classifiers = util.classifiers(args.lm_dir)

    #how many sections does the target classifier get right?
    log.logger.debug("loading the target classifier")
    order = srilm.max_order(args.clean_lm)
    log.logger.debug("order: " + str(order))
    clean_server = srilm.Server(args.clean_port, args.clean_lm)
    dirty_server = srilm.Server(args.dirty_port, args.dirty_lm)
    clean_client = srilm.Client(args.clean_port, order)
    dirty_client = srilm.Client(args.dirty_port, order)

    log.logger.debug("testing the target classifier")
    target_outcomes = [1 if r > 0 else 0 for r in srilm.classify_bulk(clean_sections, clean_client, dirty_client)]
    target_outcomes += [1 if r < 0 else 0 for r in srilm.classify_bulk(dirty_sections, clean_client, dirty_client)]
    target_correct = sum(target_outcomes)
    clean_client.close()
    dirty_client.close()
    clean_server.stop()
    dirty_server.stop()
    time.sleep(30)

    print "label\tsignificance\tlevel\tdisagreements\tcorrect"
    #compare with the other classifiers
    for c in classifiers:
        log.logger.info("testing " + str(c))

        outcomes = [1 if r > 0 else 0 for r in classifier_cache.read_cache(args.lm_dir, c[0], os.path.basename(args.clean_set))]
        outcomes += [1 if r < 0 else 0 for r in classifier_cache.read_cache(args.lm_dir, c[0], os.path.basename(args.dirty_set))]

        if not outcomes:
        #load the classifier
            clean_server = srilm.Server(args.clean_port, os.path.join(args.lm_dir, c[1]), c[3])
            dirty_server = srilm.Server(args.dirty_port, os.path.join(args.lm_dir, c[2]), c[3])
            clean_client = srilm.Client(args.clean_port, c[3])
            dirty_client = srilm.Client(args.dirty_port, c[3])

        #find which sections it get right
            clean_results = srilm.classify_bulk(clean_sections, clean_client, dirty_client)
            dirty_results = srilm.classify_bulk(dirty_sections, clean_client, dirty_client)
            classifier_cache.write_cache(args.lm_dir, c[0], os.path.basename(args.clean_set), clean_results)
            classifier_cache.write_cache(args.lm_dir, c[0], os.path.basename(args.dirty_set), dirty_results)


            outcomes = [1 if r > 0 else 0 for r in clean_results]
            outcomes += [1 if r < 0 else 0 for r in dirty_results]

            clean_client.close()
            dirty_client.close()
            clean_server.stop()
            dirty_server.stop()
            time.sleep(30)

        m = 0
        w = 0
        for x, y in zip(target_outcomes, outcomes):
            if x != y:
                m += 1
                if x:
                    w += 1

#        if sum(target_outcomes) < sum(outcomes):
        sig = scipy.stats.binom.sf(w - 1, m, 0.5)
        siglvl = ''
        if sig <= 0.05:
            siglvl += '*'
        if sig <= 0.005:
            siglvl += '*'

        print "%s\t%.10f\t%s\t%i\t%i" % (c[0], sig, siglvl, m, w)
