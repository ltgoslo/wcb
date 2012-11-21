#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  $Id$
#
# Lars J|rgen Solberg <larsjsol@sh.titan.uio.no> 2012
#

import argparse
import srilm, util

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    args = parser.parse_args()

    print srilm.unexplode(util.file2s(args.file))
