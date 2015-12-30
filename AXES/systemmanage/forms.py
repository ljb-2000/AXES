#!/usr/bin/env python
# encoding: utf-8

from django import forms
from models import Game, Idc, ZabbixUrl


class addGameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ('game_name_cn', 'game_name_py', 'game_system')
        widgets = {
            'game_name_cn': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': u'请输入项目中文名'
                }
            ),
            'game_name_py': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': u'请输入项目拼音简写'
                }
            ),
            'game_system': forms.Select(
                attrs={
                    'class': 'form-control',
                },
                choices=((None, None), ('Linux', 'Linux'), ('Windows', 'Windows'))
            ),
        }

    def __init__(self, *args, **kwargs):
        super(addGameForm, self).__init__(*args, **kwargs)
        self.fields['game_name_cn'].label = u'游戏名'
        self.fields['game_name_cn'].error_messages = {'required': u'该项不能为空'}
        self.fields['game_name_py'].label = u'游戏拼音简写'
        self.fields['game_name_py'].error_messages = {'required': u'该项不能为空'}
        self.fields['game_system'].label = u'操作系统类型'


class addIdcForm(forms.ModelForm):
    class Meta:
        model = Idc
        fields = ('idc_name_cn', 'idc_name_py', 'proxy_name')
        widgets = {
            'idc_name_cn': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': u'请输入idc中文名'
                }
            ),
            'idc_name_py': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': u'请输入idc拼音简写'
                }
            ),
            'proxy_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': u'请输入代理名'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super(addIdcForm, self).__init__(*args, **kwargs)
        self.fields['idc_name_cn'].label = u'IDC'
        self.fields['idc_name_cn'].error_messages = {'required': u'该项不能为空'}
        self.fields['idc_name_py'].label = u'IDC拼音简写'
        self.fields['idc_name_py'].error_messages = {'required': u'该项不能为空'}
        self.fields['proxy_name'].label = u'代理'


class addUrlForm(forms.ModelForm):
    class Meta:
        model = ZabbixUrl
        fields = ('url', 'username', 'password')
        widgets = {
            'url': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': u'输入IPaddress即可'
                }
            ),
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': u'请输入用户名'
                }
            ),
            'password': forms.PasswordInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super(addUrlForm, self).__init__(*args, **kwargs)
        self.fields['url'].label = u'url'
        self.fields['url'].error_messages = {'required': u'该项不能为空'}
        self.fields['username'].label = u'username'
        self.fields['username'].error_messages = {'required': u'该项不能为空'}
        self.fields['password'].label = u'password'
        self.fields['password'].error_messages = {'required': u'该项不能为空'}
