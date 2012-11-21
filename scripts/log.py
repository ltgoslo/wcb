#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

import multiprocessing, logging, os

DEBUG = False


if 'DEBUG' in os.environ and bool(os.environ['DEBUG']):
    DEBUG = True
else:
    DEBUG = False

try:
    tmp = logger
except NameError:
    logger = multiprocessing.log_to_stderr()
    if DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.handlers[0].setFormatter(logging.Formatter('[%(asctime)s %(funcName)s()] %(message)s'))
