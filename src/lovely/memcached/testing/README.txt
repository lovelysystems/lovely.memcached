=====================
Memcached Test Client
=====================

For testing we provide a memcache implementation which doesn't need a running
memcache daemon.

  >>> from lovely.memcached.testing import TestMemcachedClient
  >>> cache = TestMemcachedClient()
  >>> cache.set('value', 'key')
  '613fb124907164bf8f0b04beb02cf59e'
  >>> cache.query('key')
  'value'
  >>> cache.invalidate(key='key')
  >>> cache.query('key') is None
  True

Also the lifetime is handled.

  >>> cache.set('value', 'key', 1)
  '613fb124907164bf8f0b04beb02cf59e'
  >>> cache.query('key')
  'value'
  >>> from time import sleep
  >>> sleep(1)
  >>> cache.query('key') is None
  True

The testcache has also a hit/misses counter which is sometimes useful for
testing.

  >>> cache.hits
  2
  >>> cache.misses
  2
  >>> cache.query('key') is None
  True
  >>> cache.hits
  2
  >>> cache.misses
  3
  >>> cache.set('value', 'key')
  '613fb124907164bf8f0b04beb02cf59e'
  >>> cache.query('key')
  'value'
  >>> cache.hits
  3
  >>> cache.misses
  3

  >>> cache.resetCounts()
  >>> cache.hits
  0
  >>> cache.misses
  0

The TestMemcachedClient does it's best to simulate the behaviour of the
original memcached implementation.

  >>> from lovely.memcached.testing.memcache import SimulatedMemcached
  >>> client = SimulatedMemcached()
  >>> client.set(u'\xfckey', 'value', 1)
  Traceback (most recent call last):
  ...
  UnicodeEncodeError: 'ascii' codec can't encode character u'\xfc' in position 0: ordinal not in range(128)

  >>> client.set('key', u'\xfcvalue', 1)
  Traceback (most recent call last):
  ...
  UnicodeEncodeError: 'ascii' codec can't encode character u'\xfc' in position 0: ordinal not in range(128)

  >>> client.get(u'\xfckey')
  Traceback (most recent call last):
  ...
  UnicodeEncodeError: 'ascii' codec can't encode character u'\xfc' in position 0: ordinal not in range(128)

