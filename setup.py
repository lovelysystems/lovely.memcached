#!/usr/bin/env python
""" Installer
"""
import os
from setuptools import setup, find_packages

NAME = 'lovely.memcached'
PATH = ['src'] + NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(
    name=NAME,
    version=VERSION,
    author="Lovely Systems",
    author_email="office@lovelysystems.com",
    description="A memcached client utiltiy for zope 3",
    long_description=(open("README.txt").read() + "\n" +
                      open("CHANGES.txt").read()),
    license="ZPL 2.1",
    keywords="zope3 zope memcached cache ram",
    url='http://github.com/lovelysystems/lovely.memcached',
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'':'src'},
    namespace_packages=['lovely'],
    extras_require=dict(test = ['z3c.configurator',
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
