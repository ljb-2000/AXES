# encoding: utf-8
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, HttpResponse
from systemmanage.models import Game, ZabbixUrl
import zabbixtools.zabbixapi as zabbixapi
import zabbixscript
import zabbixtools.models_mongodb as db
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
import re
from collections import OrderedDict
import sys
import copy
import time
import calendar
import datetime
import json

reload(sys)
sys.setdefaultencoding('utf8')

CHINESE_ENGILSH = {
    1: u'一',
    2: u'二',
    3: u'三',
    4: u'四',
    5: u'五',
    6: u'六',
    7: u'日',
}


def getCookieUrl(request):
    if request.COOKIES.get('url'):
        url = request.COOKIES.get('url')
    else:
        url = "http://123.59.6.164/api_jsonrpc.php"
    return url


def getUrlView(request, URL):
    if URL:
        url = "http://" + URL + "/api_jsonrpc.php"
    httpresponse = HttpResponseRedirect(reverse('isjkgamelisturl'))
    httpresponse.set_cookie(key="url", value=url)
    return httpresponse


def notjkGameListView(request):
    url = getCookieUrl(request)
    games_info = Game.objects.all()
    game_list = []
    is_exist_game = [group_name['name'].split('_')[0] for group_name in db.getGroup(url)]
    is_exist_game = list(set(is_exist_game))
    for i in games_info:
        if i.game_name_cn not in is_exist_game:
            game_list.append(i)
    context_dict = {
        'list': game_list
    }
    return render(request, 'zabbixmanage/gametablenotjk.html', context_dict)


def jkGameListView(request):
    url = getCookieUrl(request)
    zabbix_url = ZabbixUrl.objects.all()
    urllist = [i.url for i in zabbix_url]
    games_info = Game.objects.all()
    game_list = []
    is_exist_game = [group_name['name'].split('_')[0] for group_name in db.getGroup(url)]
    is_exist_game = list(set(is_exist_game))
    for i in games_info:
        if i.game_name_cn in is_exist_game:
            game_list.append(i)
    context_dict = {
        'list': game_list
    }
    request.session['urllist'] = urllist
    request.session['length'] = len(urllist)
    return render(request, 'zabbixmanage/gametableisjk.html', context_dict)


def templateListView(request):
    url = getCookieUrl(request)
    template_info = db.getTemplate(url)
    context_dict = {
        'list': template_info,
    }
    return render(request, 'zabbixmanage/templatetable.html', context_dict)


def groupListView(request):
    url = getCookieUrl(request)
    group_info = db.getGroup(url)
    context_dict = {
        'list': group_info,
    }
    return render(request, 'zabbixmanage/grouptable.html', context_dict)


def createGroupView(request):
    url = getCookieUrl(request)
    if request.method == 'POST':
        group_name = request.POST['group_name']
        zabbixapi.createGroup(url, group_name)
        return HttpResponseRedirect(reverse('grouplisturl'))
    else:
        return render(request, 'zabbixmanage/creategroup.html')


def delGroupAndHostView(request):
    url = getCookieUrl(request)
    group_ids = request.REQUEST.getlist('group_list')
    for group_id in group_ids:
        zabbixapi.deleteHost(url, group_id=group_id)
    zabbixapi.deleteGroup(url, group_ids)
    return HttpResponseRedirect(reverse('grouplisturl'))


def delGroupView(request):
    url = getCookieUrl(request)
    id_list = []
    ID = request.POST['del_ids']
    id_list.append(ID)
    zabbixapi.deleteGroup(url, id_list)
    return HttpResponseRedirect(reverse('grouplisturl'))


def delHostByNameView(request):
    url = getCookieUrl(request)
    game_name_cn = request.POST['del_names']
    groups = db.getGroup(url)
    for group in groups:
        if game_name_cn == group['name'].split('_')[0]:
            zabbixapi.deleteHost(url, group_id=group['groupid'])
            zabbixapi.deleteGroup(url, [group['groupid']])
    return HttpResponseRedirect(reverse('isjkgamelisturl'))


def delHostView(request, GNAME):
    url = getCookieUrl(request)
    host_id = request.POST['del_id']
    zabbixapi.deleteHost(url, host_id=[host_id])
    return HttpResponseRedirect(reverse('grouphostlisturl', args=[GNAME]))


