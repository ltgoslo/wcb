#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Lars Jørgen Solberg <supersolberg@gmail.com> 2013
#

import argparse
import multiprocessing
import collections
import Queue
import os
import codecs
import traceback
import re
import gzip
import signal
from timeit import default_timer as timer

import wcb
from wcb import gml
from wcb import senseg
from wcb import classify
from wcb import util
from wcb import srilm
from wcb import log
from wcb import template
from wcb import node
from wcb import purify

from mwlib import wiki


class TimeoutException(Exception):
    """ Used for debugging
    Sometimes the workers would freeze up"""
    pass

class Article:
    _nextid = 0
    def __init__(self, name):
        self.id = Article._nextid
        Article._nextid += 1
        self.name = name.encode('utf-8')
        self.gml = u''
        self.sections = []


def readfile_wm(filename):
    """ Returns the wiki markup and article name from a file as a tuple """
    with codecs.open(filename, 'r', 'utf-8') as f:
        title = readfile_wm.re_article_tag.sub('', f.readline().strip())
        content = u''
        line = f.readline()
        while line:
            content += line
            line = f.readline()
    return content, title
readfile_wm.re_article_tag = re.compile(r'</?article>', re.U)


def write_segment(outdir, articles):
    """ Writes the gml in 'articles' to disk """
    f = gzip.open(os.path.join(outdir, '{0:05}'.format(write_segment.seg_id) + '.gml.gz'), 'wb')
    for article in articles:
        sent_id = 0
        if article.gml and article.gml.strip():
            for line in article.gml.splitlines():
                line = gml.re_par.sub('\n', line)
                line = line.replace('___NL___', '')  # only insert paragraph breaks at the end of a sentence
                f.write('[1{0:07}{1:05}] |{2}\n'.format(write_segment.art_id, sent_id, line.encode('utf-8')))
                sent_id += 10
            write_segment.art_id += 1
        article.gml = None
    write_segment.seg_id += 1

# starting point for WikiWoods 1.0/2.0
write_segment.seg_id = 101
write_segment.art_id = 100



def worker(outdir, inqueue, outqueue,
           order, clean_port, dirty_port,
           preprocessor, gml_purifier,
           senseg_purifier, plain_files):
    clean_client = srilm.Client(clean_port, order)
    dirty_client = srilm.Client(dirty_port, order)

    logger = log.getLogger(__name__)

    def timeout_handler(signum, frame):
        raise TimeoutException()
    signal.signal(signal.SIGALRM, timeout_handler)

    done = False
    while not done:
        try:
            # signal.alarm(3600) #somethimes the workers freeze up...
            # get 100 entries
            articles = collections.deque([])
            i = 0
            try:
                while i < 100:
                    article = inqueue.get(True, 1)
                    articles.append(article)
                    i += 1
            except Queue.Empty as excp: # we're done when the queue is emtpy
                done = True
            sections = collections.deque([])
            for article in articles:
                if plain_files:
                    w_markup, name = readfile_wm(article.name)
                    article.sections = preprocessor.purify_string(w_markup, name)
                else:
                    article.sections = preprocessor.parse_and_purify(article.name)
                if (article.sections):
                    sections.extend(article.sections)
            classify.classify(sections, clean_client, dirty_client)

            for article in articles:
                if (article.sections):
                    gml.filter_sections(article.sections)
                    for sect in article.sections:
                        if sect.clean:
                            text = senseg.senseg(senseg_purifier.node2str(sect.tree))
                            lines = purify.markup_sentences(gml_purifier, sect, re.split('\n+', text), gml.escape)
                            article.gml += '\n'.join(lines) + '\n'
                        elif sect.sprint:
                            article.gml += gml_purifier.markup_heading(sect) + '\n'

                    if article.gml:
                        article.gml = gml.fix_templates(article.gml)
                    article.sections = None
                else:
                    article.gml = None
                outqueue.put(article)

        except Exception as excp:
            msg = repr(excp)
            logger.error(msg.encode("utf-8", "ignore"))
            logger.error(traceback.format_exc())
            if articles:
                for article in articles:
                    article.sections = None
                    if not article.gml:
                        article.gml = u''
                    outqueue.put(article)
            clean_client.close()
            dirty_client.close()
            clean_client = srilm.Client(clean_port, order)
            dirty_client = srilm.Client(dirty_port, order)

    signal.alarm(0)
    clean_client.close()
    dirty_client.close()
    outqueue.put(None)  # tell the main process that we are done

