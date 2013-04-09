#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#
import argparse, multiprocessing, subprocess, logging
import os, re, signal, time, socket, string, codecs, atexit
import inspect, gzip, mimetypes
import log, util

logger = log.getLogger(__name__)

class Server:
    pid = -1
    port = None
    lm = ''
    order = 5
    ngram_args = []
    q = None

    def __init__(self, port, lm, order=None, extra_args=[]):
        self.port = port
        self.lm = lm
        if order:
            self.order = int(order)
        else:
            self.order = max_order(lm)

        self.ngram_args = ["ngram", "-lm", self.lm, "-server-port", str(self.port), "-order", str(self.order)] + extra_args
        if not '-unk' in self.ngram_args:
            self.ngram_args.append('-unk')

        self.q = multiprocessing.Queue()
        p = multiprocessing.Process(target=Server._start_server, args=(self, self.q))
        p.daemon = True
        p.start()
        self.pid = self.q.get()
        atexit.register(self.stop)

    def __del__(self):
        self.stop()

    def stop(self):
        if self.pid != -1:
            self.q.put(None)
            time.sleep(2)
            if os.path.exists("/proc/" + str(self.pid)):
                logger.warning(str(self.pid) + " still running, attempting to kill")
                try:
                    os.kill(self.pid, signal.SIGTERM)
                except Exception as e:
                    logger.error(str(e))
            self.pid = -1

    def _start_server(self, q):
        logger.info("running: " + ' '.join(self.ngram_args))
        #print args
        server = subprocess.Popen(self.ngram_args, stderr=subprocess.PIPE, shell=False)
        #wait until the server is ready
        while True:
            time.sleep(1)
            if not q.empty():
                server.terminate()
                break
            out = server.stderr.readline()
            if len(out) > 0:
                if "starting prob server on port" in out:
                    logger.info(out.strip())
                    logger.info("server pid: " + str(server.pid))
                    q.put(server.pid)
                elif not "connection accepted" in out and not "probabilities served" in out:
                    logger.error(out.strip())
                    raise Exception(out.strip())

class Client:
    port = None
    conn = None
    order = 5
    _line_sep = re.compile('\n+', re.U)
    _buf = ''
    word_limit = 131072

    def __init__(self, port, order):
        self.port = int(port)
        self.order = int(order)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect(("localhost", self.port))
        self.conn.settimeout(60)
        reply = self.conn.recv(32)
        if not "probserver ready" in reply:
            logger("unexpected reply: " + reply)
            raise Exception("unexpected reply: " + reply)
        
    def __del__(self):
        if self.conn:
            self.conn.close()
        
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def prob(self, s):
        """Returns the log10 probability of s"""
        ngrams = self.format_ngrams(s)
        n = len(ngrams)
        self.send('\n'.join(ngrams))
        return float(self.recv(n))


    def send(self, s):
        self.conn.sendall(s)

    def format_ngrams(self, s):
        """returns a list of ngrams"""
        ret = []
        for t in self._line_sep.split(s):
            t = t.strip()
            if len(s) > 0:
                line = '<s> ' + t + ' </s>'
                words = line.split()
                for i in xrange(2, len(words) + 1):
                    ret.append(' '.join(words[max(0, i - self.order):i]) + '\n')
        return ret

    _prob_sep = re.compile('[\0\n]+')
    def recv(self, n):
        buf = self._buf
        p = Client._prob_sep.split(buf)
        probs = p[:-1]
        if len(probs) > 0 and probs[0] == '':
            probs = probs[1:]
        buf = p[-1]
        while len(probs) < n:
            reply = buf + self.conn.recv(4096)
            p = Client._prob_sep.split(reply)
            probs.extend(p[:-1])
            buf = p[-1]
            
        self._buf = '\n'.join(probs[n:]) + '\n' + buf
        ret = 0.0
        for p in probs[:n]:
            if p:
                ret += float(p)
        return ret

def vocab_size(lm):
    ngram1 = re.compile(r'^ngram 1=(\d+)')
    if mimetypes.guess_type(lm)[1] == 'gzip':
        f = gzip.open(lm, 'rb')
    else:
        f = codecs.open(lm, 'r')

    for line in f:
        if '\1-grams:' in line:
            f.close()
            break
        m =  ngram1.match(line)
        if m:
            f.close()
            return int(m.group(1)) - 3 #dont count <s> </s> <unk>

    raise Exception('Could not find vocabulary size in ' + lm)
    
        
