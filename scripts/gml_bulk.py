#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

import argparse, multiprocessing, collections, Queue
import os, codecs, traceback, re
import gml, senseg, classify, paths, util, srilm
import log, util, list_articles, template, node, purify
import wikiwoods
from mwlib import wiki

def write_results(outdir, string, num):
    if len(string):
        name = multiprocessing.current_process().name + "-" + str(num) + '.gml'
        name = os.path.join(outdir, name)
        util.s2file(string, name)



def worker(outdir, inqueue, outqueue,
           order, clean_port, dirty_port, 
           prerocessor, gml_purifier, senseg_purifier,
           ww_segments):
    clean_client = srilm.Client(clean_port, order)
    dirty_client = srilm.Client(dirty_port, order)

    chunk_num = 0
    done = False
    while not done:
        result = u''
        name = ''
        try:
            #get one segment
            if ww_segments:
                try:
                    segment = inqueue.get(True, 1)
                    chunk_num = os.path.split(segment)[1]
                except Queue.Empty as excp:
                    done = True
                sections = wikiwoods.purify_segment(segment, preprocessor)

            #get 500 names
            else:
                
                names = collections.deque([])
                i = 0
                try:
                    while i < 500:
                        name = inqueue.get(True, 1)
                        names.append(name)
                        i += 1
                    
                except Queue.Empty as excp:
                    done = True
                
                sections = collections.deque([])
                for name in names:
                    sections.extend(preprocessor.parse_and_purify(name))
                
            classify.classify(sections, clean_client, dirty_client)    
         
            sections = gml.filter_sections(sections)
            for sect in sections:
                if sect.clean or sect.sprint:
                    text = senseg.senseg(senseg_purifier.node2str(sect.tree))
                    lines = purify.markup_sentences(gml_purifier, sect, re.split('\n+', text), gml.escape)
                
                    if sect.clean:
                        result += '\n'.join(lines) + '\n'
                    elif sect.sprint and lines:
                        result += lines[0] + '\n'

            write_results(outdir, gml.fix_templates(result), chunk_num)
            if isinstance(chunk_num, int):
                chunk_num += 1
            
        except Exception as excp:
            msg = repr(excp)
            log.logger.error(msg.encode("utf-8", "ignore"))
            log.logger.error(traceback.format_exc())
        

    clean_client.close()
    dirty_client.close()
    outqueue.put(None) # tell the main process that we are done


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('article_list')
    parser.add_argument('out_dir')
    parser.add_argument('--clean-port', default='5000')
    parser.add_argument('--dirty-port', default='5001')
    parser.add_argument('--processes', '-p', default=1, type=int)
    parser.add_argument('--wikiwoods', action='store_true')
    args = parser.parse_args()

    #read the articles
    names = multiprocessing.Queue()

    with codecs.open(args.article_list, 'r', 'utf-8') as f:
        for name in f:
            names.put(name.strip())

    env = wiki.makewiki(paths.paths["wikiconf"])
    act = template.create_actions(env, paths.paths["templaterules"], paths.paths["templatecache"])

    #classifier
    order = srilm.max_order(paths.paths["clean lm"])
    clean = srilm.Server(args.clean_port, paths.paths["clean lm"])
    dirty = srilm.Server(args.dirty_port, paths.paths["dirty lm"])
    preprocessor = classify.Preprocessor(env, act, node.read_rules(paths.paths["noderules"]))
    #gml
    gml_purifier = purify.Purifier(env, act, node.read_rules(paths.paths["noderules_gml"]))
    #senseg
    senseg_purifier = purify.Purifier(env, act, node.read_rules(paths.paths["noderules_senseg"]))
    senseg_purifier.extra_newlines = True

    

   #start worker processes
    ret = multiprocessing.Queue()
    log.logger.info("starting workers")
    for i in range(0, args.processes):
        #purifier.act = template.TemplateActions(env=env, address=act.manager.address, authkey=multiprocessing.current_process().authkey)
        p = multiprocessing.Process(target=worker, name=str(i), args=(args.out_dir, names, ret,
                                                                      order, args.clean_port, args.dirty_port, 
                                                                      preprocessor, gml_purifier, senseg_purifier,
                                                                      args.wikiwoods))
            
        p.daemon = True
        p.start()

    curr_pcs = args.processes
   #wait until they are done
    while curr_pcs > 0:
        r = ret.get()
        if not r:
            curr_pcs -= 1


    clean.stop()
    dirty.stop()