def format_seconds(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return "%dd:%dh:%02dm:%02ds" % (d, h, m, s)

def log_progress(start_time, total_article_count, article_progress, empty_articles):
    logger.info("Progress: %.3f%% (saved article %d of %d)" % ((article_progress / float(total_article_count)) * 100, article_progress, total_article_count))
    articles_left = total_article_count - article_progress
    time_elapsed = timer() - start_time
    time_per_article = time_elapsed / float(article_progress)
    estimated_time_left = articles_left * time_per_article

    logger.info("Empty articles (probably redirects): %d of %d" % (empty_articles, article_progress))
    logger.info("Time per article: %.3fs" % time_per_article)
    logger.info("Time elapsed: " + format_seconds(time_elapsed))
    logger.info("Estimated time left: " + format_seconds(estimated_time_left))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('out_dir')
    parser.add_argument('--clean-port', '-c', default='5000', help='which port should the "clean" model bind to (default: 5000)')
    parser.add_argument('--dirty-port', '-d', default='5001', help='which port should the "dirty" model bind to (default: 5001)')
    parser.add_argument('--processes', '-p', default=1, type=int, help="run this many processes in parallel (default: 1)")
    parser.add_argument('--blacklist', '-b', help="do not include the articles listed in this file")
    lst_grp = parser.add_mutually_exclusive_group()
    lst_grp.add_argument('--article-list', '-a', help='only include the articles listed in this file')
    lst_grp.add_argument('--file-list', '-f', help='list of plain files to be used instead of a dump')

    args = parser.parse_args()

    logger = log.getLogger(__name__)

    blacklist = []
    if args.blacklist:
        for line in util.file2s(args.blacklist).splitlines():
            line = line.strip()
            if line:
                blacklist.append(line)

    logger.info("Getting list of articles from the cache")
    # get a list of article names
    if args.article_list or args.file_list:
        filename = args.article_list if args.article_list else args.file_list
        names = []
        with codecs.open(filename, 'r', 'utf-8') as f:
            for name in f:
                names.append(name.strip())
    else:
        names = util.articles()

    names.sort()
    articles = [Article(n) for n in names if not n in blacklist]
    article_count = len(articles)
    logger.info("Parsing a total of " + str(len(articles)) + " articles")
    names = multiprocessing.Queue()
    for e in articles:
        names.put(e)

    env = wiki.makewiki(wcb.paths["wikiconf"])
    act = template.create_actions(env, wcb.paths["templaterules"], wcb.paths["templatecache"])

    # the classifier
    order = srilm.max_order(wcb.paths["clean lm"])
    clean = srilm.Server(args.clean_port, wcb.paths["clean lm"])
    dirty = srilm.Server(args.dirty_port, wcb.paths["dirty lm"])
    preprocessor = classify.Preprocessor(env, act, node.read_rules(wcb.paths["noderules"]))
    # gml
    gml_purifier = purify.Purifier(env, act, node.read_rules(wcb.paths["noderules_gml"]))
    # senseg
    senseg_purifier = purify.Purifier(env, act, node.read_rules(wcb.paths["noderules_senseg"]))
    senseg_purifier.extra_newlines = True

    ret = multiprocessing.Queue() # the processed articles returned from worker()
    logger.info("starting " + str(args.processes or 1) + " workers")
    for i in range(0, args.processes):
        p = multiprocessing.Process(target=worker, name=str(i), args=(args.out_dir, names, ret,
                                                                      order, args.clean_port,
                                                                      args.dirty_port,
                                                                      preprocessor, gml_purifier,
                                                                      senseg_purifier, args.file_list))
        p.daemon = True
        p.start()

    # collect the finished text
    curr_pcs = args.processes
    saved = 0  # idx of first non-saved
    processed = 0  # idx of first non-processed
    ready = 0  # entries that can be written to disk
    empty_articles = 0

    articles = [None] * len(articles)

    i = 0
    last_estimate = None
    start_time = timer()
    estimate_bulk_size = 2500
    write_bulk_size = 100

    while curr_pcs > 0:
        article = ret.get()
        if not article:
            curr_pcs -= 1
        else:
            articles[article.id] = article

            while processed < article_count and articles[processed] != None:
                processed_article = articles[processed]
                if processed_article.gml and processed_article.gml.strip():
                    # simple sanity check, all articles must have a top level heading
                    if not u'⌊δ' in processed_article.gml:
                        logger.error("Missing first line of " + processed_article.name)
                    ready += 1
                else:
                    empty_articles += 1
                processed += 1

                if ready == write_bulk_size:
                    ready = 0
                    write_segment(args.out_dir, articles[saved:processed])
                    saved = processed
                    if (not last_estimate or (saved - last_estimate) > estimate_bulk_size):
                        last_estimate = saved
                        log_progress(start_time, article_count, saved, empty_articles)

        i += 1
    # add the remaining articles to the corpus
    if saved < len(articles):
        write_segment(args.out_dir, articles[saved:])
        saved = len(articles)
    logger.info('Finished parsing')
    log_progress(start_time, article_count, saved, empty_articles)
    #shut down the n-gram servers
    clean.stop()
    dirty.stop()
