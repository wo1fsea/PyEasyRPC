# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2019/7/31
Description:
    test.py
----------------------------------------------------------------------------"""

import unittest
import os

cur_dir = os.path.dirname(os.path.abspath(__file__))
tests_dir = cur_dir + '/tests'

tests = unittest.defaultTestLoader.discover(tests_dir)
runner = unittest.TextTestRunner(verbosity=2)
runner.run(tests)
