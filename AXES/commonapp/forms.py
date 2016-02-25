#!/usr/bin/env python
# encoding: utf-8

from django import forms
from django.contrib.auth.models import User
from models import UserProfile, Permission, Role, Host


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'password': forms.PasswordInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'email': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = u'用户名'
        self.fields['username'].error_messages = {'required': u'该项不能为空'}
        self.fields['password'].label = u'密 码'
        self.fields['password'].error_messages = {'required': u'该项不能为空'}
        self.fields['email'].label = u'邮 箱'
        self.fields['email'].error_messages = {'required': u'该项不能为空'}


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ('role', 'permission')
        widgets = {
            'role': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
            'permission': forms.SelectMultiple(
                choices=[(x.name) for x in Permission.objects.all()],
                attrs={
                    'class': 'form-control', 'size': '10', 'multiple': 'multiple'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['role'].label = u'角色'
        self.fields['role'].error_messages = {'required': u'该项不能为空'}
        self.fields['permission'].label = u'权限'
        self.fields['permission'].error_messages = {'required': u'该项不能为空'}
