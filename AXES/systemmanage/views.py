from django.shortcuts import render
from models import Game, Idc
from forms import addGameForm, addIdcForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

# Create your views here.


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
    ID = request.POST['del_id']
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
    GAME = request.POST['del_id']
    Game.objects.get(game_name_cn=GAME).delete()
    return HttpResponseRedirect(reverse('gamelisturl'))
