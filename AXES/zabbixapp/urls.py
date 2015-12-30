#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls import patterns, url
from zabbixapp.views import views

urlpatterns = patterns(
    '',
    url(r'^geturl/url=(?P<URL>[^/]+)/$', views.getUrlView, name='geturlurl'),
    url(r'^projectlist/$', views.jkGameListView, name='isjkgamelisturl'),
    url(r'^projectlist/nomonitor/$', views.notjkGameListView, name='notjkgamelisturl'),
    url(r'^templatelist/$', views.templateListView, name='templatelisturl'),
    url(r'^hostlist/groupname=(?P<GNAME>[^/]+)/$', views.groupHostListView, name='grouphostlisturl'),
    url(r'^hostlist/gamename=(?P<GNAME>[^/]+)/$', views.hostListView, name='hostlisturl'),
    url(r'^proxylist/$', views.proxyListView, name='proxylisturl'),
    url(r'^grouplist/$', views.groupListView, name='grouplisturl'),
    url(r'^creategroup/$', views.createGroupView, name='creategroupurl'),
    url(r'^createhosts/$', views.createHostsView, name='createhostsurl'),
    url(r'^createhost/$', views.createHostView, name='createhosturl'),
    url(r'^editgroup/groupid=(?P<GID>[^/]+)/$', views.updateGroupView, name='updategroupurl'),
    url(r'^edittemplate/templatename=(?P<TNAME>[^/]+)/$', views.updateTemplateView, name='updatetemplateurl'),
    url(r'^edithost/hostname=(?P<HNAME>[^/]+)/$', views.oneHostInfoView, name='hostinfourl'),
    url(r'^edithosts/gamename=(?P<GNAME>[^/]+)/$', views.manageHostInGroupView, name='managehosturl'),
    url(r'^delgroupsandhosts/$', views.delGroupAndHostView, name='delgroupsandhostsurl'),
    url(r'^delgroup/$', views.delGroupView, name='delgroupurl'),
    url(r'^delhostbyname/$', views.delHostByNameView, name='delhostbynameurl'),
    url(r'^deletehost/(?P<GNAME>[^/]+)/$', views.delHostView, name='delhosturl'),
    url(r'^deletehostproject/(?P<GNAME>[^/]+)/$', views.delHostProjectView, name='delhostprojecturl'),
)
