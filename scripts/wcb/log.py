#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Lars Jørgen Solberg <supersolberg@gmail.com> 2013
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


loglevels = {
    'unspecified': logging.INFO,
    '__main__': logging.INFO
}
if 'DEBUG' in os.environ:
    for module in os.environ['DEBUG'].split(':'):
        loglevels[module] = logging.DEBUG

if 'INFO' in os.environ:
    for module in os.environ['INFO'].split(':'):
        loglevels[module] = logging.INFO



logger = getLogger('unspecified') #some old scripts might still do log.logger.debug('Foo')
