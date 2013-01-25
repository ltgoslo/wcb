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
import paths, log, util


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
                log.logger.warning(str(self.pid) + " still running, attempting to kill")
                try:
                    os.kill(self.pid, signal.SIGTERM)
                except Exception as e:
                    log.logger.error(str(e))
            self.pid = -1

    def _start_server(self, q):
        log.logger.info("running: " + ' '.join(self.ngram_args))
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
                    log.logger.info(out.strip())
                    log.logger.info("server pid: " + str(server.pid))
                    q.put(server.pid)
                elif not "connection accepted" in out and not "probabilities served" in out:
                    log.logger.error(out.strip())
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
            log.logger("unexpected reply: " + reply)
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
    log.logger.debug("building " + lm)
#    print nargs

    if not overwrite:
        if os.path.exists(lm) and os.stat(lm).st_mtime > os.stat(trainset).st_mtime:
            log.logger.info(lm + ' already exists, not rebuilding it') 
            return 0.0

    start = time.time()
    p = subprocess.Popen(nargs, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
    err,out = p.communicate()
    if err:
        log.logger.error(' '.join(nargs) + ': ' + err)
    if out:
        log.logger.info(' '.join(nargs) + ': ' + out)

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

    log.logger.debug(str(len(ss)) + " sections")
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

    log.logger.debug("done")
    return probs
                
            

        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #parser.add_argument('pathsfile')
    #parser.add_argument('outdir')
    #parser.add_argument('--processes', '-p', type=int, default=1)
    args = parser.parse_args()
    #paths.read_paths(args.pathsfile)

    #start the servers
#    clean_srv = Server(3012, lm=paths.paths["clean lm"])
#    dirty_srv = Server(3013, lm=paths.paths["dirty lm"])
#    clean = Client(clean_srv.port)
#    dirty = Client(dirty_srv.port)

    #print vocab_size(paths.paths["clean lm"])
    #print lm_size(paths.paths["clean lm"])
    #print perplexity(paths.paths["clean lm"], "/ltg/larsjsol/master/exp/trainingdata/clean/0-0.exploded")
    #make_lm("/ltg/larsjsol/test.lm", "/ltg/larsjsol/master/exp/trainingdata/clean/0-0.exploded", 5, '-kndiscount')

    text = u"""<h2>Geography</h2>
<ImageLink />
<p>Alabama is the 30<sup>th</sup> largest state in the United States with 52,423 square miles (135,775Â kmÂ²) of total area: 3.19% of the area is water, making Alabama 23<sup>rd</sup> in the amount of surface water, also giving it the second largest inland waterway system in the <ArticleLink>United States</ArticleLink>. About three-fifths of the land area is a gentle plain with a general descent towards the <ArticleLink>Mississippi River</ArticleLink> and the Gulf of Mexico. The <ArticleLink>North Alabama</ArticleLink> region is mostly mountainous, with the <ArticleLink>Tennessee River</ArticleLink> cutting a large valley creating numerous creeks, streams, rivers, mountains, and lakes. A notable natural wonder in Alabama is <ArticleLink>"Natural Bridge"</ArticleLink> rock, the longest <ArticleLink>natural bridge</ArticleLink> east of the <ArticleLink>Rockies</ArticleLink>, located just south of <ArticleLink>Haleyville</ArticleLink>, in <ArticleLink>Winston County</ArticleLink>.</p>
<p>Alabama generally ranges in elevation from <ArticleLink>sea level</ArticleLink> at <ArticleLink>Mobile Bay</ArticleLink> to over 1,800Â feet (550Â m) in the <ArticleLink>Appalachian Mountains</ArticleLink> in the northeast. The highest point is <ArticleLink>Mount Cheaha</ArticleLink> (<Emphasized>see map</Emphasized>), at a height of 2,407Â ft (733Â m).</p>
<p>States bordering Alabama include <ArticleLink>Tennessee</ArticleLink> to the north; <ArticleLink>Georgia</ArticleLink> to the east; <ArticleLink>Florida</ArticleLink> to the south; and <ArticleLink>Mississippi</ArticleLink> to the west. Alabama has coastline at the <ArticleLink>Gulf of Mexico</ArticleLink>, in the extreme southern edge of the state.</p>
<p>Areas in Alabama administered by the <ArticleLink>National Park Service</ArticleLink> include <ArticleLink>Horseshoe Bend National Military Park</ArticleLink> near <ArticleLink>Alexander City</ArticleLink>; <ArticleLink>Little River Canyon National Preserve</ArticleLink> near <ArticleLink>Fort Payne</ArticleLink>; <ArticleLink>Russell Cave National Monument</ArticleLink> in <ArticleLink>Bridgeport</ArticleLink>; <ArticleLink>Tuskegee Airmen National Historic Site</ArticleLink> in <ArticleLink>Tuskegee</ArticleLink>; and <ArticleLink>Tuskegee Institute National Historic Site</ArticleLink> near <ArticleLink>Tuskegee</ArticleLink>.</p>
<p>Alabama also contains the <ArticleLink>Natchez Trace Parkway</ArticleLink>, the <ArticleLink>Selma To Montgomery National Historic Trail</ArticleLink>, and the <ArticleLink>Trail Of Tears National Historic Trail</ArticleLink>.</p>
<p>Suburban <ArticleLink>Baldwin County</ArticleLink>, along the Gulf Coast, is the largest county in the state in both land area and water area.</p>
<p>A {(Convert+5-mile (8Â km)+5+mi+km+0+sing=on)}-wide meteorite impact crater is located in <ArticleLink>Elmore County</ArticleLink>, just north of Montgomey. This is the <ArticleLink>Wetumpka crater</ArticleLink>, which is the site of "Alabama's greatest natural disaster".  A {(Convert+1000-foot (300Â m)+1000+f+m+sing=on)}-wide meteorite hit the area about 80Â million years ago. The hills just east of downtown <ArticleLink>Wetumpka</ArticleLink> showcase the erodedremains of the impact crater that was blasted into the bedrock, with the area labeled the <ArticleLink>Wetumpka crater</ArticleLink> or astrobleme ("star-wound") because of the concentric rings of fractures and zones of shattered rock that can be found beneath the surface. In 2002, Christian Koeberl with the Institute of Geochemistry University of Vienna published evidence and established the site as an internationally recognized impact crater.</p>"""
#    c = classify(text, clean, dirty)
#    print "classify(...): -> " + str(c),
#    if c > 0:
#        print " clean"
#    else:
#        print " dirty"

#print max_order('cache/lm/clean_3gram_10train_ukndiscount.lm')
