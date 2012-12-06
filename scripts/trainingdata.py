#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#
import argparse, os, csv, random, shutil, codecs, sys, re
import multiprocessing, logging, Queue, time, traceback
from mwlib import wiki, nshandling, advtree
import paths, classify, template, node, util, srilm, log
import list_articles

DEBUG = log.DEBUG
    
        
def isclean(section):
    #to be considered clean a section must:
    # * have at least four paragraphs
    # * a unique heading

    heading = section.heading.replace('_', '-').replace('\n', ' ')
    if not heading in _sects:
        return False
    elif _sects[heading][0] > 1:
        return False
    
    pars = section.getNodesByClass(advtree.Paragraph)
    if len(pars) < 4:
        return False

    return True



def isdirty(section):
    #to be considered dirty a section:
    # * must have less than 750 characters in its body and its heading must be used more than 5000 times
    # * or _dirty["heading"]  == True
    
    heading = section.heading.replace('_', '-').replace('\n', ' ')

    if section.title in _dirty:
        return _dirty[section.title]
    elif heading not in _sects:
        return False
    elif len(section.content.strip()) == 0:
        return False
    elif _sects[heading][0] > 5000 and _sects[heading][1] < 750:
        return True
    else:
        return False

 
_sects = {} #section headings (count, avg_len)
_chunk_size = 10000000 #write ~10M characters in each file
_dirty = {
    "Deaths": True,
    "Births": True,
    "Publications": True,
    "Awards": False,
    "Geography": False, 
    "Education": False,
    "Transportation": False,
    "Personal life": False,
    "Family": False,
    "Trivia": False,
    "Results": False,
    "People": False,
    "Achievments": False,
    "Transport": False,
}

def write_section(path, chunk, num=0):
    name = multiprocessing.current_process().name + "-" + str(num)

    string = srilm.explode(chunk)
    fp = codecs.open(os.path.join(path, name) + '.exploded', 'w')
    fp.write(string)
    fp.close()


def worker(outdir, inqueue, outqueue, purifier):

    env = purifier.env
    
    
    dirty_dir = os.path.join(outdir, "dirty")
    clean_dir = os.path.join(outdir, "clean")

    clean_buf = ''
    clean_num = 0
    dirty_buf = ''
    dirty_num = 0

    while True:
        try:
            #get the name of the next article
            name = inqueue.get(True, 1)
            #purify it
            sections = purifier.parse_and_purify(name)
            if not sections:
                continue
            #divide the sections into clean and dirty
            clean = ''
            dirty = ''
            for s in sections:
                if isdirty(s):
                    dirty += s.string
                if isclean(s):
                    clean += s.string


            #add the result to our buffers and save them if they are big enough 
            clean_buf += clean
            dirty_buf += dirty
            if len(clean_buf) >= _chunk_size:
                write_section(clean_dir, clean_buf, clean_num)
                clean_buf = ''
                clean_num += 1
            if len(dirty_buf) >= _chunk_size:
                write_section(dirty_dir, dirty_buf, dirty_num)
                dirty_buf = ''
                dirty_num += 1

            #tell the main process how many chars we have
            outqueue.put((len(clean), len(dirty)))
        except Queue.Empty as excp:
            #save the data we have
            if len(dirty_buf) > 0:
                write_section(dirty_dir, dirty_buf, dirty_num)
            if len(clean_buf) > 0:
                write_section(clean_dir, clean_buf, clean_num)
            #tell the main process that we're shutting down
            outqueue.put(None)
        except Exception as excp:
            msg = name + u": " + unicode(excp)
            log.logger.error(msg.encode("utf-8", "ignore"))
            if DEBUG:
                log.logger.error(traceback.format_exc())



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('sections', help="list of section headings")
    parser.add_argument('outdir')
    parser.add_argument('--processes', '-p', type=int, default=1)
    parser.add_argument('--max', '-m', type=int, help="get no more than this many articles")
    parser.add_argument('--exclude', '-e', type=str, help="list of articles to exclude from the training data")
    args = parser.parse_args()
    
    env = wiki.makewiki(paths.paths["wikiconf"])
    act = template.create_actions(env, paths.paths["templaterules"], paths.paths["templatecache"])
    #log.logger.info("adress: " + repr(act.manager.address) + " autkey: " + repr(multiprocessing.current_process().authkey))
    elementrules = node.read_rules(paths.paths["noderules"])
    #elementrules = multiprocessing.Manager().dict(node.read_rules(paths.paths["noderules"]))

    purifier = classify.Preprocessor(env, act, elementrules)

    #read the sectioncounts
    f = codecs.open(args.sections, 'rb')
    reader = csv.reader(f, delimiter='_', quoting=csv.QUOTE_NONE)
    for r in reader:
        #skip the headings
        if reader.line_num > 1:
            try:
                _sects[r[0]] = (int(r[1]), int(r[2]))
            except Exception as excp:
                log.logger.error("malformed line in " + paths.paths["sections"] + ": " + str(r))
    f.close()


    #prepare the output dir
    if os.path.exists(args.outdir):
        shutil.rmtree(args.outdir)
    os.mkdir(args.outdir)
    os.mkdir(os.path.join(args.outdir, "clean"))
    os.mkdir(os.path.join(args.outdir, "dirty"))

    #add the page names to a queue
    names = multiprocessing.Queue()
    articles = list_articles.articles()
    random.shuffle(articles)
    if not args.max:
        args.max = len(articles)

    for a in articles[:args.max]:
        names.put(a)
        
    

    #start worker processes
    ret = multiprocessing.Queue()
    log.logger.info("Starting workers")
    for i in range(0, args.processes):
        p = multiprocessing.Process(target=worker, name=str(i), args=(args.outdir, names, ret, purifier))
            
        p.daemon = True
        p.start()

    #collect the results
    clean = 0
    dirty = 0
    curr_pcs = args.processes
    while curr_pcs > 0:
        r = ret.get()
        if not r:
            curr_pcs -= 1
        else:
            clean += r[0]
            dirty += r[1]


    log.logger.info("collected " + str(clean) + " clean characters and " + str(dirty) + " dirty")
    log.logger.info("Done")

        
