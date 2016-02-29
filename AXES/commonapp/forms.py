#!/usr/bin/env python
# encoding: utf-8

from django import forms
from django.contrib.auth.models import User
from models import UserProfile, Role


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
                attrs={
                    'class': 'form-control', 'size': '10', 'multiple': 'multiple'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['role'].label = u'角色'
        self.fields['permission'].label = u'权限'


class RoleListForm(forms.ModelForm):

    class Meta:
        model = Role
        fields = ('name', 'url')
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'readonly': 'readonly',
                }
            ),
            'url': forms.SelectMultiple(
                attrs={
                    'class': 'form-control', 'size': '10', 'multiple': 'multiple'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super(RoleListForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = u'角色'
        self.fields['url'].label = u'url'


class ChangePasswordForm(forms.Form):

    old_password = forms.CharField(
        label=u'旧密码',
        error_messages={'required': '请输入旧密码'},
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label=u'新密码',
        error_messages={'required': '请输入新密码'},
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label=u'确认密码',
        error_messages={'required': '请确认您的密码'},
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        if not self.user.check_password(old_password):
            raise forms.ValidationError(u'原密码错误')
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password2 != password1:
                raise forms.ValidationError(u'两次密码输入不一致')
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user
