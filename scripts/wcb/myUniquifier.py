#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Lars Jørgen Solberg <supersolberg@gmail.com> 2013
#

from mwlib import uniq
import re

DEBUG = False

class MyUniquifier(uniq.Uniquifier):
    rep = ()
    def __init__(self):
        self.rep = ((re.compile(r'<h1>(.*?)</h1>', flags=re.U|re.I|re.S), u'= \1 ='), #rewrite html headings to wikimarkup
                    (re.compile(r'<h2>(.*?)</h2>', flags=re.U|re.I|re.S), u'== \1 =='),
                    (re.compile(r'<h3>(.*?)</h3>', flags=re.U|re.I|re.S), u'=== \1 ==='),
                    (re.compile(r'<h4>(.*?)</h4>', flags=re.U|re.I|re.S), u'==== \1 ===='),
                    (re.compile(r'<h5>(.*?)</h5>', flags=re.U|re.I|re.S), u'===== \1 ====='),
                    (re.compile(r'<h6>(.*?)</h6>', flags=re.U|re.I|re.S), u'====== \1 ======'))
        super(MyUniquifier, self).__init__()
    def replace_tags(self, txt):
        #let mwlibs uniqifier do its thing first
        txt = super(MyUniquifier, self).replace_tags(txt)
        for r in self.rep:
            txt = r[0].sub(r[1], txt)
        return txt