def delHostProjectView(request, GNAME):
    url = getCookieUrl(request)
    host_id = request.POST['del_id']
    zabbixapi.deleteHost(url, host_id=[host_id])
    return HttpResponseRedirect(reverse('hostlisturl', args=[GNAME]))


def manageHostView(request, GNAME):
    url = getCookieUrl(request)
    if request.method == 'POST':
        host_id = request.REQUEST.getlist('host_list')
        if 'create' in request.POST:
            game_list = [GNAME]
            template_list = db.getTemplate(url)
            context_dict ={
                'list': game_list,
                'options': template_list
            }
            return render(request, 'zabbixmanage/createhost.html', context_dict)
        elif 'update' in request.POST:
            host_dict = OrderedDict()
            host_info = db.getHost(url, host_id=host_id)
            host_ids = ';'.join([host['hostid'] for host in host_info])
            host_names = ';'.join([host['host'] for host in host_info])
            host_status = host_info[0]['status']
            host_group = ';'.join(list(set([host['groups'][0]['name'] for host in host_info])))
            host_templates = ';'.join(list(set([host['parentTemplates'][0]['name'] for host in host_info])))
            host_dict[u'id'] = host_ids
            host_dict[u'主机名称'] = host_names
            host_dict[u'主机组'] = host_group
            host_dict[u'模板'] = host_templates
            host_dict[u'主机状态'] = host_status
            context_dict = {
                'host_dict': host_dict,
            }
            return render(request, 'zabbixmanage/updatehosts.html', context_dict)
        elif 'off_hosts' in request.POST:
            zabbixapi.manageMonitoring(url, host_id, "1")
            return HttpResponseRedirect(reverse('hostlisturl', args=[GNAME]))
        elif 'on_hosts' in request.POST:
            zabbixapi.manageMonitoring(url, host_id, "0")
            return HttpResponseRedirect(reverse('hostlisturl', args=[GNAME]))
        elif 'delete' in request.POST:
            zabbixapi.deleteHost(url, host_id=host_id)
            return HttpResponseRedirect(reverse('hostlisturl', args=[GNAME]))


def createHostsView(request):
    url = getCookieUrl(request)
    game_list = request.REQUEST.getlist('game_list')
    if request.method == 'POST':
        template_list = request.REQUEST.getlist('template_list')[0]
        for game in game_list:
            state_list = request.REQUEST.getlist('_'.join([game, 'state_list']))
            function_list = request.REQUEST.getlist('_'.join([game, 'function_list']))
            subfunction_list = request.REQUEST.getlist('_'.join([game, 'subfunction_list']))
            zabbixscript.main(url, game, template_list, state_list, function_list, subfunction_list)
        db.updateGroupHostCount(url)
        #  db.updateProxy(url)
        if len(game_list) > 1:
            return HttpResponseRedirect(reverse('grouplisturl'))
        elif len(game_list) == 1:
            return HttpResponseRedirect(reverse('hostlisturl', args=game_list))
    else:
        template_list = db.getTemplate(url)
    context_dict ={
        'list': game_list,
        'options': template_list
    }
    return render(request, 'zabbixmanage/createhost.html', context_dict)


def createHostView(request):
    url = getCookieUrl(request)
    if request.method == 'POST':
        host = request.POST.get('host')
        name = request.POST.get('name')
        groups = [i for i in re.split(',|;| ', request.POST.get('group')) if i]
        groupid = []
        for group in groups:
            if zabbixapi.isGroup(url, group):
                groupid.append(db.getGroup(url, group_name=group)['groupid'])
            else:
                groupid.append(zabbixapi.createGroup(url, group)['result']['groupids'][0])
        template = request.POST.getlist('template')
        proxyid = request.POST.get('proxy')
        host_dict = dict(zip(['host_ip', 'host_name', 'group_id', 'template_id', 'proxy_id'], [host, name, groupid, template, proxyid]))
        macros_key = request.POST.getlist('macro_key')
        macros_value = request.POST.getlist('macro_value')
        macro_dict = {}
        macros = []
        for i in zip(macros_key, macros_value):
            macro_dict = {}
            if len(i[0]) >= 1 and len(i[1]) >= 1:
                macro_dict['macro'] = i[0].strip().upper()
                macro_dict['value'] = i[1].strip()
            if macro_dict:
                macros.append(macro_dict)
        zabbixapi.createOneHost(url, host_dict, macros)
        db.updateGroupHostCount(url, groupid)
        #  db.updateProxy(url, proxyid)
        return HttpResponseRedirect(reverse('hostinfourl', args=[host]))
    else:
        template_list = db.getTemplate(url)
        global_macro = zabbixapi.getGlobalMacrosInfo(url)['result']
        proxy_list = db.getProxy(url)
    context_dict = {
        "options": template_list,
        "global_macros": global_macro,
        "proxys": proxy_list,
    }
    return render(request, 'zabbixmanage/createonehost.html', context_dict)


