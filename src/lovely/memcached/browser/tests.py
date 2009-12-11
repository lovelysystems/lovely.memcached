##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id$
"""
__docformat__ = "reStructuredText"

import os.path
import unittest
from zope.testing import doctest
from zope.app.testing import functional
from zope.app.testing.functional import ZCMLLayer

memcachedLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'memcachedLayer', allow_teardown=True)


def test_suite():
    suite = functional.FunctionalDocFileSuite('README.txt')
    suite.layer = memcachedLayer
    suite.level = 2
    return unittest.TestSuite((suite,))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
