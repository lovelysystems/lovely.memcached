#!/usr/bin/env python
import os
from setuptools import setup, find_packages

# We can not include the full README.txt file since it contains
# unicode chars within doctests which will make setuptools break.
long_description = file('README.txt').read()

setup (
    name='lovely.memcached',
    version='0.1.4',
    author = "Lovely Systems",
    author_email = "office@lovelysystems.com",
    description = "A memcached client utiltiy for zope 3",
    long_description = long_description,
    license = "ZPL 2.1",
    keywords = "zope3 zope memcached cache ram",
    url = 'svn://svn.zope.org/repos/main/lovely.memcached',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['lovely'],
    extras_require = dict(test = ['z3c.configurator',
                                  'zope.keyreference',
                                  'zope.securitypolicy',
                                  'zope.app.testing',
                                  'zope.testbrowser',
                                  ]),
    install_requires = ['setuptools',
                        'python-memcached',
                        'zope.site',
                        'zope.intid',
                        'zope.event',
                        'zope.interface',
                        'zope.lifecycleevent',
                        'zope.schema',
                        'zope.security'
                        ],
    zip_safe = False,
    )
