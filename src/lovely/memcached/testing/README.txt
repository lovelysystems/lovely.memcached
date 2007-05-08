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

