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


import md5
import logging
import memcache
import cPickle
from threading import local
import persistent

from zope.schema.fieldproperty import FieldProperty
from zope import interface
from interfaces import IMemcachedClient

log = logging.getLogger('lovely.memcached')

class MemcachedClient(persistent.Persistent):
    interface.implements(IMemcachedClient)

    defaultNS = FieldProperty(IMemcachedClient['defaultNS'])
    servers = FieldProperty(IMemcachedClient['servers'])
    defaultLifetime = FieldProperty(IMemcachedClient['defaultLifetime'])
    
    def __init__(self, servers=None, defaultAge=None,
                 defaultNS=None):
        if servers is not None:
            self.servers = servers
        if defaultAge is not None:
            self.defaultAge = defaultAge
        if defaultNS is not None:
            self.defaultNS = defaultNS

    def getStatistics(self):
        return self.client.get_stats()

    def set(self, data, key, lifetime=None, ns=None):
        if lifetime is None:
            lifetime = self.defaultLifetime
        ns = ns or self.defaultNS or None

        data = cPickle.dumps(data)
        log.debug('set: %r, %r, %r, %r' % (key, len(data), ns, lifetime))
        self.client.set(self._buildKey(key, ns), data, lifetime)

    def query(self, key, default=None, ns=None):
        ns = ns or self.defaultNS or None
        res = self.client.get(self._buildKey(key, ns))
        if res is None:
            return default
        return cPickle.loads(res)

    def invalidate(self, key, ns=None):
        ns = ns or self.defaultNS or None
        log.debug('invalidate: %r, %r '% (key, ns))
        self.client.delete(self._buildKey(key, ns))

    def invalidateAll(self):
        # notice this does not look at namespaces
        self.client.flush_all()

    def _buildKey(self, key, ns):

        """builds a key for key and ns, if key is a persistent
        object its oid is used
        
        >>> vc1 = MemcachedClient()
        >>> k1 = vc1._buildKey(1, None)

        of course the key is the same for same arguments
        >>> k1 == vc1._buildKey(1, None)
        True
        
        the key is an md5 digest
        >>> len(k1)
        32

        for different namespaces the keys are different
        
        >>> vc2 = MemcachedClient()
        >>> k2 = vc2._buildKey(1, u'vc2')
        >>> k2 != k1
        True

        if key has an oid this is taken

        >>> class A: pass
        >>> a = A()
        >>> b = A()
        >>> a._p_oid = "oid of a"
        >>> b._p_oid = "oid of a"
        >>> ka1 = vc1._buildKey(a, 1)
        >>> kb1 = vc1._buildKey(b, 1)
        >>> ka1 == kb1
        True
        >>> b._p_oid = "oid of b"
        >>> kb1 = vc1._buildKey(b, 1)
        >>> ka1 == kb1
        False
        
        """
        oid = getattr(key, '_p_oid', None)
        if oid is not None:
            key = oid
        if ns is not None:
            m = md5.new(cPickle.dumps((ns, key)))
        else:
            m = md5.new(cPickle.dumps(key))
        return m.hexdigest()

    @property
    def client(self):
        servers = getattr(self.storage, 'servers', None)
        if servers is not self.servers:
            # we have a change in the list of servers
            self.storage.client = None
            self.storage.servers = self.servers
        client = getattr(self.storage, 'client', None)
        if client is None:
            client = memcache.Client(self.servers, debug=0)
            self.storage.client = client
        return client

    @property
    def storage(self):
        # we use a thread local storage to have a memcache client for every
        # thread.
        if not hasattr(self, '_v_storage'):
            self._v_storage = local()
        return self._v_storage

