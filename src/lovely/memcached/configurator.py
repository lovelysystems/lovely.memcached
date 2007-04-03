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

import interfaces
import utility
from zope import component
from zope.interface.interfaces import IMethod
from zope import schema
from z3c.configurator import configurator
from zope.app.component.interfaces import ISite
from zope.lifecycleevent import ObjectCreatedEvent
import zope.event
from zope.security.proxy import removeSecurityProxy

class IMemcachedClientProperties(interfaces.IMemcachedClient):

    name = schema.TextLine(title=u'Name',
                           required=False,
                           default=u'')
    
class SetUpMemcachedClient(configurator.SchemaConfigurationPluginBase):
    component.adapts(ISite)
    schema = IMemcachedClientProperties
    
    def __call__(self, data):

        for name in self.schema:
            field = self.schema[name]
            if IMethod.providedBy(field):
                continue
            if data.get(name) is None:
                data[name] = self.schema[name].default
        name = data.get('name')
        site = self.context
        # we just wanna have one
        util = component.queryUtility(interfaces.IMemcachedClient,
                                      context=site,
                                      name=name)
        if util is not None:
            return
        # needed to be called TTW
        sm = removeSecurityProxy(site.getSiteManager())
        default = sm['default']
        util = utility.MemcachedClient()
        zope.event.notify(ObjectCreatedEvent(util))
        for attr in ['trackKeys', 'defaultNS', 'servers',
                     'defaultLifetime']:
            setattr(util, attr, data[attr])
        default[u'memcachedclient_' + name] = util
        sm.registerUtility(util, interfaces.IMemcachedClient,
                           name=name)
