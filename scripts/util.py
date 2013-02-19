#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

from mwlib import nuwiki, wiki
import codecs, re, shlex, subprocess
import srilm, log, paths, os, glob

logger = log.getLogger(__name__)

#cdb is no longer supported by mwlib, we use the third party module mwlib.cdb instead
def wiki_nucdb(path=None, lang="en", **kwargs):
    from mwlib.cdb import cdbwiki
    path = os.path.expanduser(path)
    db=cdbwiki.WikiDB(path, lang=lang)
    return nuwiki.adapt(db)
wiki.dispatch = dict(wiki=dict(nucdb=wiki_nucdb))

def normalize_and_get_image_path(x, *args):
    pass
nuwiki.adapt.normalize_and_get_image_path = normalize_and_get_image_path

#use the siteinfo.json from paths.txt if present
def load_siteinfo(lang="en"):
    from mwlib import siteinfo
    try:
        import simplejson as json
    except ImportError:
        import json

    if "siteinfo" in paths.paths and os.path.exists(paths.paths["siteinfo"]):
        siteinfo._cache[lang] = json.load(open(paths.paths["siteinfo"], "rb"))["query"]
load_siteinfo()


def s2file(string, path):
    """writes string to the file path"""
    f = codecs.open(path, 'w', 'utf-8')
    f.write(string)
    f.close()

def file2s(path):
    """reads the file path and returns it as a unicode string"""
    f = codecs.open(path, 'r', 'utf-8')
    s = f.read()
    f.close()
    return s


def is_exploded(filename):
    """checks if a file is 'exploded'"""

    f = codecs.open(filename, 'r', 'utf-8')
    for line in f:
        if re.search(r'<h(\d)>.*</h\1>', line, flags=re.U):
            f.close()
            return False
        if re.search(r'< h (\d) >.*< / h \1 >', line, flags=re.U):
            f.close()
            return True


def sections(filename):
    if is_exploded(filename):
        logger.debug(filename + " seems to be exploded")
        return exploded_sections(filename)
    else:
        logger.debug(filename + " seems to be unexploded")
        return unexploded_sections(filename)


def exploded_sections(filename):
    """generator that reads an exploded file and splits it into sections"""
    ret = u''
    heading = re.compile(r'< h (\d) >.*< / h \1 >')
    with codecs.open(filename, 'r', 'ascii') as f:
        for line in f:
            if heading.search(line):
                if len(ret) > 0:
                    yield ret
                    ret = u''
            ret += line
        yield ret
    f.close()


def unexploded_sections(filename):
    """generator that reads a file and splits it into sections, it strips out sections 
    delimiters '---...' and the annotator promts '[n] clean/dirty:'"""
    heading = re.compile(r'<h(\d)>.*</h\1>')
    delimiter = '------------------------------------------------------'
    prompt = re.compile(r'^\[\d+\] clean/dirty: $')
    ret = u''
    with codecs.open(filename, 'r', 'utf-8') as f:
        for line in f:
            if delimiter in line or prompt.match(line):
                continue
            if heading.search(line):
                if len(ret) > 0:
                    yield srilm.explode(ret)
                    ret = u''
            ret += line
        yield srilm.explode(ret)
    f.close()


def split(seq, n):
    """splits seq into n roughly equal sub-sequences"""
    #taken from http://stackoverflow.com/questions/2130016/splitting-a-list-of-arbitrary-size-into-only-roughly-n-equal-parts
    k, m = len(seq) / n, len(seq) % n
    return [seq[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in xrange(n)]


def classifiers(lm_dir):
    """returns a list of tuples in the form (label, clean_lm, dirty_lm, order)"""

    classifiers = []    
    order = re.compile(r'_(\d+)gram_')
    for clean in glob.iglob(lm_dir + '/clean_*'):
        name = os.path.basename(clean)
        m = order.search(name)
        
        classifiers.append((re.sub(r'\.lm(\.gz)?', '', name[6:]),
                            name,
                            'dirty_' + name[6:],
                            int(m.group(1))))

    return classifiers

def map_cmd(agenda, command, use_stdin=False):
    if isinstance(agenda, basestring):
        if os.path.isdir(agenda):
            agenda = os.listdir(agenda)
        else:
            agenda = file2s(agenda).encode('utf-8').splitlines()

    for item in agenda:
        if use_stdin:
            args = shlex.split(command)
            input = item
        else:
            args = shlex.split(command + ' ' + item)
            input = None

        proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        yield proc.communicate(input)

def cmd(command, input=None):
    command = shlex.split(command)
    if input:
        input = input.encode('utf-8')
    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out,err = proc.communicate(input)
    err = err.decode('utf-8')
    out = out.decode('utf-8')
    return out,err

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('sections')
    args = parser.parse_args()
    
    sections = unexploded_sections(args.sections)
    for s in sections:
        print '######################'
        print s
    
