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
from z3c.configurator import configurator
from zope.app.component.interfaces import ISite
from zope.lifecycleevent import ObjectCreatedEvent
import zope.event
from zope.security.proxy import removeSecurityProxy

class SetUpMemcachedClient(configurator.ConfigurationPluginBase):
    component.adapts(ISite)

    def __call__(self, data):
        site = self.context
        # we just wanna have one
        util = component.queryUtility(interfaces.IMemcachedClient,
                                      context=site)
        if util is not None:
            return
        # needed to be called TTW
        sm = removeSecurityProxy(site.getSiteManager())
        default = sm['default']
        util = utility.MemcachedClient()
        zope.event.notify(ObjectCreatedEvent(util))
        default['memcachedclient'] = util
        sm.registerUtility(util, interfaces.IMemcachedClient)
