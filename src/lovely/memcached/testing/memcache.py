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

from datetime import datetime, timedelta

from lovely.memcached.utility import MemcachedClient


class TestMemcachedClient(MemcachedClient):
    """A memcache client which doesn't need a running memcache daemon"""

    def _instantiateClient(self, debug):
        return SimulatedMemcached()


class SimulatedMemcached(object):

    def __init__(self):
        self.cache = {}

    def getStats(self):
        return []

    def set(self, key, data, lifetime=0):
        # raise an error if not a string
        str(key)
        str(data)
        if lifetime:
            lifetime = datetime.now()+timedelta(seconds=lifetime)
        else:
            lifetime = None
        self.cache[key] = (data, lifetime)
        return True

    def get(self, key):
        str(key)
        data = self.cache.get(key, None)
        if data is None:
            return None
        if data[1] is None or datetime.now()<data[1]:
            return data[0]
        del self.cache[key]
        return None

    def delete(self, key):
        if key in self.cache:
            del self.cache[key]

    def flush_all(self):
        self.cache = {}

