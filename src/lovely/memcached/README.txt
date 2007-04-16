================
lovely.memcached
================

This package provides a utility that abstracts a client for memcached
servers see: http://www.danga.com/memcached.

IMPORTANT:

This test expects a memcache server running on local port 11211 which
is the default port for memcached.

This test runs in level 2 because it needs external resources to work. If you
want to run this test you need to use --all as parameter to your test.

Start a memcache instance with : memcached <optional options>

  >>> from lovely.memcached.utility import MemcachedClient
  >>> util = MemcachedClient()
  >>> util.servers
  ['127.0.0.1:11211']
  >>> util.defaultLifetime
  3600

To store a new value in the cache we just need to set it. The set
method returns the generated memcached key for the cache key.

  >>> util.set('cached value', 'cache_key')
  '188693688126b424eb89e1385eca6f01'
  >>> util.query('cache_key')
  'cached value'

If we no longer need the cached value we can invalidate it.

  >>> util.invalidate('cache_key')
  >>> util.query('cache_key') is None
  True

We have extended the original implementation on memcache.py for unicode.

  >>> key = util.set(u'cached value ä', 'cache_key')
  >>> util.query('cache_key') == u'cached value ä'
  True

We can invalidate the hole cache.

  >>> util.invalidateAll()
  >>> util.query('cache_key') is None
  True

Namespaces
==========

The utility provides the facility to use namespaces for keys in order
to let multiple utilities share the same memcached servers. A default
namespace can be set on the utility which is then used for any get and
query methods.

  >>> util1 = MemcachedClient(defaultNS=u'1')
  >>> util2 = MemcachedClient(defaultNS=u'2')
  >>> k = util1.set(1,1)
  >>> k = util2.set(2,2)
  >>> util1.query(1)
  1
  >>> util1.query(2) is None
  True
  >>> util1.query(2, ns=u'2')
  2
  >>> util2.query(2)
  2
  >>> util2.query(1) is None
  True

Note that if invalidatAll is called then all namespaces are deleted.

  >>> util1.invalidateAll()
  >>> util1.query(1) is util2.query(2) is None
  True

Getting existing keys
=====================

The memcached daemon does not provide the ability to retrieve a list
of all keys that are stored. In the utility this is implemented.

  >>> util1.keys()
  Traceback (most recent call last):
  ...
  NotImplementedError: trackKeys not enabled

The key tracking adds on overhead so it must be enabled explicitly.

  >>> util3 = MemcachedClient(trackKeys=True)
  >>> k = util3.set(1,1)
  >>> sorted(util3.keys())
  [1]
  >>> k = util3.set(2,2)
  >>> sorted(util3.keys())
  [1, 2]

Keys are global on memcached daemons. In order to test this we need to
have multiple threads.

  >>> import threading
  >>> log = []

Each thread has a differnt thread.

  >>> def differentConn():
  ...     util3.set(3,3)
  ...     log.append(sorted(util3.keys()))
  ...
  >>> thread = threading.Thread(target=differentConn)
  >>> thread.start()
  >>> thread.join()
  >>> log
  [[1, 2, 3]]

Keys expire too

  >>> k = util3.set(4, 4, lifetime=1)
  >>> sorted(util3.keys())
  [1, 2, 3, 4]
  >>> import time
  >>> time.sleep(2)
  >>> sorted(util3.keys())
  [1, 2, 3]
  >>> util3.query(4) is None
  True

Keys are always bound to a namespace.

  >>> k = util3.set(5, 5, ns=u'3')

If not give the ``None`` namespace is used.

  >>> sorted(util3.keys())
  [1, 2, 3]
  >>> sorted(util3.keys(u'3'))
  [5]

When an invalidation is done, the keys are updated.

  >>> util3.invalidate(1)
  >>> sorted(util3.keys())
  [2, 3]

This is just for an internal test, it updates the key records on the
server.

  >>> util3._keysUpdate([1,2], u'speed')


Raw Keys
========

Normaly the utility generates md5 hash keys in order to have short
keys. Sometimes, if an axternal application wants to have access to
the values, it is usefull to be able to set keys explicitly. This can
be done by setting the raw keyword argument to True on the set
and query methods.

  >>> util4 = MemcachedClient()

If raw is used, the key must be a string.

  >>> k = util.set(u'value of a', u'a', raw=True)
  Traceback (most recent call last):
  ValueError: u'a'

  >>> util.set(u'value of a', 'a', raw=True)
  'a'

The namespace is simply prepended to the key if provided. And must be
a string too.

  >>> util.set(u'value of a', 'a', ns=u'NS_', raw=True)
  Traceback (most recent call last):
  ValueError: u'NS_a'
  >>> util.set(u'value of a', 'a', ns='NS_', raw=True)
  'NS_a'
  >>> util.set(u'value of a', 'http://a/bc?x=1', ns='NS_', raw=True)
  
Now we need can get the value with the raw key.

  >>> util.query('a', raw=True)
  u'value of a'
  >>> util.query('a', raw=False) is None
  True

Also invalidation takes a raw argument.

  >>> util.invalidate('a')
  >>> util.query('a', raw=True)
  u'value of a'
  >>> util.invalidate('a', raw=True)
  >>> util.query('a', raw=True) is None
  True

Statistics
==========

This returns the stats for each server connected.

  >>> util.getStatistics()
  [('127.0.0.1:11211 (1)', {'total_items':...]

If we use a server which doesn't exist we can still use the cache but noting
will be stored. This behaviour allows us to run without a connected memcache
server. As soon as a server is back online it will immediately used.

  >>> util.servers = ['127.0.0.1:8125']
  >>> k = util.set('cached value', 'cache_object')
  >>> util.query('cache_object') is None
  True

