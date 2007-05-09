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
from zope import component
from zope.testing import doctest
from zope.testing.doctestunit import DocTestSuite, DocFileSuite

from zope.app.keyreference import testing
from zope.app.intid.interfaces import IIntIds
from zope.app.intid import IntIds

from zope.app.testing import setup


def setUp(test):
    test.globs['root'] = setup.placefulSetUp(site=True)
    component.provideUtility(IntIds(), IIntIds)
    component.provideAdapter(testing.SimpleKeyReference)


def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    level1Suites = (
        DocFileSuite(
            'testing/README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),
        DocTestSuite(
            'lovely.memcached.utility',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),
        )
    level2Suites = (
        DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),
        )
    for suite in level2Suites:
        suite.level = 2
    return unittest.TestSuite(level2Suites + level1Suites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
