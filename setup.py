#!python
from setuptools import setup, find_packages

setup (
    name='lovely.memcached',
    version='0.1dev',
    author = "Lovely Systems",
    author_email = "office@lovelysystems.com",
    description = "A memcached client utiltiy for zope 3",
    license = "ZPL 2.1",
    keywords = "zope3 zope memcached cache ram",
    url = 'svn://svn.zope.org/repos/main/lovely.memcached',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['lovely'],
    extras_require = dict(test = ['zope.app.testing',
                                  'zope.app.securitypolicy',
                                  'zope.app.zcmlfiles',
                                  'zope.testbrowser']),
    install_requires = ['setuptools',
                        'python-memcached',
                        'ZODB3',
                        'zope.schema',
        ],
    dependency_links = ['http://download.zope.org/distribution']
    )
