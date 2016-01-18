#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls import patterns, url
from commonapp import views

urlpatterns = patterns(
    '',
    url(r'^log/$', views.logView, name='loglisturl'),
)
