from django.shortcuts import render
from zabbixapp import models_mongodb as db

# Create your views here.


def logView(request):
    result = db.getLog()
    context_dict = {
        'log': result
    }
    return render(request, 'common/log.html', context_dict)
