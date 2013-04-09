#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

import argparse
import csv
import re

#subtract this from the template id to get its position in rows
R_OFFSET = 103

def count(ids):
    """
    Finds the total inclusions for the templates in the set ids
    """
    s = 0
    for id in ids:
        s += rows[id - R_OFFSET][0]
    return s

def printres(l):
    """
    Creates a csv file with the most frequent substrings based on inclusion
    count.

    It expects a list of list in the form count, string, ids
    """
    out = open(args.outfile, 'w')
    for i in l:
        out.write(str(i[0]) + '_' + i[1] + '_' + ', '.join([rows[x - R_OFFSET][1] for x in i[2]]) + '\n')

    out.close()

def complements(l):
    """
    Reduce the set of matching templates so each template is only counted once.

    I.e it makes sure that the template sets for 'information' and 'box'
    are disjunct.
    """
    res = []
    seen = [False]*len(rows)
    for r in l:
        newids = set([])
        for e in r[2]:
            if not seen[e - R_OFFSET]:
                newids.update(set([e]))
                seen[e - R_OFFSET] = True

        r[2] = newids
        r[0] = count(r[2])
        #we are not interested in induvidual templates
        if len(r[2]) > 1:
            res.append(r)
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Most frequenty used substrings in template names")
    parser.add_argument('templatelist', help="list of template inclusions, created with templatecount.py")
    parser.add_argument('outfile')
    parser.add_argument('--skip', help="ignore the SKIP most used templates", type=int, default=0)
    args = parser.parse_args()

    #read template-list
    rows = []
    f = open(args.templatelist, 'rb')
    reader = csv.reader(f, delimiter='_', quoting=csv.QUOTE_NONE)

    reader.next() #2496177 articles
    reader.next() #direct_total_name
    #skip the next SKIP rows
    for i in range(0, args.skip):
        reader.next()

    for r in reader:
        #we only need direct inclusions and names
        rows.append([int(r[0]), r[2]])
    f.close()

    res = {}
    l = list()

    R_OFFSET = args.skip + 3
    id = R_OFFSET
    for t in rows:
        strings = re.split(r'[^a-zA-Z0-9_^$]+', "^" + t[1].lower() + "$")
        #print t[1].lower()
        #print strings
        for part in strings:
            if len(part) < 4:
                continue
            if part in res:
                res[part].update(set([id]))
            else:
                res[part] = set([id])
        id += 1

    #create a list with count, substring, matching templates
    for k in res.keys():
        if len(res[k]) > 1:
            l.append([count(res[k]), k, res[k]])
    #sort it
    l.sort(key=lambda x: x[0], reverse=True)
    #make each set disjunct
    l = complements(l)


    l.sort(key=lambda x: x[0], reverse=True)
    print "Saving results"
    printres(l)
    print "Done"
