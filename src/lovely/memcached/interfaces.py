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

from zope import interface
from zope import schema

class IMemcachedClient(interface.Interface):
    
    """A memcache client utility"""

    defaultNS = schema.TextLine(
        title=u'Default Namespace',
        description=u"The default namespace used by this client",
        required=False,
        default=None)
        
    servers = schema.List(
        title = u'Servers',
        description = u"Servers defined as <hostname>:<port>",
        value_type = schema.BytesLine(),
        required = True,
        default=['127.0.0.1:11211']
        )
    
    defaultLifetime = schema.Int(
        title = u'Default Lifetime',
        description = u'The default lifetime of entries',
        required = True,
        default = 3600,
        )


    def getStatistics():
        """returns the memcached stats"""

    def set(data, key, lifetime=None, ns=None):
        """Sets data with the given key in namespace. Lifetime
        defaults to defautlLifetime and ns defaults to the
        default namespace"""

    def query(key, default=None, ns=None):
        """query the cache for key in namespace, returns default if
        not found. ns defaults to default namespace."""
        
    def invalidate(key, ns=None):
        """invalidates key in namespace which defaults to default
        namespace, currently we can not invalidate just a namespace"""

    def invalidateAll():
        """invalidates all data of the memcached servers, not that all
        namespaces are invalidated"""
