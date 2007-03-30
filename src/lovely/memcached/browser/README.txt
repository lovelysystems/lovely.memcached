==============================
Memcached utilit browser views
==============================

Let us add a memcached utility.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization','Basic mgr:mgrpw')
  >>> browser.handleErrors = False

  >>> browser.open('http://localhost/@@contents.html')
  >>> browser.getLink('Memcached Client').click()
  >>> browser.getControl(name="new_value").value=u'mc'
  >>> browser.getControl('Apply').click()
  >>> browser.open('http://localhost/mc/manage')
  >>> browser.getLink('Configure').click()
  >>> browser.url
  'http://localhost/mc/@@configure.html'

  >>> browser.getControl('Default Lifetime').value = '5400'
  >>> browser.getControl('Change').click()
  >>> browser.getControl('Default Lifetime').value
  '5400'

Let's look at the stats.

  >>> browser.getLink('Statistics').click()
  >>> browser.url
  'http://localhost/mc/@@stats.html'
  >>> '<th>127.0.0.1:11211 (1)</th>' in browser.contents
  True
