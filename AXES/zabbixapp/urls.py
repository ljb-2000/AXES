#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls import patterns, url
from zabbixapp.views import views

urlpatterns = patterns(
    '',
    url(r'^geturl/url=(?P<URL>[^/]+)/$', views.getUrlView, name='geturlurl'),
#    url(r'^projectlist/$', views.jkGameListView, name='isjkgamelisturl'),
    url(r'^calendar/$', views.calendarView, name='calendarurl'),
    url(r'^hostlist/$', views.sealAndZabbixViews, name='hostlisturl'),
    url(r'^notdeployhostlist/projectname=(?P<PNAME>[^/]+)/$', views.notDeployAndHostViews, name='notdeployhostlisturl'),
    url(r'^projectlist/nomonitor/$', views.notjkGameListView, name='notjkgamelisturl'),
    url(r'^templatelist/$', views.templateListView, name='templatelisturl'),
    url(r'^maintenancelist/$', views.maintenanceListView, name='maintenancelisturl'),
    url(r'^hostlist/groupid=(?P<GNAME>[^/]+)/$', views.groupHostListView, name='grouphostlisturl'),
    url(r'^hostlist/gamename=(?P<GNAME>[^/]+)/$', views.hostListView, name='hostlisturl'),
    url(r'^delmaintenance/MNAME=(?P<MNAME>[^/]+)/$', views.delMaintenanceView, name='delmaintenanceurl'),
    url(r'^proxylist/$', views.proxyListView, name='proxylisturl'),
    url(r'^grouplist/$', views.groupListView, name='grouplisturl'),
    url(r'^creategroup/$', views.createGroupView, name='creategroupurl'),
    url(r'^createhosts/$', views.createHostsView, name='createhostsurl'),
    url(r'^createhost/$', views.createHostView, name='createhosturl'),
    url(r'^createmaintenance/$', views.createMaintenanceView, name='createmaintenanceurl'),
    url(r'^groupinproject/$', views.groupInProjectView, name='groupinprojecturl'),
    url(r'^editgroup/groupid=(?P<GID>[^/]+)/$', views.updateGroupView, name='updategroupurl'),
    url(r'^edittemplate/templatename=(?P<TNAME>[^/]+)/$', views.updateTemplateView, name='updatetemplateurl'),
    url(r'^edithost/hostname=(?P<HNAME>[^/]+)/$', views.oneHostInfoView, name='hostinfourl'),
    url(r'^edithosts/gamename=(?P<GNAME>[^/]+)/$', views.manageHostView, name='managehosturl'),
    url(r'^delgroupsandhosts/$', views.delGroupAndHostView, name='delgroupsandhostsurl'),
    url(r'^delgroup/$', views.delGroupView, name='delgroupurl'),
    url(r'^delhostbyname/$', views.delHostByNameView, name='delhostbynameurl'),
    url(r'^deletehost/(?P<GNAME>[^/]+)/$', views.delHostView, name='delhosturl'),
    url(r'^deletehostproject/(?P<GNAME>[^/]+)/$', views.delHostProjectView, name='delhostprojecturl'),
    url(r'^start/$', views.startMaintenanceView, name='starturl'),
)
