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

To store a new value in the cache we just need to set it.

  >>> util.set('cached value', 'cache_key')
  >>> util.query('cache_key')
  'cached value'

If we no longer need the cached value we can invalidate it.

  >>> util.invalidate('cache_key')
  >>> util.query('cache_key') is None
  True

We have extended the original implementation on memcache.py for unicode.

  >>> util.set(u'cached value ä', 'cache_key')
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
  >>> util1.set(1,1)
  >>> util2.set(2,2)
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

Statistics
==========

This returns the stats for each server connected.

  >>> util.getStatistics()
  [('127.0.0.1:11211 (1)', {'total_items':...]

If we use a server which doesn't exist we can still use the cache but noting
will be stored. This behaviour allows us to run without a connected memcache
server. As soon as a server is back online it will immediately used.

  >>> util.servers = ['127.0.0.1:8125']
  >>> util.set('cached value', 'cache_object')
  >>> util.query('cache_object') is None
  True