def hostListView(request, GNAME):
    url = getCookieUrl(request)
    all_group = db.getGroup(url)
    host_list = []
    proxy = []
    for group in all_group:
        if re.search(GNAME, group['name']):
            result = db.getHost(url, group_id=group['groupid'])
            for i in result:
                host_list.append(i)
    result = db.getProxy(url)
    for i in result:
        proxy_dict = {}
        proxy_dict['proxyid'] = i['proxyid']
        proxy_dict['name'] = i['host']
        proxy.append(proxy_dict)
    context_dict = {
        'list': host_list,
        'proxy': proxy,
        'game_name': GNAME,
    }
    return render(request, 'zabbixmanage/hostlist.html', context_dict)


def groupHostListView(request, GNAME):
    url = getCookieUrl(request)
    host_list = db.getHost(url, group_name=GNAME)
    result = db.getProxy(url)
    game_name = GNAME.split('_')[0]
    proxy = []
    for i in result:
        proxy_dict = {}
        proxy_dict['proxyid'] = i['proxyid']
        proxy_dict['name'] = i['host']
        proxy.append(proxy_dict)
    context_dict = {
        'list': host_list,
        'proxy': proxy,
        'game_name': game_name,
    }
    return render(request, 'zabbixmanage/hostlist.html', context_dict)


def updateTemplateView(request, TNAME):
    url = getCookieUrl(request)
    result = db.getTemplate(url, template_name=TNAME)
    is_linked_template = result['parentTemplates']
    template_old_id_list = [template['templateid'] for template in is_linked_template]
    if request.method == 'POST':
        template_old = [{'templateid': template_old_id_list[i]} for i in xrange(len(template_old_id_list))]
        template_id = request.POST.get('template_id')
        host_new = request.POST.get('template_host')
        name_new = request.POST.get('template_name')
        template_new_list = request.POST.getlist('linked_template_list')
        template_old_list = request.POST.getlist('is_linked_template_list')
        template_new_list[0:0] = template_old_list
        template_new = [{'templateid': template_new_list[i]} for i in xrange(len(template_new_list))]
        if 'update' in request.POST:
            macros_key = request.POST.getlist('macro_key')
            macros_value = request.POST.getlist('macro_value')
            macros = []
            for i in zip(macros_key, macros_value):
                macro_dict = {}
                if len(i[0]) >= 1 and len(i[1]) >= 1:
                    macro_dict['macro'] = i[0].strip().upper()
                    macro_dict['value'] = i[1].strip()
                if macro_dict:
                    macros.append(macro_dict)
            zabbixapi.updateTemplate(url, template_id, host_new, name_new, template_old, template_new, macros)
        return HttpResponseRedirect(reverse('updatetemplateurl', args=[TNAME]))
    else:
        template_list = db.getTemplate(url)
        macros_list = result['macros']
        macros_flag = len(macros_list)
        global_macro = zabbixapi.getGlobalMacrosInfo(url)['result']
        item_list = zabbixapi.getItemInfo(url, template_id=result['templateid'])['result']
    context_dict = {
        "template_dict": result,
        "options": template_list,
        "TNAME": TNAME,
        "is_linked": template_old_id_list,
        "is_linked_list": is_linked_template,
        'macros_flag': macros_flag,
        "global_macros": global_macro,
        "item_list": item_list,
    }
    return render(request, 'zabbixmanage/updatetemplate.html', context_dict)


