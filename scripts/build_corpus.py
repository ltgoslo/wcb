#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

import argparse, multiprocessing, collections, Queue
import os, codecs, traceback, re, gzip, signal
import gml, senseg, classify, paths, util, srilm
import log, util, list_articles, template, node, purify
from mwlib import wiki, advtree

class TimeoutException(Exception):
    pass

_nextid = 0
def make_entry(name):
    global _nextid
    e = [_nextid, name, None, []]
    _nextid += 1
    return e #[id, name, gml, sections]

_seg_id = 101
_art_id = 100
def write_segment(outdir, entries):
    global _art_id
    global _seg_id

    f =  gzip.open(os.path.join(outdir, '{0:05}'.format(_seg_id) + '.gml.gz'), 'wb')
    for e in entries:
        sent_id = 0
        if e[2] and e[2].strip():
            for line in e[2].splitlines():
                line = gml.re_par.sub('\n', line)
                line = line.replace('___NL___', '') #only insert paragraph breaks at the end of a sentence
                f.write('[1{0:07}{1:05}] |{2}\n'.format(_art_id, sent_id, line.encode('utf-8')))
                sent_id += 10
            _art_id += 1
        e[2] = None
    _seg_id += 1
                        
def worker(outdir, inqueue, outqueue,
           order, clean_port, dirty_port, 
           prerocessor, gml_purifier, senseg_purifier):
    clean_client = srilm.Client(clean_port, order)
    dirty_client = srilm.Client(dirty_port, order)

    def timeout_handler(signum, fram):
        raise TimeoutException()
    signal.signal(signal.SIGALRM, timeout_handler)



    done = False
    while not done:
        try:
            #signal.alarm(3600) #somethimes the workers freeze up...
            #get 100 entries
            entries = collections.deque([])
            i = 0
            try: 
                while i < 100:
                    entry = inqueue.get(True, 1)
                    entries.append(entry)
                    i += 1
            except Queue.Empty as excp:
                done = True
            sections = collections.deque([])
            for e in entries:
                e[3] = preprocessor.parse_and_purify(e[1])
                sections.extend(e[3])
            classify.classify(sections, clean_client, dirty_client)

            for e in entries:
                e[2] = u''
                for sect in e[3]:
                    gml.filter_sections(e[3])

                    text = senseg.senseg(senseg_purifier.node2str(sect.tree))
                    lines = purify.markup_sentences(gml_purifier, sect, re.split('\n+', text), gml.escape)

                    if sect.clean:
                        e[2] += '\n'.join(lines) + '\n'
                    elif sect.sprint:
                        if lines and lines[0]:
                            e[2] += lines[0] + '\n'
                if e[2]:
                    e[2] = gml.fix_templates(e[2])
                else:
                    e[2] = u'' # this should not be necessary
                e[3] = None
                outqueue.put(e)

        except Exception as excp:
            msg = repr(excp)
            log.logger.error(msg.encode("utf-8", "ignore"))
            log.logger.error(traceback.format_exc())
            if entries:
                for e in entries:
                    e[3] = None
                    if not e[2]:
                        e[2] = u''
                    outqueue.put(e)
            clean_client.close()
            dirty_client.close()
            clean_client = srilm.Client(clean_port, order)
            dirty_client = srilm.Client(dirty_port, order)



    signal.alarm(0)
    clean_client.close()
    dirty_client.close()
    outqueue.put(None) # tell the main process that we are done


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('out_dir')
    parser.add_argument('--article-list', '-a', help='only include the articles listed in this file')
    parser.add_argument('--clean-port', '-c', default='5000', help='which port should the "clean" model bind to (default: 5000)')
    parser.add_argument('--dirty-port', '-d', default='5001', help='which port should the "dirty" model bind to (default: 5001)')
    parser.add_argument('--processes', '-p', default=1, type=int, help="run this many processes in parallel (default: 1)")
    parser.add_argument('--blacklist', '-b', help="do not include the articles listed in this file")
    args = parser.parse_args()



    blacklist = []
    if args.blacklist:
        for line in util.file2s(args.blacklist).splitlines():
            line = line.strip()
            if line:
                blacklist.append(line)

    #read the articles
    if args.article_list:
        names = []
        with codecs.open(args.article_list, 'r', 'utf-8') as f:
            for name in f:
                names.append(name.strip())
        names.sort()
        entries = [make_entry(n) for n in names if not n in blacklist]
    else:
        names = list_articles.articles()
        names.sort()
        entries = [make_entry(n) for n in names if not n in blacklist]
    names = multiprocessing.Queue()

    #entries = list(entries)
    #entries.sort(key=lambda e:e.name)
    for e in entries:
        names.put(e)

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
        p = multiprocessing.Process(target=worker, name=str(i), args=(args.out_dir, names, ret,
                                                                      order, args.clean_port, args.dirty_port, 
                                                                      preprocessor, gml_purifier, senseg_purifier,
                                                                      ))            
        p.daemon = True
        p.start()

    #collect the finished text
    curr_pcs = args.processes
    saved = 0#first non-saved
    processed = 0#first non-processed 
    ready = 0#entries that can be written to disk

    i = 0
    while curr_pcs > 0:
        entry = ret.get()
        if not entry:
            curr_pcs -= 1
        else:
            entries[entry[0]] = entry

            if i % 1000 == 0:
                log.logger.info(str(entry[0]) + " id (" + str(ready) + " ready)")

            while processed < len(entries) and entries[processed][2] != None:
                if entries[processed][2].strip():
                    if not u'⌊δ' in entries[processed][2]:
                        log.logger.error("Missing fist line of " + entries[processed][1])
                    ready += 1
                processed += 1

                if ready == 100:
                    ready = 0
                    write_segment(args.out_dir, entries[saved:processed])
                    saved = processed

        i += 1


    if saved < len(entries):
        write_segment(args.out_dir, entries[saved:])
    clean.stop()
    dirty.stop()
