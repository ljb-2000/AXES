# encoding: utf-8
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
import zabbixtools.models_mongodb as db
from forms import UserForm, UserProfileForm, RoleListForm, ChangePasswordForm
from django.contrib.auth import authenticate, login, logout
from models import UserProfile, Role
from django.contrib.auth.models import User
from systemmanage.models import Game
import re

# Create your views here.


@login_required
def getCookieUrl(request):
    if request.COOKIES.get('url'):
        url = request.COOKIES.get('url')
    else:
        url = "http://123.59.6.164/api_jsonrpc.php"
    return url


def permissionVerify():
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            flag = False
            user_info = UserProfile.objects.get(user=request.user)
            role_info = Role.objects.get(name=user_info.role)
            url_list = [i.url for i in role_info.url.all()]
            for i in url_list:
                if request.path == i or request.path.rstrip('/') == i:
                    flag = True
                elif re.match(i + '(.)*', request.path):
                    flag = True
                else:
                    pass
            if not flag:
                return HttpResponseRedirect(reverse('nopermissionurl'))
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


@login_required
@permissionVerify()
def logView(request):
    url = getCookieUrl(request)
    result = db.getLog(url)
    context_dict = {
        'log': result
    }
    return render(request, 'common/log.html', context_dict)


def loginView(request):
    error_flag = False
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('isjkgamelisturl'))
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse('isjkgamelisturl'))
        else:
            error_flag = True
            return render(request, 'common/login.html', {"error": u"用户名或者密码错误", 'error_flag': error_flag})
    else:
        return render(request, 'common/login.html', {'error_flag': error_flag})


@login_required
@permissionVerify()
def logoutView(request):
    logout(request)
    return HttpResponseRedirect(reverse('loginurl'))


def noPermissionView(request):
    return render(request, 'common/nopermission.html')


@login_required
@permissionVerify()
def addUserView(request):
    if request.method == 'POST':
        permission_list = [int(i) for i in request.POST.getlist('permission')]
        print permission_list
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            #  import pdb; pdb.set_trace()
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            for i in permission_list:
                profile.permission.add(Game.objects.get(id=i))
            return HttpResponseRedirect(reverse('userlisturl'))
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    context_dict = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'common/adduser.html', context_dict)


@login_required
@permissionVerify()
def delUserView(request, ID):
    User.objects.get(id=ID).delete()
    return HttpResponseRedirect(reverse('userlisturl'))


@login_required
@permissionVerify()
def editUserView(request, ID):
    user_info = User.objects.get(id=ID)
    profile_info = UserProfile.objects.get(user=user_info)
    if request.method == 'POST':
        permission_list = [int(i) for i in request.POST.getlist('permission')]
        user_form = UserForm(request.POST, instance=user_info)
        profile_form = UserProfileForm(request.POST, instance=profile_info)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            for i in permission_list:
                profile.permission.add(Game.objects.get(id=i))
            return HttpResponseRedirect(reverse('userlisturl'))
    else:
        user_form = UserForm(instance=user_info)
        profile_form = UserProfileForm(instance=profile_info)
    context_dict = {
        'ID': ID,
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'common/edituser.html', context_dict)


@login_required
@permissionVerify()
def userListView(request):
    user_list = UserProfile.objects.all()
    context_dict = {
        'list': user_list
    }
    return render(request, 'common/userlist.html', context_dict)


@login_required
def changePasswordView(request):
    if request.method == 'POST':
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('logouturl'))
    else:
        form = ChangePasswordForm(user=request.user)
    context_dict = {
        'form': form,
    }
    return render(request, 'common/changepassword.html', context_dict)


@login_required
@permissionVerify()
def roleListView(request):
    role_list = Role.objects.all()
    context_dict = {
        'list': role_list,
    }
    return render(request, 'common/rolelist.html', context_dict)


@login_required
@permissionVerify()
def editRoleView(request, ID):
    role_info = Role.objects.get(id=ID)
    if request.method == 'POST':
        form = RoleListForm(request.POST, instance=role_info)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('rolelisturl'))
    else:
        role_form = RoleListForm(instance=role_info)
    context_dict = {
        'form': role_form,
        'ID': ID,
    }
    return render(request, 'common/editrole.html', context_dict)