def lm_size(lm):
    size = float(os.path.getsize(lm))
    units = [' b', ' kb', ' mb', ' gb']
    for u in units:
        if size < 1024:
            return str(round(size, 1)) +  u
        else:
            size /= 1024
    
    return str(round(size, 2)) + units[-1]

_ppl_rx = re.compile(r'ppl= ([^ ]+)', flags=re.M)
def perplexity(lm, testset, order=None):
    """returns a tuple (perplexity, time taken)"""
    assert os.path.exists(lm)
    assert os.path.exists(testset)
    if not order:
        order = max_order(lm)
    start = time.time()
    p = subprocess.Popen(['ngram', '-unk', '-order', str(order), '-lm', lm, '-ppl', testset], stdout=subprocess.PIPE)
    output = p.communicate()[0]
    stop = time.time()
    m = _ppl_rx.search(output)
    ppl = float(m.group(1))
    return (ppl, round(stop - start))

def max_order(lm):
    if mimetypes.guess_type(lm)[1] == 'gzip':
        f = gzip.open(lm, 'rb')
    else:
        f = codecs.open(lm, 'r')
    l = f.readline()
    order = 0
    while l != '' and '\\1-grams:' not in l:
        m = re.match(r'ngram (\d+)', l)
        if m:
            order = int(m.group(1))
        l = f.readline()
    f.close()
    return order

def make_lm(lm, trainset, order, args, overwrite=False):
    nargs = ['ngram-count', '-unk', '-text', trainset, '-lm', lm, '-order', str(order), '-memuse']
    nargs.extend(args)
    logger.debug("building " + lm)
#    print nargs

    if not overwrite:
        if os.path.exists(lm) and os.stat(lm).st_mtime > os.stat(trainset).st_mtime:
            logger.info(lm + ' already exists, not rebuilding it') 
            return 0.0

    start = time.time()
    p = subprocess.Popen(nargs, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
    err,out = p.communicate()
    if err:
        logger.error(' '.join(nargs) + ': ' + err)
    if out:
        logger.info(' '.join(nargs) + ': ' + out)

    stop = time.time()
    return round(stop - start)
    

def explode(s):
    s = ' '.join([l for l in s])
    if isinstance(s, unicode):
        s = s.encode('ascii', 'backslashreplace') # shoud have used s.encode('unicode_escape')
    return s

def unexplode(s):
    if s[0] in string.whitespace:
        s = s[1:]

    s = s.decode('unicode_escape')
    return u''.join([c for i,c in enumerate(s) if i % 2 == 0])
        

def classify(s, client1, client2):
    return classify_exploded(explode(s), client1, client2)

def classify_exploded(s, client1, client2):
    """Returns a positive float if client1/server1 gives the best probability and a negative float if client2/server2 gives the best probability"""
    return classify_bulk([s], client1, client2)[0]



def classify_bulk(ss, client1, client2):

    assert isinstance(client1, Client)
    assert isinstance(client2, Client)

    if inspect.isgenerator(ss):
        ss = [s for s in ss]

    logger.debug(str(len(ss)) + " sections")
    max_size = 131072 #adjust until deadlock...
    probs = [0.0] * len(ss) # probability for each s
    ngrams = [] #all ngrams
    str_ptr = [] #points to the s that this ngram belongs to 
    # e.g if str_ptr[n_id] -> s_id

    #populate ngrams[] and str_ptr[]
    for s_id in range(0, len(ss)):
        n = client1.format_ngrams(ss[s_id])
        ngrams.extend(n)
        str_ptr.extend([s_id] * len(n))
        

    size = 0
    n_id = 0 #ngram id
    n_start = n_id
    chunk_size = 0
    while n_id < len(ngrams):
        if chunk_size < max_size:
            chunk_size += len(ngrams[n_id])
            n_id += 1

        if chunk_size >= max_size or n_id == len(ngrams):
            #print "n_id: %i/%i " % (n_id, len(ngrams))
            #send the chunk to the prob servers
            chunk = ''.join(ngrams[n_start:n_id])
            client1.send(chunk)
            client2.send(chunk)
            #collect the results
            while n_start < n_id:
                s_id = str_ptr[n_start]
                n = 0
                while n_start < n_id and str_ptr[n_start] == s_id:
                    n += 1
                    n_start += 1
                probs[s_id] += (client1.recv(n) - client2.recv(n))
                #n_start += 1
                chunk_size = 0

    logger.debug("done")
    return probs
                
if __name__ == "__main__":
    pass