def oneHostInfoView(request, HNAME):
    url = getCookieUrl(request)
    result = db.getHost(url, host_name=HNAME)
    template_current = result['parentTemplates']
    key = ['templateid' for i in range(len(template_current))]
    value = [template['templateid'] for template in template_current]
    template_old = [{key[i]: value[i]} for i in xrange(len(key))]
    if request.method == 'POST':
        template_ids = []
        host_id = request.POST.get(u'id')
        host_name = request.POST.get(u'主机名称')
        name = request.POST.get(u'可见名称')
        group_name = request.POST.get(u'主机组')
        group = [db.getGroup(url, group_name=group_name)['groupid']]
        templates = request.POST.get(u'模板')
        if len(templates):
            templates = templates.split(',')
        else:
            templates = []
        if templates:
            for template in templates:
                template = template.strip()
                template_dict = {}
                template_info = db.getTemplate(url, template_name=template)
                template_id = template_info['templateid']
                template_dict['templateid'] = template_id
                template_ids.append(template_dict)
        status = request.POST[u'主机状态']
        if 'update' in request.POST:
            macros_key = request.POST.getlist('macro_key')
            macros_value = request.POST.getlist('macro_value')
            macro_dict = {}
            macros = []
            for i in zip(macros_key, macros_value):
                macro_dict = {}
                if len(i[0]) >= 1 and len(i[1]) >= 1:
                    macro_dict['macro'] = i[0].strip().upper()
                    macro_dict['value'] = i[1].strip()
                if macro_dict:
                    macros.append(macro_dict)
            zabbixapi.updateHost(url, host_id, name, template_old, template_ids, group, status, macros)
        elif 'del-macro' in request.POST:
            macros = []
            macros_list = result['macros']
            del_macro_list = request.REQUEST.getlist('macro_list')
            macros = [macro for macro in macros_list if macro.get('macro') not in del_macro_list]
            zabbixapi.updateHost(url, host_id, name, template_old, template_ids, group, status, macros)
        return HttpResponseRedirect(reverse('hostinfourl', args=[host_name]))
    else:
        host_dict = OrderedDict()
        template_list = []
        template_list = [template['name'] for template in result['parentTemplates']]
        host_dict[u'id'] = result['hostid']
        host_dict[u'主机名称'] = result['host']
        host_dict[u'可见名称'] = result['name']
        host_dict[u'主机组'] = result['groups'][0]['name']
        host_dict[u'模板'] = ','.join(template_list)
        host_dict[u'主机状态'] = result['status']
        item_list = zabbixapi.getItemInfo(url, host_id=result['hostid'])['result']
        macros_list = result['macros']
        macros_flag = len(macros_list)
        global_macro = zabbixapi.getGlobalMacrosInfo(url)['result']
    context_dict = {
        "global_macros": global_macro,
        'host_dict': host_dict,
        'item_list': item_list,
        'macros_list': macros_list,
        'macros_flag': macros_flag,
        'HNAME': HNAME,
        'GNAME': result['groups'][0]['name'].split('_')[0],
    }
    return render(request, 'zabbixmanage/updatehost.html', context_dict)


def proxyListView(request):
    url = getCookieUrl(request)
    result = db.getProxy(url)
    lists = []
    for proxy in result:
        proxy_dict = {}
        count = len(proxy['hosts'])
        proxy_dict['count'] = count
        proxy_dict['proxy'] = proxy
        lists.append(proxy_dict)
    context_dict = {
        "proxy": lists,
    }
    return render(request, 'zabbixmanage/proxylist.html', context_dict)


def updateGroupView(request, GID):
    url = getCookieUrl(request)
    if request.method == 'POST':
        GNAME = request.POST['group_name']
        zabbixapi.updateGroup(url, group_id=GID, group_name=GNAME)
        return HttpResponseRedirect(reverse('updategroupurl', args=[GID]))
    else:
        result = db.getGroup(url, group_id=GID)
        GNAME = result['name']
    context_dict = {
        "GNAME": GNAME,
        'GID': GID,
    }
    return render(request, 'zabbixmanage/updategroup.html', context_dict)


def maintenanceListView(request):
    url = getCookieUrl(request)
    maintenance_list = []
    maintenances = db.getMaintenance(url)
    for i in maintenances:
        maintenance_dict = {}
        group_list = []
        host_list = []
        maintenance_dict['name'] = i['name']
        for groupid in i['groupids']:
            group_list.append(db.getGroup(url, group_id=groupid)['name'])
        maintenance_dict['groups'] = group_list
        for host in i['hostids']:
            host_list.append(db.getHost(url, host_id=host)['name'])
        maintenance_dict['hosts'] = host_list
        maintenance_dict['status'] = i['status']
        maintenance_list.append(maintenance_dict)
    context_dict = {
        'list': maintenance_list,
    }
    return render(request, 'zabbixmanage/maintenancelist.html', context_dict)


