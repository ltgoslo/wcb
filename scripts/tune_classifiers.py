#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

import argparse, os, time, shutil, profile
import log, srilm, util, classifier_cache


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('clean_set')
    parser.add_argument('dirty_set')
    parser.add_argument('lm_dir')
    parser.add_argument('clean_port')
    parser.add_argument('dirty_port')
    parser.add_argument('--articles', '-a', action='store_true', default=False)
    
    args = parser.parse_args()

    log.logger.info("loading sets")
    if args.articles:
        clean_sections = [srilm.explode(util.file2s(os.path.join(args.clean_set, f))) for f in os.listdir(args.clean_set)]
        dirty_sections = [srilm.explode(util.file2s(os.path.join(args.dirty_set, f))) for f in os.listdir(args.dirty_set)]
    else:
        clean_sections = [s for s in util.sections(args.clean_set)]
        dirty_sections = [s for s in util.sections(args.dirty_set)]
    

    classifiers = util.classifiers(args.lm_dir)

    print "label\tacc clean (%i)\tacc dirty (%i)" % (len(clean_sections), len(dirty_sections))
    for c in classifiers:
        log.logger.info("testing " + c[0])
        print c[0] + "\t",

        log.logger.info("classifying (" + str(len(clean_sections) + len(dirty_sections)) + ")")
        clean_results = classifier_cache.read_cache(args.lm_dir, c[0], os.path.basename(args.clean_set))
        dirty_results = classifier_cache.read_cache(args.lm_dir, c[0], os.path.basename(args.dirty_set))
 
        if not (clean_results and dirty_results):
            clean_server = srilm.Server(args.clean_port, os.path.join(args.lm_dir, c[1]), c[3])
            dirty_server = srilm.Server(args.dirty_port, os.path.join(args.lm_dir, c[2]), c[3])
            clean_client = srilm.Client(args.clean_port, c[3])
            dirty_client = srilm.Client(args.dirty_port, c[3])
            
            clean_results = [x for x in srilm.classify_bulk(clean_sections, clean_client, dirty_client)]
            dirty_results = [x for x in srilm.classify_bulk(dirty_sections, clean_client, dirty_client)]

            classifier_cache.write_cache(args.lm_dir, c[0], os.path.basename(args.clean_set), clean_results)
            classifier_cache.write_cache(args.lm_dir, c[0], os.path.basename(args.dirty_set), dirty_results)
            
            log.logger.info("stopping servers")
            clean_client.close()
            dirty_client.close()
            clean_server.stop()
            dirty_server.stop()
            time.sleep(30)


        corr = sum([1 for x in clean_results if x > 0])
        print str(corr) + "\t",
        corr = sum([1 for x in dirty_results if x < 0])
        print str(corr)


                    

