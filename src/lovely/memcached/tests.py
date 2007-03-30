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

import unittest
from zope.testing import doctest
from zope.testing.doctestunit import DocTestSuite, DocFileSuite

def test_suite():
    level1Suites = (
        DocTestSuite(
        'lovely.memcached.utility',
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),
        )
    level2Suites = (
        DocFileSuite(
        'README.txt',
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),
        )
    for suite in level2Suites:
        suite.level = 2
    return unittest.TestSuite(level2Suites + level1Suites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