def calendarView(request):
    url = getCookieUrl(request)
    print request.method
    today = datetime.date.today()
    this_year = today.year
    this_month = today.month
    _, last_day = calendar.monthrange(this_year, this_month)
    this_month_list = range(today.day, last_day + 1)
    _, next_month_last_day = calendar.monthrange(this_year, this_month + 1)
    next_month_list = range(1, next_month_last_day + 1)
    this_month_calendar_list = makeCalendarList(this_month_list, this_year, this_month, url)
    next_month_calendar_list = makeCalendarList(next_month_list, this_year, this_month + 1, url)
    context_dict = {
        'this_month': this_month,
        'this_month_list': this_month_calendar_list,
        'next_month': this_month + 1,
        'next_month_list': next_month_calendar_list,
    }
    return render(request, 'zabbixmanage/calendar.html', context_dict)


def makeCalendarList(this_month_list, year, month, url):
    month_list = []
    for i in this_month_list:
        month_dict = {}
        if this_month_list[0] != 1:
            the_day = (datetime.date.today() + datetime.timedelta(days=(i - this_month_list[0]))).strftime("%Y-%m-%d %H:%M:%S")
            day_sec = time.mktime(time.strptime(the_day, '%Y-%m-%d %H:%M:%S'))
        else:
            the_day = (datetime.date(day=1, month=month, year=year) + datetime.timedelta(days=(i - this_month_list[0]))).strftime('%Y-%m-%d %H:%M:%S')
            day_sec = time.mktime(time.strptime(the_day, '%Y-%m-%d %H:%M:%S'))
        maintenance_info = db.getMaintenance(url)
        tmp_list = []
        num = 0
        for j in maintenance_info:
            tmp_dict = {}
            if day_sec < j['active_till'] and j['active_since'] - day_sec <= 86400:
                timeperiods = j['timeperiods'][0]
                if timeperiods['timeperiod_type'] == '0':
                    diff = timeperiods['start_date'] - day_sec
                    if diff <= 86400 and diff >= 0:
                        num += 1
                        tmp_dict[u'maintenancename'] = j['name']
                        tmp_dict[u'类型'] = '一次性'
                        tmp_dict[u'开始时间'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timeperiods['start_date'])).split(' ')[1]
                        tmp_dict[u'时长(h)'] = timeperiods['period'] / 3600.0
                        tmp_dict[u'组'] = ';'.join([db.getGroup(url, group_id=k)['name'] for k in j['groupids']])
                        tmp_dict[u'主机'] = ';'.join([db.getHost(url, host_id=k)['name'] for k in j['hostids']])
                        tmp_list.append(tmp_dict)
                elif timeperiods['timeperiod_type'] == '2':
                    num += 1
                    tmp_dict['maintenancename'] = j['name']
                    tmp_dict[u'类型'] = '每天'
                    tmp_dict[u'开始时间'] = time.strftime('%H:%M:%S', time.gmtime(timeperiods['start_time']))
                    tmp_dict[u'时长(h)'] = timeperiods['period'] / 3600.0
                    tmp_dict[u'组'] = ';'.join([db.getGroup(url, group_id=k)['name'] for k in j['groupids']])
                    tmp_dict[u'主机'] = ';'.join([db.getHost(url, host_id=k)['name'] for k in j['hostids']])
                    tmp_list.append(tmp_dict)
                elif timeperiods['timeperiod_type'] == '3':
                    week = binToDec(timeperiods['dayofweek'])
                    dayofweek_list = []
                    dayofweek_list.append(str(len(week)))
                    flag = len(week)
                    for k in week[1:]:
                        flag -= 1
                        if k == '1':
                            dayofweek_list.append(str(flag))
                    print dayofweek_list
                    print todayWeek(year, month, i)
                    if str(todayWeek(year, month, i)) in dayofweek_list:
                        num += 1
                        tmp_dict['maintenancename'] = j['name']
                        tmp_dict[u'类型'] = '每周'
                        tmp_dict[u'开始时间'] = time.strftime('%H:%M:%S', time.gmtime(timeperiods['start_time']))
                        tmp_dict[u'时长(h)'] = timeperiods['period'] / 3600.0
                        tmp_dict[u'组'] = ';'.join([db.getGroup(url, group_id=k)['name'] for k in j['groupids']])
                        tmp_dict[u'主机'] = ';'.join([db.getHost(url, host_id=k)['name'] for k in j['hostids']])
                        tmp_list.append(tmp_dict)
                else:
                    pass
            else:
                continue
        month_dict['day'] = i
        month_dict['job'] = num
        month_dict['week'] = todayWeek(year, month, i)
        month_dict['weekchinese'] = CHINESE_ENGILSH[month_dict['week']]
        month_dict['maintenance'] = tmp_list
        month_list.append(month_dict)
    return month_list


