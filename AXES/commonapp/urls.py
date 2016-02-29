#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls import patterns, url
from commonapp import views

urlpatterns = patterns(
    '',
    url(r'^log/$', views.logView, name='loglisturl'),
    url(r'^logout/$', views.logoutView, name='logouturl'),
    url(r'^usermanage/adduser/$', views.addUserView, name='adduserurl'),
    url(r'^usermanage/userlist/$', views.userListView, name='userlisturl'),
    url(r'^usermanage/rolelist/$', views.roleListView, name='rolelisturl'),
    url(r'^usermanage/editrole/(?P<ID>[^/]+)/$', views.editRoleView, name='editroleurl'),
    url(r'^usermanage/deluser/(?P<ID>[^/]+)/$', views.delUserView, name='deluserurl'),
    url(r'^usermanage/edituser/(?P<ID>[^/]+)/$', views.editUserView, name='edituserurl'),
    url(r'^changepassword/$', views.changePasswordView, name='changepasswordurl'),
)
