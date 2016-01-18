from django.shortcuts import render
from models import Game, Idc, ZabbixUrl
from forms import addGameForm, addIdcForm, addUrlForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

the_salt = "oXg#Xk^z4GYP%SEv"
key = "UmGBaI[YuF]H=hi&"


def idcListView(request):
    idc_info = Idc.objects.all()
    context_dict = {
        'list': idc_info
    }
    return render(request, 'systemmanage/idctable.html', context_dict)


def gameListView(request):
    game_info = Game.objects.all()
    context_dict = {
        'list': game_info
    }
    return render(request, 'systemmanage/gametable.html', context_dict)


def addGameView(request):
    if request.method == 'POST':
        form = addGameForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('gamelisturl'))
    else:
        form = addGameForm()
    context_dict = {
        'form': form,
    }
    return render(request, 'systemmanage/addgame.html', context_dict)


def addIdcView(request):
    if request.method == 'POST':
        form = addIdcForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('idclisturl'))
    else:
        form = addIdcForm()
    context_dict = {
        'form': form,
    }
    return render(request, 'systemmanage/addidc.html', context_dict)


def editIdcView(request, ID):
    idc_info = Idc.objects.get(idc_name_cn=ID)
    if request.method == 'POST':
        form = addIdcForm(request.POST, instance=idc_info)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('idclisturl'))
    else:
        form = addIdcForm(instance=idc_info)
    context_dict = {
        "form": form,
        'ID': ID,
    }
    return render(request, 'systemmanage/editidc.html', context_dict)


def delIdcView(request):
    ID = request.POST.get('del_id')
    Idc.objects.get(idc_name_cn=ID).delete()
    return HttpResponseRedirect(reverse('idclisturl'))


def editGameView(request, ID):
    game_info = Game.objects.get(game_name_cn=ID)
    if request.method == 'POST':
        form = addGameForm(request.POST, instance=game_info)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('gamelisturl'))
    else:
        form = addGameForm(instance=game_info)
    context_dict = {
        "form": form,
        'ID': ID,
    }
    return render(request, 'systemmanage/editgame.html', context_dict)


def delGameView(request):
    GAME = request.POST.get('del_id')
    Game.objects.get(game_name_cn=GAME).delete()
    return HttpResponseRedirect(reverse('gamelisturl'))


def urlListView(request):
    zabbix_url = ZabbixUrl.objects.all()
    urllist = [i.url for i in zabbix_url]
    request.session['urllist'] = urllist
    request.session['length'] = len(urllist)
    context_dict = {
        'list': zabbix_url,
    }
    return render(request, 'systemmanage/urltable.html', context_dict)


def addUrlView(request):
    if request.method == 'POST':
        form = addUrlForm(request.POST)
        if form.is_valid():
            zabbix_url = form.save(commit=False)
            crypt_password = encrypt(zabbix_url.password)
            zabbix_url.password = crypt_password
            form.save()
            return HttpResponseRedirect(reverse('urllisturl'))
    else:
        form = addUrlForm()
    context_dict = {
        'form': form,
    }
    return render(request, 'systemmanage/addurl.html', context_dict)


def delUrlView(request):
    url = request.POST.get('del_id')
    ZabbixUrl.objects.get(url=url).delete()
    return HttpResponseRedirect(reverse('urllisturl'))


def encrypt(password):
    password = password + '\0' * (16 - len(password)) if len(password) < 16 else password
    print len(password)
    cryptor = AES.new(key, AES.MODE_CBC, the_salt)
    cryptor_text = cryptor.encrypt(password)
    return b2a_hex(cryptor_text)


def decrypt(password):
    cryptor = AES.new(key, AES.MODE_CBC, the_salt)
    plain_text = cryptor.decrypt(a2b_hex(password))
    return plain_text.rstrip('\0')
