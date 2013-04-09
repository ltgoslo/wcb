#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Lars Jørgen Solberg <supersolberg@gmail.com> 2013
#

from mwlib.templ import magics
from mwlib.templ import marks
from mwlib.templ.nodes import *

from collections import Sequence
import copy

import myMagic, log

logger = log.getLogger(__name__)


class mark_argument(marks.mark): pass


#a mixin for  mwlib.templ.nodes.Template
#inserts mark_argument for all template calls
class MyTemplate:
    def _flatten(self, expander, variables, res):
        name = []

        flatten(self[0], expander, variables, name)
        name = u"".join(name).strip()
        if len(name)>256*1024:
            raise MemoryLimitError("template name too long: %s bytes" % (len(name),))

        args = self._get_args()

        remainder = None
        if ":" in name:
            try_name, try_remainder = name.split(':', 1)
            from mwlib.templ import magic_nodes
            try_name = expander.resolve_magic_alias(try_name) or try_name

            klass = magic_nodes.registry.get(try_name)
            if klass is not None:
                children = (try_remainder, )+args
                # print "MAGIC:", klass,  children
                klass(children).flatten(expander, variables, res)
                return
            
            if expander.resolver.has_magic(try_name):
                name=try_name
                remainder = try_remainder
                
            if name=='#ifeq':
                res.append(maybe_newline)
                tmp=[]
                if len(args)>=1:
                    flatten(args[0], expander, variables, tmp)
                other = u"".join(tmp).strip()
                remainder = remainder.strip()
                tmp = []
                if magics.maybe_numeric_compare(remainder, other):
                    if len(args)>=2:
                        flatten(args[1], expander, variables, tmp)
                        res.append(u"".join(tmp).strip())
                else:
                    if len(args)>=3:
                        flatten(args[2], expander, variables, tmp)
                        res.append(u"".join(tmp).strip())
                res.append(dummy_mark)
                return
        
        var = []
        if remainder is not None:
            var.append(remainder)
        
        for x in args:
            var.append(x)

        var = ArgumentList(args=var, expander=expander, variables=variables)
        
        rep = expander.resolver(name, var)
        if rep is not None:
            res.append(maybe_newline)
            res.append(rep)
            res.append(dummy_mark)
        else:            
            p = expander.getParsedTemplate(name)
            if p:
                oldidx = len(res)
                res.append(mark_start(repr(name)))
                for i in var.args:
                    if isinstance(i, Variable):
                        if isinstance(i[0], basestring) or isinstance(i[0], int):
                            val = var.get(i[0], None)
                        else:
                            val = u''
                    else:
                        val = i
                    if val:
                        if isinstance(val, basestring):
                            res.append(mark_argument(repr(val)))
                            #res.append(maybe_newline)
                        else:
                        #the argument can be any statement in the template system
                        #we have to expand it to get the wikitext
                            argres = []
                            flatten(val, expander, var, argres)
                            res.append(mark_argument(repr(u''.join([unicode(x) for x in argres]))))
                            #res.append(maybe_newline)

                res.append(maybe_newline)
                flatten(p, expander, var, res)
                res.append(mark_end(repr(name)))
                
                logger.debug("EXPANDING {{%r}} %r  ===> %s" % (name, var, "".join(res[oldidx:])))
        
Template.__bases__ = (MyTemplate,) + Template.__bases__
Template._flatten = MyTemplate._flatten
