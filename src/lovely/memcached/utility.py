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
import random
import sys
import time
import logging
import memcache
import cPickle
import threading
import persistent
import os
import socket
from zope.schema.fieldproperty import FieldProperty
from zope import interface
from interfaces import IMemcachedClient

TLOCAL = threading.local()

log = logging.getLogger('lovely.memcached')

# base namespace for key management
NS = 'lovely.memcached'
# namespace for key timesamps
STAMP_NS = NS + '.stamps'
# namespace for deps
DEP_NS = NS + '.dep'

class Storage(object):
    pass

class MemcachedClient(persistent.Persistent):
    interface.implements(IMemcachedClient)

    defaultNS = FieldProperty(IMemcachedClient['defaultNS'])
    servers = FieldProperty(IMemcachedClient['servers'])
    defaultLifetime = FieldProperty(
        IMemcachedClient['defaultLifetime'])
    trackKeys = FieldProperty(IMemcachedClient['trackKeys'])

    def __init__(self, servers=None, defaultAge=None,
                 defaultNS=None, trackKeys=None):
        if servers is not None:
            self.servers = servers
        if defaultAge is not None:
            self.defaultAge = defaultAge
        if defaultNS is not None:
            self.defaultNS = defaultNS
        if trackKeys is not None:
            self.trackKeys = trackKeys

    def getStatistics(self):
        return self.client.get_stats()


    def _getNS(self, ns, raw):
        if not ns and self.defaultNS:
            if raw:
                ns = str(self.defaultNS)
            else:
                ns = self.defaultNS
        return ns or None

    def set(self, data, key, lifetime=None, ns=None, raw=False,
            dependencies=[]):
        if lifetime is None:
            lifetime = self.defaultLifetime
        ns = self._getNS(ns, raw)
        if not raw:
            data = cPickle.dumps(data)
        elif not isinstance(data, str):
            raise ValueError, data
        log.debug('set: %r, %r, %r, %r' % (key,
                                           len(data), ns,
                                           lifetime))

        bKey = self._buildKey(key, ns, raw=raw)
        if self.client.set(bKey, data, lifetime):
            self._keysSet(key, ns, lifetime)
            self._depSet(bKey, ns, dependencies)
            return bKey
        return None

    def _depSet(self, key, ns, deps):
        for dep in deps:
            depKey = self._buildDepKey(dep, ns)
            keys = self.client.get(depKey)
            if keys is None:
                keys = (key,)
            else:
                keys = keys +  (key,)
            self.client.set(depKey, keys)

    def query(self, key, default=None, ns=None, raw=False):
        ns = self._getNS(ns, raw)
        res = self.client.get(self._buildKey(key, ns, raw=raw))
        if res is None:
            return default
        if raw:
            return res
        return cPickle.loads(res)

    def _buildDepKey(self, dep, ns):
        return DEP_NS + self._buildKey(dep, ns)

    def invalidate(self, key=None, ns=None, raw=False,
                   dependencies=[]):
        ns = self._getNS(ns, raw)
        log.debug('invalidate: %r, %r '% (key, ns))
        if self.trackKeys:
            self.client.delete(self._buildKey((ns, key), STAMP_NS))
        if key is not None:
            self.client.delete(self._buildKey(key, ns, raw))
        for dep in dependencies:
            depKey = self._buildDepKey(dep, ns)
            keys = self.client.get(depKey)
            if keys is not None:
                self.client.delete(depKey)
                for key in keys:
                    self.client.delete(key)

    def invalidateAll(self):
        # notice this does not look at namespaces
        self.client.flush_all()
        key = (tuple(self.servers), self.trackKeys)
        del self._storages()[key]

    def _buildKey(self, key, ns, raw=False):

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

        If we set the key to raw we must provide a string
        """
        if raw is True:
            if ns:
                key = ns+key
            if not isinstance(key, str):
                raise ValueError, repr(key)
            return key

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
#        servers = getattr(self.storage, 'servers', None)
#         if servers is not self.servers:
#             # we have a change in the list of servers
#             self.storage.client = None
#             self.storage.servers = self.servers
        client = getattr(self.storage, 'client', None)
        if client is None:
            client = self._instantiateClient(debug=0)
            self.storage.client = client
        return client

    def _storages(self):
        return TLOCAL.__dict__

    @property
    def storage(self):
        # we use a thread local storage to have a memcache client for every
        # thread.
        key = (tuple(self.servers), self.trackKeys)
        storage = self._storages().get(key)
        if storage is None:
            log.info('Creating new local storage with key %r' % (key,))
            storage = self._storages()[key] = Storage()
        if self.trackKeys and not hasattr(storage, 'keys'):
            tName = threading.currentThread().getName()
            pid = os.getpid()
            hostName = socket.gethostname()
            uid = '%s-%s-%s' % (hostName,
                                pid,
                                tName)
            self._keysInit(storage, uid)
        return storage

    def _instantiateClient(self, debug):
        return memcache.Client(self.servers, debug=debug)

    def _keysInit(self, storage, uid, clients=None):
        log.info('Init of keytracking uid: %r' % uid)
        storage.keys = {}
        storage.uid = uid
        storage.dirtyKeys = set()
        storage.lastUpdates = {}
        if clients is None:
            clients = self._getClients()
        if not storage.uid in clients:
            log.info('Adding new client uid: %r' % storage.uid)
            clients.add(storage.uid)
            self.set(clients, 'clients', lifetime=0, ns=NS)
        return clients

    def _keysSet(self, key, ns, lifetime):
        """track a key"""
        if not self.trackKeys or ns in (NS, STAMP_NS): return
        s = self.storage
        keys = s.keys.get(ns)
        if keys is None:
            keys = set([key])
            s.keys[ns] = keys
        elif not key in keys:
            keys.add(key)
        self.set(s.uid, (ns, key), lifetime=lifetime, ns=STAMP_NS)
        self.set(keys, (s.uid, ns), lifetime=0, ns=NS)

    def _getClients(self):
        return self.query('clients', set(), ns=NS)

    def keys(self, ns=None):
        if not self.trackKeys:
            raise NotImplementedError, "trackKeys not enabled"
        res = set()
        s = self.storage
        t = time.time()
        clients = self._getClients()
        changed = False
        if not s.uid in clients:
            clients = self._keysInit(s, s.uid, clients)
        localKeys = s.keys.get(ns, set())
        for client in clients:
            if client == s.uid:
                v = localKeys
            else:
                v = self.query((client, ns), default=set(), ns=NS)
            res.update(v)
        # look at the timestamps
        for k in list(res):
            uid = self.query((ns, k), ns=STAMP_NS)
            if uid is None:
                if localKeys:
                    changed=True
                    localKeys.discard(k)
                res.discard(k)
        if changed:
            # update the server, we do this just here, because the
            # keys method always looks at the stamps, so it is not
            # required to delete keys from the stored keylist at key
            # setting time
            s.dirtyKeys.add(ns)
            self._keysUpdate(localKeys, ns)
        return res


    def _keysUpdate(self, keys, ns):
        # updates the key set of this thread on server
        s = self.storage
        if not ns in s.dirtyKeys:
            return
        t = time.time()
        # we update only every 5 minutes
        if s.lastUpdates.get(ns, 0) + 300 > t:
            return
        self.set(keys, (s.uid, ns), lifetime=0, ns=NS)
        s.dirtyKeys.discard(ns)
        s.lastUpdates[ns] = t

