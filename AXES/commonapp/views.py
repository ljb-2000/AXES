from django.shortcuts import render
import zabbixtools.models_mongodb as db
from zabbixapp.views.views import getCookieUrl
from forms import UserForm, UserProfileForm
from models import UserProfile, Role, Permission, Host

# Create your views here.


def logView(request):
    url = getCookieUrl(request)
    result = db.getLog(url)
    context_dict = {
        'log': result
    }
    return render(request, 'common/log.html', context_dict)


def loginView(request):
    pass


def logoutView(request):
    pass


def addUserView(request):
    if request.method == 'POST':
        print request.POST
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return render(request, 'common/adduser.html')
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    context_dict = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'common/adduser.html', context_dict)


def delUserView(request):
    pass


def editUserView(request):
    pass


def userListView(request):
    #  user_list = User.objects.all()
    pass


def changePasswordView(request):
    pass