def todayWeek(year, month, day):
    return calendar.weekday(year, month, day) + 1


def binToDec(num):
    return bin(num).split('0b')[1]


def createMaintenanceView(request):
    url = getCookieUrl(request)
    if request.method == 'POST':
        maintenance_dict = {}
        timeperiod_dict = {}
        begin_time = request.POST.get('date-begin')
        end_time = request.POST.get('date-end')
        period_selected = request.POST.get('period')
        lasted_time = int(request.POST.get('duration')) * 60 if request.POST.get('duration') else 7200
        maintenance_name = request.POST.get('name')
        if not begin_time:
            begin_time = time.time()
        else:
            begin_time = time.mktime(time.strptime(begin_time, '%Y-%m-%d %H:%M'))
        if not end_time:
            end_time = None
        else:
            end_time = time.mktime(time.strptime(end_time, '%Y-%m-%d %H:%M'))
        if period_selected != '0':
            if period_selected == '2':
                start_time = request.POST.get('start-time').split(':')
                start_time_sec = int(start_time[0]) * 3600 + int(start_time[1]) * 60
                every = int(request.POST.get("every-day").strip())
                timeperiod_dict['every'] = every
                timeperiod_dict['start_time'] = start_time_sec
            elif period_selected == '3':
                day_of_week_dec = request.POST.getlist('day-of-week')
                day_of_week = addList(day_of_week_dec)
                start_time = request.POST.get('start-time').split(':')
                start_time_sec = int(start_time[0]) * 3600 + int(start_time[1]) * 60
                every = int(request.POST.get("every-week").strip())
                day_of_week_dec = request.POST.getlist('day-of-week')
                timeperiod_dict['dayofweek'] = day_of_week
                timeperiod_dict['every'] = every
                timeperiod_dict['start_time'] = start_time_sec
            else:
                if request.POST.get('dayorweek') == 'day':
                    month_dec = request.POST.getlist('month')
                    month = addList(month_dec)
                    start_time = request.POST.get('start-time').split(':')
                    start_time_sec = int(start_time[0]) * 3600 + int(start_time[1]) * 60
                    day = request.POST.get('which-day')
                    every = request.POST.get('which-week')
                    timeperiod_dict['day'] = day
                else:
                    month_dec = request.POST.getlist('month')
                    day_of_week_dec = request.POST.getlist('day-of-week')
                    month = addList(month_dec)
                    day_of_week = addList(day_of_week_dec)
                    start_time = request.POST.get('start-time').split(':')
                    start_time_sec = int(start_time[0]) * 3600 + int(start_time[1]) * 60
                    every = request.POST.get('which-week')
                    timeperiod_dict['dayofweek'] = day_of_week
                timeperiod_dict['every'] = every
                timeperiod_dict['month'] = month
                timeperiod_dict['start_time'] = start_time_sec
        else:
            start_time = request.POST.get('start-time-date')
            start_date_sec = int(time.mktime(time.strptime(start_time, '%Y-%m-%d %H:%M')))
            timeperiod_dict['start_date'] = start_date_sec
        all_or_some = request.POST.get('choose-hosts')
        if all_or_some == u'allhosts':
            group_id = request.POST.getlist('group_id')
            maintenance_dict['groupids'] = group_id
            maintenance_dict['hostids'] = []
        else:
            host_ids = []
            group_id = request.POST.getlist('group_id')
            host_list = request.POST.getlist('host_list')
            for host in host_list:
                host_ids.append(db.getHost(url, host_name=host)['hostid'])
            maintenance_dict['groupids'] = group_id
            maintenance_dict['hostids'] = []
            if host_ids:
                maintenance_dict['hostids'] = host_ids
        maintenance_dict['name'] = maintenance_name
        maintenance_dict['active_since'] = begin_time
        maintenance_dict['active_till'] = end_time
        timeperiod_dict['timeperiod_type'] = period_selected
        timeperiod_dict['period'] = lasted_time
        maintenance_dict['timeperiods'] = [timeperiod_dict]
        if period_selected == '0':
            result = zabbixapi.createMaintenance(url, params=[maintenance_dict])
            if 'result' in result:
                maintenance_dict['status'] = 0
                db.createMaintenance(url, maintenance_dict)
        else:
            document = copy.deepcopy(maintenance_dict)
            time_now = int(time.time())
            maintenance_dict['active_since'] = time_now
            maintenance_dict['active_till'] = time_now
            result = zabbixapi.createMaintenance(url, params=[maintenance_dict])
            if 'result' in result:
                document['status'] = 0
                db.createMaintenance(url, document)
        return HttpResponseRedirect(reverse('createmaintenanceurl'))
    else:
        project_list = Game.objects.all()
    context_dict = {
        'project_list': project_list,
    }
    return render(request, 'zabbixmanage/createmaintenance.html', context_dict)


