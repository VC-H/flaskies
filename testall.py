#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import doctest
import unittest
import hello, queriesdemo, templateview, basics, attrsview

suite = unittest.TestSuite()
suite.addTest(doctest.DocTestSuite(hello))
suite.addTest(doctest.DocTestSuite(queriesdemo))
suite.addTest(doctest.DocTestSuite(templateview))
suite.addTest(doctest.DocTestSuite(basics))
suite.addTest(doctest.DocTestSuite(attrsview))

runner = unittest.TextTestRunner(verbosity=1,failfast=True)
runner.run(suite)
