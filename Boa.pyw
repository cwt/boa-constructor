#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-

import sys
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    set_default_encoding = getattr(sys, 'setdefaultencoding')
    set_default_encoding('utf-8')

import Boa

Boa.main(sys.argv[1:])
