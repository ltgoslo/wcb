#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

import suffix_tree
import argparse, csv, time, codecs, re

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


def checknode(node, res, prefix):
    """
    Creates a dict with parts of template names and the ids of the matching
    templates.
    """
    if len(node.ids) > 5 or isinstance(node, suffix_tree.RootNode):
        s = prefix + re.sub(r'\$\d*$', '$', node.string)

        if len(s) > 4:
            if s in res:
                res[s].update(node.ids)
            else:
                res[s] = node.ids

        if not '$' in node.string:
            for c in node.children:
                checknode(c, res, s)

def printres(l):
    """
    Creates a csv file with the most frequent substrings based on inclusion
    count.

    It expects a list of list in the form count, string, ids
    """
    out = open(args.outfile, 'w')
    for i in l:
        out.write(str(i[0]) + '_' + i[1] + '_' + ', '.join([rows[x - 103][1] for x in i[2]]) + '\n')

    out.close()

def collapse(l):
    """
    Merge the elements in l that consists of the same templates.
    """
    count = 0
    string = 1
    ids = 2
    pre = l[0]

    res = []
    for r in l[1:]:
        #we are not interested in induvidual templates

        if pre[ids] == r[ids]:
            if len(r[string]) >  len(pre[string]): 
                pre[string] = r[string]
        else:
            res.append(pre)
            pre = r    
    
    return res

def complements(l):
    """
    Reduce the set of matching templates so each template is only counted once. 

    I.e it makes sure that the template sets for 'information' and 'box' 
    are disjunkt.
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



parser = argparse.ArgumentParser(description="Most frequent substrings in \
template names factored by inclusions")
parser.add_argument('templatelist', help="list of template inclusions, created \
with templatecount.py")
parser.add_argument('--word', '-w', action='store_true', 
                    help="examine substring based on word bounderies")
parser.add_argument('outfile')
args = parser.parse_args()


#read template-list
rows = []
f = open(args.templatelist, 'rb')
reader = csv.reader(f, delimiter='_', quoting=csv.QUOTE_NONE)

reader.next() #2496177 articles
reader.next() #direct_total_name
#skip the next hundred rows
for i in range(0, 100):
    reader.next()

for r in reader:
    #we only need direct inclusions and names
    rows.append([int(r[0]), r[2]])
f.close()

res = {}
l = list()

if args.word:
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
    #make each set disjunkt
    l = complements(l)


else:
#insert all names in to a suffix tree
    tree = suffix_tree.GeneralisedSuffixTree()
    tree.nextid = 103 # so the ids match the line numbers
    tree.short = 4    # dont bother with substring shorter than 4 charachters
    i = 0
    for r in rows:
        tree.add("^" + str(r[1]).lower())
        i += 1
        if i % 1000 == 0:
            print time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + ": " + str(i) + " strings added"

    print "Examining tree"
    checknode(tree.root, res, "")
    
    #create a list with count, substring, matching templates
    for k in res.keys():
        l.append([count(res[k]), k, res[k]])
    #sort it
    l.sort(key=lambda x: x[0], reverse=True)
    l = collapse(l)
    l = complements(l)

    
l.sort(key=lambda x: x[0], reverse=True)
print "Saving results"
printres(l)
print "Done"
