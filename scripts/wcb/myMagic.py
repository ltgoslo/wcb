#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

from mwlib.templ import magics

class MyMagic(object):
    @magics.noarg
    def CURRENTHOUR(self):
        """Returns the current hour"""
        return self.utcnow.strftime("%H")

    @magics.noarg
    def LOCALHOUR(self):
        """Returns the current hour"""
        return self.now.strftime("%H")

    @magics.noarg
    def CONTENTLANGUAGE(self):
        """Returns the defualt interface language"""
        return self.wikidb.siteinfo["general"]["lang"]

    @magics.noarg
    def SCRIPTPATH(self):
        """Returns the scipt path"""
        return self.wikidb.siteinfo["general"]["scriptpath"]


    #these are only marginally better than the dummy resolver...
    @magics.noarg
    def PADDEDNUMBER(self):
        log.warn("magic word returning made up value")
        return "04"

    @magics.noarg
    def UNPADDEDNUMBER(self):
        log.warn("magic word returning made up value")
        return "4"

    @magics.noarg
    def REVISIONYEAR(self):
        log.warn("magic word returning made up value")
        return "2008"


    

magics.MagicResolver.__bases__ += (MyMagic,)
setattr(magics.DummyResolver, "CURRENTHOUR", MyMagic.CURRENTHOUR)
setattr(magics.DummyResolver, "LOCALHOUR", MyMagic.LOCALHOUR)
setattr(magics.DummyResolver, "CONTENTLANGUAGE", MyMagic.CONTENTLANGUAGE)
setattr(magics.DummyResolver, "LANGUAGE", MyMagic.CONTENTLANGUAGE)
setattr(magics.DummyResolver, "CURRENTMONTHNAMEGEN", magics.TimeMagic.CURRENTMONTHNAME)
setattr(magics.DummyResolver, "SCRIPTPATH", MyMagic.SCRIPTPATH)
setattr(magics.DummyResolver, "REVISIONDAY", MyMagic.UNPADDEDNUMBER)
setattr(magics.DummyResolver, "REVISIONMONTH", MyMagic.UNPADDEDNUMBER)
setattr(magics.DummyResolver, "REVISIONDAY2", MyMagic.PADDEDNUMBER)
setattr(magics.DummyResolver, "REVISIONMONTH", MyMagic.PADDEDNUMBER)
setattr(magics.DummyResolver, "REVISIONYEAR", MyMagic.REVISIONYEAR)
