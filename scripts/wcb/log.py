#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Lars Jørgen Solberg <supersolberg@gmail.com> 2013
#

import logging
import os
import ConfigParser
import wcb

loglevel_dict = {
    'WARN': logging.WARN,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG
}
default_log_level = logging.WARN

config_parser = ConfigParser.RawConfigParser()
config_parser.read(wcb.paths["cfg"])

if (config_parser.get('WCB', 'default_log_level')):
    default_log_level = loglevel_dict[config_parser.get('WCB', 'default_log_level')]

if (config_parser.has_option('WCB', 'log_directory')):
    logging.basicConfig(filename=str(config_parser.get('WCB', 'log_directory')) + 'wcb.log')

def getLogger(module):
    logger = logging.getLogger(module)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[%(asctime)s %(module)s.%(funcName)s()] %(message)s'))
    logger.addHandler(handler)

    if module in loglevels:
        logger.setLevel(loglevels[module])
    else:
        logger.setLevel(default_log_level)

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