def groupInProjectView(request):
    url = getCookieUrl(request)
    project_name = request.POST.get('PROJECT')
    collection = db.processUrl(url)
    database = db.connDB(collection, 'host_group')
    document = database.find({'name': re.compile(project_name)})
    host_lists = []
    project_list = []
    result = {}
    for doc in document:
        project_dict = {}
        project_dict['name'] = doc['name']
        project_dict['groupid'] = doc['groupid']
        hosts = db.getHost(url, group_id=doc['groupid'])
        for host in hosts:
            host_list = []
            host_list.append(host['host'])
            host_list.append(host['name'])
            host_list.append(host['groups'][0]['name'])
            host_lists.append(host_list)
        project_list.append(project_dict)
    result['group'] = project_list
    result['hosts'] = host_lists
    return JsonResponse(result, safe=False)


@csrf_exempt
def startMaintenanceView(request):
    print request.method
    if request.method == 'POST':
        try:
            url = request.POST.get('url')
            url = "http://" + url + "/api_jsonrpc.php"
            maintenance_name = request.POST.get('name')
            start_time = int(request.POST.get('start'))
            end_time = start_time + 86400
            x = time.localtime(start_time)
            hour = time.strftime('%Y-%m-%d %H:%M:%S', x).split(' ')[1].split(':')
            hour_sec = int(hour[0]) * 3600 + int(hour[1]) * 60
            maintenance_info = db.getMaintenance(url, maintenance_name)
            status = maintenance_info['status']
            if status == 1:
                error = zabbixapi.processLogData('start maintenance', {'maintenance_name': maintenance_name}, url, {'info': "状态已经为1"}, 'error')
                db.insertLog(log=error)
                return HttpResponse('start error! already start')
        except Exception, e:
            return HttpResponse('start error! %s' %e)
        else:
            try:
                zabbixapi.startMaintenance(url, maintenance_name, start_time, end_time, hour_sec)
            except Exception, e:
                return HttpResponse('start error! %s' %e)
            else:
                return HttpResponse('start success')
    else:
        return HttpResponse('start error! you need use POST method')


@csrf_exempt
def stopMaintenanceView(request):
    if request.method == 'POST':
        try:
            url = request.POST.get('url')
            url = "http://" + url + "/api_jsonrpc.php"
            maintenance_name = request.POST.get('name')
            end_time = int(request.POST.get('end'))
            maintenance_info = db.getMaintenance(url, maintenance_name)
            status = maintenance_info['status']
            if status == 0:
                error = zabbixapi.processLogData('stop maintenance', {'maintenance_name': maintenance_name}, url, {"info": "状态已经为0"}, 'error')
                db.insertLog(log=error)
                return HttpResponse('stop error! already stop')
        except Exception, e:
            return HttpResponse('stop error! %s' %e)
        else:
            try:
                zabbixapi.stopMaintenance(url, maintenance_name, end_time)
            except Exception, e:
                return HttpResponse('stop error! %s' %e)
            else:
                return HttpResponse('stop success')
    else:
        return HttpResponse('stop error! you need use POST method')


def addList(dec_num_list):
    sum = 0
    for dec_num in dec_num_list:
        sum += decsToBins(int(dec_num))
    return sum


def decsToBins(num):
    return int(('1' + '0' * (num - 1)), 2)
