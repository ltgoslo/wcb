#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

import logging
import os

def getLogger(module):
    logger = logging.getLogger(module)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[%(asctime)s %(module)s.%(funcName)s()] %(message)s'))
    logger.addHandler(handler)


    if module in loglevels:
        logger.setLevel(loglevels[module])
    else:
        logger.setLevel(logging.WARN)
    
    return logger


DEBUG = False

loglevels = {'unspecified': logging.INFO}
if 'DEBUG' in os.environ:
    for module in os.environ['DEBUG'].split(':'):
        loglevels[module] = logging.DEBUG
if 'INFO' in os.environ:
    for module in os.environ['INFO'].split(':'):
        loglevels[module] = logging.INFO



logger = getLogger('unspecified') #some old scripts might still do log.logger.debug('Foo')
